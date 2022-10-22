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
c_name = 'Silicon'

def runSCMTests():

    from pyemaps import Crystal as cr
    from pyemaps import BlochError, EMC, SIMC
    si = cr.from_builtin(c_name)
    
    print(si)
    # -----generate scattering matrix on this crystal instance----- 
    #      controls set as follows. 

    # -----For a list beams coordinates 
    #      to generate more scattering matrix, run cr.printIBDetails()
    try:
        ec =EMC(cl=200, zone=(1,1,2),
                            simc = SIMC(gmax=1.0, excitation=(0.3,1.0))
                           )
        ds = 0.25
        si_scm = si.generateSCMatrix(em_controls = ec, 
                                    disk_size = ds,
                                    ib_coords = (-6,3))

    except BlochError as e:
        print(f'Failed to generate scattering matrix {e.message}')
    else:
        print('Scattering matrix generated successfully!')
        print(si_scm)
        print('more possible beams coordinate input as follows...')
        cr.printIBDetails()

if __name__ == "__main__":
    runSCMTests()
