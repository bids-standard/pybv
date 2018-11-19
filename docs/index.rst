====
pybv
====

``pybv`` is a lightweight exporter to the BrainVision data format. It is meant
for use with electrophysiology datasets stored in the `Brain Imaging Data Structure <https://bids.neuroimaging.io>`_.

Usage
=====

``pybv`` provides lightweight I/O functionality for the BrainVision data format.
See below for an example of how this works.

Writing BrainVision files
-------------------------

The primary functionality provided by ``pybv`` is the ``write_brainvision`` function.
This writes a numpy array of data and provided metadata into a collection of BrainVision
files on disk.

.. code-block:: python

   from pybv import write_brainvision

   # data: an ndarray of shape (n_channels, n_times)
   # sfreq: the sampling frequency
   # ch_names: a list of strings for channel names
   # fname: the base file name for all created BrainVision files
   # tmpdir: a path to where the output files will be placed
   # events: an ndarray of shape (n_events, 2). Each row is an event,
   #         the first column is the index of the event, second column is event ID.
   # resolution: the desired resolution (in volts) of the stored data.
   write_brainvision(data, sfreq, ch_names, fname, tmpdir, events, resolution=1e-6)

Reading BrainVision files
-------------------------

Currently, BrainVision recommends using `MNE-Python <https://martinos.org/mne/stable/index.html>`_
for reading BrainVision files written with ``pybv``. This results in a nearly-round-trip
conversion of the data (up to the numerical precision you specify in the ``resolution`` parameter.

Here's an example of the MNE code required to read in BrainVision data:

.. code-block:: python

   import mne

   # Import the BrainVision data into an MNE Raw object
   raw = mne.io.read_raw_brainvision('tmp/test.vhdr', preload=True, stim_channel=False)

   # Read in the event information as MNE annotations
   annot = mne.read_annotations('tmp/test.vmrk')

   # Add the annotations to our raw object so we can use them with the data
   raw.set_annotations(annot)

   # Reconstruct the original events from our Raw object
   events, event_ids = mne.events_from_annotations(raw)
