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

import asyncio

import wrapt

from .._util import get_time


def time(metric, future=None):
    """
    Call ``metric.observe(time)`` with the runtime in seconds.

    Works as a decorator as well as on :class:`asyncio.Future`\ s.

    :returns: coroutine function (if decorator) or coroutine.
    """
    if future is None:
        @wrapt.decorator
        @asyncio.coroutine
        def decorator(wrapped, _, args, kw):
            def observe():
                metric.observe(get_time() - start_time)
            start_time = get_time()
            try:
                rv = yield from wrapped(*args, **kw)
                return rv
            finally:
                observe()

        return decorator
    else:
        @asyncio.coroutine
        def measure():
            def observe():
                metric.observe(get_time() - start_time)
            try:
                rv = yield from future
                return rv
            finally:
                observe()

        start_time = get_time()
        return measure()


def count_exceptions(metric, future=None, exc=BaseException):
    """
    Call ``metric.inc()`` whenever *exc* is caught.

    Works as a decorator as well as on :class:`asyncio.Future`\ s.

    :returns: coroutine function (if decorator) or coroutine.
    """
    if future is None:
        @asyncio.coroutine
        @wrapt.decorator
        def count(wrapped, _, args, kw):
            try:
                rv = yield from wrapped(*args, **kw)
            except exc:
                metric.inc()
                raise
            return rv

        return count
    else:
        @asyncio.coroutine
        def count():
            try:
                rv = yield from future
            except exc:
                metric.inc()
                raise
            return rv
        return count()


def track_inprogress(metric, future=None):
    """
    Call ``metrics.inc()`` on entry and ``metric.dec()`` on exit.

    Works as a decorator, as well on :class:`asyncio.Future`\ s.

    :returns: coroutine function (if decorator) or coroutine.
    """
    if future is None:
        @asyncio.coroutine
        @wrapt.decorator
        def track(wrapped, _, args, kw):
            metric.inc()
            try:
                rv = yield from wrapped(*args, **kw)
            finally:
                metric.dec()

            return rv

        return track
    else:
        metric.inc()

        @asyncio.coroutine
        def track():
            try:
                rv = yield from future
            finally:
                metric.dec()
            return rv
        return track()
