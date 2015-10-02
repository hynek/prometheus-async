from __future__ import absolute_import, division, print_function

try:
    import asyncio
except ImportError:
    asyncio = None

import time

import pytest
import six

from prometheus_async import decorators


py2_only = pytest.mark.skipif(six.PY3, reason="Python 2-only test.")
py3_only = pytest.mark.skipif(six.PY2, reason="Python 3-only test.")


def test_async_time_sync(fo, patch_timer):
    """
    async_time works with sync results functions.
    """
    @decorators.async_time(fo)
    def func():
        return 42

    func()

    assert [1] == fo._observed


class TestMkTime(object):
    @py2_only
    def test_py2(self):
        """
        Use time.time on Python 2
        """
        import monotonic
        assert (
            decorators.get_time is
            monotonic.time is
            decorators.mk_get_time()
        )

    @py3_only
    def test_py3(self):
        """
        Use time.perf_counter on Python 3
        """
        assert (
            decorators.get_time is
            time.perf_counter is
            decorators.mk_get_time()
        )
