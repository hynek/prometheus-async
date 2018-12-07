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

import wrapt

from .._utils import get_time


def time(metric, future=None):
    r"""
    Call ``metric.observe(time)`` with the runtime in seconds.

    Works as a decorator as well as on :class:`asyncio.Future`\ s.

    :returns: coroutine function (if decorator) or coroutine.
    """
    if future is None:

        @wrapt.decorator
        async def decorator(wrapped, _, args, kw):
            def observe():
                metric.observe(get_time() - start_time)

            start_time = get_time()
            try:
                rv = await wrapped(*args, **kw)
                return rv
            finally:
                observe()

        return decorator
    else:

        async def measure():
            def observe():
                metric.observe(get_time() - start_time)

            try:
                rv = await future
                return rv
            finally:
                observe()

        start_time = get_time()
        return measure()


def count_exceptions(metric, future=None, exc=BaseException):
    r"""
    Call ``metric.inc()`` whenever *exc* is caught.

    Works as a decorator as well as on :class:`asyncio.Future`\ s.

    :returns: coroutine function (if decorator) or coroutine.
    """
    if future is None:

        @wrapt.decorator
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


def track_inprogress(metric, future=None):
    r"""
    Call ``metrics.inc()`` on entry and ``metric.dec()`` on exit.

    Works as a decorator, as well on :class:`asyncio.Future`\ s.

    :returns: coroutine function (if decorator) or coroutine.
    """
    if future is None:

        @wrapt.decorator
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
