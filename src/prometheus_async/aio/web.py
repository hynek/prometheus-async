"""
aiohttp-based metrics exposure.
"""

import asyncio
import queue
import threading

from collections import namedtuple
from functools import wraps

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

    :rtype: bytes
    """
    rsp = web.Response(body=generate_latest(core.REGISTRY))
    rsp.content_type = CONTENT_TYPE_LATEST
    return rsp


def cheap(request):
    """
    A view that links to metrics.

    Useful for cheap health checks.
    """
    return web.Response(
        body=b'<html><body><a href="/metrics">Metrics</a></body></html>'
    )


def needs_aiohttp(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if web is None:
            raise RuntimeError("aiohttp is required for the http server.")
        return f(*a, **kw)
    return wrapper


@asyncio.coroutine
@needs_aiohttp
def start_http_server(*, port=0, addr="", ssl_ctx=None, loop=None):
    """
    Start an HTTP(S) server on *addr*:*port* using *loop*.

    If *ssl_ctx* is set, use TLS.

    :param int port: Port to listen on.
    :param str addr: Interface to listen on.
    :param ssl.SSLContext ssl_ctx: TLS settings
    :param asyncio.BaseEventLoop loop: Event loop.

    :rtype: MetricsHTTPServer
    """
    if loop is None:  # pragma: nocover
        loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def start():
        app = web.Application()
        app.router.add_route("GET", "/", cheap)
        app.router.add_route("GET", "/metrics", server_stats)
        handler = app.make_handler(access_log=None)
        srv = yield from loop.create_server(
            handler,
            addr, port, ssl=ssl_ctx,
        )
        return MetricsHTTPServer.from_server(
            srv, app, handler, loop,
        )

    return (yield from start())


class MetricsHTTPServer:
    """
    A stoppable metrics HTTP server.

    Returned by :func:`start_http_server`.  Do *not* instantiate it yourself.

    :attribute sockets: Sockets the server is listening on.  List of tuples of
        either (:class:`ipaddress.IPv4Address`, port) or
        (:class:`ipaddress.IPv6Address`, port).
    :attribute loop: The :class:`event loop <asyncio.BaseEventLoop>` the server
        uses.
    """
    def __init__(self, sockets, server, app, handler, loop):
        self._app = app
        self._handler = handler
        self._server = server

        self.sockets = sockets
        self.loop = loop

    @classmethod
    def from_server(cls, server, app, handler, loop):
        return cls(
            sockets=[
                (s.getsockname()[0], s.getsockname()[1])
                for s in server.sockets
            ],
            server=server,
            app=app,
            handler=handler,
            loop=loop,
        )

    @asyncio.coroutine
    def stop(self):
        """
        Stop the server.
        """
        yield from self._handler.finish_connections(1.0)
        self._server.close()
        yield from self._server.wait_closed()
        yield from self._app.finish()


Socket = namedtuple("Socket", "address port")


class ThreadedMetricsHTTPServer:
    """
    A stoppable metrics HTTP server that runs in a separate thread.

    Returned by :func:`start_http_server_in_thread`.  Do *not* instantiate it
    yourself.

    :attribute sockets: Sockets the server is listening on.  List of
        namedtuples of ``Socket(address, port)``.
    """
    def __init__(self, http_server, thread):
        self._http_server = http_server
        self._thread = thread

    def stop(self):
        """
        Stop the server, close the event loop, and join the thread.
        """
        loop = self._http_server.loop

        loop.call_soon_threadsafe(loop.stop)

        self._thread.join()
        loop.close()

    @property
    def sockets(self):
        return [Socket(*socket) for socket in self._http_server.sockets]


@needs_aiohttp
def start_http_server_in_thread(*, port=0, addr="", ssl_ctx=None):
    """
    Start an asyncio HTTP(S) server in a new thread with an own event loop.

    Ideal to expose your metrics in regular (non-asyncio) Python 3
    applications.

    For arguments see :func:`start_http_server`.

    :rtype: ThreadedMetricsHTTPServer
    """
    q = queue.Queue()
    loop = asyncio.new_event_loop()

    def server():
        asyncio.set_event_loop(loop)
        http = loop.run_until_complete(
            start_http_server(port=port, addr=addr, ssl_ctx=ssl_ctx, loop=loop)
        )
        q.put(http)
        loop.run_forever()
        loop.run_until_complete(http.stop())

    t = threading.Thread(target=server, daemon=True)
    t.start()

    return ThreadedMetricsHTTPServer(q.get(), t)
