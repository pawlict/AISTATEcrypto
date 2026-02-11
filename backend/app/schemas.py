from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


class SyncResult(BaseModel):
    chain: str
    processed_blocks: int
    processed_transactions: int
    processed_edges: int


class FlowNode(BaseModel):
    id: str
    type: str
    in_degree: int
    out_degree: int
    is_focus: bool


class FlowEdge(BaseModel):
    id: str
    source: str
    target: str
    value: int
    tx_hash: str
    asset: str
    block_time: str


class FlowResponse(BaseModel):
    chain: str
    entity: str
    nodes: list[FlowNode]
    edges: list[FlowEdge]
    meta: dict


class UserContextResponse(BaseModel):
    id: int
    email: str
    display_name: str | None = None


class WorkspaceCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=128)


class WorkspaceResponse(BaseModel):
    id: int
    name: str
    created_by_user_id: int


class WorkspaceMembershipResponse(BaseModel):
    workspace_id: int
    user_id: int
    role: str


class AddWorkspaceMemberRequest(BaseModel):
    email: str
    role: str


class WatchlistEntityRequest(BaseModel):
    chain: str
    entity_type: str
    entity_value: str
    label: str | None = None


class WatchlistEntityResponse(BaseModel):
    id: int
    workspace_id: int
    chain: str
    entity_type: str
    entity_value: str
    label: str | None = None
    created_by_user_id: int
