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
import http.client
import inspect

import pytest

from prometheus_client import Counter

from prometheus_async import aio


try:
    import aiohttp
except ImportError:
    aiohttp = None

try:
    import consul
except ImportError:
    consul = None
else:
    import uuid

    from prometheus_async.aio.sd import ConsulAgent


async def coro():
    await asyncio.sleep(0)


class TestTime:
    @pytest.mark.asyncio
    async def test_still_coroutine_function(self, fo):
        """
        It's ensured that a decorated function still passes as a coroutine
        function.  Otherwise PYTHONASYNCIODEBUG=1 breaks.
        """
        func = aio.time(fo)(coro)
        new_coro = func()

        assert inspect.iscoroutine(new_coro)
        assert inspect.iscoroutinefunction(func)

        await new_coro

    @pytest.mark.asyncio
    async def test_decorator_sync(self, fo, patch_timer):
        """
        time works with sync results functions.
        """
        @aio.time(fo)
        async def func():
            if True:
                return 42
            else:
                await asyncio.sleep(0)

        assert 42 == await func()
        assert [1] == fo._observed

    @pytest.mark.asyncio
    async def test_decorator(self, fo, patch_timer):
        """
        time works with asyncio results functions.
        """
        @aio.time(fo)
        async def func():
            await asyncio.sleep(0)
            return 42

        rv = func()

        assert asyncio.iscoroutine(rv)
        assert [] == fo._observed

        rv = await rv

        assert [1] == fo._observed
        assert 42 == rv

    @pytest.mark.asyncio
    async def test_decorator_exc(self, fo, patch_timer):
        """
        Does not swallow exceptions.
        """
        v = ValueError("foo")

        @aio.time(fo)
        async def func():
            await asyncio.sleep(0)
            raise v

        with pytest.raises(ValueError) as e:
            await func()

        assert v is e.value
        assert [1] == fo._observed

    @pytest.mark.asyncio
    async def test_future(self, fo, patch_timer, event_loop):
        """
        time works with a asyncio.Future.
        """
        fut = asyncio.Future(loop=event_loop)
        coro = aio.time(fo, fut)

        assert [] == fo._observed

        fut.set_result(42)

        assert 42 == await coro
        assert [1] == fo._observed

    @pytest.mark.asyncio
    async def test_future_exc(self, fo, patch_timer, event_loop):
        """
        Does not swallow exceptions.
        """
        fut = asyncio.Future(loop=event_loop)
        coro = aio.time(fo, fut)
        v = ValueError("foo")

        assert [] == fo._observed

        fut.set_exception(v)

        with pytest.raises(ValueError) as e:
            await coro

        assert [1] == fo._observed
        assert v is e.value


class TestCountExceptions:
    @pytest.mark.asyncio
    async def test_decorator_no_exc(self, fc, event_loop):
        """
        If no exception is raised, the counter does not change.
        """
        @aio.count_exceptions(fc)
        async def func():
            await asyncio.sleep(0.0)
            return 42

        assert 42 == await func()
        assert 0 == fc._val

    @pytest.mark.asyncio
    async def test_decorator_wrong_exc(self, fc, event_loop):
        """
        If a wrong exception is raised, the counter does not change.
        """
        @aio.count_exceptions(fc, exc=ValueError)
        async def func():
            await asyncio.sleep(0.0)
            raise Exception()

        with pytest.raises(Exception):
            await func()

        assert 0 == fc._val

    @pytest.mark.asyncio
    async def test_decorator_exc(self, fc, event_loop):
        """
        If the correct exception is raised, count it.
        """
        @aio.count_exceptions(fc, exc=ValueError)
        async def func():
            await asyncio.sleep(0.0)
            raise ValueError()

        with pytest.raises(ValueError):
            await func()

        assert 1 == fc._val

    @pytest.mark.asyncio
    async def test_future_no_exc(self, fc, event_loop):
        """
        If no exception is raised, the counter does not change.
        """
        fut = asyncio.Future(loop=event_loop)
        coro = aio.count_exceptions(fc, future=fut)

        fut.set_result(42)

        assert 42 == await coro
        assert 0 == fc._val

    @pytest.mark.asyncio
    async def test_future_wrong_exc(self, fc, event_loop):
        """
        If a wrong exception is raised, the counter does not change.
        """
        fut = asyncio.Future(loop=event_loop)
        coro = aio.count_exceptions(fc, exc=ValueError, future=fut)
        exc = Exception()

        fut.set_exception(exc)

        with pytest.raises(Exception):
            assert 42 == await coro
        assert 0 == fc._val

    @pytest.mark.asyncio
    async def test_future_exc(self, fc, event_loop):
        """
        If the correct exception is raised, count it.
        """
        fut = asyncio.Future(loop=event_loop)
        coro = aio.count_exceptions(fc, exc=ValueError, future=fut)
        exc = ValueError()

        fut.set_exception(exc)

        with pytest.raises(Exception):
            assert 42 == await coro
        assert 1 == fc._val


