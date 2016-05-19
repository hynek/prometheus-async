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

import asyncio
import inspect
import http.client

import pytest

try:
    import aiohttp
except ImportError:
    aiohttp = None

from prometheus_client import Counter

from prometheus_async import aio


@asyncio.coroutine
def coro():
    yield from asyncio.sleep(0)


class TestTime:
    def test_still_coroutine_function(self, fo):
        """
        It's ensured that a decorated function still passes as a coroutine
        function.  Otherwise PYTHONASYNCIODEBUG=1 breaks.

        iscoroutine[function] sadly only works with async def.
        """
        func = aio.time(fo)(coro)

        assert inspect.isgenerator(func())
        assert inspect.isgeneratorfunction(func)

    @pytest.mark.asyncio
    def test_decorator_sync(self, fo, patch_timer):
        """
        time works with sync results functions.
        """
        @aio.time(fo)
        @asyncio.coroutine
        def func():
            if True:
                return 42
            else:
                yield from asyncio.sleep(0)

        assert 42 == (yield from func())
        assert [1] == fo._observed

    @pytest.mark.asyncio
    def test_decorator(self, fo, patch_timer):
        """
        time works with asyncio results functions.
        """
        @aio.time(fo)
        @asyncio.coroutine
        def func():
            yield from asyncio.sleep(0)
            return 42

        rv = func()

        assert asyncio.iscoroutine(rv)
        assert [] == fo._observed

        rv = yield from rv
        assert [1] == fo._observed
        assert 42 == rv

    @pytest.mark.asyncio
    def test_decorator_exc(self, fo, patch_timer):
        """
        Does not swallow exceptions.
        """
        v = ValueError("foo")

        @aio.time(fo)
        @asyncio.coroutine
        def func():
            yield from asyncio.sleep(0)
            raise v

        with pytest.raises(ValueError) as e:
            yield from func()

        assert v is e.value
        assert [1] == fo._observed

    @pytest.mark.asyncio
    def test_future(self, fo, patch_timer, event_loop):
        """
        time works with a asyncio.Future.
        """
        fut = asyncio.Future(loop=event_loop)
        coro = aio.time(fo, fut)

        assert [] == fo._observed

        fut.set_result(42)

        assert 42 == (yield from coro)
        assert [1] == fo._observed

    @pytest.mark.asyncio
    def test_future_exc(self, fo, patch_timer, event_loop):
        """
        Does not swallow exceptions.
        """
        fut = asyncio.Future(loop=event_loop)
        coro = aio.time(fo, fut)
        v = ValueError("foo")

        assert [] == fo._observed

        fut.set_exception(v)

        with pytest.raises(ValueError) as e:
            yield from coro

        assert [1] == fo._observed
        assert v is e.value


class TestCountExceptions:
    @pytest.mark.asyncio
    def test_decorator_no_exc(self, fc, event_loop):
        """
        If no exception is raised, the counter does not change.
        """
        @aio.count_exceptions(fc)
        def func():
            yield from asyncio.sleep(0.0)
            return 42

        assert 42 == (yield from func())
        assert 0 == fc._val

    @pytest.mark.asyncio
    def test_decorator_wrong_exc(self, fc, event_loop):
        """
        If a wrong exception is raised, the counter does not change.
        """
        @aio.count_exceptions(fc, exc=ValueError)
        def func():
            yield from asyncio.sleep(0.0)
            raise Exception()

        with pytest.raises(Exception):
            yield from func()

        assert 0 == fc._val

    @pytest.mark.asyncio
    def test_decorator_exc(self, fc, event_loop):
        """
        If the correct exception is raised, count it.
        """
        @aio.count_exceptions(fc, exc=ValueError)
        def func():
            yield from asyncio.sleep(0.0)
            raise ValueError()

        with pytest.raises(ValueError):
            yield from func()

        assert 1 == fc._val

    @pytest.mark.asyncio
    def test_future_no_exc(self, fc, event_loop):
        """
        If no exception is raised, the counter does not change.
        """
        fut = asyncio.Future(loop=event_loop)
        coro = aio.count_exceptions(fc, future=fut)

        fut.set_result(42)

        assert 42 == (yield from coro)
        assert 0 == fc._val

    @pytest.mark.asyncio
    def test_future_wrong_exc(self, fc, event_loop):
        """
        If a wrong exception is raised, the counter does not change.
        """
        fut = asyncio.Future(loop=event_loop)
        coro = aio.count_exceptions(fc, exc=ValueError, future=fut)
        exc = Exception()

        fut.set_exception(exc)

        with pytest.raises(Exception):
            assert 42 == (yield from coro)
        assert 0 == fc._val

    @pytest.mark.asyncio
    def test_future_exc(self, fc, event_loop):
        """
        If the correct exception is raised, count it.
        """
        fut = asyncio.Future(loop=event_loop)
        coro = aio.count_exceptions(fc, exc=ValueError, future=fut)
        exc = ValueError()

        fut.set_exception(exc)

        with pytest.raises(Exception):
            assert 42 == (yield from coro)
        assert 1 == fc._val


