"""
aiohttp-based metrics exposure.
"""

import asyncio

try:
    from aiohttp import web
except ImportError:
    web = None

from prometheus_client.exposition import (
    generate_latest, CONTENT_TYPE_LATEST, core,
)


def server_stats(request):
    """
    Return a web response with the plain text version of the metrics.
    """
    rsp = web.Response(body=generate_latest(core.REGISTRY))
    rsp.content_type = CONTENT_TYPE_LATEST
    return rsp


@asyncio.coroutine
def start_http_server(port, addr="", ssl_ctx=None, loop=None):
    """
    Start an HTTP(S) server on *addr*:*port* using *loop*.

    If *ssl_ctx* is set, use TLS.
    """
    if loop is None:  # pragma: nocover
        loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def start():
        app = web.Application()
        app.router.add_route("GET", "/metrics", server_stats)
        handler = app.make_handler()
        srv = yield from loop.create_server(
            handler,
            addr, port, ssl=ssl_ctx,
        )
        return srv, handler

    return (yield from start())
