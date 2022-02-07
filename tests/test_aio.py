# SPDX-License-Identifier: Apache-2.0
#
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
import sys
import uuid

from types import SimpleNamespace
from unittest import mock

import pytest

from prometheus_client import CONTENT_TYPE_LATEST, Counter
from prometheus_client.openmetrics import exposition as openmetrics

from prometheus_async import aio
from prometheus_async.aio.sd import ConsulAgent, _LocalConsulAgentClient


try:
    import aiohttp

    from multidict import CIMultiDict
except ImportError:
    aiohttp = None
    CIMultiDict = dict


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
    @pytest.mark.usefixtures("patch_timer")
    async def test_decorator_sync(self, fo):
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
    @pytest.mark.usefixtures("patch_timer")
    async def test_decorator(self, fo):
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
    @pytest.mark.usefixtures("patch_timer")
    async def test_decorator_exc(self, fo):
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
    @pytest.mark.usefixtures("patch_timer")
    async def test_future(self, fo):
        """
        time works with a asyncio.Future.
        """
        fut = asyncio.Future()
        coro = aio.time(fo, fut)

        assert [] == fo._observed

        fut.set_result(42)

        assert 42 == await coro
        assert [1] == fo._observed

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("patch_timer")
    async def test_future_exc(self, fo):
        """
        Does not swallow exceptions.
        """
        fut = asyncio.Future()
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
    async def test_decorator_no_exc(self, fc):
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
    async def test_decorator_wrong_exc(self, fc):
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
    async def test_decorator_exc(self, fc):
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
    async def test_future_no_exc(self, fc):
        """
        If no exception is raised, the counter does not change.
        """
        fut = asyncio.Future()
        coro = aio.count_exceptions(fc, future=fut)

        fut.set_result(42)

        assert 42 == await coro
        assert 0 == fc._val

    @pytest.mark.asyncio
    async def test_future_wrong_exc(self, fc):
        """
        If a wrong exception is raised, the counter does not change.
        """
        fut = asyncio.Future()
        coro = aio.count_exceptions(fc, exc=ValueError, future=fut)
        exc = Exception()

        fut.set_exception(exc)

        with pytest.raises(Exception):
            assert 42 == await coro
        assert 0 == fc._val

    @pytest.mark.asyncio
    async def test_future_exc(self, fc):
        """
        If the correct exception is raised, count it.
        """
        fut = asyncio.Future()
        coro = aio.count_exceptions(fc, exc=ValueError, future=fut)
        exc = ValueError()

        fut.set_exception(exc)

        with pytest.raises(Exception):
            assert 42 == await coro
        assert 1 == fc._val


@pytest.mark.asyncio
class TestTrackInprogress:
    async def test_async_decorator(self, fake_gauge):
        """
        Works as a decorator of async functions.
        """

        @aio.track_inprogress(fake_gauge)
        async def f():
            await asyncio.sleep(0)

        await f()

        assert 0 == fake_gauge._val
        assert 2 == fake_gauge._calls

    async def test_coroutine(self, fake_gauge):
        """
        Incs and decs.
        """
        f = aio.track_inprogress(fake_gauge)(coro)

        await f()

        assert 0 == fake_gauge._val
        assert 2 == fake_gauge._calls

    async def test_future(self, fake_gauge):
        """
        Incs and decs.
        """
        fut = asyncio.Future()

        wrapped = aio.track_inprogress(fake_gauge, fut)

        assert 1 == fake_gauge._val

        fut.set_result(42)

        await wrapped

        assert 0 == fake_gauge._val


class FakeSD:
    """
    Fake Service Discovery.
    """

    registered_ms = None

    async def register(self, metrics_server):
        self.registered_ms = metrics_server

        async def deregister():
            return True

        return deregister


