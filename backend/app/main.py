from fastapi import FastAPI

from app.api import router
from app.init_db import init_db

app = FastAPI(title="AISTATEcrypto backend", version="0.1.0")
app.include_router(router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
