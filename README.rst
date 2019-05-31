================
prometheus_async
================

.. image:: https://img.shields.io/pypi/v/prometheus_async.svg
   :target: https://pypi.org/project/prometheus-async/
   :alt: PyPI

.. image:: https://readthedocs.org/projects/prometheus-async/badge/?version=stable
   :target: https://prometheus-async.readthedocs.io/en/stable/?badge=stable
   :alt: Documentation Status

.. image:: https://dev.azure.com/the-hynek/prometheus-async/_apis/build/status/hynek.prometheus-async?branchName=master
   :target: https://dev.azure.com/the-hynek/prometheus-async/_build?definitionId=1
   :alt: CI Status

.. image:: https://codecov.io/github/hynek/prometheus_async/branch/master/graph/badge.svg
   :target: https://codecov.io/github/hynek/prometheus_async
   :alt: Test Coverage

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/ambv/black
   :alt: Code style: black

.. teaser-begin

``prometheus_async`` adds support for asynchronous frameworks to the official `Python client`_ for the Prometheus_ metrics and monitoring system.

Currently asyncio_ (Python 3.5+, PyPy3) and Twisted_ (Python 2.7, 3.5+, PyPy) are supported.


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
