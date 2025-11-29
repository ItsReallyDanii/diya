from fastapi import FastAPI

from .api.v1 import router as api_router
from .db import models, session

app = FastAPI(title="DIYA backend v1")
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
def on_startup() -> None:
    models.Base.metadata.create_all(bind=session.engine)
