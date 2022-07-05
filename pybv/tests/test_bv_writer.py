"""BrainVision writer tests."""

import os
import os.path as op
import re
from datetime import datetime, timezone

import mne
import numpy as np
import pytest
from mne.utils import requires_version
from numpy.testing import assert_allclose, assert_array_equal

from pybv.io import (SUPPORTED_FORMATS, SUPPORTED_VOLTAGE_SCALINGS,
                     _check_data_in_range, _chk_fmt, _scale_data_to_unit,
                     _write_bveeg_file, _write_vhdr_file, write_brainvision)

# create testing data
fname = 'pybv'
rng = np.random.default_rng(1337)
n_chans = 10
ch_names = [f'ch_{i}' for i in range(n_chans)]
sfreq = 1000
n_seconds = 5
n_times = n_seconds * sfreq
event_times = np.arange(1, 5)
events_array = np.column_stack([event_times * sfreq, [1, 1, 2, 2]]).astype(int)
events = [
    {"onset": 1,
     "duration": 10,
     "description": 1,
     "type": "Stimulus",
     "channels": "all",
     },
    {"onset": 0,
     "description": "Some string :-)",
     "type": "Comment",
     "channels": "ch_1",
     },
    {"onset": 1000,
     "description": 2,
     "type": "Response",
     "channels": ["ch_1", "ch_2"],
     },
    {"onset": 200,
     "description": 1234,
     "channels": [],
     },
]
# scale random data to reasonable EEG signal magnitude in V
data = rng.normal(size=(n_chans, n_times)) * 10 * 1e-6

# add reference channel
ref_ch_name = ch_names[-1]
data[-1, :] = 0.


@pytest.mark.parametrize(
    "events_errormsg",
    [({}, 'events must be an array, a list of dict, or None'),
     (rng.normal(size=(10, 20, 30)), 'When array, events must be 2D, but got 3'),
     (rng.normal(size=(10, 4)), 'When array, events must have 2 or 3 columns, but got: 4'),  # noqa: E501
     (np.array([i for i in "abcd"]).reshape(2, -1), 'When array, all entries in events must be int'),  # noqa: E501
     (events_array, ''),
     (None, ''),
     (np.arange(90).reshape(30, 3), ''),
     ])
def test_bv_writer_events_array(tmpdir, events_errormsg):
    """Test that all array-based event options work without throwing an error."""
    kwargs = dict(data=data, sfreq=sfreq, ch_names=ch_names,
                  fname_base=fname, folder_out=tmpdir)

    ev, errormsg = events_errormsg
    if errormsg:
        with pytest.raises(ValueError, match=errormsg):
            write_brainvision(**kwargs, events=ev)
    else:
        write_brainvision(**kwargs, events=ev)


@pytest.mark.parametrize(
    "events_errormsg",
    [([{}, {"onset": 1}], "must have the keys 'onset' and 'description'"),
     ([{"onset": 1, "description": 2}, np.ones(12)], "events must be a list of dict"),
     ([{"onset": "1", "description": 2}], "events: `onset` must be int"),
     ([{"onset": -1, "description": 2}], r"events: at least one onset sample is not in range of data \(0-4999\)"),  # noqa: E501
     ([{"onset": 100, "description": 1, "duration": -1}], "events: at least one duration is negative."),  # noqa: E501
     ([{"onset": 100, "description": 1, "duration": 4901}], "events: at least one event has a duration that exceeds"),  # noqa: E501
     ([{"onset": 1, "description": 2, "type": "bogus"}], "`type` must be one of"),  # noqa: E501
     ([{"onset": 1, "description": "bogus"}], "when `type` is Stimulus, `description` must be non-negative int"),  # noqa: E501
     ([{"onset": 1, "description": {}, "type": "Comment"}], "when `type` is Comment, `description` must be str or int"),  # noqa: E501
     ([{"onset": 1, "description": -1}], "when `type` is Stimulus, descriptions must be non-negative ints."),  # noqa: E501
     ([{"onset": 1, "description": 1, "channels": "bogus"}], "found channel .* bogus"),
     ([{"onset": 1, "description": 1, "channels": ["ch_1", "ch_1"]}], "events: found duplicate channel names"),  # noqa: E501
     ([{"onset": 1, "description": 1, "channels": ["ch_1", "ch_2"]}], "warn___feature may not be supported"),  # noqa: E501
     ([{"onset": 1, "description": 1, "channels": 1}], "events: `channels` must be str or list of str"),  # noqa: E501
     ([{"onset": 1, "description": 1, "channels": [{}]}], "be list of str or list of int corresponding to ch_names"),  # noqa: E501
     ([], ''),
     (events, 'warn___you specified at least one event that impacts more than one'),
     ])
