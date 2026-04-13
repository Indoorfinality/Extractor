from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .dependencies import get_db
from .routes import studio, prompt, document, extraction, deployment
from . import models  # noqa: F401

app = FastAPI(title = "DocExtractor Prompt Studio API", version = "0.1")

app.include_router(studio.router, prefix="/api/studios", tags=["studios"])
app.include_router(prompt.router, prefix="/api/prompts", tags=["prompts"])
app.include_router(document.router, prefix="/api/documents", tags=["documents"])
app.include_router(extraction.router, prefix="/api/extraction", tags=["extraction"])
app.include_router(deployment.router, prefix='/api/deployments', tags=['deployments'])


@app.get("/health")
def health(_: Session = Depends(get_db)):
    return {"status": "ok", "db": "connected"}
