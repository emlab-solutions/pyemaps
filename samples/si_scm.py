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
    ib_coords = (0,0)
    
    try:
        
        ns, s = si.beginSCMatrix(em_controls = ec, 
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
            print(f'----Sampling points in this scattering matrix calculation---:')
            print(f'{s}')

            print(f'----Sacattering matrix at sampling point {ib_coords}----:')
            print(f' \n{si_scm}')

            print(f'----Eigen values at: {ib_coords}----')
            print(cr.getEigen(ib_coords = ib_coords))

            print(f'----Diffracted Beams in Miller Indexes at: {ib_coords}----: ')
            cr.getBeams(ib_coords = ib_coords, bPrint=True)

            print(f'----Beam Tilts In Reciprical Space and misc. info') 
            cr.printIBDetails()

            #       get a random sampling point from available list of
            #       sampling points and print the corresponding 
            #       scattering matrix

            import random
            radnum = random.randrange(1, ns-1)
            ib_coords = s[radnum]
            scm = cr.getSCMatrix(ib_coords = ib_coords)
            print(f'--Sacattering matrix at a random sampling point {ib_coords}----:')
            print(f'{scm}')
            

    # cleanup 
    cr.endSCMatrix()

if __name__ == "__main__":
    runSCMTests()
