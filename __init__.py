"""
pyemaps package: 
This python package contains python modules that simulates
diffraction over selected crystal:

   1) Dif: Kinematic Diffraction Simulation (free, MIT license)
   2) Bloch: Dynamic Bloch Diffraction Simulation (proprietory, license needed)
   3) crystals: python modules for cystal data class: Crystal

All of the above python modules are based on Fortran application.

More modules are developed in the future.

Usage:
    from pyemaps import dif
    from pyemaps import crystal as cryst


"""
from pyemaps import __config__

from .diffract import dif
from .crystals import Crystal
from .kdiffs import diffPattern as DP
from .kdiffs import Diffraction as DPList
from .kdiffs import DEF_CONTROLS
from .kdiffs import XMAX, YMAX