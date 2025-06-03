# How To Contribute

First off, thank you for considering contributing to *prometheus-async*!
It's people like *you* who make it such a great tool for everyone.

This document intends to make contribution more accessible by codifying tribal knowledge and expectations.
Don't be afraid to open half-finished PRs, and ask questions if something is unclear!

Please note that this project is released with a Contributor [Code of Conduct](https://github.com/hynek/prometheus-async/blob/main/.github/CODE_OF_CONDUCT.md).
By participating in this project you agree to abide by its terms.
Please report any harm to [Hynek Schlawack] in any way you find appropriate.


## Workflow

- No contribution is too small!
  Please submit as many fixes for typos and grammar bloopers as you can!
- Try to limit each pull request to *one* change only.
- Since we squash on merge, it's up to you how you handle updates to the main branch.
  Whether you prefer to rebase on main or merge main into your branch, do whatever is more comfortable for you.
- *Always* add tests and docs for your code.
  This is a hard rule; patches with missing tests or documentation can't be merged.
- Make sure your changes pass our [CI].
  You won't get any feedback until it's green unless you ask for it.
- For the CI to pass, the coverage must be 100%.
  If you have problems to test something, open anyway and ask for advice.
  In some situations, we may agree to add an `# pragma: no cover`.
- Once you've addressed review feedback, make sure to bump the pull request with a short note, so we know you're done.
- Don’t break backwards-compatibility.


## Local Development Environment

You can (and should) run our test suite using [*tox*].
However, you’ll probably want a more traditional environment as well.

First, create a [virtual environment](https://virtualenv.pypa.io/) so you don't break your system-wide Python installation.
We recommend using the Python version from the `.python-version-default` file in project's root directory.

If you're using [*direnv*](https://direnv.net), you can automate the creation of a virtual environment with the correct Python version by adding the following `.envrc` to the project root:

```bash
layout python python$(cat .python-version-default)
```

[Create a fork](https://github.com/hynek/prometheus-async/fork) of the repository and clone it:

```console
$ git clone git@github.com:YOU/prometheus-async.git
```

Or if you prefer to use Git via HTTPS:

```console
$ git clone https://github.com/YOU/prometheus-async.git
```

> [!WARNING]
> - **Before** you start working on a new pull request, use the "*Sync fork*" button in GitHub's web UI to ensure your fork is up to date.
> - **Always create a new branch off `main` for each new pull request.**
>   Yes, you can work on `main` in your fork and submit pull requests.
>   But this will *inevitably* lead to you not being able to synchronize your fork with upstream and having to start over.

Change into the newly created directory and **after activating your virtual environment** install it with its tests requirements:

```console
$ cd prometheus-async
$ python -Im pip install --upgrade pip  # PLEASE don't skip this step
$ python -Im pip install --editable . --group dev
```

At this point,

```console
$ python -Im pytest
```

should work and pass.

When working on the documentation, use:

```console
$ tox run -e docs-watch
```

... to watch your files and automatically rebuild when a file changes.
And use:

```console
$ tox run -e docs
```

... to build it once and run our doctests.

The built documentation can then be found in `docs/_build/html/`.

---

To avoid committing code that violates our style guide, we strongly advise you to install [*pre-commit*] and its hooks:

```console
$ pre-commit install
```

This is not strictly necessary, because our [*tox*] file contains an environment that runs:

```console
$ pre-commit run --all-files
```

and our CI has integration with `pre-commit.ci <https://pre-commit.ci>`_.
But it's way more comfortable to run it locally and *git* catching avoidable errors.


## Code

- Obey [PEP 8](https://www.python.org/dev/peps/pep-0008/) and [PEP 257](https://www.python.org/dev/peps/pep-0257/).
  We use the `"""`-on-separate-lines style for docstrings:

  ```python
  def func(x):
      """
      Do something.

      :param str x: A very important parameter.

      :rtype: str
      """
  ```

- If you add or change public APIs, tag the docstring using `..  versionadded:: 16.0.0 WHAT` or `..  versionchanged:: 16.2.0 WHAT`.

- We use [Ruff](https://ruff.rs/) to sort our imports and format our code with a line length of 79 characters.
  As long as you run our full [*tox*] suite before committing, or install our [*pre-commit*] hooks (ideally you'll do both – see [*Local Development Environment*](#local-development-environment) above), you won't have to spend any time on formatting your code at all.
  If you don't, [CI] will catch it for you – but that seems like a waste of your time!


## Tests

- Write your asserts as `expected == actual` to line them up nicely:

  ```python
  x = f()

  assert 42 == x.some_attribute
  assert "foo" == x._a_private_attribute
  ```

- To run the test suite, all you need is a recent [*tox*].
  It will ensure the test suite runs with all dependencies against all Python versions just as it will in our [CI].
  If you lack some Python versions, you can can always limit the environments like `tox -e py38,py39`, or make it a non-failure using `tox --skip-missing-interpreters`.

  In that case you should look into [*asdf*](https://asdf-vm.com) or [*pyenv*](https://github.com/pyenv/pyenv), which make it very easy to install many different Python versions in parallel.
- Write [good test docstrings](https://jml.io/pages/test-docstrings.html).


## Documentation

- Use [semantic newlines] in [*Markdown*](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax) files (files ending in `.md`):

  ```markdown
  This is a sentence.
  This is another sentence.
  ```


### Changelog

If your change is noteworthy, there needs to be a changelog entry in `CHANGELOG.md`.

- The changelog follows the [*Keep a Changelog*](https://keepachangelog.com/en/1.0.0/) standard.
  Please add the best-fitting section if it's missing for the current release.
  We use the following order: `Security`, `Removed`, `Deprecated`, `Added`, `Changed`, `Fixed`.
- As with other docs, please use [semantic newlines] in the changelog.
- Make the last line a link to your pull request.
  You probably have to open it first to know the number.
- Wrap symbols like modules, functions, or classes into backticks so they are rendered in a `monospace font`.
- Wrap arguments into asterisks like in docstrings:
  `Added new argument *an_argument*.`
- If you mention functions or other callables, add parentheses at the end of their names:
  `prometheus_async.func()` or `prometheus_async.Class.method()`.
  This makes the changelog a lot more readable.
- Prefer simple past tense or constructions with "now".
  For example:

  * Added `prometheus_async.func()`.
  * `prometheus_async.func()` now doesn't crash the Large Hadron Collider anymore when passed the *foobar* argument.


#### Example entries

```markdown
Added `prometheus_async.func()`.
The feature really *is* awesome.
```

or:

```markdown
`prometheus_async.func()` now doesn't crash the Large Hadron Collider anymore when passed the *foobar* argument.
The bug really *was* nasty.
```


[CI]: https://github.com/hynek/prometheus-async/actions
[Hynek Schlawack]: https://hynek.me/about/
[*pre-commit*]: https://pre-commit.com/
[*tox*]: https://https://tox.wiki/
[semantic newlines]: https://rhodesmill.org/brandon/2012/one-sentence-per-line/
