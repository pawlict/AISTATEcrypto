from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Select, and_, or_, select
from sqlalchemy.orm import Session

from app.models import TransferEdge


@dataclass
class FlowQuery:
    chain: str
    entity: str
    time_from: datetime | None = None
    time_to: datetime | None = None
    min_amount_sats: int | None = None
    max_edges: int = 500


def _build_stmt(query: FlowQuery) -> Select[tuple[TransferEdge]]:
    conditions = [TransferEdge.chain == query.chain]
    conditions.append(or_(TransferEdge.src_entity == query.entity, TransferEdge.dst_entity == query.entity))

    if query.time_from is not None:
        conditions.append(TransferEdge.block_time >= query.time_from)
    if query.time_to is not None:
        conditions.append(TransferEdge.block_time <= query.time_to)
    if query.min_amount_sats is not None:
        conditions.append(TransferEdge.amount_sats >= query.min_amount_sats)

    return (
        select(TransferEdge)
        .where(and_(*conditions))
        .order_by(TransferEdge.block_time.desc(), TransferEdge.id.desc())
        .limit(max(query.max_edges, 1))
    )


def load_flow_graph(db: Session, query: FlowQuery) -> dict:
    stmt = _build_stmt(query)
    rows = db.execute(stmt).scalars().all()

    nodes_map: dict[str, dict] = {}
    edges: list[dict] = []

    inbound_count: dict[str, int] = defaultdict(int)
    outbound_count: dict[str, int] = defaultdict(int)

    for edge in rows:
        for entity in (edge.src_entity, edge.dst_entity):
            if entity not in nodes_map:
                node_type = "address"
                if entity in {"unknown", "coinbase"}:
                    node_type = "system"
                nodes_map[entity] = {"id": entity, "type": node_type}

        outbound_count[edge.src_entity] += 1
        inbound_count[edge.dst_entity] += 1

        edges.append(
            {
                "id": f"{edge.tx_hash}:{edge.id}",
                "source": edge.src_entity,
                "target": edge.dst_entity,
                "value": edge.amount_sats,
                "tx_hash": edge.tx_hash,
                "asset": edge.asset_symbol,
                "block_time": edge.block_time.isoformat(),
            }
        )

    nodes = []
    for entity, node in nodes_map.items():
        nodes.append(
            {
                **node,
                "in_degree": inbound_count[entity],
                "out_degree": outbound_count[entity],
                "is_focus": entity == query.entity,
            }
        )

    return {
        "chain": query.chain,
        "entity": query.entity,
        "nodes": nodes,
        "edges": edges,
        "meta": {
            "from": query.time_from.isoformat() if query.time_from else None,
            "to": query.time_to.isoformat() if query.time_to else None,
            "hops": 1,
            "returned_edges": len(edges),
            "max_edges": query.max_edges,
            "min_amount_sats": query.min_amount_sats,
        },
    }
