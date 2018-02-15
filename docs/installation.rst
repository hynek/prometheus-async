=============================
Installation and Requirements
=============================


Installation
============

If you want to expose metrics using aiohttp:

.. code-block:: shell

  $ python -m pip install -U pip setuptools
  $ python -m pip install prometheus_async[aiohttp]

If you want to instrument a Twisted application:

.. code-block:: shell

  $ python -m pip install -U pip setuptools
  $ python -m pip install prometheus_async[twisted]


Please do not skip the update of ``pip`` and ``setuptools`` because ``prometheus_async`` uses modern packaging features.
