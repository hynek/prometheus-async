"""
Wrappers to make prometheus_client's decorators async-aware.
"""

from __future__ import absolute_import, division, print_function

try:
    import asyncio
except ImportError:
    asyncio = None
    aio = None
else:
    from . import aio

try:
    import twisted
except ImportError:
    twisted = None
    tx = None
else:
    from . import tx

import time

from functools import wraps


def mk_get_time():
    """
    Create the best possible time function.
    """
    try:
        return time.perf_counter
    except AttributeError:
        import monotonic
        return monotonic.time

get_time = mk_get_time()


def mk_get_async_system():
    """
    Create a working is_future function for the respective platform.
    """
    systems = []

    if tx is not None:
        systems.append(tx)
    if aio is not None:
        systems.append(aio)

    if systems == []:
        raise RuntimeError("No async system found.")

    def get_async_system(val):
        for s in systems:
            if s.is_async(val):
                return s

    return get_async_system


get_async_system = mk_get_async_system()
"""
Returns async module responsible for *val* or `None`.
"""


def async_time(metric):
    """
    Decorator that wraps *metric* and calls ``metric.observe()`` w/ run time.

    Works with both sync and async results.  Run time is in seconds.
    """
    def decorator(f):
        @wraps(f)
        def measure(*a, **kw):
            def observe(value):
                metric.observe(get_time() - start_time)
                return value

            start_time = get_time()
            rv = f(*a, **kw)
            a = get_async_system(rv)
            if a is not None:
                return a.add_cb(rv, observe)
            else:
                observe(None)
                return rv

        return measure

    return decorator
