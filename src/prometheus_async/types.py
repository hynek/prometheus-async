from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Callable, Protocol


if TYPE_CHECKING:
    from prometheus_async.aio.web import MetricsHTTPServer

try:
    from typing import ParamSpec
except ImportError:
    from typing_extensions import ParamSpec


__all__ = [
    "ParamSpec",
    "Deregisterer",
    "ServiceDiscovery",
    "Observer",
    "Incrementer",
    "IncDecrementer",
]

Deregisterer = Callable[[], Awaitable[None]]


class ServiceDiscovery(Protocol):
    async def register(
        self, metrics_server: MetricsHTTPServer
    ) -> Deregisterer | None:
        ...


class Observer(Protocol):
    def observe(self, value: float) -> None:
        ...


class Incrementer(Protocol):
    def inc(
        self, amount: float = 1, exemplar: dict[str, str] | None = None
    ) -> None:
        ...


class IncDecrementer(Protocol):
    def inc(
        self, amount: float = 1, exemplar: dict[str, str] | None = None
    ) -> None:
        ...

    def dec(self, amount: float = 1) -> None:
        ...
