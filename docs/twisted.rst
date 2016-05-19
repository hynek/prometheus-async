.. _twisted-api:

Twisted Support
===============

.. currentmodule:: prometheus_async.tx

The Twisted-related APIs can be found within the ``prometheus_async.tx`` package.


Decorator Wrappers
------------------

.. autofunction:: time

   The fact it's accepting ``Deferred``\ s is useful in conjunction with `twisted.web`_ views that don't allow to return a ``Deferred``:

   .. code-block:: python

      from prometheus_client import Histogram
      from prometheus_async.tx import time
      from twisted.internet.task import deferLater
      from twisted.web.resource import Resource
      from twisted.web.server import NOT_DONE_YET
      from twisted.internet import reactor

      REQ_TIME = Histogram("req_time_seconds", "time spent in requests")

      class DelayedResource(Resource):
         def _delayedRender(self, request):
            request.write("<html><body>Sorry to keep you waiting.</body></html>")
            request.finish()

         def render_GET(self, request):
            d = deferLater(reactor, 5, lambda: request)
            time(REQ_TIME, d.addCallback(self._delayedRender))
            return NOT_DONE_YET

.. autofunction:: count_exceptions

.. autofunction:: track_inprogress


.. _twisted-web:

Metric Exposure
---------------

:doc:`TODO <future>`


.. _twisted.web: https://twistedmatrix.com/documents/current/web/howto/web-in-60/index.html
