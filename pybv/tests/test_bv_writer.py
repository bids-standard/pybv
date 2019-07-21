# -*- coding: utf-8 -*-
"""BrainVision Writer tests."""

# Authors: Philip Alday <phillip.alday@unisa.edu.au>
#          Chris Holdgraf <choldgraf@berkeley.edu>
#          Stefan Appelhoff <stefan.appelhoff@mailbox.org>
#
# License: BSD (3-clause)

import os
import os.path as op
from shutil import rmtree
from tempfile import mkdtemp
from time import gmtime

import pytest

import mne
import numpy as np
from numpy.testing import assert_allclose, assert_array_equal

from pybv.io import write_brainvision, _write_bveeg_file, _write_vhdr_file

# Create data we'll use for testing
fname = 'pybv'
np.random.seed(1337)
n_chans = 10
ch_names = ['ch_{}'.format(ii) for ii in range(n_chans)]
sfreq = 1000.
n_seconds = 5
n_times = int(n_seconds * sfreq)
event_times = np.array([1., 2., 3., 4.])
events = np.column_stack([(event_times * sfreq).astype(int), [1, 1, 2, 2]])
data = np.random.randn(n_chans, n_times)


def _mktmpdir():
    """Create a temporary directory for testing writers."""
    return mkdtemp(prefix='pybv_tmp_')


def test_bv_writer_events():
    """Test that all event options work without throwing an error."""
    tmpdir = _mktmpdir()

    # Events should be none or ndarray
    with pytest.raises(ValueError):
        write_brainvision(data, sfreq, ch_names, fname, tmpdir, events=[])

    # Correct arguments should work
    write_brainvision(data, sfreq, ch_names, fname, tmpdir, events=events)
    write_brainvision(data, sfreq, ch_names, fname, tmpdir, events=None)
    rmtree(tmpdir)


def test_bv_bad_format():
    """Test that bad formats cause an error."""
    tmpdir = _mktmpdir()

    vhdr_fname = os.path.join(tmpdir, fname+".vhdr")
    vmrk_fname = os.path.join(tmpdir, fname+".vmrk")
    eeg_fname = os.path.join(tmpdir, fname+".eeg")
    # events = np.array([[10, 0, 31]])

    with pytest.raises(ValueError):
        _write_vhdr_file(vhdr_fname, vmrk_fname,
                         eeg_fname, data, sfreq, ch_names, orientation='bad')
    with pytest.raises(ValueError):
        _write_vhdr_file(vhdr_fname, vmrk_fname,
                         eeg_fname, data, sfreq, ch_names, format='bad')
    with pytest.raises(ValueError):
        _write_bveeg_file(eeg_fname, data, orientation='bad')
    with pytest.raises(ValueError):
        _write_bveeg_file(eeg_fname, data, format='bad')

    rmtree(tmpdir)


@pytest.mark.parametrize("meas_date,match",
                         [(1, '`meas_date` must be of type str or None but'),
                          ('', '`meas_date` must be None, or a string'),
                          ('1973', '`meas_date` must be None, or a string')])
def test_bad_meas_date(meas_date, match):
    """Test that bad measurement dates raise errors."""
    tmpdir = _mktmpdir()
    with pytest.raises(ValueError, match=match):
        write_brainvision(data, sfreq, ch_names, fname, tmpdir,
                          meas_date=meas_date)

    rmtree(tmpdir)


def test_bv_writer_oi_cycle():
    """Test that a write-read cycle produces identical data."""
    tmpdir = _mktmpdir()

    # Some sensible measurement date
    meas_date = '20000101120000000000'

    # Write, then read the data to BV format
    write_brainvision(data, sfreq, ch_names, fname, tmpdir, events=events,
                      resolution=np.power(10., -np.arange(10)),
                      meas_date=meas_date)
    vhdr_fname = op.join(tmpdir, fname + '.vhdr')
    raw_written = mne.io.read_raw_brainvision(vhdr_fname, preload=True)
    # Delete the first annotation because it's just marking a new segment
    raw_written.annotations.delete(0)
    # Convert our annotations to events
    events_written, event_id = mne.events_from_annotations(raw_written)

    # sfreq
    assert sfreq == raw_written.info['sfreq']

    # Event timing should be exactly the same
    assert_array_equal(events[:, 0], events_written[:, 0])
    assert_array_equal(events[:, 1], events_written[:, 2])
    # Should be 2 unique event types
    assert len(event_id) == 2

    # data round-trip.
    assert_allclose(data, raw_written._data)

    # channels
    assert ch_names == raw_written.ch_names

    # measurement date, we do not test microsecs
    unix_seconds = raw_written.info['meas_date'][0]
    time_str = ('{:04}{:02}{:02}{:02}{:02}{:02}'.format(*gmtime(unix_seconds)))
    assert meas_date[:-6] == time_str

    rmtree(tmpdir)


def test_scale_data():
    """Test that scale_data=False keeps the data untouched."""
    tmpdir = _mktmpdir()
    write_brainvision(data, sfreq, ch_names, fname, tmpdir, scale_data=False)
    data_written = np.fromfile(tmpdir + '/' + fname + '.eeg', dtype=np.float32)
    assert_allclose(data_written, data.T.flatten())
    rmtree(tmpdir)
