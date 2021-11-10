================
prometheus-async
================

.. image:: https://img.shields.io/badge/Docs-Read%20The%20Docs-black
   :target: https://prometheus-async.readthedocs.io/en/stable/
   :alt: Documentation

.. image:: https://img.shields.io/badge/license-Apache--2.0-C06524
   :target: https://github.com/hynek/prometheus-async/blob/main/LICENSE
   :alt: License: Apache 2.0

.. image:: https://img.shields.io/pypi/v/prometheus-async
   :target: https://pypi.org/project/prometheus-async/
   :alt: PyPI version

.. image:: https://static.pepy.tech/personalized-badge/prometheus-async?period=month&units=international_system&left_color=grey&right_color=blue&left_text=Downloads%20/%20Month
   :target: https://pepy.tech/project/prometheus-async
   :alt: Downloads / Month

.. teaser-begin

*prometheus-async* adds support for asynchronous frameworks to the official `Python client`_ for the Prometheus_ metrics and monitoring system.

Currently asyncio_ and Twisted_ on Python 3.6 and later are supported.

It works by wrapping the metrics from the official client:

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


Even for *synchronous* applications, the metrics exposure methods can be useful since they are more powerful than the one shipped with the official client.
For that, helper functions have been added that run them in separate threads (*asyncio*-only).

The source code is hosted on GitHub_ and the documentation on `Read The Docs`_.


.. _asyncio: https://docs.python.org/3/library/asyncio.html
.. _`Python client`: https://github.com/prometheus/client_python
.. _Prometheus: https://prometheus.io/
.. _Twisted: https://twistedmatrix.com/
.. _GitHub: https://github.com/hynek/prometheus_async
.. _`Read The Docs`: https://prometheus-async.readthedocs.io/
