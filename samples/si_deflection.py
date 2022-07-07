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
Date:       May 11, 2022    


This sample code is to render kinematic diffraction patterns generated
by pyemaps by changing deflection in x direction

Required: sample_base.py in the same directory
'''
from sample_base import generate_difs 

if __name__ == '__main__':
    from pyemaps import showDif

    key = 'defl'
    dps = generate_difs(ckey=key)
    showDif(dps)

    dps_cbed = generate_difs(mode = 2, ckey=key)
    showDif(dps_cbed, ishow=False)