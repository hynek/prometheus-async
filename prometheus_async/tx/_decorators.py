"""
Decorators for Twisted.
"""

from twisted.internet.defer import Deferred

from .._util import mk_time


def is_async(val):
    return isinstance(val, Deferred)


def add_cb(val, observer):
    return val.addBoth(observer)


time = mk_time(is_async, add_cb)
