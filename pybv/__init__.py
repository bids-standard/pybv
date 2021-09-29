# -*- coding: utf-8 -*-
"""A lightweight I/O utility for the BrainVision data format."""

# Authors: Phillip Alday <phillip.alday@unisa.edu.au>
#          Chris Holdgraf <choldgraf@berkeley.edu>
#          Stefan Appelhoff <stefan.appelhoff@mailbox.org>
#          Tristan Stenner <stenner@med-psych.uni-kiel.de>
#          Clemens Brunner <clemens.brunner@gmail.com>
#          Richard Höchenberger <richard.hoechenberger@gmail.com>
#          Adam Li <adam2392@gmail.com>
#
# License: BSD-3-Clause

__version__ = '0.6.0'
from .io import write_brainvision

__all__ = ['write_brainvision']
