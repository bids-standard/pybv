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
   ]

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
