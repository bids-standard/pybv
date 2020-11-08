:orphan:

.. _changelog:

=========
Changelog
=========

Here we list a changelog of pybv.

.. contents:: Contents
   :local:
   :depth: 1

Current
=======

Changelog
~~~~~~~~~
- Passing a "greek small letter mu" to the ``unit`` parameter in :func:`pybv.write_brainvision` instead of a "micro sign" is now permitted, because the former will be automatically convert to the latter, by `Stefan Appelhoff`_ (`#47 <https://github.com/bids-standard/pybv/pull/47>`_)

Bug
~~~
- Fix bug where :func:`pybv.write_brainvision` did not properly deal with commas in channel names and non-numeric events, by `Stefan Appelhoff`_ (`#53 <https://github.com/bids-standard/pybv/pull/53>`_)
- :func:`pybv.write_brainvision` now properly handles sampling frequencies that are not multiples of 10 (even floats), by `Clemens Brunner`_ (`#59 <https://github.com/bids-standard/pybv/pull/59>`_)
- Fix bug where :func:`pybv.write_brainvision` would write a different resolution to the ``vhdr`` file than specified with the ``resolution`` parameter. Note that this did *not* affect the roundtrip accuracy of the written data, because of internal scaling of the data, by `Stefan Appelhoff`_ (`#58 <https://github.com/bids-standard/pybv/pull/58>`_)
- Fix bug where values for the ``resolution`` parameter like ``0.5``, ``0.123``, ``3.143`` were not written with adequate decimal precision in :func:`pybv.write_brainvision`, by `Stefan Appelhoff`_ (`#58 <https://github.com/bids-standard/pybv/pull/58>`_)
- Fix bug where :func:`pybv.write_brainvision` did not warn users that a particular combination of ``fmt``, ``unit``, and ``resolution`` can lead to broken data. For example high resolution µV data in int16 format. In such cases, an error is raised now, by `Stefan Appelhoff`_ (`#62 <https://github.com/bids-standard/pybv/pull/62>`_)

API
~~~
- :func:`pybv.write_brainvision` now accepts keyword arguments only. Positional arguments are no longer allowed, by `Stefan Appelhoff`_ (`#57 <https://github.com/bids-standard/pybv/pull/57>`_)
- In :func:`pybv.write_brainvision`, the ``scale_data`` parameter was removed from :func:`pybv.write_brainvision`, by `Stefan Appelhoff`_ (`#58 <https://github.com/bids-standard/pybv/pull/58>`_)
- In :func:`pybv.write_brainvision`, the ``unit`` parameter no longer accepts an argument ``None`` to automatically determine a unit based on the ``resolution``, by `Stefan Appelhoff`_ (`#58 <https://github.com/bids-standard/pybv/pull/58>`_)

Authors
~~~~~~~
- `Clemens Brunner`_
- `Richard Höchenberger`_
- `Stefan Appelhoff`_

0.3.0
=====

Changelog
~~~~~~~~~
- Add ``unit`` parameter for exporting signals in a specific unit (V, mV, µV or uV, nV), by `Clemens Brunner`_ (`#39 <https://github.com/bids-standard/pybv/pull/39>`_)

API
~~~
- The order of parameters in :func:`pybv.write_brainvision` has changed, by `Clemens Brunner`_ (`#39 <https://github.com/bids-standard/pybv/pull/39>`_)

Authors
~~~~~~~
- `Clemens Brunner`_
- `Stefan Appelhoff`_
- `Tristan Stenner`_

0.2.0
=====

Changelog
~~~~~~~~~
- Add option to disable writing a meas_date event (which is also the new default), by `Clemens Brunner`_ (`#32 <https://github.com/bids-standard/pybv/pull/32>`_)
- Support event durations by passing an (N, 3) array to the events parameter (the third column contains the event durations), by `Clemens Brunner`_ (`#33 <https://github.com/bids-standard/pybv/pull/33>`_)

Authors
~~~~~~~
- `Clemens Brunner`_
- `Stefan Appelhoff`_

0.1.0
=====

Changelog
~~~~~~~~~
- Add measurement date parameter to public API, by `Stefan Appelhoff`_ (`#29 <https://github.com/bids-standard/pybv/pull/29>`_)
- Add binary format parameter to public API, by `Tristan Stenner`_ (`#22 <https://github.com/bids-standard/pybv/pull/22>`_)

Bug
~~~
- fix bug with events indexing. VMRK events are now correctly written with 1-based indexing, by `Stefan Appelhoff`_ (`#29 <https://github.com/bids-standard/pybv/pull/29>`_)
- fix bug with events that only have integer codes of length less than 3, by `Stefan Appelhoff`_ (`#26 <https://github.com/bids-standard/pybv/pull/26>`_)

Authors
~~~~~~~
- `Chris Holdgraf`_
- `Stefan Appelhoff`_
- `Tristan Stenner`_

0.0.2
=====

Changelog
~~~~~~~~~
- Support channel-specific scaling factors, by `Tristan Stenner`_ (`#17 <https://github.com/bids-standard/pybv/pull/17>`_)

Authors
~~~~~~~
- `Chris Holdgraf`_
- `Stefan Appelhoff`_
- `Tristan Stenner`_

0.0.1
=====

Changelog
~~~~~~~~~
- Initial import from philistine package by `Phillip Alday`_ and removing dependency on MNE-Python, by `Chris Holdgraf`_, and `Stefan Appelhoff`_

Authors
~~~~~~~
- `Chris Holdgraf`_
- `Phillip Alday`_
- `Stefan Appelhoff`_
- `Tristan Stenner`_

.. _Chris Holdgraf: https://bids.berkeley.edu/people/chris-holdgraf
.. _Stefan Appelhoff: http://stefanappelhoff.com/
.. _Tristan Stenner: https://github.com/tstenner
.. _Phillip Alday: https://palday.bitbucket.io/
.. _Clemens Brunner: https://cbrnr.github.io/
.. _Richard Höchenberger: https://hoechenberger.net/
