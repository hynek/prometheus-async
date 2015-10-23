"""
Decorators for asyncio.
"""

import asyncio

from functools import wraps

from .._util import get_time


def time(metric, future=None):
    """
    Call ``metric.observe(time)`` with the runtime in seconds.

    Works as a decorator as well as on :class:`asyncio.Future`\ s.

    :returns: coroutine function (if decorator) or coroutine.
    """
    if future is None:
        def decorator(f):
            @asyncio.coroutine
            @wraps(f)
            def measure(*a, **kw):
                def observe():
                    metric.observe(get_time() - start_time)
                start_time = get_time()
                try:
                    rv = yield from f(*a, **kw)
                except:
                    observe()
                    raise
                observe()
                return rv

            return measure
        return decorator
    else:
        @asyncio.coroutine
        def measure():
            def observe():
                metric.observe(get_time() - start_time)
            try:
                rv = yield from future
            except:
                observe()
                raise
            observe()
            return rv

        start_time = get_time()
        return measure()


def count_exceptions(metric, future=None, exc=BaseException):
    """
    Call ``metric.inc()`` whenever *exc* is caught.

    Works as a decorator as well as on :class:`asyncio.Future`\ s.

    :returns: coroutine function (if decorator) or coroutine.
    """
    if future is None:
        def decorator(f):
            @asyncio.coroutine
            @wraps(f)
            def count(*a, **kw):
                try:
                    rv = yield from f(*a, **kw)
                except exc:
                    metric.inc()
                    raise
                return rv

            return count
        return decorator
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