@pytest.mark.skipif(aiohttp is None, reason="Needs aiohttp.")
@pytest.mark.asyncio
class TestWeb:
    async def test_server_stats_old(self):
        """
        Returns a response with the current stats in the old format.
        """
        Counter("test_server_stats_total", "cnt").inc()
        rv = await aio.web.server_stats(SimpleNamespace(headers=CIMultiDict()))

        body = rv.body.decode()

        assert CONTENT_TYPE_LATEST == rv.headers["Content-Type"]
        assert body.startswith(
            """\
# HELP test_server_stats_total cnt
# TYPE test_server_stats_total counter
test_server_stats_total 1.0
# HELP test_server_stats_created cnt
# TYPE test_server_stats_created gauge
test_server_stats_created """
        )

    async def test_server_stats_openmetrics(self):
        """
        Returns a response with the current stats in the open metrics format.
        """
        Counter("test_server_stats_total", "cnt").inc()
        rv = await aio.web.server_stats(
            SimpleNamespace(
                headers=CIMultiDict(
                    Accept="application/openmetrics-text; version=0.0.1,"
                    "text/plain;version=0.0.4;q=0.5,*/*;q=0.1"
                )
            )
        )

        body = rv.body.decode()

        assert openmetrics.CONTENT_TYPE_LATEST == rv.headers["Content-Type"]
        assert body.startswith(
            """\
# HELP test_server_stats cnt
# TYPE test_server_stats counter
test_server_stats_total 1.0
test_server_stats_created """
        )
        assert body.endswith("EOF\n")

    async def test_cheap(self):
        """
        Returns a simple string.
        """
        rv = await aio.web._cheap(None)

        assert (
            b'<html><body><a href="/metrics">Metrics</a></body></html>'
            == rv.body
        )
        assert "text/html" == rv.content_type

    @pytest.mark.parametrize("sd", [None, FakeSD()])
    async def test_start_http_server(self, sd):
        """
        Integration test: server gets started, is registered, and serves stats.
        """
        server = await aio.web.start_http_server(
            addr="127.0.0.1", service_discovery=sd
        )

        assert isinstance(server, aio.web.MetricsHTTPServer)
        assert server.is_registered is (sd is not None)
        if sd is not None:
            assert sd.registered_ms is server

        addr, port = server.socket
        Counter("test_start_http_server_total", "cnt").inc()

        async with aiohttp.ClientSession() as s:
            rv = await s.request(
                "GET",
                f"http://{addr}:{port}/metrics",
            )
            body = await rv.text()

        assert (
            "# HELP test_start_http_server_total cnt\n# "
            "TYPE test_start_http_server_total"
            " counter\ntest_start_http_server_total 1.0\n" in body
        )
        await server.close()

    @pytest.mark.parametrize("sd", [None, FakeSD()])
    def test_start_in_thread(self, sd):
        """
        Threaded version starts and exits properly, passes on service
        discovery.
        """
        Counter("test_start_http_server_in_thread_total", "cnt").inc()
        t = aio.web.start_http_server_in_thread(
            addr="127.0.0.1", service_discovery=sd
        )

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

        assert "HELP test_start_http_server_in_thread_total cnt" in body

        t.close()

        assert False is t._thread.is_alive()

    @pytest.mark.parametrize("addr,url", [("127.0.0.1", "127.0.0.1:")])
    async def test_url(self, addr, url):
        """
        The URL of a MetricsHTTPServer is correctly computed.
        """
        server = await aio.web.start_http_server(addr=addr)
        sock = server.socket

        part = url + str(sock.port) + "/"
        assert "http://" + part == server.url

        server.https = True
        assert "https://" + part == server.url

        await server.close()


@pytest.mark.skipif(aiohttp is None, reason="Needs aiohttp.")
@pytest.mark.asyncio
class TestConsulAgent:
    @pytest.mark.parametrize("deregister", [True, False])
    async def test_integration(self, deregister):
        """
        Integration test with a real consul agent. Start a service, register
        it, close it, verify it's deregistered.
        """
        tags = ("foo", "bar")
        service_id = str(uuid.uuid4())  # allow for parallel tests

        con = _LocalConsulAgentClient(token=None)
        ca = ConsulAgent(
            name="test-metrics",
            service_id=service_id,
            tags=tags,
            deregister=deregister,
        )

        try:
            server = await aio.web.start_http_server(
                addr="127.0.0.1", service_discovery=ca
            )
        except aiohttp.ClientOSError:
            pytest.skip("Missing consul agent.")

        svc = (await con.get_services())[service_id]

        assert "test-metrics" == svc["Service"]
        assert sorted(tags) == sorted(svc["Tags"])
        assert server.socket.addr == svc["Address"]
        assert server.socket.port == svc["Port"]

        await server.close()

        services = await con.get_services()

        if deregister:
            # Assert service is gone iff we are supposed to deregister.
            assert service_id not in services
        else:
            assert service_id in services

            # Clean up behind ourselves.
            resp = await con.deregister_service(service_id)
            assert 200 == resp.status

    @pytest.mark.parametrize("deregister", [True, False])
    @pytest.mark.skipif(sys.version_info < (3, 8), reason="AsyncMock is 3.8+")
    async def test_mocked(self, deregister):
        """
        Same as test_integration, but using mocks instead of a real consul
        agent.
        """
        tags = ("foo", "bar")
        service_id = str(uuid.uuid4())  # allow for parallel tests

        con = mock.AsyncMock(auto_spec=_LocalConsulAgentClient)
        ca = ConsulAgent(
            name="test-metrics",
            service_id=service_id,
            tags=tags,
            deregister=deregister,
        )
        ca.consul = con

        server = await aio.web.start_http_server(
            addr="127.0.0.1", service_discovery=ca
        )

        con.register_service.assert_awaited_once()
        reg = con.register_service.await_args.kwargs

        assert service_id == reg["service_id"]
        assert "test-metrics" == reg["name"]
        assert sorted(tags) == sorted(reg["tags"])
        assert (
            f"http://{server.socket.addr}:{server.socket.port}/"
            == reg["metrics_server"].url
        )

        await server.close()

        if deregister:
            # Assert service is gone iff we are supposed to deregister.
            con.deregister_service.assert_awaited_once_with(service_id)
        else:
            con.deregister_service.assert_not_called()

    async def test_none_if_register_fails(self):
        """
        If register fails, return None.
        """

        class FakeMetricsServer:
            socket = mock.Mock(addr="127.0.0.1", port=12345)
            url = "http://127.0.0.1:12345/metrics"

        class FakeSession:
            async def __aexit__(self, exc_type, exc_value, traceback):
                pass

            async def __aenter__(self):
                class FakeConnection:
                    async def put(self, *args, **kw):
                        return mock.Mock(status=400)

                return FakeConnection()

        ca = ConsulAgent()
        ca.consul.session_factory = FakeSession

        assert None is (await ca.register(FakeMetricsServer()))


@pytest.mark.skipif(aiohttp is None, reason="Needs aiohttp.")
class TestLocalConsulAgentClient:
    def test_sets_headers(self):
        """
        If a token is passed, "X-Consul-Token" header is set.
        """
        con = _LocalConsulAgentClient(token="token42")

        assert "token42" == con.headers["X-Consul-Token"]
