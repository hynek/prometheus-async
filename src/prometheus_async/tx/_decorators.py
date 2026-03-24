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
Decorators for Twisted.
"""

from __future__ import annotations

from time import perf_counter
from typing import TYPE_CHECKING, Any, Callable, overload

from twisted.internet.defer import Deferred
from wrapt import decorator


if TYPE_CHECKING:
    from prometheus_client import Gauge

from ..types import F, Incrementer, Observer, P, T


@overload
def time(
    metric: Observer,
) -> Callable[
    [Callable[P, T | Deferred[T]]], Callable[P, T | Deferred[T]]
]: ...


@overload
def time(metric: Observer, deferred: Deferred[T]) -> Deferred[T]: ...


def time(
    metric: Observer, deferred: Deferred[T] | None = None
) -> (
    Deferred[T]
    | Callable[[Callable[P, T | Deferred[T]]], Callable[P, T | Deferred[T]]]
):
    r"""
    Call ``metric.observe(time)`` with runtime in seconds.

    Can be used as a decorator as well as on ``Deferred``\ s.

    Works with both sync and async results.

    :returns: function or ``Deferred``.
    """
    if deferred is None:

        @decorator
        def time_decorator(
            wrapped: Callable[P, T | Deferred[T]],
            instance: Any,
            args: tuple[Any, ...],
            kwargs: dict[str, Any],
        ) -> T | Deferred[T]:
            def observe(value: T) -> T:
                metric.observe(perf_counter() - start_time)
                return value

            start_time = perf_counter()
            rv = wrapped(*args, **kwargs)
            if isinstance(rv, Deferred):
                return rv.addBoth(observe)

            return observe(rv)

        return time_decorator

    def observe(value: T) -> T:
        metric.observe(perf_counter() - start_time)
        return value

    start_time = perf_counter()
    return deferred.addBoth(observe)


@overload
def count_exceptions(
    metric: Incrementer, *, exc: type[BaseException] = ...
) -> Callable[[Callable[P, T]], Callable[P, T]]: ...


@overload
def count_exceptions(
    metric: Incrementer,
    deferred: Deferred[T],
    *,
    exc: type[BaseException] = ...,
) -> Deferred[T]: ...


def count_exceptions(
    metric: Incrementer,
    deferred: Deferred[T] | None = None,
    *,
    exc: type[BaseException] = BaseException,
) -> Deferred[T] | Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Call ``metric.inc()`` whenever *exc* is caught.

    Can be used as a decorator or on a ``Deferred``.

    :returns: function (if decorator) or ``Deferred``.
    """

    def inc(fail: F) -> F:
        fail.trap(exc)  # type: ignore[no-untyped-call]
        metric.inc()
        return fail

    if deferred is None:

        @decorator
        def count_exceptions_decorator(
            wrapped: Callable[P, T | Deferred[T]],
            instance: Any,
            args: tuple[Any, ...],
            kwargs: dict[str, Any],
        ) -> T | Deferred[T]:
            try:
                rv = wrapped(*args, **kwargs)
            except exc:
                metric.inc()
                raise

            if isinstance(rv, Deferred):
                return rv.addErrback(inc)

            return rv

        return count_exceptions_decorator

    return deferred.addErrback(inc)


@overload
def track_inprogress(
    metric: Gauge,
) -> Callable[[Callable[P, T]], Callable[P, T]]: ...


@overload
def track_inprogress(metric: Gauge, deferred: Deferred[T]) -> Deferred[T]: ...


def track_inprogress(
    metric: Gauge, deferred: Deferred[T] | None = None
) -> Deferred[T] | Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Call ``metrics.inc()`` on entry and ``metric.dec()`` on exit.

    Can be used as a decorator or on a ``Deferred``.

    :returns: function (if decorator) or ``Deferred``.
    """

    def dec(rv: T) -> T:
        metric.dec()
        return rv

    if deferred is None:

        @decorator
        def track_inprogress_decorator(
            wrapped: Callable[P, T | Deferred[T]],
            instance: Any,
            args: tuple[Any, ...],
            kwargs: dict[str, Any],
        ) -> T | Deferred[T]:
            metric.inc()
            rv = wrapped(*args, **kwargs)
            if isinstance(rv, Deferred):
                return rv.addBoth(dec)

            metric.dec()
            return rv

        return track_inprogress_decorator

    metric.inc()
    return deferred.addBoth(dec)
