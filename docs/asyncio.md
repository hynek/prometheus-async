(asyncio-api)=

# asyncio Support

```{eval-rst}
.. currentmodule:: prometheus_async.aio
```

The asyncio-related APIs can be found within the `prometheus_async.aio` package.


## Decorator Wrappers

All of these functions take a *prometheus_client* metrics object and can either be applied as a decorator to functions and methods, or they can be passed an {class}`asyncio.Future` for a second argument.

```{eval-rst}
.. autocofunction:: time
```

The most common use case is using it as a decorator:

```python
import asyncio

from aiohttp import web
from prometheus_client import Histogram
from prometheus_async.aio import time

REQ_TIME = Histogram("req_time_seconds", "time spent in requests")

@time(REQ_TIME)
async def req(request):
    await asyncio.sleep(1)
    return web.Response(body=b"hello")
```

```{eval-rst}
.. autocofunction:: count_exceptions
.. autocofunction:: track_inprogress

```


(asyncio-web)=

## Metric Exposure

```{eval-rst}
.. currentmodule:: prometheus_async.aio.web
```

*prometheus-async* offers methods to expose your metrics using [*aiohttp*](https://aiohttp.readthedocs.io/) under `prometheus_async.aio.web`:

```{eval-rst}
.. autocofunction:: start_http_server
.. autofunction:: start_http_server_in_thread
```

```{admonition} Warning
Please note that if you want to use [*uWSGI*](https://uwsgi-docs.readthedocs.io/) together with `start_http_server_in_thread()`, you have to tell *uWSGI* to enable threads using its [configuration option](https://uwsgi-docs.readthedocs.io/en/latest/Options.html#enable-threads) or by passing it `--enable-threads`.

Currently the recommended mode to run *uWSGI* with `--master` [is broken](https://github.com/unbit/uwsgi/issues/1609) if you want to clean up using {mod}`atexit` handlers.

Therefore the usage of `prometheus_sync.aio.web` together with *uWSGI* is **strongly discouraged**.
```

```{eval-rst}
.. autofunction:: server_stats
```

Useful if you want to install your metrics within your own application:

```python
from aiohttp import web
from prometheus_async import aio

app = web.Application()
app.router.add_get("/metrics", aio.web.server_stats)
# your other routes go here.
```

```{eval-rst}
.. autoclass:: MetricsHTTPServer
   :members: close

.. autoclass:: ThreadedMetricsHTTPServer
   :members: close
```


(sd)=

## Service Discovery

```{eval-rst}
.. currentmodule:: prometheus_async.aio.sd
```

Web exposure is much more useful if it comes with an easy way to integrate it with service discovery.

Currently *prometheus-async* only ships integration with a local *Consul* agent using *aiohttp*.
We do **not** plan add more.

```{eval-rst}
.. autoclass:: ConsulAgent
```


### Custom Service Discovery

Adding own service discovery methods is simple:
all you need is to provide an instance with a coroutine `register(self, metrics_server, loop)` that registers the passed `metrics_server` with the service of your choicer and returns another coroutine that is called for de-registration when the metrics server is shut down.

Have a look at [our implementations](https://github.com/hynek/prometheus-async/blob/main/src/prometheus_async/aio/sd.py) if you need inspiration or check out the `ServiceDiscovery` {class}`typing.Protocol` in the [`types` module](https://github.com/hynek/prometheus-async/blob/main/src/prometheus_async/types.py)
