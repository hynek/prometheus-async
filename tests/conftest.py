from __future__ import absolute_import, division, print_function

import sys

import pytest


collect_ignore = []
if sys.version_info[0] == 2:
    collect_ignore.append("test_aio.py")


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


@pytest.fixture
def fo():
    return FakeObserver()


@pytest.fixture
def patch_timer(monkeypatch):
    try:
        from prometheus_async.tx import _decorators
        monkeypatch.setattr(_decorators, "get_time", mk_monotonic_timer())
    except:
        pass
    try:
        from prometheus_async.aio import _decorators
        monkeypatch.setattr(_decorators, "get_time", mk_monotonic_timer())
    except:
        print("failed")
