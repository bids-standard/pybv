# -*- coding: utf-8 -*-
"""File I/O utilities for EEG data."""

# Authors: Phillip Alday <phillip.alday@unisa.edu.au>
#          Chris Holdgraf <choldgraf@berkeley.edu>
#          Stefan Appelhoff <stefan.appelhoff@mailbox.org>
#          Tristan Stenner <stenner@med-psych.uni-kiel.de>
#          Clemens Brunner <clemens.brunner@gmail.com>
#          Richard Höchenberger <richard.hoechenberger@gmail.com>
#
# License: BSD (3-clause)

import codecs
import datetime
import os
import warnings
from os import path as op

import numpy as np

from pybv import __version__

# ASCII as future formats
SUPPORTED_FORMATS = {
    'binary_float32': ('IEEE_FLOAT_32', np.float32),
    'binary_int16': ('INT_16', np.int16),
}

SUPPORTED_ORIENTS = {'multiplexed'}

SUPPORTED_UNITS = {'V': 1e0, 'mV': 1e3, 'µV': 1e6, 'uV': 1e6, 'nV': 1e9}


def write_brainvision(*, data, sfreq, ch_names, fname_base, folder_out,
                      events=None, resolution=0.1, unit='µV',
                      fmt='binary_float32', meas_date=None):
    """Write raw data to BrainVision format.

    Parameters
    ----------
    data : ndarray, shape (n_channels, n_times)
        The raw data to export. Data is assumed to be in **Volts** and will be
        stored as specified by `unit`.
    sfreq : int | float
        The sampling frequency of the data.
    ch_names : list of strings, shape (n_channels,)
        The name of each channel.
    fname_base : str
        The base name for the output files. Three files will be created
        (.vhdr, .vmrk, .eeg) and all will share this base name.
    folder_out : str
        The folder where output files will be saved. Will be created if it
        does not exist yet.
    events : ndarray, shape (n_events, 2) or (n_events, 3) | None
        Events to write in the marker file. This array has either two or three
        columns. The first column is always the zero-based index of each event
        (corresponding to the "time" dimension of the data array). The second
        column is a number associated with the "type" of event. The (optional)
        third column specifies the length of each event (default 1 sample).
        Currently all events are written as type "Stimulus" and must be
        numeric.
        Defaults to None (not writing any events).
    resolution : float | ndarray, shape(nchannels,)
        The resolution in `unit` in which you'd like the data to be stored.
        If float, the same resolution is applied to all channels.
        If ndarray with n_channels elements, each channel is scaled with
        its own corresponding resolution from the ndarray.
        Note that `resolution` is applied on top of the default resolution
        that a data format (see `fmt`) has. For example, the binary_int16
        format by design has no floating point support, but when scaling the
        data in µV for 0.1 resolution (default), accurate writing for all
        values >= 0.1 µV will be guaranteed. In contrast, the binary_float32
        format by design already supports floating points up to 1e-6
        resolution, and writing data in µV with 0.1 resolution will thus
        guarantee accurate writing vor all values >= 1e-7 µV
        (``1e-6 * 0.1``).
    unit : str
        The unit of the exported data. This can be one of 'V', 'mV', 'µV' (or
        equivalently 'uV') , or 'nV'. Defaults to 'µV'.
    fmt : str
        Binary format the data should be written as. Valid choices are
        'binary_float32' (default) and 'binary_int16'.
    meas_date : datetime.datetime | str | None
        The measurement date specified as a datetime.datetime object.
        Alternatively, can be a string in the format 'YYYYMMDDhhmmssuuuuuu'
        ('u' stands for microseconds). Note that setting a measurement date
        implies that one additional event is created in the .vmrk file. To
        prevent this, set this parameter to None (default).
    """
    # Create output file names/paths
    os.makedirs(folder_out, exist_ok=True)
    vhdr_fname = op.join(folder_out, fname_base + '.vhdr')
    vmrk_fname = op.join(folder_out, fname_base + '.vmrk')
    eeg_fname = op.join(folder_out, fname_base + '.eeg')

    # Input checks
    ev_err = ("events must be an ndarray of shape (n_events, 2) or "
              "(n_events, 3) containing numeric values, or None")
    if not isinstance(events, (np.ndarray, type(None))):
        raise ValueError(ev_err)
    if isinstance(events, np.ndarray):
        if events.ndim != 2:
            raise ValueError(ev_err)
        if events.shape[1] not in (2, 3):
            raise ValueError(ev_err)
        try:
            events.astype(float)
        except ValueError:
            raise ValueError(ev_err)

    nchan = len(ch_names)

    if len(data) != nchan:
        raise ValueError(f"Number of channels in data ({len(data)}) does not "
                         f"match number of channel names ({len(ch_names)})")

    if len(set(ch_names)) != nchan:
        raise ValueError("Channel names must be unique, found duplicate name.")

    if not isinstance(sfreq, (int, float)):
        raise ValueError("sfreq must be one of (float | int)")
    sfreq = float(sfreq)

    resolution = np.atleast_1d(resolution)
    if not np.issubdtype(resolution.dtype, np.number):
        raise ValueError(f"Resolution should be numeric, is {resolution.dtype}")  # noqa: E501

    if resolution.shape != (1,) and resolution.shape != (nchan,):
        raise ValueError("Resolution should be one or n_chan floats")

    if np.any(resolution <= 0):
        raise ValueError("Resolution should be > 0")

    _chk_fmt(fmt)

    if unit == 'μV':
        # this is greek mu: μ
        # https://www.compart.com/de/unicode/U+03BC
        warnings.warn(
            f"Encountered small greek letter mu: 'μ' in unit: {unit} ... "
            f"converting to micro sign: 'µ': {unit.replace('μ', 'µ')}"
        )
        unit = 'µV'

    # measurement date
    if not isinstance(meas_date, (str, datetime.datetime, type(None))):
        raise ValueError(f'`meas_date` must be of type str, datetime.datetime,'
                         f' or None but is of type "{type(meas_date)}"')
    elif isinstance(meas_date, datetime.datetime):
        meas_date = meas_date.strftime('%Y%m%d%H%M%S%f')
    elif meas_date is None:
        pass
    elif not (meas_date.isdigit() and len(meas_date) == 20):
        raise ValueError('Got a str for `meas_date`, but it was not formatted '
                         'as expected. Please supply a str in the format: '
                         '"YYYYMMDDhhmmssuuuuuu".')

    # Write output files
    # NOTE: call _write_bveeg_file first, so that if it raises ValueError,
    # no files are written.
    _write_bveeg_file(eeg_fname, data, orientation='multiplexed', format=fmt,
                      resolution=resolution, unit=unit)
    _write_vmrk_file(vmrk_fname, eeg_fname, events, meas_date)
    _write_vhdr_file(vhdr_fname, vmrk_fname, eeg_fname, data, sfreq,
                     ch_names, orientation='multiplexed', format=fmt,
                     resolution=resolution, unit=unit)


