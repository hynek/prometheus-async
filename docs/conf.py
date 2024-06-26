# SPDX-License-Identifier: Apache-2.0
#
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

from importlib import metadata


# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_parser",
    "notfound.extension",
    "sphinx.ext.autodoc",
    "sphinx.ext.autodoc.typehints",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
]

myst_enable_extensions = [
    "colon_fence",
    "smartquotes",
    "deflist",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "prometheus-async"
copyright = "2016, Hynek Schlawack"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.

# The full version, including alpha/beta/rc tags.
release = metadata.version("prometheus-async")
# The short X.Y version.
version = release.rsplit(".", 1)[0]

if "dev" in release:
    release = version = "UNRELEASED"


# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build"]

nitpick_ignore = [
    ("py:class", "Gauge"),
    ("py:class", "Incrementer"),
    ("py:class", "Observer"),
    ("py:class", "ServiceDiscovery"),
    ("py:class", "P"),
    ("py:class", "T"),
    ("py:class", "R"),
    ("py:class", "D"),
    ("py:class", "C"),
    ("py:class", "twisted.web.resource.Resource"),
]

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# Move type hints into the description block, instead of the func definition.
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"

highlight_language = "python3"

# -- Options for HTML output ----------------------------------------------

html_theme = "furo"
html_theme_options = {"top_of_page_buttons": []}

# Output file base name for HTML help builder.
htmlhelp_basename = "prometheus_asyncdoc"

linkcheck_ignore = [
    # Rate limits
    r"https://github.com/.*/(issues|pull)/\d+",
    r"https://twitter.com/.*",
    # Anchors are a problem
    r"https://github.com/prometheus/client_python#twisted",
    r"https://github.com/prometheus/client_python#counter",
    # This breaks releases because of non-existent tags.
    r"https://github.com/hynek/prometheus-async/compare/.*",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "aiohttp": ("https://aiohttp.readthedocs.io/en/stable/", None),
    "twisted": ("https://docs.twistedmatrix.com/en/stable/", None),
}
