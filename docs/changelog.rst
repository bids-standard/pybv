:orphan:

.. _changelog:

=========
Changelog
=========

Here we list a changelog of pybv.

.. contents:: Contents
   :local:
   :depth: 2

Current
=======

0.1.0
=====

Changelog
~~~~~~~~~
- Add measurement date parameter to public API, by `Stefan Appelhoff`_ (`#29 <https://github.com/bids-standard/pybv/pull/29>`_)
- Add binary format parameter to public API by `Tristan Stenner`_ (`#22 <https://github.com/bids-standard/pybv/pull/22>`_)

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
- Support channel-specific scaling factors by `Tristan Stenner`_ (`#17 <https://github.com/bids-standard/pybv/pull/17>`_)

Authors
~~~~~~~
- `Chris Holdgraf`_
- `Stefan Appelhoff`_
- `Tristan Stenner`_

0.0.1
=====

Changelog
~~~~~~~~~
- Initial import from philistine package by `Phillip Alday`_ and removing dependency on MNE-Python, by `Chris Holdgraf`_ and `Stefan Appelhoff`_

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
