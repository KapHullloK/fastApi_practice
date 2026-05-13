from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api import routers
from app.context import build_app_context
from app.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.context = build_app_context()
    try:
        yield
    finally:
        await app.state.context.cache_manager.close()


def create_app() -> FastAPI:
    prefix = settings.app.path_prefix or ""
    app = FastAPI(
        title="fastApi_",
        openapi_url=f"{prefix}/openapi.json",
        docs_url=f"{prefix}/docs",
        redoc_url=f"{prefix}/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    for router in routers:
        app.include_router(router, prefix=prefix)
    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "app.__main__:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=True,
    )
