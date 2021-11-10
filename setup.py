# Copyright 2016 Hynek Schlawack
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import codecs
import os
import re

from setuptools import find_packages, setup


###############################################################################

NAME = "prometheus-async"
KEYWORDS = ["metrics", "prometheus", "twisted", "asyncio"]
PROJECT_URLS = {
    "Documentation": "https://prometheus-async.readthedocs.io/",
    "Bug Tracker": "https://github.com/hynek/prometheus-async/issues",
    "Source Code": "https://github.com/hynek/prometheus-async",
    "Funding": "https://hynek.me/say-thanks/",
    "Ko-fi": "https://ko-fi.com/the_hynek",
}

CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
PYTHON_REQUIRES = ">=3.6"
INSTALL_REQUIRES = [
    "prometheus_client >= 0.0.18",
    "wrapt",
]
EXTRAS_REQUIRE = {
    "aiohttp": ["aiohttp>=3"],
    "consul": ["aiohttp>=3"],
    "twisted": ["twisted"],
    "tests": [
        "coverage[toml]",
        "pytest",
        "pytest-asyncio",
    ],
    "docs": ["aiohttp", "furo", "sphinx", "sphinxcontrib-asyncio", "twisted"],
}
EXTRAS_REQUIRE["dev"] = (
    EXTRAS_REQUIRE["aiohttp"]
    + EXTRAS_REQUIRE["consul"]
    + EXTRAS_REQUIRE["twisted"]
    + EXTRAS_REQUIRE["docs"]
    + EXTRAS_REQUIRE["tests"]
    + ["pytest-twisted", "pre-commit"]
)

###############################################################################

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()


try:
    PACKAGES
except NameError:
    PACKAGES = find_packages(where="src")

try:
    META_PATH
except NameError:
    META_PATH = os.path.join(
        HERE, "src", NAME.replace("-", "_"), "__init__.py"
    )
finally:
    META_FILE = read(META_PATH)


def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        fr"^__{meta}__ = ['\"]([^'\"]*)['\"]", META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError(f"Unable to find __{meta}__ string.")


VERSION = find_meta("version")
URL = find_meta("uri")
LONG = (
    read("README.rst")
    + "\n\n"
    + "Release Information\n"
    + "===================\n\n"
    + re.search(
        r"(\d+.\d.\d \(.*?\)\r?\n.*?)\r?\n\r?\n\r?\n----\r?\n\r?\n\r?\n",
        read("CHANGELOG.rst"),
        re.S,
    ).group(1)
    + "\n\n`Full changelog "
    + f"<{URL}en/stable/changelog.html>`_.\n\n"
    + read("AUTHORS.rst")
)


if __name__ == "__main__":
    setup(
        name=NAME,
        description=find_meta("description"),
        license=find_meta("license"),
        url=URL,
        project_urls=PROJECT_URLS,
        version=VERSION,
        author=find_meta("author"),
        author_email=find_meta("email"),
        maintainer=find_meta("author"),
        maintainer_email=find_meta("email"),
        long_description=LONG,
        long_description_content_type="text/x-rst",
        keywords=KEYWORDS,
        packages=PACKAGES,
        package_dir={"": "src"},
        include_package_data=True,
        classifiers=CLASSIFIERS,
        python_requires=PYTHON_REQUIRES,
        install_requires=INSTALL_REQUIRES,
        extras_require=EXTRAS_REQUIRE,
        zip_safe=False,
        options={"bdist_wheel": {"universal": "1"}},
    )
