:orphan:

.. _changelog:

=========
Changelog
=========

Here we list a changelog of pybv.

.. contents:: Contents
   :local:
   :depth: 2

current
=======

Changelog
~~~~~~~~~
Add measurement date parameter to public API, by `Stefan Appelhoff`_ (`#29 <https://github.com/bids-standard/pybv/pull/29>`_)
Add binary format parameter to public API by `Tristan Stenner`_ (`#22 <https://github.com/bids-standard/pybv/pull/22>`_)

Bug
~~~
fix bug with events indexing. VMRK events are now correctly written with 1-based indexing, by `Stefan Appelhoff`_ (`#29 <https://github.com/bids-standard/pybv/pull/29>`_)
fix bug with events that only have integer codes of length less than 3, by `Stefan Appelhoff`_ (`#26 <https://github.com/bids-standard/pybv/pull/26>`_)

0.0.2
=====

Changelog
~~~~~~~~~
Support channel-specific scaling factors by `Tristan Stenner`_ (`#17 <https://github.com/bids-standard/pybv/pull/17>`_)

0.0.1
=====

Changelog
~~~~~~~~~
Initial import from palday's philistine package and removing dependency on MNE-Python, by `Chris Holdgraf`_ and `Stefan Appelhoff`_

.. _Chris Holdgraf: https://bids.berkeley.edu/people/chris-holdgraf
.. _Stefan Appelhoff: http://stefanappelhoff.com/
.. _Tristan Stenner: https://github.com/tstenner
