"""Test export from software packages to BrainVision via pybv."""

import mne
import numpy as np
import pytest
from mne.io.constants import FIFF

from pybv._export import _export_mne_raw


@pytest.mark.filterwarnings("ignore:.*non-voltage units.*n/a:UserWarning:pybv")
def test_export_mne_raw(tmpdir):
    """Test mne export."""
    # Create a Raw object
    sfreq = 250.0

    ch_names = ["Fp1", "Fp2", "Fz", "Cz", "Pz", "O1", "O2", "analog", "temp"]
    ch_types = ["eeg"] * (len(ch_names) - 2) + ["misc"] * 2

    info = mne.create_info(ch_names, ch_types=ch_types, sfreq=sfreq)

    info.set_montage("standard_1020")

    data = np.random.randn(len(ch_names), int(sfreq * 100))

    raw = mne.io.RawArray(data, info)

    # Make a fake channel in °C
    raw.info["chs"][-1]["unit"] = FIFF.FIFF_UNIT_CEL

    annots = mne.Annotations(
        onset=[3, 13, 30, 70, 90],  # seconds
        duration=[1, 1, 0.5, 0.25, 9],  # seconds
        description=[
            "Stimulus/S  1",
            "Stimulus/S2.50",
            "Response/R101",
            "Look at this",
            "Comment/And at this",
        ],
        ch_names=[(), (), (), ("Fp1",), ("Fp1", "Fp2")],
    )
    raw.set_annotations(annots)

    # export to BrainVision
    fname = tmpdir / "mne_export.vhdr"
    with pytest.warns(RuntimeWarning, match="'double' .* Converting to float32"):
        _export_mne_raw(raw=raw, fname=fname)

    with pytest.raises(ValueError, match="`fname` must have the '.vhdr'"):
        _export_mne_raw(raw=raw, fname=str(fname).replace(".vhdr", ".eeg.tar.gz"))

    # test overwrite
    with pytest.warns():
        _export_mne_raw(raw=raw, fname=fname, overwrite=True)

    # try once more with "single" data and mne events
    fname = tmpdir / "mne_export_events.vhdr"
    raw = mne.io.RawArray(data.astype(np.single), info)
    raw.orig_format = "single"
    events = np.vstack(
        [
            np.linspace(0, sfreq * 00, 10).astype(int),
            np.zeros(10).astype(int),
            np.arange(1, 11).astype(int),
        ]
    ).T
    _export_mne_raw(raw=raw, fname=fname, events=events)
    raw_read = mne.io.read_raw_brainvision(fname)
    np.testing.assert_allclose(raw_read.get_data(), raw.get_data())
