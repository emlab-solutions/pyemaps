'''
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

Author:     EMLab Solutions, Inc.
Date:       May 31, 2022    


This sample code is to demonstrate how to generate powder diffraction.
'''

def runPowderTests():
    from pyemaps import Crystal as cryst
    from pyemaps import plot2Powder
    import time

    si = cryst.from_builtin('Silicon')
    print(si)
    psi = si.generatePowder() 

    # si.plotPowder(psi)
    di = cryst.from_builtin('Diamond')
    print(di)
    pdi = di.generatePowder(absp = 1)

    plot2Powder(psi, pdi)

if __name__ == "__main__":
    
    runPowderTests()
