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

from __future__ import absolute_import, division, print_function

import sys

import pytest


try:
    import twisted
except ImportError:
    twisted = None


collect_ignore = []
if sys.version_info[0] == 2:
    collect_ignore.append("tests/test_aio.py")

if twisted is None:
    collect_ignore.append("tests/test_tx.py")


def mk_monotonic_timer():
    """
    Create a function that always returns the next integer beginning at 0.
    """

    def timer():
        timer.i += 1
        return timer.i

    timer.i = 0

    return timer


class FakeObserver(object):
    """
    A fake metric observer that saves all observed values in a list.
    """

    def __init__(self):
        self._observed = []

    def observe(self, value):
        self._observed.append(value)


class FakeCounter(object):
    """
    A fake counter metric.
    """

    def __init__(self):
        self._val = 0

    def inc(self):
        self._val += 1


class FakeGauge(object):
    """
    A fake Gauge.
    """

    def __init__(self):
        self._val = 0
        self._calls = 0

    def inc(self, val=1):
        self._val += val
        self._calls += 1

    def dec(self, val=1):
        self._val -= val
        self._calls += 1


@pytest.fixture(autouse=True)
def reset_registry(monkeypatch):
    """
    Ensures prometheus_client's CollectorRegistry is empty before each test.
    """
    from prometheus_client import REGISTRY

    for c in list(REGISTRY._collector_to_names):
        REGISTRY.unregister(c)


@pytest.fixture
def fo():
    return FakeObserver()


@pytest.fixture
def fc():
    return FakeCounter()


@pytest.fixture
def fg():
    return FakeGauge()


@pytest.fixture
def patch_timer(monkeypatch):
    try:
        from prometheus_async.tx import _decorators

        monkeypatch.setattr(_decorators, "get_time", mk_monotonic_timer())
    except BaseException:
        pass
    try:
        from prometheus_async.aio import _decorators

        monkeypatch.setattr(_decorators, "get_time", mk_monotonic_timer())
    except BaseException:
        pass
