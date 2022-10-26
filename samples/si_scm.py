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
Date:       October 19th, 2022    


This sample code is to demonstrate how to generated scattering matrix
'''
# c_name = 'Germanium'
c_name = 'silicon'

def runSCMTests():

    from pyemaps import Crystal as cr
    from pyemaps import BlochError, EMC, SIMC
    si = cr.from_builtin(c_name)
    
    print(si)
    # -----generate scattering matrix on this crystal instance----- 
    #      controls set as follows. 

    # -----For a list beams coordinates 
    #      to generate more scattering matrix, run cr.printIBDetails()
    ec =EMC(cl=200,
            tilt=(0.0, 0.0),
            simc = SIMC(gmax=2.0, excitation=(1.0,2.0))
            )
    ds = 0.25
    ib_coords = ( 0,0)
    try:
        
        # s  = list of sampling points (x,y)
        _, s = si.beginSCMatrix(em_controls = ec, 
                        disk_size = ds)

    except BlochError as e:
        print(f'Failed to generate scattering matrix {e.message}')
    else:
        # get the scattering matrix now
        try:
            si_scm = cr.getSCMatrix(ib_coords = ib_coords)
        except BlochError as e:
            print(f'Failed to generate scattering matrix {e.message}')
        else:
            print(f'Sacattering matrix at sampling point {ib_coords}:\n{si_scm}')
            # output eigen values at ib_coords
            print(f'\nEigen values at: {ib_coords}: ')
            print(cr.getEigen(ib_coords = ib_coords))
            # outputMiller Indices at ib_coords
            print(f'\nDiffracted Beams at: {ib_coords}: ')
            cr.getBeams(ib_coords = ib_coords, bPrint=True)
            # output list if ib_coords and tilts and etc...
            print(f'\nBeam Tilts In Reciprical Space and Misc') 
            cr.printIBDetails()
            
            # ------enable below to step through all sampling points 
            #       and print all scattering matrix

            # for sc in s:
            #     scm = cr.getSCMatrix(ib_coords = sc)
            #     print(f'--Sacattering matrix at sampling point {sc}:\n{scm}--')
            #     print(scm)

    
    # cleanup backend module memory
    cr.endSCMatrix()

if __name__ == "__main__":
    runSCMTests()
