import unittest
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.flow_service import FlowQuery, load_flow_graph
from app.models import TransferEdge


class FlowServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        engine = create_engine("sqlite:///:memory:", future=True)
        Base.metadata.create_all(bind=engine)
        self.Session = sessionmaker(bind=engine, future=True)

        with self.Session() as db:
            db.add_all(
                [
                    TransferEdge(
                        chain="btc",
                        tx_hash="tx-1",
                        src_entity="addr-a",
                        dst_entity="addr-b",
                        amount_sats=1200,
                        asset_symbol="BTC",
                        block_time=datetime(2024, 1, 1, tzinfo=timezone.utc),
                    ),
                    TransferEdge(
                        chain="btc",
                        tx_hash="tx-2",
                        src_entity="addr-c",
                        dst_entity="addr-a",
                        amount_sats=3300,
                        asset_symbol="BTC",
                        block_time=datetime(2024, 1, 2, tzinfo=timezone.utc),
                    ),
                    TransferEdge(
                        chain="eth",
                        tx_hash="tx-3",
                        src_entity="addr-a",
                        dst_entity="addr-z",
                        amount_sats=1,
                        asset_symbol="ETH",
                        block_time=datetime(2024, 1, 3, tzinfo=timezone.utc),
                    ),
                ]
            )
            db.commit()

    def test_load_flow_graph_filters_by_chain_and_entity(self) -> None:
        with self.Session() as db:
            response = load_flow_graph(
                db,
                FlowQuery(chain="btc", entity="addr-a", max_edges=10),
            )

        self.assertEqual(response["chain"], "btc")
        self.assertEqual(response["entity"], "addr-a")
        self.assertEqual(len(response["edges"]), 2)
        self.assertTrue(any(node["is_focus"] for node in response["nodes"]))

    def test_load_flow_graph_respects_min_amount(self) -> None:
        with self.Session() as db:
            response = load_flow_graph(
                db,
                FlowQuery(chain="btc", entity="addr-a", min_amount_sats=2000, max_edges=10),
            )

        self.assertEqual(len(response["edges"]), 1)
        self.assertEqual(response["edges"][0]["tx_hash"], "tx-2")


if __name__ == "__main__":
    unittest.main()
