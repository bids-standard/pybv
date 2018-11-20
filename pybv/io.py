# -*- coding: utf-8 -*-
# Copyright (C) 2018 The BIDS Community
# License: BSD (3-clause)
"""File I/O utilities for EEG data."""

import codecs
import os
import os.path as op
import numpy as np

from . import __version__

# ascii as future formats
supported_formats = {
    'binary_float32' : 'IEEE_FLOAT_32',  # noqa: E203
    'binary_int16'   : 'INT_16',  # noqa: E203
}

supported_orients = set(['multiplexed'])


def write_brainvision(data, sfreq, ch_names, fname_base, folder_out, events=None,
                      resolution=1e-7):
    """Write raw data to BrainVision format.

    Parameters
    ----------
    data : ndarray, shape (n_channels, n_times)
        The raw data to export. Data is assumed to be in
        **volts**. The data will be stored in **microvolts**.
    sfreq : int | float
        The sampling frequency of the data
    ch_names : list of strings, shape (n_channels,)
        The name of each channel
    fname_base : str
        The base name for the output files. Three files will be created
        (.vhdr, .vmrk, .eeg) and all will share this base name.
    folder_out : str
        The folder where output files will be saved.
    events : ndarray, shape (n_events, 2)
        Events to write in the marker file. This array has two columns.
        The first column is the index of each event (corresponding to the
        "time" dimension of the data array). The second column is a number
        associated with the "type" of event. 
    resolution : float
        The resolution **in volts** in which you'd like the data to be stored.
        By default, this will be 1e-7, or .1 microvolts. Since data is stored
        in microvolts, the data will be multiplied by the inverse of this factor,
        and all decimals will be cut off after this. So, this number controls
        the amount of round-trip resolution you want.
    """
    # Create output file names/paths
    if not op.isdir(folder_out):
        os.makedirs(folder_out)
    vhdr_fname = op.join(folder_out, fname_base + '.vhdr')
    vmrk_fname = op.join(folder_out, fname_base + '.vmrk')
    eeg_fname = op.join(folder_out, fname_base + '.eeg')

    # Input checks
    ev_err = "events must be an (n_events x 2) ndarray or None'"
    if not isinstance(events, (np.ndarray, type(None))):
        raise ValueError(ev_err)
    if isinstance(events, np.ndarray):
        if events.ndim != 2:
            raise ValueError(ev_err)
        if events.shape[1] != 2:
            raise ValueError(ev_err)

    if len(data) != len(ch_names):
        raise ValueError("Number of channels in data ({}) does "
                         "not match number of channel names ({})".format(len(data), len(ch_names)))
    
    if len(set(ch_names)) != len(ch_names):
        raise ValueError("Channel names must be unique, found a repeated name.")

    if not isinstance(sfreq, (int, float)):
        raise ValueError("sfreq must be one of (float | int)")
    sfreq = float(sfreq)

    if not isinstance(resolution, (int, float)):
        raise ValueError("Resolution should be a (small) float")

    # Write output files
    _write_vmrk_file(vmrk_fname, eeg_fname, events)
    _write_vhdr_file(vhdr_fname, vmrk_fname, eeg_fname, data, sfreq,
                     ch_names, resolution=resolution)
    _write_bveeg_file(eeg_fname, data, resolution=resolution)


def _write_vmrk_file(vmrk_fname, eeg_fname, events):
    """Write BrainvVision marker file."""
    with codecs.open(vmrk_fname, 'w', encoding='utf-8') as fout:
        print(r'Brain Vision Data Exchange Marker File, Version 1.0', file=fout)  # noqa: E501
        print(r';Exported using pybv {}'.format(__version__), file=fout)  # noqa: E501
        print(r'', file=fout)
        print(r'[Common Infos]', file=fout)
        print(r'Codepage=UTF-8', file=fout)
        print(r'DataFile={}'.format(eeg_fname.split(os.sep)[-1]), file=fout)  # noqa: E501
        print(r'', file=fout)
        print(r'[Marker Infos]', file=fout)
        print(r'; Each entry: Mk<Marker number>=<Type>,<Description>,<Position in data points>,', file=fout)  # noqa: E501
        print(r';             <Size in data points>, <Channel number (0 = marker is related to all channels)>', file=fout)  # noqa: E501
        print(r'; Fields are delimited by commas, some fields might be omitted (empty).', file=fout)  # noqa: E501
        print(r'; Commas in type or description text are coded as "\1".', file=fout)  # noqa: E501
        print(r'Mk1=New Segment,,1,1,0,0', file=fout)

        if events is None:
            return

        # Handle events
        twidth = int(np.ceil(np.log10(np.max(events[:, 1]))))
        tformat = 'S{:>' + str(twidth) + '}'

        for ii, irow in enumerate(range(len(events)), start=2):
            i_ix = events[irow, 0]
            i_val = events[irow, 1]
            print(r'Mk{}=Stimulus,{},{},1,0'.format(ii, tformat.format(i_val), i_ix), file=fout)