def test_bv_writer_events_list_of_dict(tmpdir, events_errormsg):
    """Test that events are written properly when list of dict."""
    kwargs = dict(data=data, sfreq=sfreq, ch_names=ch_names,
                  fname_base=fname, folder_out=tmpdir)

    ev, errormsg = events_errormsg
    if errormsg.startswith("warn"):
        warnmsg = errormsg.split("___")[-1]
        with pytest.warns(UserWarning, match=warnmsg):
            write_brainvision(**kwargs, events=ev)
    elif len(errormsg) > 0:
        with pytest.raises(ValueError, match=errormsg):
            write_brainvision(**kwargs, events=ev)
    else:
        write_brainvision(**kwargs, events=ev)


def test_kw_only_args(tmpdir):
    """Test that keyword only arguments are allowed."""
    msg = r'write_brainvision\(\) takes 0 positional arguments'
    with pytest.raises(TypeError, match=msg):
        write_brainvision(data, sfreq, ch_names, fname, folder_out=tmpdir)


def test_bv_writer_inputs(tmpdir):
    """Test data, channels, sfreq, resolution, ref_ch_names, and overwrite."""
    with pytest.raises(ValueError, match='data must be np.ndarray'):
        write_brainvision(data=[1, 2, 3], sfreq=sfreq, ch_names=ch_names,
                          fname_base=fname, folder_out=tmpdir)
    with pytest.raises(ValueError, match='data must be 2D: shape'):
        write_brainvision(data=rng.normal(size=(3, 3, 3)), sfreq=sfreq,
                          ch_names=ch_names, fname_base=fname, folder_out=tmpdir)
    with pytest.raises(ValueError, match='Number of channels in data'):
        write_brainvision(data=data[1:, :], sfreq=sfreq, ch_names=ch_names,
                          fname_base=fname, folder_out=tmpdir)
    with pytest.raises(ValueError, match='Channel names must be unique'):
        write_brainvision(data=data[0:2, :], sfreq=sfreq, ch_names=['b', 'b'],
                          fname_base=fname, folder_out=tmpdir)
    with pytest.raises(ValueError, match='ch_names must be a list of str.'):
        write_brainvision(data=data[0:2, :], sfreq=sfreq, ch_names=['b', 2.3],
                          fname_base=fname, folder_out=tmpdir)
    with pytest.raises(ValueError, match='sfreq must be one of '):
        write_brainvision(data=data, sfreq='100', ch_names=ch_names,
                          fname_base=fname, folder_out=tmpdir)
    with pytest.raises(ValueError, match='Resolution should be numeric, is'):
        write_brainvision(data=data, sfreq=sfreq, ch_names=ch_names,
                          fname_base=fname, folder_out=tmpdir, resolution='y')
    with pytest.raises(ValueError, match='Resolution should be > 0'):
        write_brainvision(data=data, sfreq=sfreq, ch_names=ch_names,
                          fname_base=fname, folder_out=tmpdir, resolution=0)
    with pytest.raises(ValueError, match='Resolution should be one or n_chan'):
        write_brainvision(data=data, sfreq=sfreq, ch_names=ch_names,
                          fname_base=fname, folder_out=tmpdir,
                          resolution=np.arange(n_chans-1))
    with pytest.raises(ValueError, match='overwrite must be a boolean'):
        write_brainvision(data=data[1:, :], sfreq=sfreq, ch_names=ch_names,
                          fname_base=fname, folder_out=tmpdir, overwrite=1)
    with pytest.raises(ValueError, match='number of reference channel names'):
        write_brainvision(data=data, sfreq=sfreq, ch_names=ch_names,
                          ref_ch_names=['foo', 'bar'], fname_base=fname,
                          folder_out=tmpdir)
    # Passing data that's not all-zero for a reference channel should raise
    # an exception
    data_ = data.copy()
    data_[ch_names.index(ref_ch_name), :] = 5
    with pytest.raises(ValueError, match='reference channel.*not.*zero'):
        write_brainvision(data=data_, sfreq=sfreq, ch_names=ch_names,
                          ref_ch_names=ref_ch_name, fname_base=fname,
                          folder_out=tmpdir)
    # Empty str is a reserved value for ref_ch_names
    with pytest.raises(ValueError, match='Empty strings are reserved values'):
        _ref_ch_names = [""] + ch_names[1:]
        write_brainvision(data=data_, sfreq=sfreq, ch_names=ch_names,
                          ref_ch_names=_ref_ch_names, fname_base=fname,
                          folder_out=tmpdir)
    # Try ambiguous list of dict events with "all" ch
    with pytest.raises(ValueError, match="Found channel named 'all'.*ambiguous"):
        write_brainvision(data=data[:1, :], sfreq=sfreq, ch_names=["all"],
                          fname_base=fname, folder_out=tmpdir, events=events)