class TestTrackInprogress:
    @pytest.mark.asyncio
    async def test_coroutine(self, fg):
        """
        Incs and decs.
        """
        f = aio.track_inprogress(fg)(coro)

        await f()

        assert 0 == fg._val
        assert 2 == fg._calls

    @pytest.mark.asyncio
    async def test_future(self, fg, event_loop):
        """
        Incs and decs.
        """
        fut = asyncio.Future(loop=event_loop)

        wrapped = aio.track_inprogress(fg, fut)

        assert 1 == fg._val

        fut.set_result(42)

        await wrapped

        assert 0 == fg._val


class FakeSD:
    """
    Fake Service Discovery.
    """
    registered_ms = None

    async def register(self, metrics_server, loop):
        self.registered_ms = metrics_server

        async def deregister():
            return True

        return deregister


@pytest.mark.skipif(aiohttp is None, reason="Needs aiohttp.")
class TestWeb:
    @pytest.mark.asyncio
    async def test_server_stats(self):
        """
        Returns a response with the current stats.
        """
        Counter("test_server_stats", "cnt").inc()
        rv = await aio.web.server_stats(None)

        assert (
            b'# HELP test_server_stats cnt\n# TYPE test_server_stats counter\n'
            b'test_server_stats 1.0\n'
            in rv.body
        )

    @pytest.mark.asyncio
    async def test_cheap(self):
        """
        Returns a simple string.
        """
        rv = await aio.web._cheap(None)

        assert (
            b'<html><body><a href="/metrics">Metrics</a></body></html>' ==
            rv.body
        )
        assert "text/html" == rv.content_type

    @pytest.mark.asyncio
    @pytest.mark.parametrize("sd", [
        None,
        FakeSD(),
    ])
    async def test_start_http_server(self, event_loop, sd):
        """
        Integration test: server gets started, is registered, and serves stats.
        """
        server = await aio.web.start_http_server(
            addr="127.0.0.1", loop=event_loop, service_discovery=sd,
        )

        assert isinstance(server, aio.web.MetricsHTTPServer)
        assert server.is_registered is (sd is not None)
        if sd is not None:
            assert sd.registered_ms is server

        addr, port = server.socket
        Counter("test_start_http_server", "cnt").inc()

        async with aiohttp.ClientSession() as s:
            rv = await s.request(
                "GET",
                "http://{addr}:{port}/metrics"
                .format(addr=addr, port=port)
            )
            body = await rv.text()

        assert (
            '# HELP test_start_http_server cnt\n# TYPE test_start_http_server'
            ' counter\ntest_start_http_server 1.0\n'
            in body
        )
        await server.close()

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
        assert "PrometheusAsyncWebEndpoint" == t._thread.name
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
    ]
    )
    async def test_url(self, addr, url, event_loop):
        """
        The URL of a MetricsHTTPServer is correctly computed.
        """
        server = await aio.web.start_http_server(
            addr=addr, loop=event_loop
        )
        sock = server.socket

        part = url + str(sock.port) + "/"
        assert "http://" + part == server.url

        server.https = True
        assert "https://" + part == server.url

        await server.close()


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


@pytest.mark.skipif(consul is None, reason="Needs python-consul.")
@pytest.mark.parametrize("deregister", [True, False])
@pytest.mark.asyncio
@pytest.mark.xfail
async def test_consul_agent(event_loop, deregister):
    """
    Integration test with a real consul agent.  Start a service, register it,
    close it, verify it's deregistered.
    """
    tags = ("foo", "bar")
    service_id = str(uuid.uuid4())  # allow for parallel tests

    con = consul.aio.Consul()
    ca = ConsulAgent(
        name="test-metrics",
        service_id=service_id,
        tags=tags,
        deregister=deregister,
    )

    try:
        server = await aio.web.start_http_server(
            addr="127.0.0.1", loop=event_loop, service_discovery=ca,
        )
    except aiohttp.ClientOSError:
        pytest.skip("Missing consul agent.")

    assert service_id in await con.agent.services()

    svc = (await con.agent.services())[service_id]

    assert "test-metrics" == svc["Service"]
    assert sorted(tags) == sorted(svc["Tags"])
    assert server.socket.addr == svc["Address"]
    assert server.socket.port == svc["Port"]

    await server.close()
    # Eventual consistency...
    await asyncio.sleep(1.5)

    services = await con.agent.services()

    # Assert service is gone iff we are supposed to deregister.
    assert (service_id in services) is not deregister

    con.close()
