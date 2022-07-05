"""BrainVision writer."""

import copy
import datetime
import os
import shutil
import sys
from os import path as op
from warnings import warn

import numpy as np

from pybv import __version__

# ASCII as future formats
SUPPORTED_FORMATS = {
    'binary_float32': ('IEEE_FLOAT_32', np.float32),
    'binary_int16': ('INT_16', np.int16),
}

SUPPORTED_ORIENTS = {'multiplexed'}

SUPPORTED_VOLTAGE_SCALINGS = {
    'V': 1e0, 'mV': 1e3, 'µV': 1e6, 'uV': 1e6, 'nV': 1e9
}


def write_brainvision(*, data, sfreq, ch_names,
                      ref_ch_names=None,
                      fname_base,
                      folder_out,
                      overwrite=False,
                      events=None,
                      resolution=0.1,
                      unit='µV',
                      fmt='binary_float32',
                      meas_date=None):
    """Write raw data to the BrainVision format [1]_.

    Parameters
    ----------
    data : np.ndarray, shape (n_channels, n_times)
        The raw data to export. Voltage data is assumed to be in **volts** and
        will be scaled as specified by `unit`. Non-voltage channels (as
        specified by `unit`) are never scaled (e.g., `"°C"`).
    sfreq : int | float
        The sampling frequency of the data in Hz.
    ch_names : list of {str | int}, len (n_channels)
        The names of the channels. Integer channel names are converted to string.
    ref_ch_names : str | list of str, len (n_channels) | None
        The name of the channel used as a reference during the recording. If
        references differed between channels, you may supply a list of
        reference channel names corresponding to each channel in `ch_names`.
        If ``None`` (default), assume that all channels are referenced to a
        common channel that is not further specified (BrainVision default).

        .. note:: The reference channel name specified here does not need to
                  appear in `ch_names`. It is permissible to specify a
                  reference channel that is not present in `data`.
    fname_base : str
        The base name for the output files. Three files will be created
        (*.vhdr*, *.vmrk*, *.eeg*) and all will share this base name.
    folder_out : str
        The folder where output files will be saved. Will be created if it does
        not exist yet.
    overwrite : bool
        Whether or not to overwrite existing files. Defaults to ``False``.
    events : np.ndarray, shape (n_events, {2, 3}) | list of dict, len (n_events) | None
        Events to write in the marker file (*.vmrk*). Defaults to ``None``
        (not writing any events).

        If an array is passed, it must have either two or three columns and
        consist of non-negative integers. The first column is always the
        zero-based *onset* index of each event (corresponding to the
        time dimension of the `data` array). The second column is a number
        associated with the *description* of the event. The (optional) third
        column specifies the *duration* of each event in samples (defaults to
        ``1``). All events are written as *type* "Stimulus" and interpreted
        as relevant to all *channels*. For more fine-grained control over how to
        write events, pass a list of dict as described next.

        If list of dict is passed, each dict in the list corresponds to an
        event and may have the following entries:

            - ``"onset"`` : int
                The zero-based index of the event onset, corresponding to the
                time dimension of the `data` array.
            - ``"duration"`` : int
                The duration of the event in samples (defaults to ``1``).
            - ``"description"`` : str | int
                The description of the event. Must be a non-negative int when
                `type` (see below) is either ``"Stimulus"`` or ``"Response"``, and may
                be a str when `type` is ``"Comment"``.
            - ``"type"`` : str
                The type of the event, must be one of ``{"Stimulus", "Response",
                "Comment"}`` (defaults to ``"Stimulus"``). Additional types like
                the known BrainVision types ``"New Segment"``, ``"SyncStatus"``, etc.
                are currently not supported.
            - ``"channels"`` : str | list of {str | int}
                The channels that are impacted by the event. Can be ``"all"``
                (reflecting all channels), or a channel name, or a list of
                channel names. An empty list means the same as ``"all"``.
                Integer channel names are converted to strings, as in the
                `ch_names` parameter. Defaults to ``"all"``.

        Note that ``onset`` and ``description`` MUST be specified in each
        dict.

        .. note:: When specifying more than one but less than "all" channels
                  that are impacted by an event, ``pybv`` will write the same
                  event for as many times as channels are specified (see
                  :gh:`77` for a discussion). This is valid according to the
                  BrainVision specification, however for maximum compatibility
                  with other BrainVision readers, we do not (yet) recommend
                  using this feature.

    resolution : float | np.ndarray, shape (n_channels,)
        The resolution in `unit` in which you'd like the data to be stored. If
        float, the same resolution is applied to all channels. If array with
        n_channels elements, each channel is scaled with its own corresponding
        resolution from the array. Note that `resolution` is applied on top
        of the default resolution that a data format (see `fmt`) has. For
        example, the ``"binary_int16"`` format by design has no floating point
        support, but when scaling the data in µV for ``0.1`` resolution (default),
        accurate writing for all values >= 0.1 µV is guaranteed. In contrast,
        the ``"binary_float32"`` format by design already supports floating points
        up to 1e-6 resolution, and writing data in µV with 0.1 resolution
        will thus guarantee accurate writing for all values >= 1e-7 µV
        (``1e-6 * 0.1``).
    unit : str | list of str
        The unit of the exported data. This can be one of ``"V"``, ``"mV"``, ``"µV"``
        (or equivalently ``"uV"``) , or ``"nV"``, which will scale the data
        accordingly. Defaults to ``"µV"``. Can also be a list of units with one unit
        per channel. Non-voltage channels are stored "as is", for example
        temperature might be available in ``"°C"``, which ``pybv`` will not scale.
    fmt : str
        Binary format the data should be written as. Valid choices are
        ``"binary_float32"`` (default) and ``"binary_int16"``.
    meas_date : datetime.datetime | str | None
        The measurement date specified as a :class:`datetime.datetime` object.
        Alternatively, can be a str in the format "YYYYMMDDhhmmssuuuuuu"
        ("u" stands for microseconds). Note that setting a measurement date
        implies that one additional event is created in the *.vmrk* file. To
        prevent this, set this parameter to ``None`` (default).

    Notes
    -----
    iEEG/EEG/MEG data is assumed to be in V, and ``pybv`` will scale these data
    to µV by default. Any unit besides µV is officially unsupported in the
    BrainVision specification. However, if one specifies other voltage units
    such as mV or nV, we will still scale the signals accordingly in the
    exported file. We will also write channels with non-voltage units such as
    °C as is (without scaling). For maximum compatibility, all signals
    should be written as µV.

    When passing a list of dict to `events`, the event ``type`` that can be passed
    is currently limited to one of ``{"Stimulus", "Response", "Comment"}``. The
    BrainVision specification itself does not limit event types, and future
    extensions of ``pybv`` may permit additional or even arbitrary event types.

    References
    ----------
    .. [1] https://www.brainproducts.com/support-resources/brainvision-core-data-format-1-0/

    Examples
    --------
    >>> data = np.random.random((3, 5))
    >>> # write data with varying units
    ... # Note channels A1 and A2 are expected to be in volt and will get
    ... # rescaled to µV and mV respectively.
    ... # TEMP is expected to be in some other unit (i.e., NOT volt), and
    ... # will not get scaled (it is written "as is")
    ... write_brainvision(data=data, sfreq=1, ch_names=["A1", "A2", "TEMP"],
    ...                   folder_out="./",
    ...                   fname_base="pybv_test_file",
    ...                   unit=["µV", "mV", "°C"])
    >>> # remove the files
    >>> for ext in [".vhdr", ".vmrk", ".eeg"]:
    ...     os.remove("pybv_test_file" + ext)
    """  # noqa: E501
    # Input checks
    if not isinstance(data, np.ndarray):
        raise ValueError(f"data must be np.ndarray, but found: {type(data)}")

    if not data.ndim == 2:
        raise ValueError("data must be 2D: shape (n_channels, n_times), "
                         f"but found {data.ndim}")

    if not isinstance(overwrite, bool):
        raise ValueError("overwrite must be a boolean (True or False).")

    nchan = len(ch_names)
    for ch in ch_names:
        if not isinstance(ch, (str, int)):
            raise ValueError("ch_names must be a list of str or list of int.")
    ch_names = [str(ch) for ch in ch_names]

    if len(data) != nchan:
        raise ValueError(f"Number of channels in data ({len(data)}) does not "
                         f"match number of channel names ({len(ch_names)})")

    if len(set(ch_names)) != nchan:
        raise ValueError("Channel names must be unique, found duplicate name.")

    events = _chk_events(events, ch_names, data.shape[1])

    # Ensure we have a list of strings as reference channel names
    if ref_ch_names is None:
        ref_ch_names = [''] * nchan  # common but unspecified reference
    elif isinstance(ref_ch_names, str):
        ref_ch_names = [ref_ch_names] * nchan
    else:
        if "" in ref_ch_names:
            msg = (f"ref_ch_names contains an empty string: {ref_ch_names}\n"
                   f"Empty strings are reserved values and not permitted "
                   f"as reference channel names.")
            raise ValueError(msg)
        ref_ch_names = [str(ref_ch_name) for ref_ch_name in ref_ch_names]

    if len(ref_ch_names) != nchan:
        raise ValueError(
            f'The number of reference channel names ({len(ref_ch_names)})'
            f'must match the number of channels in your data ({nchan})'
        )

    # ensure ref chs that are in data are zero
    for ref_ch_name in list(set(ref_ch_names) & set(ch_names)):
        if not np.allclose(data[ch_names.index(ref_ch_name), :], 0):
            raise ValueError(
                f"The provided data for the reference channel "
                f"{ref_ch_name} does not appear to be zero across "
                f"all time points. This indicates that this channel "
                f"either did not serve as a reference during the recording, "
                f"or the data has been altered since. Please either pick a "
                f"different reference channel, or omit the "
                f"ref_ch_name parameter."
            )

    if not isinstance(sfreq, (int, float)):
        raise ValueError("sfreq must be one of (float | int)")
    sfreq = float(sfreq)

    resolution = np.atleast_1d(resolution)
    if not np.issubdtype(resolution.dtype, np.number):
        raise ValueError(f"Resolution should be numeric, is {resolution.dtype}")

    if resolution.shape != (1,) and resolution.shape != (nchan,):
        raise ValueError("Resolution should be one or n_channels floats")

    if np.any(resolution <= 0):
        raise ValueError("Resolution should be > 0")

    # check unit is single str
    if isinstance(unit, str):
        # convert unit to list, assuming all units are the same
        unit = [unit] * nchan
    if len(unit) != nchan:
        raise ValueError(f"Number of channels in unit ({len(unit)}) does not "
                         f"match number of channel names ({nchan})")
    units = unit

    # check units for compatibility with greek lettering
    show_warning = False
    for idx, unit in enumerate(units):
        # Greek mu μ (U+03BC)
        if unit == 'μV' or unit == 'uV':
            unit = 'µV'  # micro symbol µ (U+00B5)
            units[idx] = unit
            show_warning = True

    # only show the warning once if a greek letter was encountered
    if show_warning:
        warn(
            f"Encountered small Greek letter mu 'μ' or 'u' in unit: {unit}. "
            f"Converting to micro sign 'µ'."
        )

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

    # Create output file names/paths, checking if they already exist
    folder_out_created = not op.exists(folder_out)
    os.makedirs(folder_out, exist_ok=True)
    eeg_fname = op.join(folder_out, fname_base + '.eeg')
    vmrk_fname = op.join(folder_out, fname_base + '.vmrk')
    vhdr_fname = op.join(folder_out, fname_base + '.vhdr')
    for fname in (eeg_fname, vmrk_fname, vhdr_fname):
        if op.exists(fname) and not overwrite:
            raise IOError(f"File already exists: {fname}.\n"
                          f"Consider setting overwrite=True.")

    # Write output files, but delete everything if we come across an error
    try:

        _write_bveeg_file(eeg_fname, data, orientation='multiplexed',
                          format=fmt, resolution=resolution, units=units)
        _write_vmrk_file(vmrk_fname, eeg_fname, events, meas_date)
        _write_vhdr_file(vhdr_fname=vhdr_fname, vmrk_fname=vmrk_fname,
                         eeg_fname=eeg_fname, data=data, sfreq=sfreq,
                         ch_names=ch_names, ref_ch_names=ref_ch_names,
                         orientation='multiplexed',
                         format=fmt, resolution=resolution, units=units)
    except ValueError:
        if folder_out_created:
            # if this is a new folder, remove everything
            shutil.rmtree(folder_out)
        else:
            # else, only remove the files we might have created
            for fname in (eeg_fname, vmrk_fname, vhdr_fname):
                if op.exists(fname):  # pragma: no cover
                    os.remove(fname)

        raise


