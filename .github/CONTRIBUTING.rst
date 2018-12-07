How To Contribute
=================

First off, thank you for considering contributing to ``prometheus_async``!
It's people like *you* who make it is such a great tool for everyone.

This document intends to make contribution more accessible by codifying tribal knowledge and expectations.
Don't be afraid to open half-finished PRs, and ask questions if something is unclear!


Workflow
--------

- No contribution is too small!
  Please submit as many fixes for typos and grammar bloopers as you can!
- Try to limit each pull request to *one* change only.
- Since we squash on merge, it's up to you how you handle updates to the master branch.
  Whether you prefer to rebase on master or merge master into your branch, do whatever is more comfortable for you.
- *Always* add tests and docs for your code.
  This is a hard rule; patches with missing tests or documentation can't be merged.
- Make sure your changes pass our CI_.
  You won't get any feedback until it's green unless you ask for it.
- Once you've addressed review feedback, make sure to bump the pull request with a short note, so we know you're done.
- Don’t break `backward compatibility`_.


Code
----

- Obey `PEP 8`_ and `PEP 257`_.
  We use the ``"""``\ -on-separate-lines style for docstrings:

  .. code-block:: python

     def func(x):
         """
         Do something.

         :param str x: A very important parameter.

         :rtype: str
         """
- If you add or change public APIs, tag the docstring using ``..  versionadded:: 16.0.0 WHAT`` or ``..  versionchanged:: 16.2.0 WHAT``.
- We use isort_ to sort our imports, and we follow the Black_ code style with a line length of 79 characters.
  As long as you run our full tox suite before committing, or install our pre-commit_ hooks (ideally you'll do both -- see below "Local Development Environment"), you won't have to spend any time on formatting your code at all.
  If you don't, CI will catch it for you -- but that seems like a waste of your time!


Tests
-----

- Write your asserts as ``expected == actual`` to line them up nicely:

  .. code-block:: python

     x = f()

     assert 42 == x.some_attribute
     assert "foo" == x._a_private_attribute

- To run the test suite, all you need is a recent tox_.
  It will ensure the test suite runs with all dependencies against all Python versions just as it will on Travis CI.
  If you lack some Python versions, you can can always limit the environments like ``tox -e py27,py35`` (in that case you may want to look into pyenv_, which makes it very easy to install many different Python versions in parallel).
- Write `good test docstrings`_.


Consul
^^^^^^

If you want to run the *full* test suite, you'll also need a Consul_ agent running.
Once it's installed, you can run it in development mode:

.. code-block:: bash

   $ consul agent -dev -advertise 127.0.0.1

The lack of Consul on Travis CI is the only reason why our coverage badge reports a coverage under 100%.

Documentation
-------------

- Use `semantic newlines`_ in reStructuredText_ files (files ending in ``.rst``):

  .. code-block:: rst

     This is a sentence.
     This is another sentence.

- If you start a new section, add two blank lines before and one blank line after the header:

  .. code-block:: rst

     Last line of previous section.


     Header of New Section
     ^^^^^^^^^^^^^^^^^^^^^

     First line of new section.


Changelog
^^^^^^^^^

If your change is noteworthy, there needs to be a changelog entry in ``CHANGELOG.rst`` so our users can learn about it!

- As with other docs, please use `semantic newlines`_ in the changelog.
- Wrap symbols like modules, functions, or classes into double backticks so they are rendered in a ``monospace font``.
- Wrap arguments into asterisks like in docstrings: *these* or *attributes*.
- If you mention functions or other callables, add parentheses at the end of their names: ``prometheus_async.func()`` or ``prometheus_async.Class.method()``.
  This makes the changelog a lot more readable.
- Prefer simple past tense or constructions with "now".
  For example:

  + Added ``prometheus_async.func()``.
  + ``prometheus_async.func()`` now doesn't crash the Large Hadron Collider anymore when passed the *foobar* argument.

Example entries:

  .. code-block:: rst

     Added ``prometheus_async.func()``.
     The feature really *is* awesome.

or:

  .. code-block:: rst

     ``prometheus_async.func()`` now doesn't crash the Large Hadron Collider anymore when passed the *foobar* argument.
     The bug really *was* nasty.


Local Development Environment
-----------------------------

You can (and should) run our test suite using tox_.
However, you’ll probably want a more traditional environment as well.
We highly recommend to develop using the latest Python 3 release because we try to take advantage of modern features whenever possible.

First create a `virtual environment <https://virtualenv.pypa.io/>`_.
It’s out of scope for this document to list all the ways to manage virtual environments in Python, but if you don’t already have a pet way, take some time to look at tools like `pew <https://github.com/berdario/pew>`_, `virtualfish <https://virtualfish.readthedocs.io/>`_, and `virtualenvwrapper <https://virtualenvwrapper.readthedocs.io/>`_.

Next, get an up to date checkout of the ``prometheus_async`` repository:

.. code-block:: bash

    $ git clone git@github.com:hynek/prometheus_async.git

or if you want to use git via ``https``:

.. code-block:: bash

    $ git clone https://github.com/hynek/prometheus_async.git

Change into the newly created directory and **after activating your virtual environment** install an editable version of ``prometheus_async`` along with its tests and docs requirements:

.. code-block:: bash

    $ cd prometheus_async
    $ pip install -e '.[dev]'

At this point,

.. code-block:: bash

   $ python -m pytest

should work and pass, as should:

.. code-block:: bash

   $ cd docs
   $ make html

The built documentation can then be found in ``docs/_build/html/``.

To avoid committing code that violates our style guide, we strongly advise you to install pre-commit_ [#f1]_ hooks:

.. code-block:: bash

   $ pre-commit install

You can also run them anytime (as our tox does) using:

.. code-block:: bash

   $ pre-commit run --all-files


.. [#f1] pre-commit should have been installed into your virtualenv automatically when you ran ``pip install -e '.[dev]'`` above. If pre-commit is missing, it may be that you need to re-run ``pip install -e '.[dev]'``.

****

Again, this list is mainly to help you to get started by codifying tribal knowledge and expectations.
If something is unclear, feel free to ask for help!

Please note that this project is released with a Contributor `Code of Conduct`_.
By participating in this project you agree to abide by its terms.
Please report any harm to `Hynek Schlawack`_ in any way you find appropriate.

Thank you for considering contributing to ``prometheus_async``!


.. _`Hynek Schlawack`: https://hynek.me/about/
.. _`PEP 8`: https://www.python.org/dev/peps/pep-0008/
.. _`PEP 257`: https://www.python.org/dev/peps/pep-0257/
.. _`good test docstrings`: https://jml.io/pages/test-docstrings.html
.. _`Code of Conduct`: https://github.com/hynek/prometheus_async/blob/master/.github/CODE_OF_CONDUCT.rst
.. _changelog: https://github.com/hynek/prometheus_async/blob/master/CHANGELOG.rst
.. _`backward compatibility`: https://prometheus-async.readthedocs.io/en/latest/backward-compatibility.html
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _pyenv: https://github.com/pyenv/pyenv
.. _reStructuredText: https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
.. _semantic newlines: https://rhodesmill.org/brandon/2012/one-sentence-per-line/
.. _CI: https://travis-ci.org/hynek/prometheus_async/
.. _black: https://github.com/ambv/black
.. _pre-commit: https://pre-commit.com/
.. _isort: https://github.com/timothycrosley/isort
.. _Consul: https://www.consul.io/
