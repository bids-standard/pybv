[![CircleCI](https://circleci.com/gh/bids-standard/pybv.svg?style=svg)](https://circleci.com/gh/bids-standard/pybv)
[![codecov](https://codecov.io/gh/bids-standard/pybv/branch/master/graph/badge.svg)](https://codecov.io/gh/bids-standard/pybv)
[![Downloads](https://pepy.tech/badge/pybv)](https://pepy.tech/project/pybv)
[![Documentation Status](https://readthedocs.org/projects/pybv/badge/?version=latest)](https://pybv.readthedocs.io/en/latest/?badge=latest)

# pybv

A lightweight I/O utility for the BrainVision data format, written in Python.

**See the [pybv documentation](https://pybv.readthedocs.io) for more
information.**

**ALPHA SOFTWARE**. This package is currently in its early stages of iteration.
It may change both its internals or its user-facing API in the near future. Any
feedback and ideas on how to improve either of these is more than welcome!

## Acknowledgements

This package was originally adapted from
[palday](https://palday.bitbucket.io/)'s
[Philistine package](https://gitlab.com/palday/philistine). It copies much of
the BrainVision exporting code, removes the dependence on MNE, and focuses the
code around BrainVision I/O.
