import hashlib
import json
import logging
from functools import wraps
from inspect import Parameter, Signature, signature
from typing import Any, Awaitable, Callable, TypeVar, cast

from fastapi.dependencies.utils import get_typed_signature
from fastapi_cache.coder import JsonCoder
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.manager import CacheManager
from app.context import AppContext

logger = logging.getLogger(__name__)
R = TypeVar("R")
_CACHE_KEY_EXCLUDE_ATTR = "__cache_key_exclude__"


def _normalize(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, (list, tuple)):
        return [_normalize(v) for v in value]
    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in value.items()}
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _should_include_in_cache_key(value: Any) -> bool:
    if isinstance(value, (Request, Response, AsyncSession)):
        return False
    if getattr(value, _CACHE_KEY_EXCLUDE_ATTR, False):
        return False
    return True


def api_cache_key_builder(func, namespace: str = "", **kwargs) -> str:
    route_args = kwargs.get("args", ())
    route_kwargs = kwargs.get("kwargs", {})
    filtered_route_args = [value for value in route_args if _should_include_in_cache_key(value)]
    filtered_route_kwargs = {k: v for k, v in route_kwargs.items() if _should_include_in_cache_key(v)}
    payload = {
        "namespace": namespace,
        "func": f"{func.__module__}.{func.__name__}",
        "args": _normalize(filtered_route_args),
        "kwargs": _normalize(filtered_route_kwargs),
    }
    serialized = json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str)
    return f"cache:{hashlib.sha256(serialized.encode('utf-8')).hexdigest()}"


def _augment_signature(signature_obj: Signature, *extra: Parameter) -> Signature:
    if not extra:
        return signature_obj

    parameters = list(signature_obj.parameters.values())
    variadic_keyword_params: list[Parameter] = []
    while parameters and parameters[-1].kind is Parameter.VAR_KEYWORD:
        variadic_keyword_params.append(parameters.pop())

    return signature_obj.replace(parameters=[*parameters, *extra, *variadic_keyword_params])


def _locate_param(signature_obj: Signature, dep: Parameter, to_inject: list[Parameter]) -> Parameter:
    param = next(
        (parameter for parameter in signature_obj.parameters.values() if parameter.annotation is dep.annotation), None
    )
    if param is None:
        to_inject.append(dep)
        param = dep
    return param


def _get_cache_manager(request: Request) -> CacheManager:
    context = getattr(request.app.state, "context", None)
    if not isinstance(context, AppContext):
        raise RuntimeError("AppContext is not configured")
    return context.cache_manager


def cache_until_reset(
        key_builder: Callable[..., str] = api_cache_key_builder,
        namespace: str = "",
) -> Callable[[Callable[..., Awaitable[R]]], Callable[..., Awaitable[R]]]:
    def decorator(func: Callable[..., Awaitable[R]]) -> Callable[..., Awaitable[R]]:
        request_dependency = Parameter(
            name="__cache_request",
            annotation=Request,
            kind=Parameter.KEYWORD_ONLY,
        )
        typed_signature = get_typed_signature(func)
        injected_params: list[Parameter] = []
        request_param = _locate_param(typed_signature, request_dependency, injected_params)
        return_type = signature(func).return_annotation

        @wraps(func)
        async def inner(*args, **kwargs) -> R:
            request = kwargs.pop(request_param.name, None)
            if not isinstance(request, Request):
                raise RuntimeError("Request is not available for cached endpoint")
            cache_manager = _get_cache_manager(request)
            backend = cache_manager.get_backend()
            coder = JsonCoder
            cache_key = key_builder(
                func,
                cache_manager.get_namespace(namespace),
                args=args,
                kwargs=kwargs,
            )

            try:
                _, cached = await backend.get_with_ttl(cache_key)
            except Exception:
                logger.warning("Error retrieving cache key '%s' from backend", cache_key, exc_info=True)
                cached = None

            if cached is None:
                result = await func(*args, **kwargs)
                try:
                    await backend.set(cache_key, coder.encode(result), cache_manager.seconds_until_reset())
                except Exception:
                    logger.warning("Error setting cache key '%s' in backend", cache_key, exc_info=True)
                return result

            if return_type is Signature.empty:
                return cast(R, coder.decode(cached))
            return cast(R, coder.decode_as_type(cached, type_=return_type))

        inner.__signature__ = _augment_signature(typed_signature, *injected_params)
        return inner

    return decorator
