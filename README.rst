.. image:: https://circleci.com/gh/bids-standard/pybv.svg?style=svg
   :target: https://circleci.com/gh/bids-standard/pybv
   :alt: CircleCI

.. image:: https://codecov.io/gh/bids-standard/pybv/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/bids-standard/pybv
   :alt: codecov

.. image:: https://badge.fury.io/py/pybv.svg
   :target: https://badge.fury.io/py/pybv
   :alt: pypi

.. image:: https://pepy.tech/badge/pybv
   :target: https://pepy.tech/project/pybv
   :alt: Downloads

.. image:: https://readthedocs.org/projects/pybv/badge/?version=stable
   :target: https://pybv.readthedocs.io/en/stable/?badge=stable
   :alt: Documentation Status

====
pybv
====

``pybv`` is a lightweight exporter to the BrainVision data format. It is meant
for use with electrophysiology datasets stored in the
`Brain Imaging Data Structure <https://bids.neuroimaging.io>`_.


The documentation can be found under the following links:

- for the `stable release <https://pybv.rtfd.io/en/stable/>`_
- for the `latest (development) version <https://pybv.rtfd.io/en/latest/>`_

About the BrainVision data format
=================================

BrainVision is the name of a file format commonly used for storing
electrophysiology data. Originally, it was put forward by the
company `Brain Products <https://www.brainproducts.com>`_, however the
simplicity of the format has allowed for a diversity of tools reading from and
writing to the format.

The format consists of three separate files:

1. A text header file (``.vhdr``) containing meta data
2. A text marker file (``.vmrk``) containing information about events in the
   data
3. A binary data file (``.eeg``) containing the voltage values of the EEG

Both text files are based on the
`Microsoft Windows INI format <https://en.wikipedia.org/wiki/INI_file>`_
consisting of:

- sections marked as ``[square brackets]``
- comments marked as ``; comment``
- key-value pairs marked as ``key=value``

A documentation for core BrainVision file format is provided by Brain Products.
You can `view the specification <https://www.brainproducts.com/productdetails.php?id=21&tab=5>`_
as hosted by Brain Products.


Installation
============
``pybv``'s only dependency is ``numpy``. However, we currently recommend that
you install MNE-Python for reading BrainVision data. See their instructions
`here <https://www.martinos.org/mne/stable/install_mne_python.html>`_.

After you have a working installation of MNE-Python (or only ``numpy`` if you
don't want to read data and only write it), you can install ``pybv`` through
the following: ``pip install -U pybv``

Contributing
============
The development of ``pybv`` is taking place on
`Github <https://github.com/bids-standard/pybv>`_.

For more information, please see
`CONTRIBUTING.md <https://github.com/bids-standard/pybv/blob/master/CONTRIBUTING.md>`_

Usage
=====

Writing BrainVision files
-------------------------

The primary functionality provided by ``pybv`` is the ``write_brainvision``
function. This writes a numpy array of data and provided metadata into a
collection of BrainVision files on disk.

.. code-block:: python

    from pybv import write_brainvision

    # for further parameters see our API documentation in the docs
    write_brainvision(data, sfreq, ch_names, fname, tmpdir, events,
                      resolution=1e-6, fmt='binary_float32')

Reading BrainVision files
-------------------------

Currently, pybv recommends using
`MNE-Python <https://martinos.org/mne/stable/index.html>`_
for reading BrainVision files written with ``pybv``. This results in a
nearly-round-trip conversion of the data (up to the numerical precision you
specify in the ``resolution`` parameter).

Here is an example of the MNE code required to read in BrainVision data:

.. code-block:: python

    import mne

    # Import the BrainVision data into an MNE Raw object
    raw = mne.io.read_raw_brainvision('tmp/test.vhdr', preload=True)

    # Read in the event information as MNE annotations
    annot = mne.read_annotations('tmp/test.vmrk')

    # Add the annotations to our raw object so we can use them with the data
    raw.set_annotations(annot)

    # Reconstruct the original events from our Raw object
    events, event_ids = mne.events_from_annotations(raw)

Acknowledgements
================

This package was originally adapted from the
`Philistine package <https://gitlab.com/palday/philistine>`_ by
`palday <https://palday.bitbucket.io/>`_. It copies much of the BrainVision
exporting code, removes the dependence on MNE, and focuses the code around
BrainVision I/O.
