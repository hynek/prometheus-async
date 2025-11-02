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

from collections.abc import Awaitable
from time import perf_counter
from typing import TYPE_CHECKING, Any, Callable, overload

from wrapt import decorator


if TYPE_CHECKING:
    from prometheus_client import Gauge

    from ..types import Incrementer, Observer, P, R, T


@overload
def time(metric: Observer) -> Callable[[Callable[P, R]], Callable[P, R]]: ...


@overload
def time(metric: Observer, future: Awaitable[T]) -> Awaitable[T]: ...


def time(
    metric: Observer, future: Awaitable[T] | None = None
) -> Awaitable[T] | Callable[[Callable[P, R]], Callable[P, R]]:
    r"""
    Call ``metric.observe(time)`` with the runtime in seconds.

    Works as a decorator as well as on :class:`asyncio.Future`\ s.

    :returns: coroutine function (if decorator) or coroutine.
    """

    def observe(start_time: float) -> None:
        metric.observe(perf_counter() - start_time)

    if future is None:

        @decorator  # type: ignore[arg-type]
        async def time_decorator(
            wrapped: Callable[P, R],
            instance: Any,
            args: tuple[Any, ...],
            kwargs: dict[str, Any],
        ) -> R:
            start_time = perf_counter()
            try:
                return await wrapped(*args, **kwargs)
            finally:
                observe(start_time)

        return time_decorator  # type: ignore[return-value]

    f = future

    async def measure(start_time: float) -> T:
        try:
            return await f
        finally:
            observe(start_time)

    start_time = perf_counter()
    return measure(start_time)


@overload
def count_exceptions(
    metric: Incrementer, *, exc: type[BaseException] = BaseException
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...


@overload
def count_exceptions(
    metric: Incrementer,
    future: Awaitable[T],
    *,
    exc: type[BaseException] = BaseException,
) -> Awaitable[T]: ...


def count_exceptions(
    metric: Incrementer,
    future: Awaitable[T] | None = None,
    *,
    exc: type[BaseException] = BaseException,
) -> Callable[[Callable[P, R]], Callable[P, R]] | Awaitable[T]:
    r"""
    Call ``metric.inc()`` whenever *exc* is caught.

    Works as a decorator as well as on :class:`asyncio.Future`\ s.

    :returns: coroutine function (if decorator) or coroutine.
    """
    if future is None:

        @decorator  # type: ignore[arg-type]
        async def count_decorator(
            wrapped: Callable[P, R],
            instance: Any,
            args: tuple[Any, ...],
            kwargs: dict[str, Any],
        ) -> R:
            try:
                rv = await wrapped(*args, **kwargs)
            except exc:
                metric.inc()
                raise
            return rv

        return count_decorator  # type: ignore[return-value]

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
    metric: Gauge,
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...


@overload
def track_inprogress(metric: Gauge, future: Awaitable[T]) -> Awaitable[T]: ...


def track_inprogress(
    metric: Gauge, future: Awaitable[T] | None = None
) -> Callable[[Callable[P, R]], Callable[P, R]] | Awaitable[T]:
    r"""
    Call ``metrics.inc()`` on entry and ``metric.dec()`` on exit.

    Works as a decorator, as well on :class:`asyncio.Future`\ s.

    :returns: coroutine function (if decorator) or coroutine.
    """
    if future is None:

        @decorator  # type: ignore[arg-type]
        async def track_decorator(
            wrapped: Callable[P, R],
            instance: Any,
            args: tuple[Any, ...],
            kwargs: dict[str, Any],
        ) -> R:
            metric.inc()
            try:
                rv = await wrapped(*args, **kwargs)
            finally:
                metric.dec()

            return rv

        return track_decorator  # type: ignore[return-value]

    else:  # noqa: RET505
        f = future
        metric.inc()

        async def track_future() -> T:
            try:
                rv = await f
            finally:
                metric.dec()
            return rv

        return track_future()
