"""
Decorators for Twisted.
"""

from functools import wraps

from twisted.internet.defer import Deferred

from .._util import get_time


def time(metric, deferred=None):
    """
    Call ``metric.observe(time)`` with  runtime in seconds.

    Can be used as a decorator as well as on ``Deferred``\ s.

    Works with both sync and async results.

    :returns: callable or ``Deferred``.
    """
    if deferred is None:
        def decorator(f):
            @wraps(f)
            def measure(*a, **kw):
                def observe(value):
                    metric.observe(get_time() - start_time)
                    return value

                start_time = get_time()
                rv = f(*a, **kw)
                if isinstance(rv, Deferred):
                    return rv.addBoth(observe)
                else:
                    observe(None)
                    return rv

            return measure
        return decorator
    else:
        def observe(value):
            metric.observe(get_time() - start_time)
            return value

        start_time = get_time()
        return deferred.addBoth(observe)


def count_exceptions(metric, deferred=None, exc=BaseException):
    """
    Call ``metric.inc()`` whenever *exc* is caught.

    Can be used as a decorator or on a ``Deferred``.
    """
    def inc(fail):
        fail.trap(exc)
        metric.inc()
        return fail

    if deferred is None:
        def decorator(f):
            @wraps(f)
            def count(*a, **kw):
                try:
                    rv = f(*a, **kw)
                except exc:
                    metric.inc()
                    raise

                if isinstance(rv, Deferred):
                    return rv.addErrback(inc)
                else:
                    return rv

            return count

        return decorator
    else:
        return deferred.addErrback(inc)
