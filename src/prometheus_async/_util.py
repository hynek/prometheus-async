"""
Generic helpers.
"""

from __future__ import absolute_import, division, print_function

import time


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
