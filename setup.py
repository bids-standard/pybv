#! /usr/bin/env python

# Authors: Philip Alday <phillip.alday@unisa.edu.au>
#          Chris Holdgraf <choldgraf@berkeley.edu>
#          Stefan Appelhoff <stefan.appelhoff@mailbox.org>
#
# License: BSD (3-clause)

import os
from setuptools import setup, find_packages

# get the version
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
MAINTAINER = 'Stefan Appelhoff'
MAINTAINER_EMAIL = 'stefan.appelhoff@mailbox.org'
URL = 'https://github.com/bids-standard/pybv'
LICENSE = 'BSD (3-clause)'
DOWNLOAD_URL = 'https://github.com/bids-standard/pybv'
VERSION = version


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
          long_description_content_type='text/markdown',
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
          keywords='Brain Products BrainVision vhdr vmrk eeg',
          packages=find_packages(),
          project_urls={
            'Documentation': 'https://pybv.readthedocs.io',
            'Bug Reports': 'https://github.com/bids-standard/pybv/issues',
            'Source': 'https://github.com/bids-standard/pybv'
            }
          )
