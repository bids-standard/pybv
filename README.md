# pyBV

A lightweight I/O utility for the BrainVision data format, written in Python.

**See the [pybv documentation for usage information](https://pybv.readthedocs.io)**

**ALPHA SOFTWARE**. This package is currently in its early stages of iteration.
It may change both its internals or its user-facing API in the near future. Any
feedback and ideas on how to improve either of these is more than welcome!

BrainVision is the name of a file format commonly used for storing
electroencephalography (EEG) data. Originally, it was put forward by the
company [Brain Products](https://www.brainproducts.com/), however the
simplicity of the format has allowed for a diversity of tools reading from and
writing to the format.
 The format consists of three separate files:
1. A text header file (`.vhdr`) containing meta data
2. A text marker file (`.vmrk`) containing information about events in the data
3. A binary data file (`.eeg`) containing the voltage values of the EEG
 Both text files are based on the
[Microsoft Windows INI format](https://en.wikipedia.org/wiki/INI_file)
consisting of:
- sections marked as `[square brackets]`
- comments marked as `; comment`
- key-value pairs marked as `key=value`
 A documentation for core BrainVision file format is provided by Brain Products.
You can [view the specification here](/docs/BrainVisionCoreFileFormat.pdf).


## Acknowledgements

This package was originally adapted from [palday](https://github.com/palday)'s
[Philistine package](https://gitlab.com/palday/philistine). It copies much of
the BrainVision exporting code, removes the dependence on MNE, and focuses the
code around BrainVision I/O.