# SPDX-License-Identifier: Apache-2.0
#
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

__title__ = "prometheus_async"

__author__ = "Hynek Schlawack"

__license__ = "Apache License, Version 2.0"
__copyright__ = f"Copyright (c) 2016 {__author__}"


from . import aio


__all__ = ["aio"]

try:
    from . import tx  # noqa: F401

    __all__.append("tx")
except ImportError:
    pass


def __getattr__(name: str) -> str:
    dunder_to_metadata = {
        "__version__": "version",
        "__description__": "summary",
        "__uri__": "",
        "__email__": "",
    }
    if name not in dunder_to_metadata.keys():
        raise AttributeError(f"module {__name__} has no attribute {name}")

    import sys
    import warnings

    if sys.version_info < (3, 8):
        from importlib_metadata import metadata
    else:
        from importlib.metadata import metadata

    warnings.warn(
        f"Accessing prometheus_async.{name} is deprecated and will be "
        "removed in a future release. Use importlib.metadata directly "
        "to query for prometheus_async's packaging metadata.",
        DeprecationWarning,
        stacklevel=2,
    )

    meta = metadata("prometheus-async")

    if name == "__uri__":
        return meta["Project-URL"].split(" ", 1)[-1]

    if name == "__email__":
        return meta["Author-email"].split("<", 1)[1].rstrip(">")

    return meta[dunder_to_metadata[name]]
