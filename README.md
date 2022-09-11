# prometheus-async

<a href="https://prometheus-async.readthedocs.io/en/stable/">
   <img src="https://img.shields.io/badge/Docs-Read%20The%20Docs-black" alt="Documentation" />
</a>
<a href="https://github.com/hynek/prometheus-async/blob/main/LICENSE">
   <img src="https://img.shields.io/badge/license-Apache--2.0-C06524" alt="License: Apache 2.0" />
</a>
<a href="https://pypi.org/project/prometheus-async/">
   <img src="https://img.shields.io/pypi/v/prometheus-async" alt="PyPI version" />
</a>
<a href="https://pepy.tech/project/prometheus-async">
   <img src="https://static.pepy.tech/personalized-badge/prometheus-async?period=month&amp;units=international_system&amp;left_color=grey&amp;right_color=blue&amp;left_text=Downloads%20/%20Month" alt="Downloads / Month" />
</a>

<!-- teaser-begin -->

*prometheus-async* adds support for asynchronous frameworks to the official [Python client] for the [*Prometheus*] metrics and monitoring system.

Currently [*asyncio*] and [*Twisted*] on Python 3.7 and later are supported.

It works by wrapping the metrics from the official client:

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


Even for *synchronous* applications, the metrics exposure methods can be useful since they are more powerful than the one shipped with the official client.
For that, helper functions have been added that run them in separate threads (*asyncio*-only).

The source code is hosted on [GitHub] and the documentation on [Read The Docs].


## *prometheus-async* for Enterprise

Available as part of the Tidelift Subscription.

The maintainers of *prometheus-async* and thousands of other packages are working with Tidelift to deliver commercial support and maintenance for the open source packages you use to build your applications.
Save time, reduce risk, and improve code health, while paying the maintainers of the exact packages you use.
[Learn more.](https://tidelift.com/subscription/pkg/pypi-prometheus-async?utm_source=pypi-prometheus-async&utm_medium=referral&utm_campaign=enterprise)


[*asyncio*]: https://docs.python.org/3/library/asyncio.html
[Python client]: https://github.com/prometheus/client_python
[*Prometheus*]: https://prometheus.io/
[*Twisted*]: https://twisted.org
[GitHub]: https://github.com/hynek/prometheus-async
[Read The Docs]: https://prometheus-async.readthedocs.io/
