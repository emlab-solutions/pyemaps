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
Date:       May 24, 2022    


This sample code is to render kinematic diffraction patterns generated
by pyemaps by changing zone axis
'''
c_name = 'Silicon'

def runCSFTests():
    from pyemaps import Crystal as cr
    si = cr.from_builtin(c_name)
    
    print(si)
    # generate diffraction on the crystal instance with all default controls
    # parameters, default controls returned as the first output ignored
    v = 100
    sm = 1.0

    for i in [1,2,3,4]:
        for j in [1, 0]:
            sfs = si.generateCSF(kv = v, smax = sm, sftype = i, aptype = j)
            si.printCSF(sfs, kv = v, smax = sm, sftype = i, aptype = j)

if __name__ == "__main__":
    runCSFTests()
