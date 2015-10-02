import asyncio

import pytest

try:
    from twisted.internet.defer import Deferred
except ImportError:
    Deferred = object

from prometheus_async import decorators, aio


@asyncio.coroutine
def coro():
    yield from asyncio.sleep(0)


class TestAsyncIO:
    @pytest.mark.parametrize("async_val", [
        asyncio.Future(),
        coro(),
    ])
    def test_is_async_true(self, async_val):
        """
        is_async recognizes asynchronous objects.
        """
        assert True is aio.is_async(async_val)

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
        assert False is aio.is_async(sync_val)

    @pytest.mark.asyncio
    def test_asyncio(self, fo, patch_timer):
        """
        async_time works with asyncio results functions.
        """
        @decorators.async_time(fo)
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
        @decorators.async_time(fo)
        @asyncio.coroutine
        def func():
            yield from asyncio.sleep(0)
            raise ValueError

        with pytest.raises(ValueError):
            yield from func()
