"""
This file is part of pyemaps
___________________________

pyemaps is free software. You can redistribute it and/or modify 
it under the terms of the GNU General Public License as published 
by the Free Software Foundation, either version 3 of the License, 
or (at your option) any later version.

pyemaps is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pyemaps.  If not, see <https://www.gnu.org/licenses/>.

Contact supprort@emlabsoftware.com for any questions and comments.
___________________________

An example of using pyemaps crystal and diffraction modules to 
1) create a crystal from built-in data for Silicon 
2) generate kinematical diffraction patterns
3) display the diffraction pattern using pyemaps's built-in plot function 

See https://emlab-solutions.github.io/pyemaps/ for pemaps usage

Author:     EMLab Solutions, Inc.
Date:       May 07, 2022    

"""


def run_si_sample():
    #import Crystal class from pyemaps as cryst
    from pyemaps import Crystal as cr
    from pyemaps import showDif, showBloch
    from pyemaps import DPList
    from pyemaps import BImgList
    # create a crystal class instance and load it with builtin silicon data
    c_name = 'Silicon'
    si = cr.from_builtin(c_name)

    # generate diffraction on the crystal instance with all default controls
    # parameters, default controls returned as the first output ignored
    
    dpl = DPList(c_name)

    emc, si_dp = si.generateDP()
    dpl.add(emc, si_dp) 
    
    #plot and show the diffraction pattern using pyemaps built-in plot function
    showDif(dpl)

    #hide Kikuchi lines
    showDif(dpl, kShow=False, bClose=True) 

    #plot the following two DP in CBED mode (mode = 2)
    dpl = DPList(c_name, mode = 2)

    emc, si_dp = si.generateDP(mode = 2)
    dpl.add(emc, si_dp) 

    #hide both Kukuchi line and Miller Indices
    showDif(dpl, kShow=False, iShow=False, bClose=True) 

    #hide Miller Indices
    showDif(dpl, iShow=False, bClose=True)

    #Generate dynamic diffraction patterns using pyemaps' bloch module
    
    try:
      bloch_imgs_list = si.generateBloch(sampling = 20) 
      
    except Exception as e:
      print(f'Error: {e}')

    else:        
      showBloch(bloch_imgs_list, bClose=True) #grey color map
      showBloch(bloch_imgs_list, bColor=True, bClose=True) #with predefined color map