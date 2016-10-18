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

The underlying prometheus client library, `prometheus_client`_ exposes a :class:`twisted.web.resource.Resource` -- namely `prometheus_client.twisted.MetricsResource`_ -- that makes it extremely easy to expose your metrics.

     .. code-block:: python

        from prometheus_client.twisted import MetricsResource
        from twisted.web.server import Site
        from twisted.web.resource import Resource
        from twisted.internet import reactor

        root = Resource()
        root.putChild(b'metrics', MetricsResource())

        factory = Site(root)
        reactor.listenTCP(8000, factory)
        reactor.run()

As a slightly more in-depth example, the following exposes the application's metrics under ``/metrics`` and sets up a `prometheus_client.Counter`_ for inbound HTTP requests.
It also uses `Klein`_ to set up the routes instead of relying directly on `twisted.web`_ for routing.

     .. code-block:: python

        from prometheus_client.twisted import MetricsResource
        from twisted.web.server import Site
        from twisted.internet import reactor

        from klein import Klein

        from prometheus_client import Counter


        INBOUND_REQUESTS = Counter(
           'inbound_requests_total',
           'Counter (int) of inbound http requests',
           ['endpoint', 'method']
        )

        app = Klein()

        @app.route('/metrics')
        def metrics(request):
            INBOUND_REQUESTS.labels('/metrics', 'GET').inc()
            return MetricsResource()


        factory = Site(app.resource())
        reactor.listenTCP(8000, factory)
        reactor.run()



.. _twisted.web: https://twistedmatrix.com/documents/current/web/howto/web-in-60/index.html
.. _prometheus_client: https://github.com/prometheus/client_python#twisted
.. _prometheus_client.twisted.MetricsResource: https://github.com/prometheus/client_python/blob/master/prometheus_client/twisted/_exposition.py
.. _prometheus_client.counter: https://github.com/prometheus/client_python#counter
.. _klein: https://github.com/twisted/klein
