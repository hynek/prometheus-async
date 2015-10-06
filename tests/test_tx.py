from __future__ import absolute_import, division, print_function

import pytest

pytest.importorskip("twisted")

from twisted.internet.defer import Deferred, succeed, fail

from prometheus_async import tx


class TestTime(object):
    @pytest.inlineCallbacks
    def test_decorator(self, fo, patch_timer):
        """
        time works with functions returning Deferreds.
        """
        @tx.time(fo)
        def func():
            return succeed(42)

        rv = func()

        # Twisted runs fires callbacks immediately.
        assert [1] == fo._observed
        assert 42 == (yield rv)
        assert [1] == fo._observed

    @pytest.inlineCallbacks
    def test_decorator_exc(self, fo, patch_timer):
        """
        Does not swallow exceptions.
        """
        v = ValueError("foo")

        @tx.time(fo)
        def func():
            return fail(v)

        with pytest.raises(ValueError) as e:
            yield func()

        assert v is e.value

    @pytest.inlineCallbacks
    def test_deferred(self, fo, patch_timer):
        """
        time works with Deferreds.
        """
        d = tx.time(fo, Deferred())

        assert [] == fo._observed

        d.callback(42)

        assert 42 == (yield d)
        assert [1] == fo._observed
