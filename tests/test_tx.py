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


import pytest
import pytest_twisted

from twisted.internet.defer import Deferred, fail, succeed

from prometheus_async import tx


class TestTime:
    @pytest.mark.usefixtures("patch_timer")
    @pytest_twisted.inlineCallbacks
    def test_decorator_sync(self, fake_observer):
        """
        time works with sync results functions.
        """

        @tx.time(fake_observer)
        def func():
            return 42

        assert 42 == (yield func())
        assert [1] == fake_observer._observed

    @pytest.mark.usefixtures("patch_timer")
    @pytest_twisted.inlineCallbacks
    def test_decorator(self, fake_observer):
        """
        time works with functions returning Deferreds.
        """

        @tx.time(fake_observer)
        def func():
            return succeed(42)

        rv = func()

        # Twisted runs fires callbacks immediately.
        assert [1] == fake_observer._observed
        assert 42 == (yield rv)
        assert [1] == fake_observer._observed

    @pytest.mark.usefixtures("patch_timer")
    @pytest_twisted.inlineCallbacks
    def test_decorator_exc(self, fake_observer):
        """
        Does not swallow exceptions.
        """
        v = ValueError("foo")

        @tx.time(fake_observer)
        def func():
            return fail(v)

        with pytest.raises(ValueError) as e:
            yield func()

        assert v is e.value

    @pytest.mark.usefixtures("patch_timer")
    @pytest_twisted.inlineCallbacks
    def test_deferred(self, fake_observer):
        """
        time works with Deferreds.
        """
        d = tx.time(fake_observer, Deferred())

        assert [] == fake_observer._observed

        d.callback(42)

        assert 42 == (yield d)
        assert [1] == fake_observer._observed


class TestCountExceptions:
    @pytest_twisted.inlineCallbacks
    def test_decorator_no_exc(self, fake_counter):
        """
        If no exception is raised, the counter does not change.
        """

        @tx.count_exceptions(fake_counter)
        def func():
            return succeed(42)

        assert 42 == (yield func())
        assert 0 == fake_counter._val

    def test_decorator_no_exc_sync(self, fake_counter):
        """
        If no exception is raised, the counter does not change.
        """

        @tx.count_exceptions(fake_counter)
        def func():
            return 42

        assert 42 == func()
        assert 0 == fake_counter._val

    @pytest_twisted.inlineCallbacks
    def test_decorator_wrong_exc(self, fake_counter):
        """
        If a wrong exception is raised, the counter does not change.
        """

        @tx.count_exceptions(fake_counter, exc=ValueError)
        def func():
            return fail(TypeError())

        with pytest.raises(TypeError):
            yield func()

        assert 0 == fake_counter._val

    @pytest_twisted.inlineCallbacks
    def test_decorator_exc(self, fake_counter):
        """
        If the correct exception is raised, count it.
        """

        @tx.count_exceptions(fake_counter, exc=TypeError)
        def func():
            return fail(TypeError())

        with pytest.raises(TypeError):
            yield func()

        assert 1 == fake_counter._val

    def test_decorator_exc_sync(self, fake_counter):
        """
        If the correct synchronous exception is raised, count it.
        """

        @tx.count_exceptions(fake_counter)
        def func():
            if True:
                raise TypeError("foo")
            return succeed(42)

        with pytest.raises(TypeError):
            func()

        assert 1 == fake_counter._val

    @pytest_twisted.inlineCallbacks
    def test_deferred_no_exc(self, fake_counter):
        """
        If no exception is raised, the counter does not change.
        """
        d = succeed(42)

        assert 42 == (yield tx.count_exceptions(fake_counter, d))
        assert 0 == fake_counter._val


class TestTrackInprogress:
    @pytest_twisted.inlineCallbacks
    def test_deferred(self, fake_gauge):
        """
        Incs and decs if its passed a Deferred.
        """
        d = tx.track_inprogress(fake_gauge, Deferred())

        assert 1 == fake_gauge._val

        d.callback(42)
        rv = yield d

        assert 42 == rv
        assert 0 == fake_gauge._val

    @pytest_twisted.inlineCallbacks
    def test_decorator_deferred(self, fake_gauge):
        """
        Incs and decs if the decorated function returns a Deferred.
        """
        d = Deferred()

        @tx.track_inprogress(fake_gauge)
        def func():
            return d

        rv = func()

        assert 1 == fake_gauge._val

        d.callback(42)
        rv = yield rv

        assert 42 == rv
        assert 0 == fake_gauge._val

    def test_decorator_value(self, fake_gauge):
        """
        Incs and decs if the decorated function returns a value.
        """

        @tx.track_inprogress(fake_gauge)
        def func():
            return 42

        rv = func()

        assert 42 == rv
        assert 0 == fake_gauge._val
        assert 2 == fake_gauge._calls