def test_bv_bad_format(tmpdir):
    """Test that bad formats throw an error."""
    vhdr_fname = tmpdir / fname + ".vhdr"
    vmrk_fname = tmpdir / fname + ".vmrk"
    eeg_fname = tmpdir / fname + ".eeg"

    with pytest.raises(ValueError, match='Orientation bad not supported'):
        _write_vhdr_file(vhdr_fname=vhdr_fname, vmrk_fname=vmrk_fname,
                         eeg_fname=eeg_fname, data=data,
                         sfreq=sfreq, ch_names=ch_names, ref_ch_names=None,
                         orientation='bad',
                         format="binary_float32", resolution=1e-6,
                         units=["V"] * n_chans)
    with pytest.raises(ValueError, match='Data format bad not supported'):
        _write_vhdr_file(vhdr_fname=vhdr_fname, vmrk_fname=vmrk_fname,
                         eeg_fname=eeg_fname, data=data,
                         sfreq=sfreq, ch_names=ch_names, ref_ch_names=None,
                         orientation='multiplexed', format="bad",
                         resolution=1e-6,
                         units=["V"] * n_chans)
    with pytest.raises(ValueError, match='Orientation bad not supported'):
        _write_bveeg_file(eeg_fname, data=data, orientation='bad',
                          format="bad", resolution=1e-6,
                          units=["µV"] * n_chans)
    with pytest.raises(ValueError, match='Data format bad not supported'):
        _write_bveeg_file(eeg_fname, data=data, orientation='multiplexed',
                          format="bad", resolution=1e-6,
                          units=["µV"] * n_chans)


@pytest.mark.parametrize("meas_date,match",
                         [(1, '`meas_date` must be of type str, datetime'),
                          ('', 'Got a str for `meas_date`, but it was'),
                          ('1973', 'Got a str for `meas_date`, but it was')])
def test_bad_meas_date(tmpdir, meas_date, match):
    """Test that bad measurement dates raise errors."""
    with pytest.raises(ValueError, match=match):
        write_brainvision(data=data, sfreq=sfreq, ch_names=ch_names,
                          fname_base=fname, folder_out=tmpdir,
                          meas_date=meas_date)


@requires_version("mne", min_version="0.22")
@pytest.mark.parametrize("ch_names_tricky",
                         [[ch + ' f o o' for ch in ch_names],
                          [ch + ',foo' for ch in ch_names],
                          ]
                         )
def test_comma_in_ch_name(tmpdir, ch_names_tricky):
    """Test that writing channel names with special characters works."""
    # write and read data to BV format
    write_brainvision(data=data, sfreq=sfreq, ch_names=ch_names_tricky,
                      fname_base=fname, folder_out=tmpdir)
    vhdr_fname = tmpdir / fname + '.vhdr'
    raw_written = mne.io.read_raw_brainvision(vhdr_fname=vhdr_fname,
                                              preload=True)

    assert ch_names_tricky == raw_written.ch_names  # channels

    assert_allclose(data, raw_written._data)  # data round-trip