def _chk_events(events, ch_names, n_times):
    """Check that the events parameter is as expected.

    This function will always return `events` as a list of dicts.
    If `events` is ``None``, it will be an empty list.
    If `events` is a list of dict, it will add missing keys to each dict with
    default values, and it will -- for each ith event -- turn ``events[i]["channels"]``
    into a list of 1-based channel name indices, where ``0`` equals ``"all"``.
    Event descriptions for ``"Stimulus"`` and ``"Response"`` will be reformatted to
    a str of the format ``"S{:>n}"`` (or with a leading ``"R"`` for ``"Response"``),
    where ``n`` is determined by the description with the most digits (minimum 3).
    For each ith event, the onset (``events[i]["onset"]``) will be incremented by 1
    to comply with the 1-based indexing used in BrainVision marker files (*.vmrk*).

    Parameters
    ----------
    events : np.ndarray, shape (n_events, {2, 3}) | list of dict, len (n_events) | None
        The events parameter as passed to :func:`pybv.write_brainvision`.
    ch_names : list of str, len (n_channels)
        The channel names, preprocessed in :func:`pybv.write_brainvision`.
    n_times : int
        The length of the data in samples.

    Returns
    -------
    events_out : list of dict, len (n_events)
        The preprocessed events, always provided as list of dict.
    """
    if not isinstance(events, (type(None), np.ndarray, list)):
        raise ValueError("events must be an array, a list of dict, or None")

    # validate input: None
    if isinstance(events, type(None)):
        events_out = []

    # default events
    # NOTE: using "ch_names" as default for channels translates directly
    #       into "all" but is robust with respect to channels named "all"
    event_defaults = dict(duration=1, type="Stimulus", channels=ch_names)

    # validate input: ndarray
    if isinstance(events, np.ndarray):
        if events.ndim != 2:
            raise ValueError(f"When array, events must be 2D, but got {events.ndim}")
        if events.shape[1] not in (2, 3):
            raise ValueError("When array, events must have 2 or 3 columns, "
                             f"but got: {events.shape[1]}")
        if not all([np.issubdtype(i, np.integer) for i in events.flat]):
            raise ValueError("When array, all entries in events must be int, but "
                             "found other types")

        # convert array to list of dict
        durations = np.ones(events.shape[0], dtype=int) * event_defaults["duration"]
        if events.shape[1] == 3:
            durations = events[:, -1]
        events_out = []
        for irow, row in enumerate(events[:, 0:2]):
            events_out.append(dict(onset=int(row[0]),
                                   duration=int(durations[irow]),
                                   description=int(row[1]),
                                   type=event_defaults["type"],
                                   channels=event_defaults["channels"]))

    # validate input: list of dict
    if isinstance(events, list):
        # we must not edit the original parameter
        events_out = [copy.deepcopy(i) for i in events]

    # now always list of dict: do full validation
    for event in events_out:
        # each item must be dict
        if not isinstance(event, dict):
            raise ValueError("When list, events must be a list of dict, but found "
                             "non-dict element in list")

    for iev, event in enumerate(events_out):
        # required keys
        for required_key in ["onset", "description"]:
            if required_key not in event:
                raise ValueError("When list of dict, each dict in events must have "
                                 "the keys 'onset' and 'description'")

        # populate keys with default if missing (in-place)
        for optional_key, default in event_defaults.items():
            event[optional_key] = event.get(optional_key, default)

        # validate key types
        # `onset`, `duration`
        for key in ["onset", "duration"]:
            if not isinstance(event[key], (int, np.integer)):
                raise ValueError(f"events: `{key}` must be int")

        if not (0 <= event["onset"] < n_times):
            raise ValueError("events: at least one onset sample is not in range of "
                             f"data (0-{n_times-1})")

        if event["duration"] < 0:
            raise ValueError("events: at least one duration is negative. Durations "
                             "must be >= 0 samples.")

        if not (0 <= event["onset"] + event["duration"] <= n_times):
            raise ValueError("events: at least one event has a duration that exceeds "
                             f"the range of data (0-{n_times-1})")

        event["onset"] = event["onset"] + 1  # VMRK uses 1-based indexing

        # `type`
        event_types = ["Stimulus", "Response", "Comment"]
        if event["type"] not in event_types:
            raise ValueError(f"events: `type` must be one of {event_types}")

        # `description`
        if event["type"] in ["Stimulus", "Response"]:
            if not isinstance(event["description"], int):
                raise ValueError(f"events: when `type` is {event['type']}, "
                                 "`description` must be non-negative int")

            if event["description"] < 0:
                raise ValueError(f"events: when `type` is {event['type']}, "
                                 "descriptions must be non-negative ints.")

            # NOTE: We format 1 -> "S  1", 10 -> "S 10", 100 -> "S100", etc.,
            # https://github.com/bids-standard/pybv/issues/24#issuecomment-512746677
            if iev == 0:
                max_event_descr = max([1] + [ev["description"]
                                      for ev in events_out
                                      if isinstance(ev["description"], int)])
            twidth = max(3, int(np.ceil(np.log10(max_event_descr))))
            tformat = event["type"][0] + '{:>' + str(twidth) + '}'
            event["description"] = tformat.format(event["description"])

        else:
            assert event["type"] == "Comment"
            if not isinstance(event["description"], (int, str)):
                raise ValueError(f"events: when `type` is {event['type']}, "
                                 "`description` must be str or int")
            event["description"] = str(event["description"])

        # `channels`
        # "all" becomes ch_names (list of all channel names)
        # single str 'ch_name' becomes [ch_name]
        if not isinstance(event["channels"], (list, str)):
            raise ValueError("events: `channels` must be str or list of str")

        if isinstance(event["channels"], str):
            if event["channels"] == "all":
                if "all" in ch_names:
                    raise ValueError(
                        "Found channel named 'all'. Your `channels` specification in "
                        "events is also 'all'. This is ambiguous, because 'all' is a "
                        "reserved keyword. Either rename the channel called 'all', "
                        "or explicitly list all ch_names in `channels` in each event "
                        "instead of using 'all'.")
                event["channels"] = ch_names
            else:
                event["channels"] = [event["channels"]]

        # now channels is a list
        for ch in event["channels"]:
            if not isinstance(ch, (str, int)):
                raise ValueError("events: `channels` must be list of str or list of "
                                 "int corresponding to ch_names")

            if str(ch) not in ch_names:
                raise ValueError(
                    f"events: found channel name that is not present in the data: {ch}"
                    )

        # check for duplicates
        event["channels"] = [str(ch) for ch in event["channels"]]
        if len(set(event["channels"])) != len(event["channels"]):
            raise ValueError("events: found duplicate channel names")

        # warn if more than one but less than all channels are specified
        # (experimental feature)
        if len(event["channels"]) > 1 and len(event["channels"]) < len(ch_names):
            warn("events: you specified at least one event that impacts more "
                 "than one but less than all channels in the data. "
                 "Such events will be written to .vmrk for as many times as "
                 "channels are specified.\n\n"
                 "This feature may not be supported by all BrainVision readers.")

        # convert channels to indices (1-based, 0="all")
        ch_idxs = [ch_names.index(ch) + 1 for ch in event["channels"]]
        if set(ch_idxs) == {i + 1 for i in range(len(ch_names))}:
            ch_idxs = [0]
        elif len(ch_idxs) == 0:
            # if not related to any channel: same as related to all channels
            ch_idxs = [0]
        event["channels"] = sorted(ch_idxs)

    return events_out


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
                  f'supported orientations are: {", ".join(SUPPORTED_ORIENTS)}')
        raise ValueError(errmsg)
    return orientation == 'multiplexed'


