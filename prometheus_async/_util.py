"""
Generic helpers.
"""

from __future__ import absolute_import, division, print_function

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


def mk_time(is_async, add_cb):
    """
    Create a time decorator that uses *is_async_ and *add_cb*.
    """
    def time(metric):
        """
        Decorator that wraps *metric* and calls ``metric.observe()`` w/ run
        time.

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
                if is_async(rv):
                    return add_cb(rv, observe)
                else:
                    observe(None)
                    return rv

            return measure
        return decorator
    return time
