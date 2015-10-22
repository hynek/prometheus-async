"""
aiohttp-based metrics exposure.
"""

import asyncio
import ipaddress
import queue
import threading

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
    """
    rsp = web.Response(body=generate_latest(core.REGISTRY))
    rsp.content_type = CONTENT_TYPE_LATEST
    return rsp


def needs_aiohttp(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if web is None:
            raise RuntimeError("aiohttp is required for the http server.")
        return f(*a, **kw)
    return wrapper


@asyncio.coroutine
@needs_aiohttp
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
        return app, srv, handler

    return (yield from start())


class HTTPServer:
    """
    A stopable HTTPServer as returned by :func:`start_http_server_in_thread`.

    :attribute sockets: Sockets the server is listening on.
    :type sockets: list of tuples
    """
    def __init__(self, thread, loop, srv, handler):
        self._loop = loop
        self._thread = thread
        self.sockets = [
            (ipaddress.ip_address(s.getsockname()[0]), s.getsockname()[1])
            for s in srv.sockets
        ]

    def stop(self):
        """
        Stops the server and joins the thread.
        """
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join()


@needs_aiohttp
def start_http_server_in_thread(port, addr="", ssl_ctx=None):
    """
    Start an asyncio HTTP(S) server in a new thread.

    Starts an own event loop.

    Ideal to expose your metrics in non-asyncio Python 3 applications.
    """
    q = queue.Queue()
    loop = asyncio.new_event_loop()

    def server():
        asyncio.set_event_loop(loop)
        app, srv, handler = loop.run_until_complete(
            start_http_server(port, addr, ssl_ctx=ssl_ctx)
        )
        q.put((srv, handler))
        loop.run_forever()
        loop.run_until_complete(handler.finish_connections(1.0))
        srv.close()
        loop.run_until_complete(srv.wait_closed())
        loop.run_until_complete(app.finish())
        loop.close()

    t = threading.Thread(target=server)
    t.start()

    srv, handler = q.get()

    return HTTPServer(t, loop, srv, handler)