def _write_vhdr_file(vhdr_fname, vmrk_fname, eeg_fname, data, sfreq, ch_names,
                     orientation='multiplexed', format='binary_float32', resolution=1e-7):
    """Write BrainvVision header file."""
    fmt = format.lower()

    if orientation.lower() not in supported_orients:
        errmsg = ('Orientation {} not supported.'.format(orientation) +
                  'Currently supported orientations are: ' +
                  ', '.join(supported_orients))
        raise ValueError(errmsg)

    if fmt not in supported_formats:
        errmsg = ('Data format {} not supported.'.format(format) +
                  'Currently supported formats are: ' +
                  ', '.join(supported_formats))
        raise ValueError(errmsg)

    with codecs.open(vhdr_fname, 'w', encoding='utf-8') as fout:
        print(r'Brain Vision Data Exchange Header File Version 1.0', file=fout)  # noqa: E501
        print(r';Written using pybv {}'.format(__version__), file=fout)  # noqa: E501
        print(r'', file=fout)
        print(r'[Common Infos]', file=fout)
        print(r'Codepage=UTF-8', file=fout)
        print(r'DataFile={}'.format(op.basename(eeg_fname)), file=fout)  # noqa: E501
        print(r'MarkerFile={}'.format(op.basename(vmrk_fname)), file=fout)  # noqa: E501

        if 'binary' in format.lower():
            print(r'DataFormat=BINARY', file=fout)

        if 'multiplexed' == orientation.lower():
            print(r'Data orientation: MULTIPLEXED=ch1,pt1, ch2,pt1 ...', file=fout)  # noqa: E501
            print(r'DataOrientation=MULTIPLEXED', file=fout)

        print(r'NumberOfChannels={}'.format(len(data)), file=fout)  # noqa: E501
        print(r'; Sampling interval in microseconds', file=fout)
        print(r'SamplingInterval={}'.format(int(1e6 / sfreq)), file=fout)  # noqa: E501
        print(r'', file=fout)

        if 'binary' in format.lower():
            print(r'[Binary Infos]', file=fout)
            print(r'BinaryFormat={}'.format(supported_formats[format]), file=fout)  # noqa: E501
            print(r'', file=fout)

        print(r'[Channel Infos]', file=fout)
        print(r'; Each entry: Ch<Channel number>=<Name>,<Reference channel name>,', file=fout)  # noqa: E501
        print(r';             <Resolution in microvolts>,<Future extensions..', file=fout)
        print(r'; Fields are delimited by commas, some fields might be omitted (empty).', file=fout)  # noqa: E501
        print(r'; Commas in channel names are coded as "\1".', file=fout)
        resolution_in_microv = resolution / 1e-6
        for ii, ch in enumerate(ch_names, start=1):
            print(r'Ch{}={},,{:0.1f}'.format(ii, ch, resolution_in_microv), file=fout)

        print(r'', file=fout)
        print(r'[Comment]', file=fout)
        print(r'', file=fout)


def _write_bveeg_file(eeg_fname, data, orientation='multiplexed',
                      format='binary_float32', resolution=1e-7):
    """Write BrainVision data file."""
    fmt = format.lower()

    if orientation.lower() not in supported_orients:
        errmsg = ('Orientation {} not supported.'.format(orientation) +
                  'Currently supported orientations are: ' +
                  ', '.join(supported_orients))
        raise ValueError(errmsg)

    if fmt not in supported_formats:
        errmsg = ('Data format {} not supported.'.format(format) +
                  'Currently supported formats are: ' +
                  ', '.join(supported_formats))
        raise ValueError(errmsg)

    if fmt[:len('binary')] == 'binary':
        dtype = np.dtype(format.lower()[len('binary') + 1:])
    else:
        errmsg = 'Cannot map data format {} to NumPy dtype'.format(format)
        raise ValueError(errmsg)

    # Invert the resolution so that we know how much to scale our data
    scaling_factor = 1 / resolution
    with open(eeg_fname, 'wb') as fout:
        data = data * scaling_factor
        fout.write(data.astype(dtype=dtype).ravel(order='F').tobytes())
