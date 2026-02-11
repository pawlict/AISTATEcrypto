import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone

import requests
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import BLOCKSTREAM_API_URL
from app.models import ChainTransaction, TransferEdge

logger = logging.getLogger(__name__)


@dataclass
class IngestStats:
    processed_blocks: int = 0
    processed_transactions: int = 0
    processed_edges: int = 0


class BlockstreamClient:
    def __init__(self, base_url: str = BLOCKSTREAM_API_URL, timeout_s: int = 20) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s

    def get_tip_height(self) -> int:
        response = requests.get(f"{self.base_url}/blocks/tip/height", timeout=self.timeout_s)
        response.raise_for_status()
        return int(response.text)

    def get_block_hash(self, height: int) -> str:
        response = requests.get(f"{self.base_url}/block-height/{height}", timeout=self.timeout_s)
        response.raise_for_status()
        return response.text.strip()

    def get_block_txs(self, block_hash: str) -> list[dict]:
        response = requests.get(f"{self.base_url}/block/{block_hash}/txs", timeout=self.timeout_s)
        response.raise_for_status()
        return response.json()


def _extract_addresses(vin_or_vout: dict) -> list[str]:
    prev = vin_or_vout.get("prevout")
    scriptpubkey_address = vin_or_vout.get("scriptpubkey_address")
    if scriptpubkey_address:
        return [scriptpubkey_address]
    if isinstance(prev, dict) and prev.get("scriptpubkey_address"):
        return [prev["scriptpubkey_address"]]
    return ["unknown"]


def _block_time_from_tx(tx: dict) -> datetime:
    block_time = tx.get("status", {}).get("block_time")
    if block_time is None:
        return datetime.now(timezone.utc)
    return datetime.fromtimestamp(block_time, tz=timezone.utc)


def ingest_recent_blocks(db: Session, blocks_count: int, client: BlockstreamClient | None = None) -> IngestStats:
    if blocks_count <= 0:
        return IngestStats()

    client = client or BlockstreamClient()
    tip_height = client.get_tip_height()
    stats = IngestStats()

    for height in range(tip_height - blocks_count + 1, tip_height + 1):
        block_hash = client.get_block_hash(height)
        txs = client.get_block_txs(block_hash)
        stats.processed_blocks += 1

        for tx in txs:
            tx_hash = tx["txid"]
            existing_tx = db.execute(select(ChainTransaction.id).where(ChainTransaction.tx_hash == tx_hash)).scalar_one_or_none()
            if existing_tx is not None:
                continue

            block_time = _block_time_from_tx(tx)
            fee_sats = int(tx.get("fee", 0))

            db.add(
                ChainTransaction(
                    chain="btc",
                    tx_hash=tx_hash,
                    block_number=height,
                    block_time=block_time,
                    fee_sats=fee_sats,
                    raw_json=json.dumps(tx),
                )
            )
            stats.processed_transactions += 1

            input_addresses: list[str] = []
            for vin in tx.get("vin", []):
                input_addresses.extend(_extract_addresses(vin))

            if not input_addresses:
                input_addresses = ["coinbase"]

            for vout in tx.get("vout", []):
                output_addresses = _extract_addresses(vout)
                value = int(vout.get("value", 0))
                for src in input_addresses:
                    for dst in output_addresses:
                        db.add(
                            TransferEdge(
                                chain="btc",
                                tx_hash=tx_hash,
                                src_entity=src,
                                dst_entity=dst,
                                amount_sats=value,
                                asset_symbol="BTC",
                                block_time=block_time,
                            )
                        )
                        stats.processed_edges += 1

        db.commit()
        logger.info("Processed BTC block height=%s txs=%s", height, len(txs))

    return stats
