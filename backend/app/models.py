from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class Workspace(Base):
    __tablename__ = "workspace"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class WorkspaceMember(Base):
    __tablename__ = "workspace_member"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspace.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (UniqueConstraint("workspace_id", "user_id", name="uq_workspace_member_workspace_user"),)


class WatchlistEntity(Base):
    __tablename__ = "watchlist_entity"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspace.id"), nullable=False, index=True)
    chain: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    entity_value: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(128), nullable=True)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (UniqueConstraint("workspace_id", "chain", "entity_value", name="uq_watchlist_workspace_chain_entity"),)


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

    __table_args__ = (Index("ix_transfer_edge_src_dst", "src_entity", "dst_entity"),)


class TrackedEntity(Base):
    __tablename__ = "tracked_entity"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    chain: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    entity_value: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(128), nullable=True)