def _chk_fmt(fmt):
    """Check that the format string is valid, return (BV, numpy) datatypes."""
    if fmt not in SUPPORTED_FORMATS:
        errmsg = (f'Data format {fmt} not supported. Currently supported '
                  f'formats are: {", ".join(SUPPORTED_FORMATS)}')
        raise ValueError(errmsg)
    return SUPPORTED_FORMATS[fmt]


def _chk_multiplexed(orientation):
    """Validate an orientation, return if it is multiplexed or not."""
    if orientation not in SUPPORTED_ORIENTS:
        errmsg = (f'Orientation {orientation} not supported. Currently '
                  f'supported orientations are: {", ".join(SUPPORTED_ORIENTS)}')  # noqa: E501
        raise ValueError(errmsg)
    return orientation == 'multiplexed'


def _write_vmrk_file(vmrk_fname, eeg_fname, events, meas_date):
    """Write BrainvVision marker file."""
    with codecs.open(vmrk_fname, 'w', encoding='utf-8') as fout:
        print('Brain Vision Data Exchange Marker File, Version 1.0', file=fout)
        print(f';Exported using pybv {__version__}', file=fout)
        print('', file=fout)
        print('[Common Infos]', file=fout)
        print('Codepage=UTF-8', file=fout)
        print(f'DataFile={eeg_fname.split(os.sep)[-1]}', file=fout)
        print('', file=fout)
        print('[Marker Infos]', file=fout)
        print('; Each entry: Mk<Marker number>=<Type>,<Description>,<Position in data points>,', file=fout)  # noqa: E501
        print(';             <Size in data points>, <Channel number (0 = marker is related to all channels)>', file=fout)  # noqa: E501
        print(';             <Date (YYYYMMDDhhmmssuuuuuu)>', file=fout)
        print('; Fields are delimited by commas, some fields might be omitted (empty).', file=fout)  # noqa: E501
        print(r'; Commas in type or description text are coded as "\1".', file=fout)  # noqa: E501
        if meas_date is not None:
            print(f'Mk1=New Segment,,1,1,0,{meas_date}', file=fout)

        if events is None or len(events) == 0:
            return

        if events.shape[1] == 2:  # add third column with event durations of 1
            events = np.column_stack([events, np.ones(len(events), dtype=int)])

        # Handle events: We write all of them as "Stimulus" events for now.
        # This is a string staring with "S" and followed by an integer of
        # minimum length 3, padded with "space" if the integer is < length 3.
        # For example "S  1", "S 23", "S345"
        # XXX: see https://github.com/bids-standard/pybv/issues/24#issuecomment-512746677  # noqa: E501
        twidth = int(np.ceil(np.log10(np.max(events[:, 1]))))
        twidth = max(3, twidth)
        tformat = 'S{:>' + str(twidth) + '}'

        # Currently all events are written as type "Stimulus"
        # Currently all event descriptions must be numeric
        for marker_number, irow in enumerate(range(len(events)), start=1 if meas_date is None else 2):  # noqa: E501
            i_ix = events[irow, 0] + 1  # BrainVision uses 1-based indexing
            i_val = events[irow, 1]
            i_dur = events[irow, 2]
            print(f'Mk{marker_number}=Stimulus,{tformat.format(i_val)},{i_ix},'
                  f'{i_dur},0', file=fout)


