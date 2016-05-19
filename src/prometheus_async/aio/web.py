# Copyright 2016 Hynek Schlawack
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
aiohttp-based metrics exposure.
"""

import asyncio
import queue
import threading

from collections import namedtuple

try:
    from aiohttp import web
except ImportError:
    web = None

from prometheus_client.exposition import (
    generate_latest, CONTENT_TYPE_LATEST, core,
)


def _needs_aiohttp(obj):
    """
    Decorator that returns *obj* if aiohttp is available else a callable that
    raises a RuntimeError.
    """
    if web is None:
        def raiser(*a, **kw):
            """
            Notifies about missing aiohttp dependency.
            """
            raise RuntimeError("'{}' requires aiohttp.".format(obj.__name__))
        return raiser
    else:
        return obj


@_needs_aiohttp
def server_stats(request):
    """
    Return a web response with the plain text version of the metrics.

    :rtype: :class:`aiohttp.web.Response`
    """
    rsp = web.Response(body=generate_latest(core.REGISTRY))
    rsp.content_type = CONTENT_TYPE_LATEST
    return rsp


_REF = b'<html><body><a href="/metrics">Metrics</a></body></html>'


def _cheap(request):
    """
    A view that links to metrics.

    Useful for cheap health checks.
    """
    return web.Response(body=_REF)


@asyncio.coroutine
@_needs_aiohttp
def start_http_server(*, addr="", port=0, ssl_ctx=None, service_discovery=None,
                      loop=None):
    """
    Start an HTTP(S) server on *addr*:*port* using *loop*.

    If *ssl_ctx* is set, use TLS.

    :param str addr: Interface to listen on. Leaving empty will listen on all
        interfaces.
    :param int port: Port to listen on.
    :param ssl.SSLContext ssl_ctx: TLS settings
    :param asyncio.BaseEventLoop loop: Event loop to use.
    :param service_discovery: see :ref:`sd`

    :rtype: MetricsHTTPServer
    """
    if loop is None:  # pragma: nocover
        loop = asyncio.get_event_loop()

    app = web.Application()
    app.router.add_route("GET", "/", _cheap)
    app.router.add_route("GET", "/metrics", server_stats)
    handler = app.make_handler(access_log=None)
    srv = yield from loop.create_server(
        handler,
        addr, port, ssl=ssl_ctx,
    )
    ms = MetricsHTTPServer.from_server(
        server=srv,
        app=app,
        handler=handler,
        https=ssl_ctx is not None,
        loop=loop,
    )
    if service_discovery is not None:
        ms._deregister = yield from service_discovery.register(ms, loop)
    return ms


class MetricsHTTPServer:
    """
    A stoppable metrics HTTP server.

    Returned by :func:`start_http_server`.  Do *not* instantiate it yourself.

    :ivar socket: Socket the server is listening on.  namedtuple of
        either (:class:`ipaddress.IPv4Address`, port) or
        (:class:`ipaddress.IPv6Address`, port).
    :ivar bool https: Whether the server uses SSL/TLS.
    :ivar loop: The :class:`event loop <asyncio.BaseEventLoop>` the server
        uses.
    :ivar str url: A valid URL to the metrics endpoint.
    :ivar bool is_registered: Is the web endpoint registered with a
        service discovery system?
    """
    def __init__(self, socket, server, app, handler, https, loop):
        self._app = app
        self._handler = handler
        self._server = server
        self._deregister = None

        self.socket = socket
        self.https = https
        self.loop = loop

    @classmethod
    def from_server(cls, server, app, handler, https, loop):
        sock = server.sockets[0].getsockname()
        return cls(
            socket=Socket(*sock[:2]),
            server=server,
            app=app,
            handler=handler,
            https=https,
            loop=loop,
        )

    @property
    def is_registered(self):
        """
        Is the web endpoint registered with a service discovery system?
        """
        return self._deregister is not None

    @property
    def url(self):
        addr = self.socket.addr
        return "http{s}://{host}:{port}/".format(
            s="s" if self.https else "",
            host=addr if ":" not in addr else "[{}]".format(addr),
            port=self.socket.port,
        )

    @asyncio.coroutine
    def close(self):
        """
        Stop the server and clean up.
        """
        if self._deregister is not None:
            yield from self._deregister()
        yield from self._handler.finish_connections(1.0)
        self._server.close()
        yield from self._server.wait_closed()
        yield from self._app.finish()


Socket = namedtuple("Socket", "addr port")


class ThreadedMetricsHTTPServer:
    """
    A stoppable metrics HTTP server that runs in a separate thread.

    Returned by :func:`start_http_server_in_thread`.  Do *not* instantiate it
    yourself.

    :ivar socket: Socket the server is listening on.  namedtuple of
        ``Socket(addr, port)``.
    :ivar bool https: Whether the server uses SSL/TLS.
    :ivar loop: The :class:`event loop <asyncio.BaseEventLoop>` the server
        uses.
    :ivar str url: A valid URL to the metrics endpoint.
    :ivar bool is_registered: Is the web endpoint registered with a
        service discovery system?
    """
    def __init__(self, http_server, thread):
        self._http_server = http_server
        self._thread = thread

    def close(self):
        """
        Stop the server, close the event loop, and join the thread.
        """
        loop = self._http_server.loop

        loop.call_soon_threadsafe(loop.stop)

        self._thread.join()
        loop.close()

    @property
    def https(self):
        return self._http_server.https

    @property
    def socket(self):
        return self._http_server.socket

    @property
    def url(self):
        return self._http_server.url

    @property
    def is_registered(self):
        return self._http_server.is_registered


@_needs_aiohttp
def start_http_server_in_thread(*, port=0, addr="", ssl_ctx=None,
                                service_discovery=None):
    """
    Start an asyncio HTTP(S) server in a new thread with an own event loop.

    Ideal to expose your metrics in non-asyncio Python 3 applications.

    For arguments see :func:`start_http_server`.

    :rtype: ThreadedMetricsHTTPServer
    """
    q = queue.Queue()
    loop = asyncio.new_event_loop()

    def server():
        asyncio.set_event_loop(loop)
        http = loop.run_until_complete(
            start_http_server(
                port=port, addr=addr, ssl_ctx=ssl_ctx,
                service_discovery=service_discovery, loop=loop
            )
        )
        q.put(http)
        loop.run_forever()
        loop.run_until_complete(http.close())

    t = threading.Thread(target=server, daemon=True)
    t.start()

    return ThreadedMetricsHTTPServer(q.get(), t)
