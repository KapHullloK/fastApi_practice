from contextlib import asynccontextmanager
from datetime import datetime, time

import uvicorn
from fastapi import FastAPI, Request
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from starlette.middleware.cors import CORSMiddleware

from app.api import routers
from app.config.settings import settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    redis = aioredis.from_url(settings.redis.dsn, encoding="utf-8", decode_responses=False)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    try:
        yield
    finally:
        await redis.close()


def create_app() -> FastAPI:
    prefix = settings.app.path_prefix or ""
    app = FastAPI(
        title="fastApi_",
        openapi_url=f"{prefix}/openapi.json",
        docs_url=f"{prefix}/docs",
        redoc_url=f"{prefix}/redoc",
        lifespan=lifespan,
    )
    app.state.cache_last_reset_date = None

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def reset_cache(request: Request, call_next):
        now = datetime.now()
        reset_time = time(settings.cache.reset_hour, settings.cache.reset_minute)

        if now.time() >= reset_time and app.state.cache_last_reset_date != now.date():
            await FastAPICache.clear()
            app.state.cache_last_reset_date = now.date()

        return await call_next(request)

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
