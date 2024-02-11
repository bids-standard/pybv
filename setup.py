"""Setup pybv."""

import os
import sys

from setuptools import setup

# Give setuptools a hint to complain if it's too old a version
SETUP_REQUIRES = ["setuptools >= 46.4.0"]
# This enables setuptools to install wheel on-the-fly
SETUP_REQUIRES += ["wheel"] if "bdist_wheel" in sys.argv else []

# get the version
version = None
with open(os.path.join("pybv", "__init__.py")) as fid:
    for line in (line.strip() for line in fid):
        if line.startswith("__version__"):
            version_str = line.split("=")[1].strip()
            # strip " or ', depending on what was used
            version = version_str.strip(version_str[0])
            break
if version is None:
    raise RuntimeError("Could not determine version from __init__.py")

if __name__ == "__main__":
    setup(
        version=version,
        setup_requires=SETUP_REQUIRES,
    )