class TestTrackInprogress:
    @pytest.mark.asyncio
    def test_coroutine(self, fg):
        """
        Incs and decs.
        """
        f = aio.track_inprogress(fg)(coro)

        yield from f()

        assert 0 == fg._val
        assert 2 == fg._calls

    @pytest.mark.asyncio
    def test_future(self, fg, event_loop):
        """
        Incs and decs.
        """
        fut = asyncio.Future(loop=event_loop)

        wrapped = aio.track_inprogress(fg, fut)

        assert 1 == fg._val

        fut.set_result(42)

        yield from wrapped

        assert 0 == fg._val


class FakeSD:
    """
    Fake Service Discovery.
    """
    registered_ms = None

    @asyncio.coroutine
    def register(self, metrics_server, loop):
        self.registered_ms = metrics_server

        @asyncio.coroutine
        def deregister():
            return True

        return deregister


@pytest.mark.skipif(aiohttp is None, reason="Tests require aiohttp")
class TestWeb:
    def test_server_stats(self):
        """
        Returns a response with the current stats.
        """
        Counter("test_server_stats", "cnt").inc()
        rv = aio.web.server_stats(None)
        assert (
            b'# HELP test_server_stats cnt\n# TYPE test_server_stats counter\n'
            b'test_server_stats 1.0\n'
            in rv.body
        )

    def test_cheap(self):
        """
        Returns a simple string.
        """
        rv = aio.web._cheap(None)
        assert (
            b'<html><body><a href="/metrics">Metrics</a></body></html>' ==
            rv.body
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("sd", [
        None,
        FakeSD(),
    ])
    def test_start_http_server(self, event_loop, sd):
        """
        Integration test: server gets started, is registered, and serves stats.
        """
        server = yield from aio.web.start_http_server(
            addr="127.0.0.1", loop=event_loop, service_discovery=sd,
        )
        assert isinstance(server, aio.web.MetricsHTTPServer)
        assert server.is_registered is (sd is not None)
        if sd is not None:
            assert sd.registered_ms is server

        addr, port = server.socket
        Counter("test_start_http_server", "cnt").inc()

        rv = yield from aiohttp.request(
            "GET",
            "http://{addr}:{port}/metrics"
            .format(addr=addr, port=port)
        )
        body = yield from rv.text()
        assert (
            '# HELP test_start_http_server cnt\n# TYPE test_start_http_server'
            ' counter\ntest_start_http_server 1.0\n'
            in body
        )
        yield from server.close()

    @pytest.mark.parametrize("sd", [
        None,
        FakeSD(),
    ])
    def test_start_in_thread(self, sd):
        """
        Threaded version starts and exits properly, passes on service
        discovery.
        """
        Counter("test_start_http_server_in_thread", "cnt").inc()
        t = aio.web.start_http_server_in_thread(addr="127.0.0.1",
                                                service_discovery=sd)

        assert isinstance(t, aio.web.ThreadedMetricsHTTPServer)
        assert t.url.startswith("http")
        assert False is t.https
        assert t.is_registered is (sd is not None)
        if sd is not None:
            assert sd.registered_ms is t._http_server

        s = t.socket
        h = http.client.HTTPConnection(s.addr, port=s[1])
        h.request("GET", "/metrics")
        rsp = h.getresponse()
        body = rsp.read().decode()
        rsp.close()
        h.close()

        assert "HELP test_start_http_server_in_thread cnt" in body

        t.close()

        assert False is t._thread.is_alive()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("addr,url", [
        ("127.0.0.1", "127.0.0.1:"),
        ("::1", "[::1]:")
    ]
    )
    def test_url(self, addr, url, event_loop):
        """
        The URL of a MetricsHTTPServer is correctly computed.
        """
        server = yield from aio.web.start_http_server(
            addr=addr, loop=event_loop
        )
        sock = server.socket

        part = url + str(sock.port) + "/"
        assert "http://" + part == server.url

        server.https = True
        assert "https://" + part == server.url

        yield from server.close()


class TestNeedsAioHTTP:
    @pytest.mark.skipif(aiohttp is None, reason="Needs aiohttp.")
    def test_present(self):
        """
        If aiohttp is present, the original object is returned.
        """
        o = object()
        assert o is aio.web._needs_aiohttp(o)

    @pytest.mark.skipif(aiohttp is not None, reason="Needs missing aiohttp.")
    def test_missing(self):
        """
        If aiohttp is missing, raise RuntimeError if called.
        """
        with pytest.raises(RuntimeError) as e:
            aio.web._needs_aiohttp(coro)()

        assert "'coro' requires aiohttp." == str(e.value)
