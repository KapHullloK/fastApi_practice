import hashlib
import json
from typing import Any

from pydantic import BaseModel


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


def api_cache_key_builder(
    func,
    namespace: str = "",
    *,
    request=None,
    response=None,
    **kwargs,
) -> str:
    filtered_kwargs = {k: v for k, v in kwargs.items() if k not in {"session", "response", "request"}}
    normalized = _normalize(filtered_kwargs)

    payload = {
        "namespace": namespace,
        "func": func.__module__ + "." + func.__name__,
        "path": getattr(request.url, "path", "") if request else "",
        "query": dict(request.query_params) if request else {},
        "kwargs": normalized,
    }
    serialized = json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return f"cache:{digest}"
