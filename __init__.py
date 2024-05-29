
"""
This file is part of pyemaps

pyemaps is free software for non-comercial use: you can 
redistribute it and/or modify it under the terms of the GNU General 
Public License as published by the Free Software Foundation, either 
version 3 of the License, or (at your option) any later version.

pyemaps is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pyemaps.  If not, see <https://www.gnu.org/licenses/>.

Contact supprort@emlabsoftware.com for any questions and comments.

```

Author:     EMLab Solutions, Inc.
Date:       May 07, 2022    
"""


from . import __config__

#--------------from diffraction extension module------------------------
try:
    from emaps import dif
except ImportError:
    raise Exception('No diffraction module found')
else:
    PKG_TYPE = dif.get_pkgtype()
#--------------defaults from the backend for simulation control parameters
    # Default excitation from backend: DEF_EXCITATION (low, high)
    # Default gmax from backend: DEF_GMAX  
    # Default bmin from backend: DEF_BMIN  
    # Default intensity from backend: DEF_INTENSITY (low, high)
    # Default gctl from backend: DEF_GCTL  
    # Default zctl from backend: DEF_ZCTL
#------------------------------------------------------------------------
    (sgmn, 
     sgmx, 
     DEF_GMAX, 
     DEF_BMIN, 
     intc, 
     intz, 
     DEF_GCTL, 
     DEF_ZCTL, 
     DEF_MODE) = dif.get_sim_defs()

    DEF_EXCITATION= (sgmn, sgmx)
    DEF_INTENSITY = (intz, intc)
    XMAX = 75  # set in dif backend as constant for now, may need to change to variable set by users
    YMAX = 75  # set in dif backend, same as the above

#-------------- defaults from backend for sample controls---------------
    # Default starting zone setting: DEF_ZONE
    # Default tilt: DEF_TILT (x, y)
    # Default xaxis: DEF_XAXIS
#------------------------------------------------------------------------
    zn0, zn1, zn2, tlt0, xax0 = dif.get_sam_defs()
    DEF_ZONE= (zn0, zn1, zn2)
    DEF_TILT =(tlt0, tlt0)
    DEF_XAXIS = (xax0, xax0, xax0)

#-------------- defaults from backend for microscope controls-----------
    # Default hight voltage setting: DEF_KV
    # Default camera length: DEF_CL (x, y)
    # Default deflection: DEF_DEFL
    # Default normal disk size: DEF_NORM_DSIZE
    # Default CBED disk size: DEF_CBED_DS
    # Default disk size: DEF_DS_LIMITS (min, max)
#------------------------------------------------------------------------

    DEF_DEFL = (tlt0, tlt0)
    (DEF_CL, 
     DEF_KV, 
     DEF_NORM_DSIZE, 
     DEF_CBED_DSIZE, 
     dmin, 
     dmax) = dif.get_mic_defs()

    DEF_DSIZE_LIMITS = (dmin, dmax)
    
#------------------------Pyemaps Helper Modules---------------------------------

from emaps import spgseek
from emaps import sct

#------------------------Crystal Structure Factor Module------------------------
try:
    from emaps import csf

except ImportError as e:
    pass


#------------------------Powder Diffraction Module------------------------------
try:
    from emaps import powder

except ImportError as e:
    pass

#------------------------Dynamic Diffraction Module----------------------------
try:
    from emaps import bloch
    
except ImportError as e:
    raise Exception('No diffraction module found')
else:

    TY_NORMAL = 0 # Normal Bloch Image type
    TY_LACBED = 1 # Large angle Bloch image type
    th_start, th_end, th_step = bloch.get_sam_defs()
    
    DEF_THICKNESS = (th_start, th_end, th_step)
  
    (DEF_SAMPLING, 
     DEF_PIXSIZE, 
     DEF_DETSIZE, 
     MAX_DEPTH, 
     DEF_OMEGA) = bloch.get_sim_defs()
    DEF_APERTURE = bloch.get_mic_defs()

#------------------------Stereodiagram Module--------------------------------
try:
    from emaps import stereo
    
except ImportError as e:
    raise Exception('No stereo module found')
else:
    pass


#------------------Crystal Constructor Module--------------------------------
try:
    from emaps import mxtal
    
except ImportError as e:
    raise Exception('No mxtal module found')
else:

    ID_MATRIX = [[1,0,0], [0,1,0], [0,0,1]]
    MLEN = 10 
    DEF_TRSHIFT = [0,0,0]
    DEF_CELLBOX = [[0,0,0], [3,3,3]]
    DEF_XZ = [[1,0,0], [0,0,1]]
    DEF_ORSHIFT = [0, 0, 0] # Origin shift
    DEF_LOCASPACE = [0, 0, 0] # location in A Space


# #------------------Diffraction Database Generator - paid package only---------------------------
try:
    from emaps import dpgen
    
except ImportError as e:
    # skip this in free package
    pass


# #------------------Diffraction Pattern Indexing - paid package only---------------------------
#  used only with dpgen module above

try:
    from emaps import ediom
except ImportError:
    pass
else:
    E_INT = ediom.E_INT 
    EM_INT = ediom.EM_INT

    E_FLOAT = ediom.E_FLOAT
    EM_FLOAT = ediom.EM_FLOAT

    E_DOUBLE = ediom.E_DOUBLE
    EM_DOUBLE = ediom.EM_DOUBLE

    MAX_IMAGESIZE = ediom.MAX_IMAGESIZE
    MIN_IMAGESIZE = ediom.MIN_IMAGESIZE
    MAX_IMAGESTACK = ediom.MAX_IMAGESTACK
    MIN_IMAGESTACK = 1
    DEF_FILTER_THRESHOLD = 0.2                       
    DEF_SEARCH_THRESHOLD = 0.825
    DEF_RMIN = 7
    DEF_BOXSIZE = 10
    DEF_CC = ediom.cvar.edc.cc      #default value from backend
    DEF_SIGMA = ediom.cvar.edc.sigma
    DEF_ICENTER = ediom.cvar.edc.get_center()
    DEF_XSCALE = 1
    DEF_TSCALE = 2

    E_SH = 0
    E_RAW = 1
    E_NPY = 2

    # imageloading mode
    EL_ONE = 1  #EDIOM image loading one stack at one time
    EL_MORE = 2 #EDIOM image loading all stacks


#--------------Wrapper classes around diffraction extensions---------------
from .errors import *

#---------Microscope control data classes handling data properties----------
from .emcontrols import EMControl as EMC
from .emcontrols import SIMControl as SIMC

#---------Diffraction classes handling diffraction pattern data-------------
from .kdiffs import diffPattern as DP
from .kdiffs import Diffraction as DPList
from .ddiffs import BlochImgs as BImgList

#--------------Crystal Classes and subclasses-------------------------------
from .crystals import Cell, Atom, SPG, Crystal
try:
    from .kdiffs import XMAX, YMAX
except ImportError as e:
    print(f'Error importing kinematic constants: {e}')

#--------------ediom features -------------------------------
from .stackimg import StackImage

#--------------Pyemaps Display Functions-------------------------------------
from .display import showDif, showBloch, showStereo, plot2Powder
