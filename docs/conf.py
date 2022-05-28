"""Configure docs.

See: https://www.sphinx-doc.org/en/master/usage/configuration.html
"""
import os
import sys
from datetime import date

import pybv

curdir = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(curdir, '..', 'pybv')))
sys.path.append(os.path.abspath(os.path.join(curdir, 'sphinxext')))

# see: https://sphinx.readthedocs.io/en/1.3/extensions.html
extensions = [
   'sphinx.ext.autosummary',
   'sphinx.ext.viewcode',
   'sphinx.ext.intersphinx',
   'numpydoc',
   'sphinx_copybutton',
   'gh_substitutions',  # custom extension, see ./sphinxext/gh_substitutions.py
   ]

# configure sphinx-copybutton
copybutton_prompt_text = r'>>> |\.\.\. '
copybutton_prompt_is_regexp = True

# configure numpydoc
numpydoc_xref_param_type = True
numpydoc_xref_ignore = {
    # words
    "shape", "of", "len", "or",
    # shapes
    "n_channels", "n_times", "n_events"
}

# Generate the autosummary
autosummary_generate = True

# General information about the project.
project = 'pybv'
copyright = '2018-{}, pybv developers'.format(date.today().year)
author = 'pybv developers'
version = pybv.__version__
release = version

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Define master doc
master_doc = 'index'

# Options for HTML output
html_theme = "alabaster"
html_theme_options = {"description": "A lightweight I/O utility for the BrainVision data format.",  # noqa: E501
                      "fixed_sidebar": True,
                      "github_button": True,
                      "github_type": "star",
                      "github_repo": "pybv",
                      "github_user": "bids-standard",
                      }
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',
        'searchbox.html',
    ]
}

# When functions from other packages are mentioned, link to them
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'mne': ('https://mne.tools/dev/', None),
    'numpy': ('https://numpy.org/devdocs', None),
}
intersphinx_timeout = 10
