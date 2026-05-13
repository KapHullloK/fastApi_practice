from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Request

from app.cache.manager import CacheManager
from app.config.settings import settings


@dataclass(slots=True)
class AppContext:
    cache_manager: CacheManager


def build_app_context() -> AppContext:
    return AppContext(
        cache_manager=CacheManager(
            redis_dsn=settings.redis.dsn,
            prefix=settings.cache.prefix,
            reset_hour=settings.cache.reset_hour,
            reset_minute=settings.cache.reset_minute,
        )
    )


def get_app_context(request: Request) -> AppContext:
    return request.app.state.context


ContextDep = Annotated[AppContext, Depends(get_app_context)]
