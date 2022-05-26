"""Use pybv to export data from different software packages to BrainVision."""

from pathlib import Path

from pybv import write_brainvision


def _export_mne_raw(*, raw, fname, overwrite=False):
    """Export raw data from MNE-Python.

    Parameters
    ----------
    raw : mne.io.Raw
        The raw data to export.
    fname : str
        The name of the file where raw data will be exported to. Must end with ".vhdr",
        and accompanying ".vmrk" and ".eeg" files will be written inside the same
        directory.
    overwrite: bool
        Whether or not to overwrite existing data. Default to False
    """
    data = raw.get_data()
    sfreq = raw.info["sfreq"]
    ch_names = raw.ch_names
    fname = Path(fname)
    folder_out = fname.parents()[0]
    fname_base = fname.name
    write_brainvision(data=data, sfreq=sfreq, ch_names=ch_names, fname_base=fname_base,
                      folder_out=folder_out, overwrite=overwrite)
