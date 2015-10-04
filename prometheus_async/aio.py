"""
asyncio-related functions.
"""

import asyncio
import sys

try:
    from aiohttp import web
except ImportError:
    web = None

from prometheus_client.exposition import (
    generate_latest, CONTENT_TYPE_LATEST, core,
)


vi = sys.version_info
if vi[0:2] == (3, 4) and vi[2] < 4:
    ensure_future = asyncio.async
else:
    ensure_future = asyncio.ensure_future


def is_async(val):
    return asyncio.iscoroutine(val) or isinstance(val, asyncio.Future)


def add_cb(val, observer):
    fut = ensure_future(val)
    fut.add_done_callback(observer)
    return fut


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
