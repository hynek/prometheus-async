How To Contribute
=================

Every open source project lives from the generous help by contributors that sacrifice their time and ``prometheus_async`` is no different.

Here are a few guidelines to get you started:

- To run the test suite, all you need is a recent tox_.
  It will ensure the test suite runs with all dependencies against all Python versions just as it will on `Travis CI`_.
  If you lack some Python version, you can can always limit the environments like ``tox -e py27,py35`` (in that case you may want to look into pyenv_ that makes it very easy to install many different Python versions in parallel).
- Make sure your changes pass our CI.
  You won't get any feedback until it's green unless you ask for it.
- If your change is noteworthy, add an entry to the changelog_.
- No contribution is too small; please submit as many fixes for typos and grammar bloopers as you can!
- Don’t break `backward compatibility`_.
- *Always* add tests and docs for your code.
  This is a hard rule; patches with missing tests or documentation won’t be merged.
- Write `good test docstrings`_.
- Obey `PEP 8`_ and `PEP 257`_.
- If you address review feedback, make sure to bump the pull request.
  Maintainers don’t receive notifications if you push new commits.

Please note that this project is released with a Contributor `Code of Conduct`_.
By participating in this project you agree to abide by its terms.
Please report any harm to me_ in any way you find appropriate.

.. note::
   If you have something great but aren’t sure whether it adheres -- or even can adhere -- to the rules above: **please submit a pull request anyway**!

   In the best case, we can mold it into something, in the worst case the pull request gets politely closed.
   There’s absolutely nothing to fear.

Thank you for considering to contribute to ``prometheus_async``!
If you have any question or concerns, feel free to reach out to me_.


.. _me: https://hynek.me/about/
.. _`PEP 8`: https://www.python.org/dev/peps/pep-0008/
.. _`PEP 257`: https://www.python.org/dev/peps/pep-0257/
.. _`good test docstrings`: https://jml.io/pages/test-docstrings.html
.. _`Code of Conduct`: https://github.com/hynek/prometheus_async/blob/master/CODE_OF_CONDUCT.rst
.. _changelog: https://github.com/hynek/prometheus_async/blob/master/docs/changelog.rst
.. _`backward compatibility`: https://prometheus-async.readthedocs.io/en/latest/backward-compatibility.html
.. _`tox`: https://testrun.org/tox/
.. _`Travis CI`: https://travis-ci.org/
.. _pyenv: https://github.com/yyuu/pyenv
