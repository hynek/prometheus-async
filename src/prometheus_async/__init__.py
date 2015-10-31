"""
Async helpers for prometheus_client.
"""

from __future__ import absolute_import, division, print_function

import six


__version__ = "15.0.0.dev1"

__title__ = "prometheus_async"
__description__ = "Async helpers for prometheus_client."
__uri__ = ""

__author__ = "Hynek Schlawack"
__email__ = "hs@ox.cx"

__license__ = "MIT"
__copyright__ = "Copyright (c) 2015 {0}".format(__author__)


__all__ = []

try:
    import twisted  # noqa -- only to detect Twisted
except ImportError:
    pass
else:
    from . import tx  # noqa -- flake8 doesn't understand the __all__.append

    __all__.append("tx")

if six.PY3:
    from . import aio  # noqa -- flake8 doesn't understand the __all__.append

    __all__.append("aio")
