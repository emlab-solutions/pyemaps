
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

Author:     EMLab Solutions, Inc.
Date:       April 02, 2023  

This sample code is to demostrate basic usage of pyemaps' dpgen - 
diffraction pattern (DP) generator module used as database
for stem4d module to search and index experimental diffraction 
patterns images. 

This script is for demonstration and only support crystal with 
space group 225. 

The complete crystal system support is available in pyemaps 
full package and for purchase. Contact:
    support@emlabsoftware.com 
for price information.

"""
def al_dpdb(cname='Aluminium'):
    from pyemaps import Crystal as cr
    from pyemaps import EMC, SIMC
    import os
   
    
    cryst = cr.from_builtin(cname)

    #  first generate a DP database file
    xa0=(2,0,0)   # x-axis, will be folded into EMC object
    res = 200
    ret, dbfn = cryst.generateDPDB(emc=EMC(zone=(0,0,1), 
                                   simc=SIMC(gmax=3.9)), 
                                   xa = xa0,
                                   res = res)
#   DP == Diffraction Pattern
    if ret != 0:
        print(f'failed to generate a DP databaes')
        return -1

    if dbfn is None or not os.path.exists(dbfn):
        print(f'Error finding generated DP database file')
        return -1


if __name__ == '__main__':
    al_dpdb()