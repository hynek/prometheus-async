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

"""
Decorators for asyncio.
"""

from __future__ import annotations

from functools import wraps
from time import perf_counter
from typing import TYPE_CHECKING, overload


if TYPE_CHECKING:
    from typing import Awaitable, Callable

    from ..types import IncDecrementer, Observer, P, T


@overload
def time(
    metric: Observer,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    ...


@overload
def time(metric: Observer, future: Awaitable[T]) -> Awaitable[T]:
    ...


def time(
    metric: Observer, future: Awaitable[T] | None = None
) -> Awaitable[T] | Callable[
    [Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]
]:
    r"""
    Call ``metric.observe(time)`` with the runtime in seconds.

    Works as a decorator as well as on :class:`asyncio.Future`\ s.

    :returns: coroutine function (if decorator) or coroutine.
    """

    def observe(start_time: float) -> None:
        metric.observe(perf_counter() - start_time)

    if future is None:

        def measure(
            wrapped: Callable[P, Awaitable[T]]
        ) -> Callable[P, Awaitable[T]]:
            @wraps(wrapped)
            async def inner(*args: P.args, **kw: P.kwargs) -> T:
                start_time = perf_counter()
                try:
                    return await wrapped(*args, **kw)
                finally:
                    observe(start_time)

            return inner

        return measure
    else:
        f = future

        async def measure_future(start_time: float) -> T:
            try:
                rv = await f
                return rv
            finally:
                observe(start_time)

        start_time = perf_counter()
        return measure_future(start_time)


@overload
def count_exceptions(
    metric: IncDecrementer, *, exc: type[BaseException] = BaseException
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    ...


@overload
def count_exceptions(
    metric: IncDecrementer,
    future: Awaitable[T],
    *,
    exc: type[BaseException] = BaseException,
) -> Awaitable[T]:
    ...


def count_exceptions(
    metric: IncDecrementer,
    future: Awaitable[T] | None = None,
    *,
    exc: type[BaseException] = BaseException,
) -> Callable[
    [Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]
] | Awaitable[T]:
    r"""
    Call ``metric.inc()`` whenever *exc* is caught.

    Works as a decorator as well as on :class:`asyncio.Future`\ s.

    :returns: coroutine function (if decorator) or coroutine.
    """
    if future is None:

        def count(
            wrapped: Callable[P, Awaitable[T]]
        ) -> Callable[P, Awaitable[T]]:
            @wraps(wrapped)
            async def inner(*args: P.args, **kw: P.kwargs) -> T:
                try:
                    rv = await wrapped(*args, **kw)
                except exc:
                    metric.inc()
                    raise

                return rv

            return inner

        return count
    else:
        f = future

        async def count_future() -> T:
            try:
                rv = await f
            except exc:
                metric.inc()
                raise
            return rv

        return count_future()


@overload
def track_inprogress(
    metric: IncDecrementer,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    ...


@overload
def track_inprogress(
    metric: IncDecrementer, future: Awaitable[T]
) -> Awaitable[T]:
    ...


def track_inprogress(
    metric: IncDecrementer, future: Awaitable[T] | None = None
) -> Callable[
    [Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]
] | Awaitable[T]:
    r"""
    Call ``metrics.inc()`` on entry and ``metric.dec()`` on exit.

    Works as a decorator, as well on :class:`asyncio.Future`\ s.

    :returns: coroutine function (if decorator) or coroutine.
    """
    if future is None:

        def track(
            wrapped: Callable[P, Awaitable[T]]
        ) -> Callable[P, Awaitable[T]]:
            @wraps(wrapped)
            async def inner(*args: P.args, **kw: P.kwargs) -> T:
                metric.inc()
                try:
                    rv = await wrapped(*args, **kw)
                finally:
                    metric.dec()

                return rv

            return inner

        return track
    else:
        f = future
        metric.inc()

        async def track_future() -> T:
            try:
                rv = await f
            finally:
                metric.dec()

            return rv

        return track_future()