def _write_vmrk_file(vmrk_fname, eeg_fname, events, meas_date):
    """Write BrainvVision marker file."""
    with open(vmrk_fname, 'w', encoding='utf-8') as fout:
        print('Brain Vision Data Exchange Marker File, Version 1.0', file=fout)
        print(f'; Exported using pybv {__version__}', file=fout)
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
        print(r'; Commas in type or description text are coded as "\1".', file=fout)
        if meas_date is not None:
            print(f'Mk1=New Segment,,1,1,0,{meas_date}', file=fout)

        iev = 1 if meas_date is None else 2
        for ev in events:

            # Write event once for each channel that this event is relevant for
            # https://github.com/bids-standard/pybv/pull/77
            for ch in ev["channels"]:
                print(f"Mk{iev}={ev['type']},{ev['description']},{ev['onset']},{ev['duration']},{ch}", file=fout)  # noqa: E501
                iev += 1


def _scale_data_to_unit(data, units):
    """Scale `data` in Volts to `data` in `units`."""
    # only µV is supported by the BrainVision specs, but we support additional
    # voltage prefixes (e.g., V, mV, nV); if such voltage units are used, we
    # issue a warning
    voltage_units = set()

    # similar to voltages other than µV, we also support arbitrary units, but
    # since these are not supported by the BrainVision specs we issue a warning
    # related signals
    non_voltage_units = set()

    # create a vector to multiply with to play nice with numpy
    scales = np.zeros((len(units), 1))
    for idx, unit in enumerate(units):
        scale = SUPPORTED_VOLTAGE_SCALINGS.get(unit, None)
        # unless the unit is 'µV', it is not supported by the specs
        if scale is not None and unit != 'µV':
            voltage_units.add(unit)
        elif scale is None:  # if not voltage unit at all, then don't scale
            non_voltage_units.add(unit)
            scale = 1
        scales[idx] = scale

    if len(voltage_units) > 0:
        msg = (f'Encountered unsupported voltage units: '
               f'{", ".join(voltage_units)}\n'
               f'We will scale the data appropriately, but for maximum '
               f'compatibility you should use µV for all channels.')
        warn(msg)

    if len(non_voltage_units) > 0:
        msg = (f'Encountered unsupported non-voltage units: '
               f'{", ".join(non_voltage_units)}\n'
               f'Note that the BrainVision format specification supports only '
               f'µV.')
        warn(msg)
    return data * scales


