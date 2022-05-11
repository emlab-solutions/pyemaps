'''
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

Author:     EMLab Solutions, Inc.
Date:       May 07, 2022    

'''

def run_si_sample_cbed():
    #import Crystal class from pyemaps as cryst
    from pyemaps import Crystal as cryst

    # create a crystal class instance and load it with builtin silican data
    si = cryst.from_builtin('silicon')
    # print(si)

    # run diffraction on the crystal instance with all default controls
    # parameters
    _, si_dp2 = si.generateDP(mode=2, dsize=0.16)
    # print(si_dp2)

    #plot and show the pattern just generated using pyemaps built-in plot function
    si_dp2.plot(mode = 2)

if __name__ == '__main__':
    run_si_sample_cbed()