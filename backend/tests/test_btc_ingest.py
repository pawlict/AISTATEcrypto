import unittest
from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.btc_ingest import IngestStats, ingest_recent_blocks
from app.db import Base
from app.models import ChainTransaction, TransferEdge


class FakeClient:
    def get_tip_height(self) -> int:
        return 100

    def get_block_hash(self, height: int) -> str:
        return f"block-{height}"

    def get_block_txs(self, block_hash: str) -> list[dict]:
        return [
            {
                "txid": f"{block_hash}-tx1",
                "fee": 111,
                "status": {"block_time": int(datetime(2024, 1, 1, tzinfo=timezone.utc).timestamp())},
                "vin": [{"prevout": {"scriptpubkey_address": "addr-in-1"}}],
                "vout": [{"scriptpubkey_address": "addr-out-1", "value": 5000}],
            }
        ]


class IngestTests(unittest.TestCase):
    def setUp(self) -> None:
        engine = create_engine("sqlite:///:memory:", future=True)
        Base.metadata.create_all(bind=engine)
        self.Session = sessionmaker(bind=engine, future=True)

    def test_ingest_recent_blocks_saves_transactions_and_edges(self) -> None:
        with self.Session() as db:
            stats: IngestStats = ingest_recent_blocks(db=db, blocks_count=2, client=FakeClient())

        self.assertEqual(stats.processed_blocks, 2)
        self.assertEqual(stats.processed_transactions, 2)
        self.assertEqual(stats.processed_edges, 2)

        with self.Session() as db:
            tx_count = db.execute(select(ChainTransaction)).scalars().all()
            edge_count = db.execute(select(TransferEdge)).scalars().all()

        self.assertEqual(len(tx_count), 2)
        self.assertEqual(len(edge_count), 2)


if __name__ == "__main__":
    unittest.main()
