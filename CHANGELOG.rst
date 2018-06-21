.. :changelog:

Changelog
=========

Versions are year-based with a strict backward compatibility policy.
The third digit is only for regressions.


18.3.0 (2018-06-21)
-------------------


Backward-incompatible changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*none*


Deprecations:
^^^^^^^^^^^^^

*none*


Changes:
^^^^^^^^

- The HTTP access log when using ``prometheus_async.start_http_server()`` is disabled now.
  It was activated accidentally when moving to ``aiohttp``'s application runner APIs.


----


18.2.0 (2018-05-29)
-------------------


Backward-incompatible changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*none*


Deprecations:
^^^^^^^^^^^^^

- Passing a *loop* argument to ``prometheus_async.aio.start_http_server()`` is a no-op and raises a ``DeprecationWarning`` now.


Changes:
^^^^^^^^

- Port to ``aiohttp``'s application runner APIs to avoid those pesky deprecation warnings.
  As a consequence, the *loop* argument has been removed from internal APIs and became a no-op in public APIs.


----


18.1.0 (2018-02-15)
-------------------


Backward-incompatible changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Python 3.4 is no longer supported.
- ``aiohttp`` 3.0 or later is now required for aio metrics exposure.


Deprecations:
^^^^^^^^^^^^^

*none*


Changes:
^^^^^^^^

- ``python-consul`` is no longer required for asyncio Consul service discovery.
  A plain ``aiohttp`` is enough now.


----


17.5.0 (2017-10-30)
-------------------

Backward-incompatible changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``prometheus_async.aio.web`` now requires ``aiohttp`` 2.0 or later.


Changes:
^^^^^^^^

- The thread created by ``prometheus_async.aio.start_http_server_in_thread()`` has a human-readable name now.
- Fixed compatibility with ``aiohttp`` 2.3.


----


17.4.0 (2017-08-14)
-------------------


Backward-incompatible changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*none*


Deprecations:
^^^^^^^^^^^^^

*none*


Changes:
^^^^^^^^

- Set proper content type header for the root redirection page.


----


17.3.0 (2017-06-01)
-------------------


Backward-incompatible changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*none*


Deprecations:
^^^^^^^^^^^^^

*none*


Changes:
^^^^^^^^

- ``prometheus_async.aio.web.start_http_server()`` now passes the *loop* argument to ``aiohttp.web.Application.make_handler()`` instead of ``Application``\ 's initializer.
  This fixes a "loop argument is deprecated" warning.


----


17.2.0 (2017-03-21)
-------------------


Deprecations:
^^^^^^^^^^^^^

- Using ``aiohttp`` older than 0.21 is now deprecated.


Changes:
^^^^^^^^

- ``prometheus_async.aio.web`` now supports ``aiohttp`` 2.0.


----


17.1.0 (2017-01-14)
-------------------

Changes:
^^^^^^^^

- Fix monotonic timer on Python 2.
  `#7 <https://github.com/hynek/prometheus_async/issues/7>`_


----


16.2.0 (2016-10-28)
-------------------

Changes:
^^^^^^^^

- When using the aiohttp metrics exporter, create the web application using an explicit loop argument.
  `#6 <https://github.com/hynek/prometheus_async/pull/6>`_


----


16.1.0 (2016-09-23)
-------------------

Changes:
^^^^^^^^

- Service discovery deregistration is optional now.


----


16.0.0 (2016-05-19)
-------------------

Changes:
^^^^^^^^

- Initial release.
