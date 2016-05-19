.. _asyncio-api:

asyncio Support
===============

.. currentmodule:: prometheus_async.aio

The asyncio-related APIs can be found within the ``prometheus_async.aio`` package.


Decorator Wrappers
------------------

.. autocofunction:: time

   ::

      import asyncio

      from aiohttp import web
      from prometheus_client import Histogram
      from prometheus_async.aio import time

      REQ_TIME = Histogram("req_time_seconds", "time spent in requests")

      @time(REQ_TIME)
      async def req(request):
         await asyncio.sleep(1)
         return web.Response(body=b"hello")

.. autocofunction:: count_exceptions

.. autocofunction:: track_inprogress


.. _asyncio-web:

Metric Exposure
---------------

.. currentmodule:: prometheus_async.aio.web

``prometheus_async`` offers methods to expose your metrics using `aiohttp <http://aiohttp.readthedocs.io/>`_ under ``prometheus_async.aio.web``:


.. autocofunction:: start_http_server

.. autofunction:: start_http_server_in_thread

.. autofunction:: server_stats

    Useful if you want to install your metrics within your own application::

         from aiohttp import web
         from prometheus_async import aio

         app = web.Application()
         app.router.add_route("GET", "/metrics", aio.web.server_stats)
         # your other routes go here.

.. autoclass:: MetricsHTTPServer
   :members: close

.. autoclass:: ThreadedMetricsHTTPServer
   :members: close



.. _sd:

Service Discovery
-----------------

.. currentmodule:: prometheus_async.aio.sd

Web exposure is much more useful if it comes with an easy way to integrate it with service discovery.

Currently ``prometheus_async`` only ships integration with a local Consul agent using `python-consul <https://github.com/cablehead/python-consul>`_ library.
Install using ``pip install prometheus_async[consul]`` to get it automatically pulled in.

.. autoclass:: ConsulAgent


Custom Service Discovery
~~~~~~~~~~~~~~~~~~~~~~~~

Adding own service discovery methods is simple:
all you need is to provide an instance with a coroutine ``register(self, metrics_server, loop)`` that registers the passed ``metrics_server`` with the service of your choicer and returns another coroutine that is called for de-registration when the metrics server is shut down.

Have a look at `our implementations <https://github.com/hynek/prometheus_async/blob/master/src/prometheus_async/aio/sd.py>`_ if you need inspiration.
