[![CircleCI](https://circleci.com/gh/bids-standard/pybv.svg?style=svg)](https://circleci.com/gh/bids-standard/pybv)
[![codecov](https://codecov.io/gh/bids-standard/pybv/branch/master/graph/badge.svg)](https://codecov.io/gh/bids-standard/pybv)
[![Downloads](https://pepy.tech/badge/pybv)](https://pepy.tech/project/pybv)
[![Documentation Status](https://readthedocs.org/projects/pybv/badge/?version=stable)](https://pybv.readthedocs.io/en/stable/?badge=stable)

# pybv

A lightweight I/O utility for the BrainVision data format, written in Python.

**See the [pybv documentation](https://pybv.rtfd.io) for more information.**

**ALPHA SOFTWARE**. This package is currently in its early stages of iteration.
It may change both its internals or its user-facing API in the near future. Any
feedback and ideas on how to improve either of these is more than welcome!

For more information on how to help, see [CONTRIBUTING.md](/CONTRIBUTING.md).

## Installation

- install dependencies: `pip install numpy`
- install pybv: `pip install -U pybv`

## Usage

```python
from pybv import write_brainvision

# data: an ndarray of shape (n_channels, n_times)
# sfreq: the sampling frequency
# ch_names: a list of strings for channel names
# fname: the base file name for all created BrainVision files
# tmpdir: a path to where the output files will be placed
# events: an ndarray of shape (n_events, 2). Each row is an event,
#         the first column is the index of the event,
#         the second column is the event ID.
# resolution: the desired resolution (in volts) of the stored data.
write_brainvision(data, sfreq, ch_names, fname, tmpdir, events,
                  resolution=1e-6)
```

## Acknowledgements

This package was originally adapted from
[palday](https://palday.bitbucket.io/)'s
[Philistine package](https://gitlab.com/palday/philistine). It copies much of
the BrainVision exporting code, removes the dependence on MNE, and focuses the
code around BrainVision I/O.
