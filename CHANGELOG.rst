.. :changelog:

Changelog
=========

Versions are year-based with a strict backward compatibility policy.
The third digit is only for regressions.


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
