#! /usr/bin/env python
#
# Copyright (C) 2017-2018 The BIDS Community

import os
from os import path as op

from setuptools import setup

# get the version (don't import mne here, so dependencies are not needed)
version = None
with open(os.path.join('pybv', '__init__.py'), 'r') as fid:
    for line in (line.strip() for line in fid):
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('\'')
            break
if version is None:
    raise RuntimeError('Could not determine version')


descr = """A lightweight I/O utility for the BrainVision data format."""

DISTNAME = 'pybv'
DESCRIPTION = descr
MAINTAINER = 'The BIDS Community'
MAINTAINER_EMAIL = 'TODO'
URL = 'https://github.com/bids-standard/pybv'
LICENSE = 'BSD (3-clause)'
DOWNLOAD_URL = 'https://github.com/bids-standard/pybv'
VERSION = version


def package_tree(pkgroot):
    """Get the submodule list."""
    # Adapted from MNE-Python
    path = os.path.dirname(__file__)
    subdirs = [os.path.relpath(i[0], path).replace(os.path.sep, '.')
               for i in os.walk(os.path.join(path, pkgroot))
               if '__init__.py' in i[2]]
    return sorted(subdirs)

if __name__ == "__main__":
    if os.path.exists('MANIFEST'):
        os.remove('MANIFEST')

    setup(name=DISTNAME,
          maintainer=MAINTAINER,
          include_package_data=True,
          maintainer_email=MAINTAINER_EMAIL,
          description=DESCRIPTION,
          license=LICENSE,
          url=URL,
          version=VERSION,
          download_url=DOWNLOAD_URL,
          long_description=open('README.md').read(),
          zip_safe=True,  # the package can run out of an .egg file
          classifiers=['Intended Audience :: Science/Research',
                       'Intended Audience :: Developers',
                       'License :: OSI Approved',
                       'Programming Language :: Python',
                       'Topic :: Software Development',
                       'Topic :: Scientific/Engineering',
                       'Operating System :: Microsoft :: Windows',
                       'Operating System :: POSIX',
                       'Operating System :: Unix',
                       'Operating System :: MacOS'],
          platforms='any',
          packages=package_tree('pybv'),
    )
