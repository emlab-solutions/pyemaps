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

from pyemaps import showDif
from sample_base import generate_difs
c_name = 'Silicon'

def run_cbed_dp_tests():
    from sample_base import generate_difs

    em_keys = ['tilt', 'zone', 'defl', 'vt', 'cl']
    for k in em_keys:
        dpl = generate_difs(ckey=k, mode = 2)
        showDif(dpl)

if __name__ == '__main__':
    
    run_cbed_dp_tests()