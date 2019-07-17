#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Configure docs.

See: https://www.sphinx-doc.org/en/master/usage/configuration.html
"""
import os
import sys
import pybv
curdir = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(curdir, '..', 'pybv')))

# see: https://sphinx.readthedocs.io/en/1.3/extensions.html
extensions = [
   'sphinx.ext.autodoc',
   'sphinx.ext.napoleon',
   'sphinx.ext.autosummary',
   'sphinx.ext.viewcode',
   'sphinx.ext.intersphinx',
   ]

# Generate the autosummary
autosummary_generate = True

# General information about the project.
project = 'pybv'
copyright = '2018-2019, pybv developers'
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
html_theme_options = {"fixed_sidebar": True}
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
    'mne': ('http://mne-tools.github.io/stable/', None),
    'numpy': ('https://www.numpy.org/devdocs', None),
    'scipy': ('https://scipy.github.io/devdocs', None),
    'matplotlib': ('https://matplotlib.org', None),
}
