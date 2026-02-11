#!/usr/bin/env python3
import argparse
import logging

from app.btc_ingest import ingest_recent_blocks
from app.db import SessionLocal
from app.init_db import init_db


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync recent BTC blocks")
    parser.add_argument("--blocks", type=int, default=3, help="How many recent blocks to ingest")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    init_db()
    with SessionLocal() as db:
        stats = ingest_recent_blocks(db=db, blocks_count=args.blocks)

    print(
        f"Done: chain=btc blocks={stats.processed_blocks} "
        f"tx={stats.processed_transactions} edges={stats.processed_edges}"
    )


if __name__ == "__main__":
    main()
