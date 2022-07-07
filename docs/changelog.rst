:orphan:

=======
Authors
=======

People who contributed to this software across releases (in **alphabetical order**):

- `Adam Li`_
- `Aniket Pradhan`_
- `Chris Holdgraf`_
- `Clemens Brunner`_
- `Phillip Alday`_
- `Pierre Cutellic`_
- `Richard Höchenberger`_
- `Stefan Appelhoff`_
- `Tristan Stenner`_

.. _Chris Holdgraf: https://bids.berkeley.edu/people/chris-holdgraf
.. _Stefan Appelhoff: http://stefanappelhoff.com/
.. _Tristan Stenner: https://github.com/tstenner
.. _Phillip Alday: https://palday.bitbucket.io/
.. _Clemens Brunner: https://cbrnr.github.io/
.. _Richard Höchenberger: https://hoechenberger.net/
.. _Adam Li: https://adam2392.github.io/
.. _Aniket Pradhan: http://home.iiitd.edu.in/~aniket17133/
.. _Pierre Cutellic: https://github.com/compmonks

.. _changelog:

=========
Changelog
=========

Here we list a changelog of pybv.

.. contents:: Contents
   :local:
   :depth: 1

0.7.4 (2022-07-07)
==================

Changelog
~~~~~~~~~
- Events: accept ``description`` label values >= 0 when ``type`` is ``"Stimulus"`` or ``"Response"``, by `Pierre Cutellic`_: (:gh:`95`)
- Events: accept ``duration == 0``, by `Clemens Brunner`_: (:gh:`96`)

0.7.3 (2022-06-04)
==================

Bug
~~~
- Fix in private ``pybv._export`` module: ``durations`` of 1 sample length are fine even if they are at the last data sample, by `Stefan Appelhoff`_: (:gh:`92`)

0.7.2 (2022-06-01)
==================

Bug
~~~
- Fixed that ``raw.annotations`` must take ``raw.first_time`` into account in private ``pybv._export`` module for export to BrainVision from MNE-Python, by `Stefan Appelhoff`_: (:gh:`91`)

0.7.1 (2022-05-28)
==================

Bug
~~~
- Fixed a bug in private ``pybv._export`` module for export to BrainVision from MNE-Python, by `Stefan Appelhoff`_: (:gh:`90`)

0.7.0 (2022-05-28)
==================

Changelog
~~~~~~~~~
- Added an overview table of alternative software for BrainVision data, by `Stefan Appelhoff`_ (:gh:`85`)
- :func:`pybv.write_brainvision` now accepts a list of dict as argument to the ``events`` parameter, allowing for more control over what to write to ``.vmrk``, by `Stefan Appelhoff`_ (:gh:`86`)

0.6.0 (2021-09-29)
==================

Changelog
~~~~~~~~~
- :func:`pybv.write_brainvision` gained a new parameter, ``ref_ch_names``, to specify the reference channels used during recording, by `Richard Höchenberger`_ and `Stefan Appelhoff`_ (:gh:`75`)

API
~~~
- :func:`pybv.write_brainvision` now has an ``overwrite`` parameter that defaults to ``False``, by `Stefan Appelhoff`_ (:gh:`78`)

Bug
~~~
- Fix bug where :func:`pybv.write_brainvision` would write the binary file in big-endian on a big-endian system, by `Aniket Pradhan`_, `Clemens Brunner`_, and `Stefan Appelhoff`_ (:gh:`80`)

0.5.0 (2021-01-03)
==================

Changelog
~~~~~~~~~
- :func:`pybv.write_brainvision` adds support for channels with non-volt units, by `Adam Li`_ (:gh:`66`)
- :func:`pybv.write_brainvision` automatically converts ``uV`` and ``μV`` (Greek μ) to ``µV`` (micro sign µ), by `Adam Li`_ (:gh:`66`)

API
~~~
- The ``unit`` parameter in :func:`pybv.write_brainvision` now accepts a list of units (one unit per channel), by `Adam Li`_ (:gh:`66`)

