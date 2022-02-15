(twisted-api)=

# Twisted Support

```{eval-rst}
.. currentmodule:: prometheus_async.tx
```

The Twisted-related APIs can be found within the `prometheus_async.tx` package.


## Decorator Wrappers

```{eval-rst}
.. autofunction:: time
```

The fact it's accepting ``Deferred``s is useful in conjunction with [`twisted.web`] views that don't allow to return a ``Deferred``:

```python
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
```

```{eval-rst}
.. autofunction:: count_exceptions
.. autofunction:: track_inprogress
```


(twisted-web)=

## Metric Exposure

[*prometheus_client*], the underlying *Prometheus* client library, exposes a {class}`twisted.web.resource.Resource` -- namely [`prometheus_client.twisted.MetricsResource`] -- that makes it extremely easy to expose your metrics.

```python
from prometheus_client.twisted import MetricsResource
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor

root = Resource()
root.putChild(b"metrics", MetricsResource())

factory = Site(root)
reactor.listenTCP(8000, factory)
reactor.run()
```

As a slightly more in-depth example, the following exposes the application's metrics under `/metrics` and sets up a [`prometheus_client.Counter`] for inbound HTTP requests.
It also uses [*Klein*] to set up the routes instead of relying directly on [`twisted.web`] for routing.

```python
from prometheus_client.twisted import MetricsResource
from twisted.web.server import Site
from twisted.internet import reactor

from klein import Klein

from prometheus_client import Counter


INBOUND_REQUESTS = Counter(
   "inbound_requests_total",
   "Counter (int) of inbound http requests",
   ["endpoint", "method"]
)

app = Klein()

@app.route("/metrics")
def metrics(request):
    INBOUND_REQUESTS.labels("/metrics", "GET").inc()
    return MetricsResource()


factory = Site(app.resource())
reactor.listenTCP(8000, factory)
reactor.run()
```

[*Klein*]: https://github.com/twisted/klein
[*prometheus_client*]: https://github.com/prometheus/client_python#twisted
[`prometheus_client.Counter`]: https://github.com/prometheus/client_python#counter
[`prometheus_client.twisted.metricsresource`]: https://github.com/prometheus/client_python/blob/master/prometheus_client/twisted/_exposition.py
[`twisted.web`]: https://twistedmatrix.com/documents/current/web/howto/web-in-60/index.html
