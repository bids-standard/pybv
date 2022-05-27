"""Test export from software packages to BrainVision via pybv."""

import mne
import numpy as np
import pytest

from pybv._export import _export_mne_raw


def test_export_mne_raw(tmpdir):
    """Test mne export."""
    # Create a Raw object
    sfreq = 250.

    ch_names = ['Fp1', 'Fp2', 'Fz', 'Cz', 'Pz', 'O1', 'O2']
    ch_types = ['eeg'] * len(ch_names)

    info = mne.create_info(ch_names, ch_types=ch_types, sfreq=sfreq)

    info.set_montage('standard_1020')

    data = np.random.randn(len(ch_names), int(sfreq * 100))

    raw = mne.io.RawArray(data, info)

    # export to BrainVision
    fname = tmpdir / "mne_export.vhdr"
    with pytest.warns(RuntimeWarning, match="'double' .* Converting to float32"):
        _export_mne_raw(raw=raw, fname=fname)
