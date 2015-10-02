"""
Async helpers for prometheus_client.
"""

from __future__ import absolute_import, division, print_function


__version__ = "15.0.0.dev0"

__title__ = "prometheus_async"
__description__ = "Async helpers for prometheus_client."
__uri__ = ""

__author__ = "Hynek Schlawack"
__email__ = "hs@ox.cx"

__license__ = "MIT"
__copyright__ = "Copyright (c) 2015 {0}".format(__author__)


from .decorators import async_time


__all__ = [
    "async_time",
]
