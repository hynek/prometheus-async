"""
Decorators for asyncio.
"""

import asyncio
import sys

from .._util import mk_async_time


vi = sys.version_info
if vi[0:2] == (3, 4) and vi[2] < 4:
    ensure_future = asyncio.async
else:
    ensure_future = asyncio.ensure_future


def is_async(val):
    return asyncio.iscoroutine(val) or isinstance(val, asyncio.Future)


def add_cb(val, observer):
    fut = ensure_future(val)
    fut.add_done_callback(observer)
    return fut


async_time = mk_async_time(is_async, add_cb)
