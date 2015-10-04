================
prometheus_async
================

.. image:: https://travis-ci.org/hynek/prometheus_async.svg?branch=master
   :target: https://travis-ci.org/hynek/prometheus_async

.. image:: https://codecov.io/github/hynek/prometheus_async/coverage.svg?branch=master
    :target: https://codecov.io/github/hynek/prometheus_async?branch=master


``prometheus_async`` adds support for asynchronous frameworks in the official prometheus_client_.

Currently asyncio_ (Python 3.4, 3.5) and Twisted_ (Python 2.6, 2.7, 3.4, 3.5, PyPy) are supported.


API
===

``prometheus_async`` consists of two packages: ``aio`` and ``tx``.
As their names suggest, they work with asyncio_ and Twisted_ respectively.


Decorator Wrappers
------------------

Both packages contain a function ``async_time`` that wraps a metric object and calls ``observe(value)`` on it with ``value`` being the total runtime in seconds:

.. code-block:: python

   import asyncio

   from aiohttp import web
   from prometheus_client import Histogram
   from prometheus_async.aio import async_time

   REQ_TIME = Histogram("req_time_seconds", "time spent in requests")

   @async_time(REQ_TIME)
   async def req(request):
      await asyncio.sleep(1)
      return web.Response(body=b"hello")


Metric Exposure
---------------

asyncio
-------

``prometheus_async.aio.web.start_http_server(port, addr='', ssl_ctx=None, loop=None)`` will start an aiohttp_ web server in the background.
You can also use ``prometheus_async.aio.web.server_stats`` as a route and add it to your own application:

.. code-block:: python

      from aiohttp import web
      from prometheus_async import aio

      app = web.Application()
      app.router.add_route("GET", "/metrics", aio.web.server_stats)
      # your other routes go here.


Future Plans
------------

- twisted.web_ based metrics exposure.
- ``Counter.count_exceptions``
- ``Gauge.track_inprogress``
- Tornado_?


.. _asyncio: https://docs.python.org/3/library/asyncio.html
.. _prometheus_client: https://pypi.python.org/pypi/prometheus_client/
.. _Twisted: https://twistedmatrix.com/
.. _aiohttp: https://aiohttp.readthedocs.org
.. _twisted.web: https://twistedmatrix.com/documents/current/web/howto/web-in-60/index.html
.. _Tornado: https://www.tornadoweb.org/
