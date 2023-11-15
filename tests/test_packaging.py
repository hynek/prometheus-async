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

import sys


if sys.version_info < (3, 8):
    import importlib_metadata as metadata
else:
    from importlib import metadata

import pytest

import prometheus_async


class TestLegacyMetadataHack:
    def test_version(self):
        """
        prometheus_async.__version__ returns the correct version.
        """
        with pytest.deprecated_call():
            assert (
                metadata.version("prometheus-async")
                == prometheus_async.__version__
            )

    def test_description(self):
        """
        prometheus_async.__description__ returns the correct description.
        """
        with pytest.deprecated_call():
            assert (
                "Async helpers for prometheus_client."
                == prometheus_async.__description__
            )

    def test_uri(self):
        """
        prometheus_async.__uri__ returns the correct project URL.
        """
        with pytest.deprecated_call():
            assert (
                "https://prometheus-async.readthedocs.io/"
                == prometheus_async.__uri__
            )

    def test_email(self):
        """
        prometheus_async.__email__ returns Hynek's email address.
        """
        with pytest.deprecated_call():
            assert "hs@ox.cx" == prometheus_async.__email__

    def test_does_not_exist(self):
        """
        Asking for unsupported dunders raises an AttributeError.
        """
        with pytest.raises(
            AttributeError,
            match="module prometheus_async has no attribute __yolo__",
        ):
            prometheus_async.__yolo__