@pytest.mark.parametrize(
    "meas_date, ref_ch_names",
    [
        ('20000101120000000000', ref_ch_name),
        (datetime(2000, 1, 1, 12, 0, 0, 0), None)
    ]
)
def test_write_read_cycle(tmpdir, meas_date, ref_ch_names):
    """Test that a write/read cycle produces identical data."""
    # First fail writing due to wrong unit
    unsupported_unit = "rV"
    with pytest.warns(UserWarning, match='Encountered unsupported '
                                         'non-voltage unit'):
        write_brainvision(data=data, sfreq=sfreq, ch_names=ch_names,
                          ref_ch_names=ref_ch_names, fname_base=fname,
                          folder_out=tmpdir, unit=unsupported_unit,
                          overwrite=True)

    # write and read data to BV format
    # ensure that greek small letter mu gets converted to micro sign
    with pytest.warns(UserWarning, match="Encountered small Greek letter mu"):
        write_brainvision(data=data, sfreq=sfreq, ch_names=ch_names,
                          ref_ch_names=ref_ch_names, fname_base=fname,
                          folder_out=tmpdir, events=events_array,
                          resolution=np.power(10., -np.arange(10)),
                          unit='μV', meas_date=meas_date, overwrite=True)
    vhdr_fname = tmpdir / fname + '.vhdr'
    raw_written = mne.io.read_raw_brainvision(vhdr_fname=vhdr_fname,
                                              preload=True)
    # delete the first annotation because it's just marking a new segment
    raw_written.annotations.delete(0)
    # convert our annotations to events
    events_written, event_id = mne.events_from_annotations(raw_written)

    # sfreq
    assert sfreq == raw_written.info['sfreq']

    # event timing should be exactly the same
    assert_array_equal(events_array[:, 0], events_written[:, 0])
    assert_array_equal(events_array[:, 1], events_written[:, 2])

    assert len(event_id) == 2  # there should be two unique event types

    assert_allclose(data, raw_written._data)  # data round-trip

    assert_array_equal(ch_names, raw_written.ch_names)  # channels

    # measurement dates must match
    assert raw_written.info['meas_date'] == datetime(2000, 1, 1, 12, 0, 0, 0,
                                                     tzinfo=timezone.utc)


resolutions = np.logspace(0, -9, 10)
resolutions = np.hstack((resolutions, [np.pi, 0.5, 0.27e-6, 13]))


@pytest.mark.filterwarnings("ignore:Encountered unsupported voltage units")
@pytest.mark.filterwarnings("ignore:Encountered small Greek letter mu")
@pytest.mark.parametrize("format", SUPPORTED_FORMATS.keys())
@pytest.mark.parametrize("resolution", resolutions)
@pytest.mark.parametrize("unit", SUPPORTED_VOLTAGE_SCALINGS)
def test_format_resolution_unit(tmpdir, format, resolution, unit):
    """Test different combinations of formats, resolutions, and units.

    This test would raise warnings for several cases of "unit"
    (Encountered unsupported voltage units), and a specific warning
    if "unit" is "uV" (Encountered small Greek letter mu).
    We ignore those warnings throughout the test.

    Each run of the test is furthermore expected to exit early
    with a ValueError for combinations of "resolution" and "format"
    that would result in data that cannot accurately be written.
    """
    # Check whether this test will be numerically possible
    tmpdata = _scale_data_to_unit(data.copy(), [unit] * n_chans)
    tmpdata = tmpdata * np.atleast_2d((1 / resolution)).T
    _, dtype = _chk_fmt(format)
    data_will_fit = _check_data_in_range(tmpdata, dtype)

    kwargs = dict(data=data, sfreq=sfreq, ch_names=ch_names,
                  fname_base=fname, folder_out=tmpdir,
                  resolution=resolution, unit=unit,
                  fmt=format)

    if not data_will_fit:
        # End this test early
        match = f"can not be represented in '{format}' given"
        with pytest.raises(ValueError, match=match):
            write_brainvision(**kwargs)
        return

    write_brainvision(**kwargs)
    vhdr_fname = tmpdir / fname + '.vhdr'
    raw_written = mne.io.read_raw_brainvision(vhdr_fname=vhdr_fname,
                                              preload=True)

    # Check that the correct units were written in the BV file
    orig_units = [u for key, u in raw_written._orig_units.items()]
    assert len(set(orig_units)) == 1
    if unit is not None:
        assert orig_units[0] == unit.replace("u", "µ")

    # Check round trip of data: in binary_int16 format, the tolerance
    # is given by the lowest resolution
    if format == "binary_int16":
        absolute_tolerance = np.atleast_2d(resolution).min()
    else:
        absolute_tolerance = 0

    assert_allclose(data, raw_written.get_data(), atol=absolute_tolerance)


