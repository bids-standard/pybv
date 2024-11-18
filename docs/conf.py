"""Configure docs.

See: https://www.sphinx-doc.org/en/master/usage/configuration.html
"""
import os
import sys
from datetime import date

from intersphinx_registry import get_intersphinx_mapping

import pybv

curdir = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(curdir, "..", "pybv")))
sys.path.append(os.path.abspath(os.path.join(curdir, "sphinxext")))

# see: https://sphinx.readthedocs.io/en/1.3/extensions.html
extensions = [
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "numpydoc",
    "sphinx_copybutton",
    "gh_substitutions",  # custom extension, see ./sphinxext/gh_substitutions.py
]

# configure sphinx-copybutton
copybutton_prompt_text = r">>> |\.\.\. "
copybutton_prompt_is_regexp = True

# configure numpydoc
numpydoc_xref_param_type = True
numpydoc_xref_ignore = {
    # words
    "shape",
    "of",
    "len",
    "or",
    # shapes
    "n_channels",
    "n_times",
    "n_events",
}

# Generate the autosummary
autosummary_generate = True

# General information about the project.
project = "pybv"
today = date.today().isoformat()
copyright = f"2018, pybv developers. Last updated on {today}"  # noqa: A001
author = "pybv developers"
version = pybv.__version__
release = version

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Define master doc
master_doc = "index"

# Options for HTML output
html_theme = "alabaster"
html_theme_options = {
    "description": "A lightweight I/O utility for the BrainVision data format.",
    "fixed_sidebar": True,
    "github_button": True,
    "github_type": "star",
    "github_repo": "pybv",
    "github_user": "bids-standard",
}
html_sidebars = {
    "**": [
        "about.html",
        "navigation.html",
        "relations.html",
        "searchbox.html",
    ]
}

# When functions from other packages are mentioned, link to them
# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = get_intersphinx_mapping(
    packages={
        "python",
        "mne",
        "numpy",
    }
)
intersphinx_timeout = 10
