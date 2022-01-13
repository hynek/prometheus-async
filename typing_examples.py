"""Some examples of prometheus-async typing integration."""
from asyncio import Future

from prometheus_client.metrics import Summary  # type: ignore

from prometheus_async.aio import time


REQ_DURATION = Summary("REQ_DUR", "Request duration")


@time(REQ_DURATION)
async def func(i: int) -> str:
    return str(i)


# The type of `func` is correct:
# "def (i: builtins.int) -> typing.Coroutine*[Any, Any, builtins.str]"
# reveal_type(func)


@time(REQ_DURATION)
def future_func(i: int) -> Future[str]:
    return Future()


# The type of `future_func` is correct:
# "def (i: builtins.int) -> asyncio.futures.Future*[builtins.str]"
# reveal_type(future_func)

# The following is a type error since the function cannot be awaited:
# "def (i: builtins.int) -> asyncio.futures.Future*[builtins.str]"
@time(REQ_DURATION)
def should_be_async_func(i: int) -> str:
    return str(i)
