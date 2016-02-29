# Copyright 2016 Hynek Schlawack
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Async helpers for prometheus_client.
"""

from __future__ import absolute_import, division, print_function

import six


__version__ = "16.0.0.dev5"

__title__ = "prometheus_async"
__description__ = "Async helpers for prometheus_client."
__uri__ = "https://prometheus-async.readthedocs.org/"

__author__ = "Hynek Schlawack"
__email__ = "hs@ox.cx"

__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright (c) 2016 {0}".format(__author__)


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
