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
Decorators for asyncio.
"""

from asyncio import Future
from time import perf_counter
from typing import Awaitable, Callable, Type, TypeVar, overload

from typing_extensions import ParamSpec
from wrapt import decorator


P = ParamSpec("P")
R = TypeVar("R", bound=Awaitable)
T = TypeVar("T")


@overload
def time(
    metric,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    ...


@overload
def time(metric, future: Awaitable[T]) -> Awaitable[T]:
    ...


def time(metric, future=None):
    r"""
    Call ``metric.observe(time)`` with the runtime in seconds.

    Works as a decorator as well as on :class:`asyncio.Future`\ s.

    :returns: coroutine function (if decorator) or coroutine.
    """

    def observe(start_time: float):
        metric.observe(perf_counter() - start_time)

    if future is None:

        @decorator
        async def time_decorator(wrapped, _, args, kw):
            start_time = perf_counter()
            try:
                rv = await wrapped(*args, **kw)
                return rv
            finally:
                observe(start_time)

        return time_decorator
    else:

        async def measure(start_time):
            try:
                rv = await future
                return rv
            finally:
                observe(start_time)

        start_time = perf_counter()
        return measure(start_time)


@overload
def count_exceptions(
    metric, exc: Type[BaseException] = BaseException
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    ...


@overload
def count_exceptions(
    metric, future: Awaitable[T], exc: Type[BaseException] = BaseException
) -> Awaitable[T]:
    ...


def count_exceptions(metric, future=None, exc=BaseException):
    r"""
    Call ``metric.inc()`` whenever *exc* is caught.

    Works as a decorator as well as on :class:`asyncio.Future`\ s.

    :returns: coroutine function (if decorator) or coroutine.
    """
    if future is None:

        @decorator
        async def count(wrapped, _, args, kw):
            try:
                rv = await wrapped(*args, **kw)
            except exc:
                metric.inc()
                raise
            return rv

        return count
    else:

        async def count():
            try:
                rv = await future
            except exc:
                metric.inc()
                raise
            return rv

        return count()


@overload
def track_inprogress(metric) -> Callable[[Callable[P, R]], Callable[P, R]]:
    ...


@overload
def track_inprogress(metric, future: Awaitable[T]) -> Awaitable[T]:
    ...


def track_inprogress(metric, future=None):
    r"""
    Call ``metrics.inc()`` on entry and ``metric.dec()`` on exit.

    Works as a decorator, as well on :class:`asyncio.Future`\ s.

    :returns: coroutine function (if decorator) or coroutine.
    """
    if future is None:

        @decorator
        async def track(wrapped, _, args, kw):
            metric.inc()
            try:
                rv = await wrapped(*args, **kw)
            finally:
                metric.dec()

            return rv

        return track
    else:
        metric.inc()

        async def track():
            try:
                rv = await future
            finally:
                metric.dec()
            return rv

        return track()
