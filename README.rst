.. image:: https://github.com/bids-standard/pybv/workflows/Python%20build/badge.svg
   :target: https://github.com/bids-standard/pybv/actions?query=workflow%3A%22Python+build%22
   :alt: GitHub Actions Python build

.. image:: https://github.com/bids-standard/pybv/workflows/Python%20tests/badge.svg
   :target: https://github.com/bids-standard/pybv/actions?query=workflow%3A%22Python+tests%22
   :alt: GitHub Actions Python tests

.. image:: https://codecov.io/gh/bids-standard/pybv/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/bids-standard/pybv
   :alt: Codecov

.. image:: https://badge.fury.io/py/pybv.svg
   :target: https://badge.fury.io/py/pybv
   :alt: PyPi version

.. image:: https://img.shields.io/conda/vn/conda-forge/pybv.svg
   :target: https://anaconda.org/conda-forge/pybv
   :alt: Conda version

.. image:: https://readthedocs.org/projects/pybv/badge/?version=stable
   :target: https://pybv.readthedocs.io/en/stable/?badge=stable
   :alt: Documentation Status

.. image:: https://zenodo.org/badge/157434681.svg
   :target: https://zenodo.org/badge/latestdoi/157434681
   :alt: Zenodo archive

====
pybv
====

``pybv`` is a lightweight I/O utility for the BrainVision data format.

The BrainVision data format is a recommended data format for use in the
`Brain Imaging Data Structure <https://bids.neuroimaging.io>`_.


The documentation can be found under the following links:

- for the `stable release <https://pybv.rtfd.io/en/stable/>`_
- for the `latest (development) version <https://pybv.rtfd.io/en/latest/>`_

About the BrainVision data format
=================================

BrainVision is the name of a file format commonly used for storing electrophysiology data.
Originally, it was put forward by the company `Brain Products <https://www.brainproducts.com>`_,
however the simplicity of the format has allowed for a diversity of tools reading from and
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

The binary ``.eeg`` data file is written in little-endian format without a Byte Order
Mark (BOM), in accordance with the specification by Brain Products.
This ensures that the data file is uniformly written irrespective of the
native system architecture.

A documentation for the BrainVision file format is provided by Brain Products.
You can `view the specification <https://www.brainproducts.com/support-resources/brainvision-core-data-format-1-0/>`_
as hosted by Brain Products.


Installation
============

``pybv`` runs on Python version 3.7 or higher.

``pybv``'s only dependency is ``numpy``.
However, we currently recommend that you install MNE-Python for reading BrainVision data.
See their `installation instructions <https://mne.tools/stable/install/index.html>`_.

After you have a working installation of MNE-Python (or only ``numpy`` if you
do not want to read data and only write it), you can install ``pybv`` through
the following:

- ``pip install --upgrade pybv``

or if you use `conda <https://docs.conda.io/en/latest/miniconda.html>`_:

- ``conda install --channel conda-forge pybv``

Contributing
============

The development of ``pybv`` is taking place on
`GitHub <https://github.com/bids-standard/pybv>`_.

For more information, please see
`CONTRIBUTING.md <https://github.com/bids-standard/pybv/blob/main/.github/CONTRIBUTING.md>`_

Usage
=====

Writing BrainVision files
-------------------------

The primary functionality provided by ``pybv`` is the ``write_brainvision``
function. This writes a numpy array of data and provided metadata into a
collection of BrainVision files on disk.

.. code-block:: python

    from pybv import write_brainvision

    # for further parameters see our API documentation
    write_brainvision(data=data, sfreq=sfreq, ch_names=ch_names,
                      fname_base=fname, folder_out=tmpdir,
                      events=events)

Reading BrainVision files
-------------------------

Currently, ``pybv`` recommends using `MNE-Python <https://mne.tools>`_
for reading BrainVision files.

Here is an example of the MNE-Python code required to read BrainVision data:

.. code-block:: python

    import mne

    # Import the BrainVision data into an MNE Raw object
    raw = mne.io.read_raw_brainvision('tmp/test.vhdr', preload=True)

    # Reconstruct the original events from our Raw object
    events, event_ids = mne.events_from_annotations(raw)

Alternatives
============

The BrainVision data format is very popular and accordingly there are many
software packages to read this format, or write to it.
The following table is intended as a quick overview of packages similar to
`pybv <https://github.com/bids-standard/pybv>`_.
Please let us know if you know of additional packages that should be listed here.

+-----------------------------------------------------------------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------+
| Name of software                                                            | Language             | Notes                                                                                                                                       |
+=============================================================================+======================+=============================================================================================================================================+
| `BioSig Project <http://biosig.sourceforge.net/index.html>`_                | miscellaneous        | Reading and writing capabilities depend on bindings used, see their `overview <https://pub.ist.ac.at/~schloegl/biosig/TESTED>`_             |
+-----------------------------------------------------------------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------+
| `Brainstorm <https://neuroimage.usc.edu/brainstorm/>`_                      | MATLAB               | Read and write, search for ``brainamp`` in their `io functions <https://github.com/brainstorm-tools/brainstorm3/tree/master/toolbox/io>`_   |
+-----------------------------------------------------------------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------+
| `BrainVision Analyzer <https://www.brainproducts.com/downloads.php?kid=9>`_ | n/a, GUI for Windows | Read and write, by Brain Products, requires commercial license                                                                              |
+-----------------------------------------------------------------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------+
| `brainvisionloader.jl <https://github.com/agricolab/brainvisionloader.jl>`_ | Julia                | Read                                                                                                                                        |
+-----------------------------------------------------------------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------+
| `EEGLAB <https://sccn.ucsd.edu/eeglab/index.php>`_                          | MATLAB / Octave      | Read and write via `BVA-IO <https://github.com/arnodelorme/bva-io>`_                                                                        |
+-----------------------------------------------------------------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------+
| `FieldTrip <https://www.fieldtriptoolbox.org>`_                             | MATLAB               | Read and write, search for ``brainvision`` in their `fileio functions <https://github.com/fieldtrip/fieldtrip/tree/master/fileio/private>`_ |
+-----------------------------------------------------------------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------+
| `MNE-Python <https://mne.tools>`_                                           | Python               | Read (writing via ``pybv``)                                                                                                                 |
+-----------------------------------------------------------------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------+

Acknowledgements
================

This package was originally adapted from the
`Philistine package <https://gitlab.com/palday/philistine>`_ by
`palday <https://phillipalday.com/>`_.
It copies much of the BrainVision exporting code, but removes the dependence on MNE.
Several features have been added, such as support for individual units for each channel.