def _write_vhdr_file(*, vhdr_fname, vmrk_fname, eeg_fname, data, sfreq,
                     ch_names, ref_ch_names, orientation, format, resolution,
                     units):
    """Write BrainvVision header file."""
    bvfmt, _ = _chk_fmt(format)

    multiplexed = _chk_multiplexed(orientation)

    with open(vhdr_fname, 'w', encoding='utf-8') as fout:
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
            print('; Data orientation: MULTIPLEXED=ch1,pt1, ch2,pt1 ...', file=fout)
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
        print('; <Resolution in "Unit">,<Unit>, Future extensions..', file=fout)
        print('; Fields are delimited by commas, some fields might be omitted (empty).', file=fout)  # noqa: E501
        print(r'; Commas in channel names are coded as "\1".', file=fout)

        nchan = len(ch_names)
        # broadcast to nchan elements if necessary
        resolutions = resolution * np.ones((nchan,))

        for i in range(nchan):
            # take care of commas in the channel names
            _ch_name = ch_names[i].replace(',', r'\1')
            _ref_ch_name = ref_ch_names[i].replace(',', r'\1')

            resolution = np.format_float_positional(resolutions[i], trim="-")
            unit = units[i]
            print(f'Ch{i + 1}={_ch_name},{_ref_ch_name},{resolution},{unit}',
                  file=fout)

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


def _write_bveeg_file(eeg_fname, data, orientation, format, resolution, units):
    """Write BrainVision data file."""
    # check the orientation and format
    _chk_multiplexed(orientation)
    _, dtype = _chk_fmt(format)

    # convert the data to the desired unit
    data = _scale_data_to_unit(data, units)

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
               f"the desired resolution{mod} and units ('{units}').")
        if format == "binary_int16":
            msg += "\nPlease consider writing using 'binary_float32' format."
        raise ValueError(msg)
    data = data.astype(dtype=dtype)

    # We always write data as little-endian without BOM
    # `data` is already in native byte order due to numpy operations that
    # result in copies of the `data` array (see above)
    assert data.dtype.byteorder == "="

    # swap bytes if system architecture is big-endian
    if sys.byteorder == "big":  # pragma: no cover
        data = data.byteswap()

    # Save to binary
    data.ravel(order='F').tofile(eeg_fname)
