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
        @asyncio.coroutine
        @wrapt.decorator
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
