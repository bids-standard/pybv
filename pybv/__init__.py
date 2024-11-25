"""A lightweight I/O utility for the BrainVision data format."""

# Authors: pybv developers
# SPDX-License-Identifier: BSD-3-Clause

from .io import write_brainvision

__all__ = ["write_brainvision"]

try:
    from importlib.metadata import version

    __version__ = version("pybv")
except Exception:
    __version__ = "0.0.0"