0.4.0 (2020-11-08)
==================

Changelog
~~~~~~~~~
- Passing a "greek small letter mu" to the ``unit`` parameter in :func:`pybv.write_brainvision` instead of a "micro sign" is now permitted, because the former will be automatically convert to the latter, by `Stefan Appelhoff`_ (:gh:`47`)

Bug
~~~
- Fix bug where :func:`pybv.write_brainvision` did not properly deal with commas in channel names and non-numeric events, by `Stefan Appelhoff`_ (:gh:`53`)
- :func:`pybv.write_brainvision` now properly handles sampling frequencies that are not multiples of 10 (even floats), by `Clemens Brunner`_ (:gh:`59`)
- Fix bug where :func:`pybv.write_brainvision` would write a different resolution to the ``vhdr`` file than specified with the ``resolution`` parameter. Note that this did *not* affect the roundtrip accuracy of the written data, because of internal scaling of the data, by `Stefan Appelhoff`_ (:gh:`58`)
- Fix bug where values for the ``resolution`` parameter like ``0.5``, ``0.123``, ``3.143`` were not written with adequate decimal precision in :func:`pybv.write_brainvision`, by `Stefan Appelhoff`_ (:gh:`58`)
- Fix bug where :func:`pybv.write_brainvision` did not warn users that a particular combination of ``fmt``, ``unit``, and ``resolution`` can lead to broken data. For example high resolution µV data in int16 format. In such cases, an error is raised now, by `Stefan Appelhoff`_ (:gh:`62`)

API
~~~
- :func:`pybv.write_brainvision` now accepts keyword arguments only. Positional arguments are no longer allowed, by `Stefan Appelhoff`_ (:gh:`57`)
- In :func:`pybv.write_brainvision`, the ``scale_data`` parameter was removed from :func:`pybv.write_brainvision`, by `Stefan Appelhoff`_ (:gh:`58`)
- In :func:`pybv.write_brainvision`, the ``unit`` parameter no longer accepts an argument ``None`` to automatically determine a unit based on the ``resolution``, by `Stefan Appelhoff`_ (:gh:`58`)

0.3.0 (2020-04-02)
==================

Changelog
~~~~~~~~~
- Add ``unit`` parameter for exporting signals in a specific unit (V, mV, µV or uV, nV), by `Clemens Brunner`_ (:gh:`39`)

API
~~~
- The order of parameters in :func:`pybv.write_brainvision` has changed, by `Clemens Brunner`_ (:gh:`39`)

0.2.0 (2019-08-26)
==================

Changelog
~~~~~~~~~
- Add option to disable writing a meas_date event (which is also the new default), by `Clemens Brunner`_ (:gh:`32`)
- Support event durations by passing an (N, 3) array to the events parameter (the third column contains the event durations), by `Clemens Brunner`_ (:gh:`33`)

0.1.0 (2019-06-23)
==================

Changelog
~~~~~~~~~
- Add measurement date parameter to public API, by `Stefan Appelhoff`_ (:gh:`29`)
- Add binary format parameter to public API, by `Tristan Stenner`_ (:gh:`22`)

Bug
~~~
- fix bug with events indexing. VMRK events are now correctly written with 1-based indexing, by `Stefan Appelhoff`_ (:gh:`29`)
- fix bug with events that only have integer codes of length less than 3, by `Stefan Appelhoff`_ (:gh:`26`)

0.0.2 (2019-04-28)
==================

Changelog
~~~~~~~~~
- Support channel-specific scaling factors, by `Tristan Stenner`_ (:gh:`17`)

0.0.1 (2018-12-10)
==================

Changelog
~~~~~~~~~
- Initial import from `philistine <https://pypi.org/project/philistine/>`_ package by `Phillip Alday`_
  and removing dependency on MNE-Python, by `Chris Holdgraf`_, and `Stefan Appelhoff`_
