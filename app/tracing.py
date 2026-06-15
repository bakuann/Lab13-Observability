from __future__ import annotations

import os
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))


def _noop_observe(func: F | None = None, **_: Any):
    def decorator(inner: F) -> F:
        return inner

    return decorator(func) if func is not None else decorator


class _DummyContext:
    def update_current_trace(self, **kwargs: Any) -> None:
        return None

    def update_current_span(self, **kwargs: Any) -> None:
        return None

    def update_current_generation(self, **kwargs: Any) -> None:
        return None

    def flush(self) -> None:
        return None


if tracing_enabled():
    try:
        from langfuse import get_client, observe

        langfuse_context = get_client()
    except Exception:  # pragma: no cover - optional external integration
        observe = _noop_observe
        langfuse_context = _DummyContext()
else:
    observe = _noop_observe
    langfuse_context = _DummyContext()


def flush_traces() -> None:
    langfuse_context.flush()
