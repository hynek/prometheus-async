# Installation and Requirements

If you just want to instrument an *asyncio*-based application:

```console
$ python -Im pip install prometheus-async
```

If you want to expose metrics using *aiohttp*, you also have to install it along with it.

```console
$ python -Im pip install prometheus-async aiohttp
```

*prometheus-async* does not require anything extra to instrument Twisted applications.
