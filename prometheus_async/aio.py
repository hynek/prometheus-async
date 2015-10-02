"""
asyncio-related functions.
"""

import asyncio
import sys


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
