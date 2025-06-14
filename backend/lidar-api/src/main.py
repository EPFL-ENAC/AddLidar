import asyncio
import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from pydantic import ValidationError
from pathlib import Path
import logging

from src.api.routes import router as public_router
from src.api.sqlite.index import public_router as sqlite_public_router
from src.api.sqlite.index import internal_router as sqlite_internal_router
from src.config.settings import settings


# Create public app (external access)
public_app = FastAPI(title="AddLidar API - Public", root_path=settings.PATH_PREFIX)

# Create internal app (cluster-only access)
internal_app = FastAPI(title="AddLidar API - Internal", root_path=settings.PATH_PREFIX)


# Shared exception handler
@public_app.exception_handler(ValidationError)
@internal_app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": exc.model.model_dump() if exc.model else None,
        },
    )


# Public app routes
@public_app.get("/")
async def get_index():
    index_path = Path(__file__).parent.parent / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Welcome to AddLidar API"}


# Internal app routes
@internal_app.get("/")
async def get_internal_index():
    return {"message": "AddLidar Internal API - Cluster Access Only"}


@internal_app.get("/health")
async def internal_health():
    return {"status": "healthy", "service": "internal"}


# Register routers
public_app.include_router(public_router)
internal_app.include_router(sqlite_internal_router, tags=["sqlite"])
public_app.include_router(sqlite_public_router, tags=["sqlite"])


# Single startup function to run both servers
async def run_servers():

    public_port = int(os.getenv("PUBLIC_PORT", 8000))
    internal_port = int(os.getenv("INTERNAL_PORT", 8001))

    config_public = uvicorn.Config(
        app=public_app,
        host="0.0.0.0",
        port=public_port,
        log_level="info",
    )
    config_internal = uvicorn.Config(
        app=internal_app,
        host="0.0.0.0",
        port=internal_port,
        log_level="info",
    )

    server_public = uvicorn.Server(config_public)
    server_internal = uvicorn.Server(config_internal)

    await asyncio.gather(server_public.serve(), server_internal.serve())


if __name__ == "__main__":
    asyncio.run(run_servers())

# For backwards compatibility when running with uvicorn directly
app = public_app
