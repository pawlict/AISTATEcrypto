from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.flow_service import FlowQuery, load_flow_graph
from app.models import Workspace, WorkspaceMember
from app.schemas import (
    AddWorkspaceMemberRequest,
    FlowResponse,
    HealthResponse,
    UserContextResponse,
    WatchlistEntityRequest,
    WatchlistEntityResponse,
    WorkspaceCreateRequest,
    WorkspaceMembershipResponse,
    WorkspaceResponse,
)
from app.workspace_service import (
    add_watchlist_entity,
    add_workspace_member,
    create_workspace,
    get_or_create_user,
    list_user_workspaces,
    list_watchlist,
    require_role,
    require_workspace_member,
)

router = APIRouter()


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(x_user_email: str | None = Header(default=None), db: Session = Depends(get_db)):
    if not x_user_email:
        raise HTTPException(status_code=401, detail="Missing X-User-Email header")
    return get_or_create_user(db, x_user_email)


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/me", response_model=UserContextResponse)
def me(user=Depends(get_current_user)) -> UserContextResponse:
    return UserContextResponse(id=user.id, email=user.email, display_name=user.display_name)


@router.post("/workspaces", response_model=WorkspaceResponse)
def create_workspace_endpoint(
    body: WorkspaceCreateRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> WorkspaceResponse:
    ws = create_workspace(db, user=user, name=body.name)
    return WorkspaceResponse(id=ws.id, name=ws.name, created_by_user_id=ws.created_by_user_id)


@router.get("/workspaces", response_model=list[WorkspaceResponse])
def list_workspaces_endpoint(db: Session = Depends(get_db), user=Depends(get_current_user)) -> list[WorkspaceResponse]:
    memberships = list_user_workspaces(db, user_id=user.id)
    workspace_ids = [m.workspace_id for m in memberships]
    if not workspace_ids:
        return []

    workspaces = db.execute(select(Workspace).where(Workspace.id.in_(workspace_ids))).scalars().all()
    return [WorkspaceResponse(id=w.id, name=w.name, created_by_user_id=w.created_by_user_id) for w in workspaces]


@router.post("/workspaces/{workspace_id}/members", response_model=WorkspaceMembershipResponse)
def add_workspace_member_endpoint(
    workspace_id: int,
    body: AddWorkspaceMemberRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> WorkspaceMembershipResponse:
    membership = require_workspace_member(db, user_id=user.id, workspace_id=workspace_id)
    require_role(membership, {"owner"})

    added = add_workspace_member(db, workspace_id=workspace_id, email=body.email, role=body.role)
    return WorkspaceMembershipResponse(workspace_id=added.workspace_id, user_id=added.user_id, role=added.role)


@router.get("/workspaces/{workspace_id}/members", response_model=list[WorkspaceMembershipResponse])
def list_workspace_members_endpoint(
    workspace_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> list[WorkspaceMembershipResponse]:
    require_workspace_member(db, user_id=user.id, workspace_id=workspace_id)
    members = db.execute(select(WorkspaceMember).where(WorkspaceMember.workspace_id == workspace_id)).scalars().all()
    return [
        WorkspaceMembershipResponse(workspace_id=m.workspace_id, user_id=m.user_id, role=m.role)
        for m in members
    ]


@router.post("/workspaces/{workspace_id}/watchlist", response_model=WatchlistEntityResponse)
def add_watchlist_endpoint(
    workspace_id: int,
    body: WatchlistEntityRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> WatchlistEntityResponse:
    membership = require_workspace_member(db, user_id=user.id, workspace_id=workspace_id)
    require_role(membership, {"owner", "analyst"})

    row = add_watchlist_entity(
        db,
        workspace_id=workspace_id,
        user_id=user.id,
        chain=body.chain,
        entity_type=body.entity_type,
        entity_value=body.entity_value,
        label=body.label,
    )
    return WatchlistEntityResponse(
        id=row.id,
        workspace_id=row.workspace_id,
        chain=row.chain,
        entity_type=row.entity_type,
        entity_value=row.entity_value,
        label=row.label,
        created_by_user_id=row.created_by_user_id,
    )


@router.get("/workspaces/{workspace_id}/watchlist", response_model=list[WatchlistEntityResponse])
def list_watchlist_endpoint(
    workspace_id: int,
    chain: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> list[WatchlistEntityResponse]:
    require_workspace_member(db, user_id=user.id, workspace_id=workspace_id)
    rows = list_watchlist(db, workspace_id=workspace_id, chain=chain)
    return [
        WatchlistEntityResponse(
            id=r.id,
            workspace_id=r.workspace_id,
            chain=r.chain,
            entity_type=r.entity_type,
            entity_value=r.entity_value,
            label=r.label,
            created_by_user_id=r.created_by_user_id,
        )
        for r in rows
    ]


@router.get("/flow/{chain}/{entity}", response_model=FlowResponse)
def flow(
    chain: str,
    entity: str,
    workspace_id: int = Query(..., description="Workspace scope for access control"),
    time_from: datetime | None = Query(default=None),
    time_to: datetime | None = Query(default=None),
    min_amount_sats: int | None = Query(default=None, ge=0),
    max_edges: int = Query(default=500, ge=1, le=2000),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> FlowResponse:
    require_workspace_member(db, user_id=user.id, workspace_id=workspace_id)

    payload = load_flow_graph(
        db,
        FlowQuery(
            chain=chain,
            entity=entity,
            time_from=time_from,
            time_to=time_to,
            min_amount_sats=min_amount_sats,
            max_edges=max_edges,
        ),
    )
    payload["meta"]["workspace_id"] = workspace_id
    return FlowResponse.model_validate(payload)
