.. _asyncio-api:

asyncio Support
===============

.. currentmodule:: prometheus_async.aio

The asyncio-related APIs can be found within the ``prometheus.aio`` package.


Decorator Wrappers
------------------

.. autofunction:: time

.. code-block:: python

   import asyncio

   from aiohttp import web
   from prometheus_client import Histogram
   from prometheus_async.aio import time

   REQ_TIME = Histogram("req_time_seconds", "time spent in requests")

   @time(REQ_TIME)
   async def req(request):
      await asyncio.sleep(1)
      return web.Response(body=b"hello")

.. autofunction:: count_exceptions


Metric Exposure
---------------

``prometheus_async`` offers methods to expose your metrics using aiohttp_:

.. currentmodule:: prometheus_async.aio.web

.. autofunction:: start_http_server

.. autofunction:: start_http_server_in_thread

.. autofunction:: server_stats

.. code-block:: python

      from aiohttp import web
      from prometheus_async import aio

      app = web.Application()
      app.router.add_route("GET", "/metrics", aio.web.server_stats)
      # your other routes go here.


.. _aiohttp: https://aiohttp.readthedocs.org
