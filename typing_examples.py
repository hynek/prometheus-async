"""
Some examples of prometheus-async typing integration.
"""

from asyncio import Future

from prometheus_client.metrics import Gauge, Summary
from twisted.internet.defer import Deferred

from prometheus_async import aio, tx


REQ_DURATION = Summary("REQ_DUR", "Request duration")
IN_PROG = Gauge("IN_PROG", "In progress")


@aio.time(REQ_DURATION)
async def func(i: int) -> str:
    return str(i)


@aio.track_inprogress(IN_PROG)
async def func2(i: int) -> str:
    return str(i)


class C:
    @aio.time(REQ_DURATION)
    async def method(self, i: int) -> str:
        return str(i)


# The type of `func` is correct:
# "def (i: builtins.int) -> typing.Coroutine*[Any, Any, builtins.str]"
# reveal_type(func)
# reveal_type(C.method)


@aio.time(REQ_DURATION)
def future_func(i: int) -> Future[str]:
    return Future()


# `time` can also be applied to futures directly.
future = Future[str]()
aio.time(REQ_DURATION, future)


async def coro() -> None:
    pass


aio.time(REQ_DURATION, coro())  # `time` can also be applied to coroutines

aio.time(REQ_DURATION, coro)  # type: ignore  # `time` errors on coroutine fns
aio.time(REQ_DURATION, int)  # type: ignore # `time` errors on non-futures

# The type of `future_func` is correct:
# "def (i: builtins.int) -> asyncio.futures.Future*[builtins.str]"
# reveal_type(future_func)

# The following is a type error since the function cannot be awaited:
# "def (i: builtins.int) -> asyncio.futures.Future*[builtins.str]"


@aio.time(REQ_DURATION)  # type: ignore
def should_be_async_func(i: int) -> str:
    return str(i)


#
# Twisted
#
tx.time(REQ_DURATION, Deferred())


@tx.time(REQ_DURATION)
def returns_deferred(param: int) -> Deferred:
    return Deferred()


returns_deferred(1)

# Invalid, takes an int.
returns_deferred("str")  # type: ignore
