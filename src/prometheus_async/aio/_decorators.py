"""
Decorators for asyncio.
"""

import asyncio

from functools import wraps

from .._util import get_time


def time(metric, future=None, *, loop=None):
    """
    Decorator that calls ``metric.observe()`` with total runtime time.

    Works as a decorator as well as on :class:`asyncio.Future`.

    Transforms decorated callable into a co-routine.  Run time is in seconds.

    :returns: coroutine function (if decorator) or coroutine.
    """
    if loop is None:
        loop = asyncio.get_event_loop()

    if future is None:
        def decorator(f):
            @asyncio.coroutine
            @wraps(f)
            def measure(*a, **kw):
                def observe():
                    metric.observe(get_time() - start_time)
                start_time = get_time()
                rv = f(*a, **kw)
                if asyncio.iscoroutine(rv) or isinstance(rv, asyncio.Future):
                    try:
                        rv = yield from rv
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
