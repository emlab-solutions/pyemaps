
"""
This file is part of pyemaps
___________________________

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
___________________________

```

Author:     EMLab Solutions, Inc.
Date:       May 07, 2022    
"""


# from pyemaps.test.sanity.em import DEF_NORM_DSIZE, DEF_OMEGA
from . import __config__

#--------------from diffraction extension module------------------------
try:
    from .diffract import dif
except ImportError:
    raise Exception('No diffraction module found')
else:
    # defaults from the backend for simulation control parameters
    # Default excitation from backend: DEF_EXCITATION
    # Default gmax from backend: DEF_GMAX  
    # Default bmin from backend: DEF_BMIN  
    # Default intencity from backend: DEF_INTENCITY
    # Default gctl from backend: DEF_GCTL  
    # Default zctl from backend: DEF_ZCTL
    #  
    sgmn, sgmx, DEF_GMAX, DEF_BMIN, intc, intz, DEF_GCTL, DEF_ZCTL, DEF_MODE = dif.get_sim_defs()

    DEF_EXCITATION= (sgmn, sgmx)
    DEF_INTENCITY = (intc, intz)

    # defaults from backend for sample controls
    # Default starting zone setting: DEF_ZONE
    # Default tilt: DEF_TILT (x, y)
    # Default xaxis: DEF_XAXIS
    zn0, zn1, zn2, tlt0, xax0 = dif.get_sam_defs()
    DEF_ZONE= (zn0, zn1, zn2)
    DEF_TILT =(tlt0, tlt0)
    DEF_XAXIS = (xax0, xax0, xax0)

    # defaults from backend for microscope controls
    # Default hight voltage setting: DEF_KV
    # Default camera length: DEF_CL (x, y)
    # Default deflection: DEF_DEFL
    # Default normal disk size: DEF_NORM_DSIZE
    # Default CBED disk size: DEF_CBED_DS
    # Default disk size: DEF_DS_LIMITS (min, max)
    DEF_DEFL = (tlt0, tlt0)
    DEF_CL, DEF_KV, DEF_NORM_DSIZE, DEF_CBED_DSIZE, dmin, dmax = dif.get_mic_defs()

    DEF_DSIZE_LIMITS = (dmin, dmax)
    # print(f'cl default: {DEF_CL}')
    # print(f'kv default: {DEF_KV}')
    # print(f'norm dsize default: {DEF_NORM_DSIZE}')
    # print(f'cbed dsize default: {DEF_CBED_DSIZE}')
    # print(f'disk limit default: {DEF_DSIZE_LIMITS}')
#CIF & XTL crystal data import dependent modules
#
#
from .spg import spgseek
from .scattering import sct

#--------------optional modules in pyemaps----------------

#fall through if dpgen is not found

try:
    from .diffract import dpgen
except ImportError as e:
    pass 

#fall through if structure factor module is not found
try:
    from .diffract import csf

except ImportError as e:
    pass

#fall through if powder module is not found
try:
    from .diffract import powder

except ImportError as e:
    pass

#fall through if blch module is not found
try:
    from .diffract import bloch
    
except ImportError as e:
    raise Exception('No diffraction module found')
else:
    # defaults sampling setting
    # sample thickness: DEF_THICKNESS (start, end, step)
    th_start, th_end, th_step = bloch.get_sam_defs()
    
    DEF_THICKNESS = (th_start, th_end, th_step)
    # defaults simulation setting
    # sampling: DEF_SAMPLING
    # pixsize: DEF_PIXSIZE
    # detsize: DEF_DETSIZE
    # default image slices number: DEF_DEPTH
    # default omega: DEF_OMEGA
    DEF_SAMPLING, DEF_PIXSIZE, DEF_DETSIZE, MAX_DEPTH, DEF_OMEGA = bloch.get_sim_defs()
    # Microoscope setting default
    DEF_APERTURE = bloch.get_mic_defs()

    
#--------------Wrapper classes around diffraction extensions---------------
from .errors import *

# from .crystals import Crystal

#Microscope control data classes handling data properties
from .emcontrols import EMControl as EMC
from .emcontrols import SIMControl as SIMC

#diffraction classes handling diffraction pattern data
from .kdiffs import diffPattern as DP
from .kdiffs import Diffraction as DPList
from .ddiffs import BlochImgs as BImgList

from .crystals import Crystal
try:
    from .kdiffs import XMAX, YMAX
except ImportError as e:
    print(f'Error importing kinematic constants: {e}')
    
from .display import showDif, showBloch
