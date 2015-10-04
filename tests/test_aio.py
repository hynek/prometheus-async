import asyncio

import pytest

try:
    import aiohttp
except ImportError:
    aiohttp = None

try:
    from twisted.internet.defer import Deferred
except ImportError:
    Deferred = object

from prometheus_client import Counter

from prometheus_async import aio


@asyncio.coroutine
def coro():
    yield from asyncio.sleep(0)


class TestAsyncIO:
    def test_time_sync(self, fo, patch_timer):
        """
        time works with sync results functions.
        """
        @aio.time(fo)
        def func():
            return 42

        func()

        assert [1] == fo._observed

    @pytest.mark.parametrize("async_val", [
        asyncio.Future(),
        coro(),
    ])
    def test_is_async_true(self, async_val):
        """
        is_async recognizes asynchronous objects.
        """
        assert True is aio._decorators.is_async(async_val)

    @pytest.mark.parametrize("sync_val", [
        None,
        "sync",
        object(),
        Deferred(),
    ])
    def test_is_async_false(self, sync_val):
        """
        is_async rejects everything else.
        """
        assert False is aio._decorators.is_async(sync_val)

    @pytest.mark.asyncio
    def test_asyncio(self, fo, patch_timer):
        """
        time works with asyncio results functions.
        """
        @aio.time(fo)
        @asyncio.coroutine
        def func():
            yield from asyncio.sleep(0)
            return 42

        rv = func()

        assert isinstance(rv, asyncio.Future)
        assert [] == fo._observed

        rv = yield from rv
        assert [1] == fo._observed
        assert 42 == rv

    @pytest.mark.asyncio
    def test_asyncio_exc(self, fo, patch_timer):
        """
        Does not swallow exceptions.
        """
        @aio.time(fo)
        @asyncio.coroutine
        def func():
            yield from asyncio.sleep(0)
            raise ValueError

        with pytest.raises(ValueError):
            yield from func()


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

    @pytest.mark.asyncio
    def test_start_http_server(self, event_loop):
        """
        Integration test: server gets started and serves stats.
        """
        srv, handler = yield from aio.web.start_http_server(0, loop=event_loop)
        addr, port = srv.sockets[0].getsockname()
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
        yield from handler.finish_connections(3)
        srv.close()
