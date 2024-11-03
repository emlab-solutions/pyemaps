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
Date:       May 24, 2022    


This sample code is to demonstrate how to generate crystal structure 
factors. 
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

    sfl = [1,2,3,4] # structure factor type list
    # 1 -----X-ray Structure Factors
    # 2 -----Electron Strcture Factors in kV
    # 3 -----Electron Structure Factor in 1/Å
    # 4 -----Electron Absorption Structure Factor in 1/Å^2

    ampl = [1, 0] # structure factor format
    # 1 -----amplitude and phase
    # 0 -----real and imaginary

    for i in sfl:
        for j in ampl:
            
            sfs = si.generateCSF(kv = v, smax = sm, sftype = i, aptype = j)
            
            si.printCSF(sfs)

if __name__ == "__main__":
    runCSFTests()