def _scale_data_to_unit(data, unit):
    """Scale `data` in Volts to `data` in `unit`."""
    scale = SUPPORTED_UNITS.get(unit, None)
    if scale is None:
        msg = (f'Encountered unsupported unit: {unit}\n'
               f'Use one of the following: {set(SUPPORTED_UNITS.keys())}')
        raise ValueError(msg)

    return data * scale


def _write_vhdr_file(vhdr_fname, vmrk_fname, eeg_fname, data, sfreq, ch_names,
                     orientation, format, resolution, unit):
    """Write BrainvVision header file."""
    bvfmt, _ = _chk_fmt(format)

    multiplexed = _chk_multiplexed(orientation)

    with codecs.open(vhdr_fname, 'w', encoding='utf-8') as fout:
        print('Brain Vision Data Exchange Header File Version 1.0', file=fout)
        print(f'; Written using pybv {__version__}', file=fout)
        print('', file=fout)
        print('[Common Infos]', file=fout)
        print('Codepage=UTF-8', file=fout)
        print(f'DataFile={op.basename(eeg_fname)}', file=fout)
        print(f'MarkerFile={op.basename(vmrk_fname)}', file=fout)

        if format.startswith('binary'):
            print('DataFormat=BINARY', file=fout)

        if multiplexed:
            print('; Data orientation: MULTIPLEXED=ch1,pt1, ch2,pt1 ...', file=fout)  # noqa: E501
            print('DataOrientation=MULTIPLEXED', file=fout)

        print(f'NumberOfChannels={len(data)}', file=fout)
        print('; Sampling interval in microseconds', file=fout)
        print(f'SamplingInterval={1e6 / sfreq}', file=fout)
        print('', file=fout)

        if format.startswith('binary'):
            print('[Binary Infos]', file=fout)
            print(f'BinaryFormat={bvfmt}', file=fout)
            print('', file=fout)

        print('[Channel Infos]', file=fout)
        print('; Each entry: Ch<Channel number>=<Name>,<Reference channel name>,', file=fout)  # noqa: E501
        print('; <Resolution in "Unit">,<Unit>, Future extensions..', file=fout)  # noqa: E501
        print('; Fields are delimited by commas, some fields might be omitted (empty).', file=fout)  # noqa: E501
        print(r'; Commas in channel names are coded as "\1".', file=fout)

        nchan = len(ch_names)
        # broadcast to nchan elements if necessary
        resolutions = resolution * np.ones((nchan,))
        units = [unit] * nchan

        for i in range(nchan):
            _ch_name = ch_names[i].replace(',', r'\1')
            resolution = np.format_float_positional(resolutions[i], trim="-")
            unit = units[i]
            print(f'Ch{i + 1}={_ch_name},,{resolution},{unit}', file=fout)

        print('', file=fout)
        print('[Comment]', file=fout)
        print('', file=fout)


def _check_data_in_range(data, dtype):
    """Check that data can be represented by dtype."""
    check_funcs = {np.int16: np.iinfo, np.float32: np.finfo}
    fun = check_funcs.get(dtype, None)
    if fun is None:  # pragma: no cover
        msg = f"Unsupported format encountered: {dtype}"
        raise ValueError(msg)
    if data.min() <= fun(dtype).min or data.max() >= fun(dtype).max:
        return False
    return True


def _write_bveeg_file(eeg_fname, data, orientation, format, resolution, unit):
    """Write BrainVision data file."""
    # check the orientation and format
    _chk_multiplexed(orientation)
    _, dtype = _chk_fmt(format)

    # convert the data to the desired unit
    data = _scale_data_to_unit(data, unit)

    # Invert the resolution so that we know how much to scale our data
    scaling_factor = 1 / resolution
    data = data * np.atleast_2d(scaling_factor).T

    # Convert the data to required format
    if not _check_data_in_range(data, dtype):
        mod = " ('{resolution}')"
        if isinstance(resolution, np.ndarray):
            # if we have individual resolutions, do not print them all
            mod = "s"
        msg = (f"`data` can not be represented in '{format}' given "
               f"the desired resolution{mod} and unit ('{unit}').")
        if format == "binary_int16":
            msg += "\nPlease consider writing using 'binary_float32' format."
        raise ValueError(msg)
    data = data.astype(dtype=dtype)

    # Save to binary
    data.ravel(order='F').tofile(eeg_fname)
