# -*- coding: utf-8 -*-
"""BrainVision Writer tests."""

# Authors: Phillip Alday <phillip.alday@unisa.edu.au>
#          Chris Holdgraf <choldgraf@berkeley.edu>
#          Stefan Appelhoff <stefan.appelhoff@mailbox.org>
#
# License: BSD (3-clause)

import os
import os.path as op
from shutil import rmtree
from tempfile import mkdtemp
from datetime import datetime, timezone

import pytest

import mne
import numpy as np
from numpy.testing import assert_allclose, assert_array_equal

from pybv.io import write_brainvision, _write_bveeg_file, _write_vhdr_file

# create testing data
fname = 'pybv'
rng = np.random.RandomState(1337)
n_chans = 10
ch_names = ['ch_{}'.format(i) for i in range(n_chans)]
sfreq = 1000
n_seconds = 5
n_times = n_seconds * sfreq
event_times = np.arange(1, 5)
events = np.column_stack([event_times * sfreq, [1, 1, 2, 2]])
data = rng.randn(n_chans, n_times)


def _mktmpdir():
    """Create a temporary directory for testing writers."""
    return mkdtemp(prefix='pybv_tmp_')


def test_bv_writer_events():
    """Test that all event options work without throwing an error."""
    tmpdir = _mktmpdir()

    # events should be none or ndarray
    with pytest.raises(ValueError, match='events must be an ndarray of shape'):
        write_brainvision(data, sfreq, ch_names, fname, tmpdir, events=[])

    with pytest.raises(ValueError, match='events must be an ndarray of shape'):
        write_brainvision(data, sfreq, ch_names, fname, tmpdir,
                          events=rng.randn(10, 20, 30))

    with pytest.raises(ValueError, match='events must be an ndarray of shape'):
        write_brainvision(data, sfreq, ch_names, fname, tmpdir,
                          events=rng.randn(10, 4))

    # correct arguments should work
    write_brainvision(data, sfreq, ch_names, fname, tmpdir, events=events)
    write_brainvision(data, sfreq, ch_names, fname, tmpdir, events=None)
    rmtree(tmpdir)


def test_bv_writer_inputs():
    """Test channels, sfreq, and resolution."""
    tmpdir = _mktmpdir()
    with pytest.raises(ValueError, match='Number of channels in data'):
        write_brainvision(data[1:, :], sfreq, ch_names, fname, tmpdir)
    with pytest.raises(ValueError, match='Channel names must be unique'):
        write_brainvision(data[0:2, :], sfreq, ['b', 'b'], fname, tmpdir)
    with pytest.raises(ValueError, match='sfreq must be one of '):
        write_brainvision(data, '100', ch_names, fname, tmpdir)
    with pytest.raises(ValueError, match='Resolution should be numeric, is'):
        write_brainvision(data, sfreq, ch_names, fname, tmpdir, resolution='y')
    with pytest.raises(ValueError, match='Resolution should be one or n_chan'):
        write_brainvision(data, sfreq, ch_names, fname, tmpdir,
                          resolution=np.arange(n_chans-1))
    rmtree(tmpdir)


def test_bv_bad_format():
    """Test that bad formats throw an error."""
    tmpdir = _mktmpdir()

    vhdr_fname = os.path.join(tmpdir, fname + ".vhdr")
    vmrk_fname = os.path.join(tmpdir, fname + ".vmrk")
    eeg_fname = os.path.join(tmpdir, fname + ".eeg")

    with pytest.raises(ValueError, match='Orientation bad not supported'):
        _write_vhdr_file(vhdr_fname, vmrk_fname,
                         eeg_fname, data, sfreq, ch_names, orientation='bad')
    with pytest.raises(ValueError, match='Data format bad not supported'):
        _write_vhdr_file(vhdr_fname, vmrk_fname,
                         eeg_fname, data, sfreq, ch_names, format='bad')
    with pytest.raises(ValueError, match='Orientation bad not supported'):
        _write_bveeg_file(eeg_fname, data, orientation='bad')
    with pytest.raises(ValueError, match='Data format bad not supported'):
        _write_bveeg_file(eeg_fname, data, format='bad')

    rmtree(tmpdir)


