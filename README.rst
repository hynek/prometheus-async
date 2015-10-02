================
prometheus_async
================

`prometheus_async` adds support for asynchronous frameworks in the official prometheus_client_.

Currently asyncio_ (Python 3.4, 3.5) and Twisted_ (2.6, 2.7, 3.4, 3.5, PyPy) are supported.

The only public API at the moment is the decorator ``prometheus_async.async_time``.
It wraps a metric object and calls ``observe(value)`` on it with ``value`` being the total runtime in seconds:

.. code-block:: python

   import asyncio

   from aiohttp import web
   from prometheus_client import Histogram
   from prometheus_async import async_time

   REQ_TIME = Histogram("req_time_seconds", "time spent in requests")

   @async_time(REQ_TIME)
   async def req(request):
      await asyncio.sleep(1)
      return web.Response(body=b"hello")


Future Plans
------------

- aiohttp_/twisted.web_ based metrics exposure.
- ``Counter.count_exceptions``
- ``Gauge.track_inprogress``
- Tornado_?


.. _asyncio: https://docs.python.org/3/library/asyncio.html
.. _prometheus_client: https://pypi.python.org/pypi/prometheus_client/
.. _Twisted: https://twistedmatrix.com/
.. _aiohttp: https://aiohttp.readthedocs.org
.. _twisted.web: https://twistedmatrix.com/documents/current/web/howto/web-in-60/index.html
.. _Tornado: https://www.tornadoweb.org/
