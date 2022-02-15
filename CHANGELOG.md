# Changelog

All notable changes to this project will be documented in this file.

The format is based on [*Keep a Changelog*](https://keepachangelog.com/en/1.0.0/) and this project adheres to [*Calendar Versioning*](https://calver.org/).

The **first number** of the version is the year.
The **second number** is incremented with each release, starting at 1 for each year.
The **third number** is when we need to start branches for older releases (only for emergencies).

*prometheus-async* has a very strong backwards-compatibility policy.
Generally speaking, you shouldn't ever be afraid of updating.

Whenever breaking changes are needed, they are:

1.  …announced here in the changelog.
2.  …the old behavior raises a `DeprecationWarning` for a year (if possible).
3.  …are done with another announcement in the changelog.

<!-- changelog follows -->

## [22.1.0](https://github.com/hynek/prometheus-async/compare/19.2.0...22.1.0) - 2022-02-15

### Removed

- Support for Python 2.7, 3.5, and 3.6 has been dropped.
- The *loop* argument has been removed from `prometheus_async.aio.start_http_server()`.


### Added

- Added type hints for all APIs.
  [#21](https://github.com/hynek/prometheus-async/pull/21)
- Added support for [OpenMetrics](https://openmetrics.io) exposition in `prometheus_async.aio.web.server_stats()` and thus `prometheus_async.aio.web.start_http_server_in_thread()`.
  [#23](https://github.com/hynek/prometheus-async/issues/23)


## [19.2.0](https://github.com/hynek/prometheus-async/compare/19.1.0...19.2.0) - 2019-01-17

### Fixed

- Revert the switch to decorator.py since it turned out to be a very breaking change.
  Please note that the now-current release of *wrapt* 1.11.0 has a [memory leak](https://github.com/GrahamDumpleton/wrapt/issues/128) so you should block it in your lockfile.

  Sorry for the inconvenience this has caused!


## [19.1.0](https://github.com/hynek/prometheus-async/compare/18.4.0...19.1.0) - 2019-01-15

### Changed

- Dropped most dependencies and switched to *decorator.py* to avoid a C dependency (*wrapt*) that produces functions that can't be pickled.


## [18.4.0](https://github.com/hynek/prometheus-async/compare/18.3.0...18.4.0) - 2018-12-07

### Removed

- *prometheus_client* 0.0.18 or newer is now required.


### Fixed

- Restored compatibility with *prometheus_client* 0.5.


## [18.3.0](https://github.com/hynek/prometheus-async/compare/18.2.0...18.3.0) - 2018-06-21

### Fixed

- The HTTP access log when using `prometheus_async.start_http_server()` is disabled now.
  It was activated accidentally when moving to *aiohttp*'s application runner APIs.


## [18.2.0](https://github.com/hynek/prometheus-async/compare/18.1.0...18.2.0) - 2018-05-29

### Deprecated

- Passing a *loop* argument to `prometheus_async.aio.start_http_server()` is a no-op and raises a `DeprecationWarning` now.


### Changed

- Port to *aiohttp*'s application runner APIs to avoid those pesky deprecation warnings.
  As a consequence, the *loop* argument has been removed from internal APIs and became a no-op in public APIs.


## [18.1.0](https://github.com/hynek/prometheus-async/compare/17.5.0...18.1.0) - 2018-02-15

### Removed

- Python 3.4 is no longer supported.
- *aiohttp* 3.0 or later is now required for aio metrics exposure.


### Changed

- *python-consul* is no longer required for asyncio Consul service discovery.
  A plain *aiohttp* is enough now.


## [17.5.0](https://github.com/hynek/prometheus-async/compare/17.4.0...17.5.0) - 2017-10-30

### Removed

- `prometheus_async.aio.web` now requires *aiohttp* 2.0 or later.


### Added

- The thread created by `prometheus_async.aio.start_http_server_in_thread()` has a human-readable name now.


### Fixed

- Fixed compatibility with *aiohttp* 2.3.


## [17.4.0](https://github.com/hynek/prometheus-async/compare/17.3.0...17.4.0) - 2017-08-14

### Fixed

- Set proper content type header for the root redirection page.


## [17.3.0](https://github.com/hynek/prometheus-async/compare/17.2.0...17.3.0) - 2017-06-01

### Fixed

- `prometheus_async.aio.web.start_http_server()` now passes the *loop* argument to `aiohttp.web.Application.make_handler()` instead of `Application`'s initializer.
  This fixes a "loop argument is deprecated" warning.


## [17.2.0](https://github.com/hynek/prometheus-async/compare/17.1.0...17.2.0) - 2017-03-21

### Deprecated

-  Using *aiohttp* older than 0.21 is now deprecated.


### Fixed

- `prometheus_async.aio.web` now supports *aiohttp* 2.0.


## [17.1.0](https://github.com/hynek/prometheus-async/compare/16.2.0...17.1.0) - 2017-01-14

### Fixed

- Fix monotonic timer on Python 2.
  [#7](https://github.com/hynek/prometheus-async/issues/7)


## [16.2.0](https://github.com/hynek/prometheus-async/compare/16.1.0...16.2.0) - 2016-10-28

### Changed

- When using the *aiohttp* metrics exporter, create the web application using an explicit loop argument.
  [#6](https://github.com/hynek/prometheus-async/pull/6)


## [16.1.0](https://github.com/hynek/prometheus-async/compare/16.0.0...16.1.0) - 2016-09-23

### Changed

- Service discovery deregistration is optional now.


## [16.0.0](https://github.com/hynek/prometheus-async/releases/tag/16.0.0) - 2016-05-19

### Added

- Initial release.
