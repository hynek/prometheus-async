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

import pytest

from twisted.internet.defer import Deferred, fail, succeed

from prometheus_async import tx


class TestTime(object):
    @pytest.inlineCallbacks
    def test_decorator_sync(self, fo, patch_timer):
        """
        time works with sync results functions.
        """

        @tx.time(fo)
        def func():
            return 42

        assert 42 == (yield func())
        assert [1] == fo._observed

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


class TestCountExceptions(object):
    @pytest.inlineCallbacks
    def test_decorator_no_exc(self, fc):
        """
        If no exception is raised, the counter does not change.
        """

        @tx.count_exceptions(fc)
        def func():
            return succeed(42)

        assert 42 == (yield func())
        assert 0 == fc._val

    def test_decorator_no_exc_sync(self, fc):
        """
        If no exception is raised, the counter does not change.
        """

        @tx.count_exceptions(fc)
        def func():
            return 42

        assert 42 == func()
        assert 0 == fc._val

    @pytest.inlineCallbacks
    def test_decorator_wrong_exc(self, fc):
        """
        If a wrong exception is raised, the counter does not change.
        """

        @tx.count_exceptions(fc, exc=ValueError)
        def func():
            return fail(TypeError())

        with pytest.raises(TypeError):
            yield func()

        assert 0 == fc._val

    @pytest.inlineCallbacks
    def test_decorator_exc(self, fc):
        """
        If the correct exception is raised, count it.
        """

        @tx.count_exceptions(fc, exc=TypeError)
        def func():
            return fail(TypeError())

        with pytest.raises(TypeError):
            yield func()

        assert 1 == fc._val

    def test_decorator_exc_sync(self, fc):
        """
        If the correct synchronous exception is raised, count it.
        """

        @tx.count_exceptions(fc)
        def func():
            if True:
                raise TypeError("foo")
            return succeed(42)

        with pytest.raises(TypeError):
            func()

        assert 1 == fc._val

    @pytest.inlineCallbacks
    def test_deferred_no_exc(self, fc):
        """
        If no exception is raised, the counter does not change.
        """
        d = succeed(42)

        assert 42 == (yield tx.count_exceptions(fc, d))
        assert 0 == fc._val


class TestTrackInprogress(object):
    @pytest.inlineCallbacks
    def test_deferred(self, fg):
        """
        Incs and decs if its passed a Deferred.
        """
        d = tx.track_inprogress(fg, Deferred())

        assert 1 == fg._val

        d.callback(42)
        rv = yield d

        assert 42 == rv
        assert 0 == fg._val

    @pytest.inlineCallbacks
    def test_decorator_deferred(self, fg):
        """
        Incs and decs if the decorated function returns a Deferred.
        """
        d = Deferred()

        @tx.track_inprogress(fg)
        def func():
            return d

        rv = func()

        assert 1 == fg._val

        d.callback(42)
        rv = yield rv

        assert 42 == rv
        assert 0 == fg._val

    def test_decorator_value(self, fg):
        """
        Incs and decs if the decorated function returns a value.
        """

        @tx.track_inprogress(fg)
        def func():
            return 42

        rv = func()

        assert 42 == rv
        assert 0 == fg._val
        assert 2 == fg._calls
