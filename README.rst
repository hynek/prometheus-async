================
prometheus_async
================

.. image:: https://img.shields.io/pypi/v/prometheus_async.svg
   :target: https://pypi.org/project/prometheus_async/
   :alt: PyPI

.. image:: https://readthedocs.org/projects/attrs/badge/?version=stable
   :target: http://attrs.readthedocs.io/en/stable/?badge=stable
   :alt: Documentation Status

.. image:: https://travis-ci.org/hynek/prometheus_async.svg?branch=master
   :target: https://travis-ci.org/hynek/prometheus_async
   :alt: CI status

.. image:: https://codecov.io/github/hynek/prometheus_async/branch/master/graph/badge.svg
   :target: https://codecov.io/github/hynek/prometheus_async
   :alt: Test Coverage

.. teaser-begin

``prometheus_async`` adds support for asynchronous frameworks to the official `Python client`_ for the Prometheus_ metrics and monitoring system.

Currently asyncio_ (Python 3.4, 3.5, 3.6) and Twisted_ (Python 2.7, 3.4, 3.5, 3.6, PyPy) are supported.


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
For that, helper functions have been added that run them in separate threads (asyncio-only for the time being).

The source code is hosted on GitHub_ and the documentation on `Read The Docs`_.


.. _asyncio: https://docs.python.org/3/library/asyncio.html
.. _`Python client`: https://github.com/prometheus/client_python
.. _Prometheus: https://prometheus.io/
.. _Twisted: https://twistedmatrix.com/
.. _GitHub: https://github.com/hynek/prometheus_async
.. _`Read The Docs`: https://prometheus-async.readthedocs.io/