@pytest.mark.parametrize("meas_date,match",
                         [(1, '`meas_date` must be of type str, datetime'),
                          ('', 'Got a str for `meas_date`, but it was'),
                          ('1973', 'Got a str for `meas_date`, but it was')])
def test_bad_meas_date(meas_date, match):
    """Test that bad measurement dates raise errors."""
    tmpdir = _mktmpdir()
    with pytest.raises(ValueError, match=match):
        write_brainvision(data, sfreq, ch_names, fname, tmpdir,
                          meas_date=meas_date)
    rmtree(tmpdir)


@pytest.mark.parametrize("meas_date",
                         [('20000101120000000000'),
                          (datetime(2000, 1, 1, 12, 0, 0, 0))])
def test_write_read_cycle(meas_date):
    """Test that a write/read cycle produces identical data."""
    tmpdir = _mktmpdir()

    # check that we create a folder that does not yet exist
    tmpdir = op.join(tmpdir, 'newfolder')

    # First fail writing due to wrong unit
    unsupported_unit = "rV"
    with pytest.raises(ValueError, match='Encountered unsupported unit'):
        write_brainvision(data, sfreq, ch_names, fname, tmpdir,
                          unit=unsupported_unit)

    # write and read data to BV format
    # ensure that greek small letter mu gets converted to micro sign
    with pytest.warns(UserWarning):
        write_brainvision(data, sfreq, ch_names, fname, tmpdir, events=events,
                          resolution=np.power(10., -np.arange(10)),
                          unit='μV',
                          meas_date=meas_date)
    vhdr_fname = op.join(tmpdir, fname + '.vhdr')
    raw_written = mne.io.read_raw_brainvision(vhdr_fname, preload=True)
    # delete the first annotation because it's just marking a new segment
    raw_written.annotations.delete(0)
    # convert our annotations to events
    events_written, event_id = mne.events_from_annotations(raw_written)

    # sfreq
    assert sfreq == raw_written.info['sfreq']

    # event timing should be exactly the same
    assert_array_equal(events[:, 0], events_written[:, 0])
    assert_array_equal(events[:, 1], events_written[:, 2])

    assert len(event_id) == 2  # there should be two unique event types

    assert_allclose(data, raw_written._data)  # data round-trip

    assert ch_names == raw_written.ch_names  # channels

    # measurement dates must match
    assert raw_written.info['meas_date'] == datetime(2000, 1, 1, 12, 0, 0, 0,
                                                     tzinfo=timezone.utc)

    rmtree(tmpdir)


def test_scale_data():
    """Test that scale_data=False keeps the data untouched."""
    tmpdir = _mktmpdir()
    write_brainvision(data, sfreq, ch_names, fname, tmpdir, scale_data=False)
    data_written = np.fromfile(tmpdir + '/' + fname + '.eeg', dtype=np.float32)
    assert_allclose(data_written, data.T.flatten())
    rmtree(tmpdir)


@pytest.mark.parametrize("resolution", np.logspace(-1, -9, 9))
@pytest.mark.parametrize("unit", ["V", "mV", "uV", "µV", "nV", None])
def test_unit_resolution(resolution, unit):
    """Test different combinations of units and resolutions."""
    tmpdir = _mktmpdir()
    write_brainvision(data, sfreq, ch_names, fname, tmpdir,
                      resolution=resolution, unit=unit)
    vhdr_fname = op.join(tmpdir, fname + '.vhdr')
    raw_written = mne.io.read_raw_brainvision(vhdr_fname, preload=True)
    assert np.allclose(data, raw_written.get_data())
    rmtree(tmpdir)
