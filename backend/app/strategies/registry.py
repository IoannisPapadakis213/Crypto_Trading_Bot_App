"""Decorator-based strategy registry.

Lets the API/dashboard list available strategies by name without importing
or hardcoding every concrete strategy class.
"""

from collections.abc import Callable

from app.strategies.base import Strategy

_REGISTRY: dict[str, type[Strategy]] = {}


def register_strategy(name: str) -> Callable[[type[Strategy]], type[Strategy]]:
    def decorator(cls: type[Strategy]) -> type[Strategy]:
        if name in _REGISTRY:
            raise ValueError(f"Strategy '{name}' is already registered")
        cls.name = name
        _REGISTRY[name] = cls
        return cls

    return decorator


def get_strategy_class(name: str) -> type[Strategy]:
    try:
        return _REGISTRY[name]
    except KeyError as exc:
        available = ", ".join(sorted(_REGISTRY)) or "(none registered)"
        raise KeyError(f"Unknown strategy '{name}'. Available: {available}") from exc


def list_strategies() -> list[str]:
    return sorted(_REGISTRY)
