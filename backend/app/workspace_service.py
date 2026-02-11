from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import User, WatchlistEntity, Workspace, WorkspaceMember

VALID_ROLES = {"owner", "analyst", "viewer"}


@dataclass
class AuthContext:
    user: User
    membership: WorkspaceMember


def get_or_create_user(db: Session, email: str) -> User:
    email = email.strip().lower()
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if user is not None:
        return user

    user = User(email=email, display_name=email.split("@")[0], created_at=datetime.now(timezone.utc))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_workspace(db: Session, user: User, name: str) -> Workspace:
    ws = Workspace(name=name.strip(), created_by_user_id=user.id, created_at=datetime.now(timezone.utc))
    db.add(ws)
    db.flush()

    member = WorkspaceMember(
        workspace_id=ws.id,
        user_id=user.id,
        role="owner",
        created_at=datetime.now(timezone.utc),
    )
    db.add(member)
    db.commit()
    db.refresh(ws)
    return ws


def list_user_workspaces(db: Session, user_id: int) -> list[WorkspaceMember]:
    return db.execute(select(WorkspaceMember).where(WorkspaceMember.user_id == user_id)).scalars().all()


def require_workspace_member(db: Session, user_id: int, workspace_id: int) -> WorkspaceMember:
    membership = db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.user_id == user_id,
            WorkspaceMember.workspace_id == workspace_id,
        )
    ).scalar_one_or_none()
    if membership is None:
        raise HTTPException(status_code=403, detail="User is not a member of this workspace")
    return membership


def require_role(membership: WorkspaceMember, allowed: set[str]) -> None:
    if membership.role not in allowed:
        raise HTTPException(status_code=403, detail="Insufficient workspace role")


def add_workspace_member(db: Session, workspace_id: int, email: str, role: str) -> WorkspaceMember:
    if role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Unsupported role. Allowed: {sorted(VALID_ROLES)}")

    user = get_or_create_user(db, email=email)
    member = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=user.id,
        role=role,
        created_at=datetime.now(timezone.utc),
    )
    db.add(member)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Member already exists in workspace") from exc
    db.refresh(member)
    return member


def list_watchlist(db: Session, workspace_id: int, chain: str | None = None) -> list[WatchlistEntity]:
    stmt = select(WatchlistEntity).where(WatchlistEntity.workspace_id == workspace_id)
    if chain:
        stmt = stmt.where(WatchlistEntity.chain == chain)
    return db.execute(stmt.order_by(WatchlistEntity.id.desc())).scalars().all()


def add_watchlist_entity(
    db: Session,
    workspace_id: int,
    user_id: int,
    chain: str,
    entity_type: str,
    entity_value: str,
    label: str | None,
) -> WatchlistEntity:
    row = WatchlistEntity(
        workspace_id=workspace_id,
        chain=chain.lower(),
        entity_type=entity_type,
        entity_value=entity_value,
        label=label,
        created_by_user_id=user_id,
        created_at=datetime.now(timezone.utc),
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Entity already exists in watchlist") from exc
    db.refresh(row)
    return row
