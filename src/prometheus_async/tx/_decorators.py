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

from functools import wraps
from time import perf_counter
from typing import TYPE_CHECKING, TypeVar, overload

from twisted.internet.defer import Deferred
from twisted.python.failure import Failure

from ..types import IncDecrementer


if TYPE_CHECKING:
    from typing import Callable

    from ..types import Observer, P, T


D = TypeVar("D", bound=Deferred)
F = TypeVar("F", bound=Failure)


@overload
def time(metric: Observer) -> Callable[[Callable[P, T]], Callable[P, T]]:
    ...


@overload
def time(metric: Observer, deferred: D) -> D:
    ...


def time(
    metric: Observer, deferred: D | None = None
) -> D | Callable[[Callable[P, T]], Callable[P, T]]:
    r"""
    Call ``metric.observe(time)`` with runtime in seconds.

    Can be used as a decorator as well as on ``Deferred``\ s.

    Works with both sync and async results.

    :returns: function or ``Deferred``.
    """
    if deferred is None:

        def measure(wrapped: Callable[P, T]) -> Callable[P, T]:
            @wraps(wrapped)
            def inner(*args: P.args, **kw: P.kwargs) -> T:
                def observe(value: T) -> T:
                    metric.observe(perf_counter() - start_time)
                    return value

                start_time = perf_counter()
                rv = wrapped(*args, **kw)
                if isinstance(rv, Deferred):
                    return rv.addBoth(observe)  # type: ignore
                else:
                    return observe(rv)

            return inner

        return measure
    else:

        def measure_deferred(value: T) -> T:
            metric.observe(perf_counter() - start_time)
            return value

        start_time = perf_counter()
        return deferred.addBoth(measure_deferred)  # type: ignore


@overload
def count_exceptions(
    metric: IncDecrementer, *, exc: type[BaseException] = ...
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    ...


@overload
def count_exceptions(
    metric: IncDecrementer,
    deferred: D,
    *,
    exc: type[BaseException] = ...,
) -> D:
    ...


def count_exceptions(
    metric: IncDecrementer,
    deferred: D | None = None,
    *,
    exc: type[BaseException] = BaseException,
) -> D | Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Call ``metric.inc()`` whenever *exc* is caught.

    Can be used as a decorator or on a ``Deferred``.

    :returns: function (if decorator) or ``Deferred``.
    """

    def inc(fail: F) -> F:
        fail.trap(exc)  # type: ignore
        metric.inc()
        return fail

    if deferred is None:

        def count_exceptions_decorator(
            wrapped: Callable[P, T]
        ) -> Callable[P, T]:
            @wraps(wrapped)
            def inner(*args: P.args, **kw: P.kwargs) -> T:
                try:
                    rv = wrapped(*args, **kw)
                except exc:
                    metric.inc()
                    raise

                if isinstance(rv, Deferred):
                    return rv.addErrback(inc)  # type: ignore
                else:
                    return rv

            return inner

        return count_exceptions_decorator
    else:
        return deferred.addErrback(inc)  # type: ignore


@overload
def track_inprogress(
    metric: IncDecrementer,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    ...


@overload
def track_inprogress(metric: IncDecrementer, deferred: D) -> D:
    ...


def track_inprogress(
    metric: IncDecrementer, deferred: D | None = None
) -> D | Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Call ``metrics.inc()`` on entry and ``metric.dec()`` on exit.

    Can be used as a decorator or on a ``Deferred``.

    :returns: function (if decorator) or ``Deferred``.
    """

    def dec(rv: T) -> T:
        metric.dec()
        return rv

    if deferred is None:

        def track_inprogress_decorator(
            wrapped: Callable[P, T]
        ) -> Callable[P, T]:
            @wraps(wrapped)
            def inner(*args: P.args, **kw: P.kwargs) -> T:
                metric.inc()
                try:
                    rv = wrapped(*args, **kw)
                finally:
                    if isinstance(rv, Deferred):
                        return rv.addBoth(dec)  # type: ignore
                    else:
                        metric.dec()
                        return rv

            return inner

        return track_inprogress_decorator
    else:
        metric.inc()
        return deferred.addBoth(dec)  # type: ignore
