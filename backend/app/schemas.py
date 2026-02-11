from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class SyncResult(BaseModel):
    chain: str
    processed_blocks: int
    processed_transactions: int
    processed_edges: int
