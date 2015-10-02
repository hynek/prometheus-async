"""
Twisted-related functions.
"""

from twisted.internet.defer import Deferred


def is_async(val):
    return isinstance(val, Deferred)


def add_cb(val, observer):
    return val.addBoth(observer)
