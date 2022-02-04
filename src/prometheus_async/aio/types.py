from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Callable, Protocol


if TYPE_CHECKING:
    from prometheus_async.aio.web import MetricsHTTPServer


Deregisterer = Callable[[], Awaitable[None]]


class ServiceDiscovery(Protocol):
    async def register(
        self, metrics_server: MetricsHTTPServer
    ) -> Deregisterer | None:
        ...
