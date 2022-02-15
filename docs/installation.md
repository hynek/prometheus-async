# Installation and Requirements

If you just want to instrument an *asyncio*-based application:

```console
$ python -m pip install -U pip
$ python -m pip install prometheus-async
```

If you want to expose metrics using *aiohttp*:

```console
$ python -m pip install -U pip
$ python -m pip install prometheus-async[aiohttp]
```

If you want to instrument a Twisted application:

```console
$ python -m pip install -U pip
$ python -m pip install prometheus-async[twisted]
```

```{admonition} Warning
:class: Warning

Please do not skip the update of *pip*, because *prometheus-async* uses modern packaging features and the installation will most likely fail otherwise.
```
