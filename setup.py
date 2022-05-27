"""Setup pybv."""

import os

from setuptools import find_packages, setup

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
URL = 'https://pybv.readthedocs.io'
LICENSE = 'BSD-3-Clause'
DOWNLOAD_URL = 'https://github.com/bids-standard/pybv'
VERSION = version


if __name__ == "__main__":

    setup(name=DISTNAME,
          maintainer=MAINTAINER,
          include_package_data=True,
          maintainer_email=MAINTAINER_EMAIL,
          description=DESCRIPTION,
          license=LICENSE,
          url=URL,
          version=VERSION,
          download_url=DOWNLOAD_URL,
          long_description=open('README.rst').read(),
          long_description_content_type='text/x-rst',
          zip_safe=True,  # the package can run out of an .egg file
          python_requires='~=3.7',
          install_requires=[
              'numpy >=1.18.1',
          ],
          extras_require={
              'export': [
                  'mne >= 0.20',
              ],
          },
          classifiers=[
              'Intended Audience :: Science/Research',
              'Intended Audience :: Developers',
              'License :: OSI Approved',
              'Programming Language :: Python',
              'Topic :: Software Development',
              'Topic :: Scientific/Engineering',
              'Operating System :: Microsoft :: Windows',
              'Operating System :: POSIX',
              'Operating System :: Unix',
              'Operating System :: MacOS',
              'Programming Language :: Python :: 3.7',
              'Programming Language :: Python :: 3.8',
              'Programming Language :: Python :: 3.9',
              'Programming Language :: Python :: 3.10',
          ],
          platforms='any',
          keywords='Brain Products BrainVision vhdr vmrk eeg',
          packages=find_packages(),
          project_urls={
            'Documentation': 'https://pybv.readthedocs.io',
            'Bug Reports': 'https://github.com/bids-standard/pybv/issues',
            'Source': 'https://github.com/bids-standard/pybv'
            }
          )