@pytest.mark.parametrize("sfreq", [100, 125, 128, 500, 512, 1000, 1024, 512.1])
def test_sampling_frequencies(tmpdir, sfreq):
    """Test different sampling frequencies."""
    # sampling frequency gets written as sampling interval
    write_brainvision(data=data, sfreq=sfreq, ch_names=ch_names,
                      fname_base=fname, folder_out=tmpdir)
    vhdr_fname = tmpdir / fname + '.vhdr'
    raw_written = mne.io.read_raw_brainvision(vhdr_fname=vhdr_fname,
                                              preload=True)
    assert_allclose(sfreq, raw_written.info['sfreq'])


@pytest.mark.parametrize("unit", SUPPORTED_VOLTAGE_SCALINGS)
def test_write_multiple_units(tmpdir, unit):
    """Test writing data with a list of units."""
    wrong_num_units = [unit]
    with pytest.raises(ValueError, match='Number of channels in unit'):
        write_brainvision(data=data, sfreq=sfreq, ch_names=ch_names,
                          fname_base=fname, folder_out=tmpdir,
                          unit=wrong_num_units)

    expect_warn = unit in ["V", "mV", "nV", "uV"]
    expect_match = "Converting" if unit == "uV" else "unsupported"

    # write brain vision file
    vhdr_fname = tmpdir / fname + '.vhdr'
    kwargs = dict(data=data, sfreq=sfreq, ch_names=ch_names,
                  fname_base=fname, folder_out=tmpdir,
                  unit=[unit] * n_chans)
    if expect_warn:
        with pytest.warns(UserWarning, match=expect_match):
            write_brainvision(**kwargs)
    else:
        write_brainvision(**kwargs)
    raw_written = mne.io.read_raw_brainvision(vhdr_fname=vhdr_fname,
                                              preload=True)

    # check round-trip works
    absolute_tolerance = 0
    assert_allclose(data, raw_written.get_data(), atol=absolute_tolerance)

    # Check that the correct units were written in the BV file
    orig_units = [u for key, u in raw_written._orig_units.items()]
    assert len(set(orig_units)) == 1
    assert orig_units[0] == unit.replace("u", "µ")

    # now write with different units across all channels
    other_unit = 'mV' if unit != 'mV' else 'V'
    units = [unit] * (n_chans // 2)
    units.extend([other_unit] * (n_chans // 2))

    # write file and read back in, we always expect a warning here
    kwargs["unit"] = units
    kwargs["overwrite"] = True
    with pytest.warns(UserWarning, match="unsupported"):
        write_brainvision(**kwargs)

    raw_written = mne.io.read_raw_brainvision(vhdr_fname=vhdr_fname,
                                              preload=True)

    # Check that the correct units were written in the BV file
    orig_units = [u for key, u in raw_written._orig_units.items()]
    assert len(set(orig_units)) == 2
    assert all([orig_units[idx] == unit.replace("u", "µ")
                for idx in range(n_chans // 2)])
    assert all([orig_units[-idx] == other_unit.replace("u", "µ")
                for idx in range(1, n_chans // 2 + 1)])


def test_write_unsupported_units(tmpdir):
    """Test writing data with a list of possibly unsupported BV units."""
    unit = 'V'  # supported test unit
    units = [unit] * n_chans
    units[-1] = '°C'

    # write brain vision file
    vhdr_fname = tmpdir / (fname + '.vhdr')
    with pytest.warns(UserWarning, match='Encountered unsupported '
                                         'non-voltage unit'):
        write_brainvision(data=data, sfreq=sfreq, ch_names=ch_names,
                          fname_base=fname, folder_out=tmpdir,
                          unit=units)
    raw_written = mne.io.read_raw_brainvision(vhdr_fname=vhdr_fname,
                                              preload=True)

    # check round-trip works
    absolute_tolerance = 0
    assert_allclose(data, raw_written.get_data(), atol=absolute_tolerance)

    # Check that the correct units were written in the BV file
    orig_units = [u for key, u in raw_written._orig_units.items()]
    assert len(set(orig_units)) == 2
    assert all([orig_units[idx] == unit for idx in range(n_chans - 1)])
    assert orig_units[-1] == '°C'


@pytest.mark.parametrize(
    'ref_ch_names', (
        None,
        ref_ch_name,
        [ref_ch_name] * n_chans,
        'foobar'
    )
)
def test_ref_ch(tmpdir, ref_ch_names):
    """Test reference channel writing."""
    # these are the default values
    resolution = '0.1'
    unit = 'µV'
    vhdr_fname = tmpdir / fname + '.vhdr'

    write_brainvision(data=data, sfreq=sfreq, ch_names=ch_names,
                      ref_ch_names=ref_ch_name, fname_base=fname,
                      folder_out=tmpdir)

    vhdr = vhdr_fname.read_text(encoding='utf-8')
    regexp = f'Ch.*=ch.*,{ref_ch_name},{resolution},{unit}'
    matches = re.findall(pattern=regexp, string=vhdr)
    assert len(matches) == len(ch_names)


def test_cleanup(tmpdir):
    """Test cleaning up intermediate data upon a writing failure."""
    folder_out = tmpdir / "my_output"
    with pytest.raises(ValueError, match="Data format binary_float999"):
        write_brainvision(data=data, sfreq=sfreq, ch_names=ch_names,
                          fname_base=fname, folder_out=folder_out,
                          fmt="binary_float999")
    assert not op.exists(folder_out)
    assert not op.exists(folder_out / fname + ".eeg")
    assert not op.exists(folder_out / fname + ".vmrk")
    assert not op.exists(folder_out / fname + ".vhdr")

    # if folder already existed before erroneous writing, it is not deleted
    os.makedirs(folder_out)
    with pytest.raises(ValueError, match="Data format binary_float999"):
        write_brainvision(data=data, sfreq=sfreq, ch_names=ch_names,
                          fname_base=fname, folder_out=folder_out,
                          fmt="binary_float999")
    assert op.exists(folder_out)

    # but all other (incomplete/erroneous) files are deleted
    assert not op.exists(folder_out / fname + ".eeg")
    assert not op.exists(folder_out / fname + ".vmrk")
    assert not op.exists(folder_out / fname + ".vhdr")


def test_overwrite(tmpdir):
    """Test overwriting behavior."""
    write_brainvision(data=data, sfreq=sfreq, ch_names=ch_names,
                      fname_base=fname, folder_out=tmpdir,
                      overwrite=False)

    with pytest.raises(IOError, match="File already exists"):
        write_brainvision(data=data, sfreq=sfreq, ch_names=ch_names,
                          fname_base=fname, folder_out=tmpdir,
                          overwrite=False)


def test_event_writing(tmpdir):
    """Test writing some advanced event specifications."""
    kwargs = dict(data=data, sfreq=sfreq, ch_names=ch_names,
                  fname_base=fname, folder_out=tmpdir)

    with pytest.warns(UserWarning, match="Such events will be written to .vmrk"):
        write_brainvision(**kwargs, events=events)

    vhdr_fname = tmpdir / fname + '.vhdr'
    raw = mne.io.read_raw_brainvision(vhdr_fname=vhdr_fname, preload=True)

    # should be one more, because event[3] is written twice (once per channel)
    assert len(raw.annotations) == len(events) + 1

    # note: mne orders events by onset, use sorted
    onsets = np.array([ev["onset"] / raw.info["sfreq"] for ev in events])
    onsets = sorted(onsets) + [1.]  # add duplicate event (due to channels)
    np.testing.assert_array_equal(raw.annotations.onset, onsets)

    # mne does not (yet; at 1.0.3) read ch_names for annotations from vmrk
    np.testing.assert_array_equal([i for i in raw.annotations.ch_names],
                                  [() for i in range(len(events) + 1)])

    # test duration and description as well
    durations = [i / raw.info["sfreq"] for i in (1, 10, 1, 1, 1)]
    np.testing.assert_array_equal(raw.annotations.duration, durations)

    descr = ['Comment/Some string :-)', 'Stimulus/S   1', 'Stimulus/S1234',
             'Response/R   2', 'Response/R   2']
    np.testing.assert_array_equal(raw.annotations.description, descr)

    # smoke test forming events from annotations
    _events, _event_id = mne.events_from_annotations(raw)
    for _d in descr:
        assert _d in _event_id
