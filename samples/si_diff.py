"""
# This file is part of pyemaps
# ___________________________
#
# pyemaps is free software for non-comercial use: you can 
# redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either 
# version 3 of the License, or (at your option) any later version.
#
# pyemaps is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyemaps.  If not, see <https://www.gnu.org/licenses/>.

# Contact supprort@emlabsoftware.com for any questions and comments.
# ___________________________

An example of using pyemaps crystal and diffraction modules to 
1) create a crystal from built-in data for Silicon 
2) generate kinematical diffraction patterns
3) display the diffraction pattern using pyemaps's built-in plot function 

Usage:
a) install pyemaps diffraction and crystal modules:
    pip install pyemaps
b) run  
    python si_diff.py

"""


def run_si_sample():
    #import Crystal class from pyemaps as cryst
    from pyemaps import Crystal as cryst

    # create a crystal class instance and load it with builtin silican data
    si = cryst.from_builtin('silicon')
    
    # use cryst.list_all_builtin_crystals() to list names of all of the builtin
    # crystals
    
    # print(si)

    # run diffraction on the crystal instance with all default controls
    # parameters
    si_dp = si.gen_diffPattern()
    # print(si_dp)

    #plot and show the pattern just generated using pyemaps built-in plot function
    si_dp.plot()

    

