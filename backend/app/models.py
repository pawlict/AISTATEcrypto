from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class ChainTransaction(Base):
    __tablename__ = "chain_transaction"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chain: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    tx_hash: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    block_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    block_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    fee_sats: Mapped[int] = mapped_column(Integer, nullable=False)
    raw_json: Mapped[str] = mapped_column(Text, nullable=False)


class TransferEdge(Base):
    __tablename__ = "transfer_edge"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chain: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    tx_hash: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    src_entity: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    dst_entity: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    amount_sats: Mapped[int] = mapped_column(Integer, nullable=False)
    asset_symbol: Mapped[str] = mapped_column(String(16), nullable=False, default="BTC")
    block_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    __table_args__ = (
        Index("ix_transfer_edge_src_dst", "src_entity", "dst_entity"),
    )


class TrackedEntity(Base):
    __tablename__ = "tracked_entity"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    chain: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    entity_value: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(128), nullable=True)
