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
    import random
    
    si = cr.from_builtin(c_name)
    
    print(si)
    # -----generate scattering matrix on this crystal instance----- 
    #      controls set as follows. 

    #      For a list beams coordinates 
    #      to generate more scattering matrix, run cr.printIBDetails()
    
    ec =EMC(cl=200,
            tilt=(0.0, 0.0),
            simc = SIMC(gmax=2.0, excitation=(1.0,2.0))
            )
    ds = 0.25
    ib_coords = (0, 0)
    
    try:
        
        ns, s = si.beginBloch(em_controls = ec, 
                        dbsize = ds)

    except Exception as e:
        print(f'Failed to generate scattering matrix {e}')
    else:
        
        print(f'----Sampling points in this dynamic diffraction session---:')
        print(f'Number of sampling points: {ns}')
        print(f'{s}')

        # get the scattering matrix and associated eigen values now
        try:
            ndim, si_scm, si_ev, si_beams = si.getSCMatrix(ib_coords = ib_coords)
        except BlochError as e:
            print(f'Failed to generate scattering matrix {e.message}')
        except Exception as e:
            print(f'Failed to generate scattering matrix {e}')
        else:
            print(f'\n----Scattering matrix at sampling point {ib_coords}----:')
            print(f'Size of the scattering matrix: {ndim}x{ndim}')
            print(f' \n{si_scm}')

            print(f'\n----Eigen values at: {ib_coords}----')
            print(si_ev)

            print(f'\n----Diffracted beams at: {ib_coords}----')
            print(si_beams)

            print(f'\n----More details associated with scattering matrix calculation') 
            si.printIBDetails()
            
            # select a random sampling point from s and calculate scattering matrix
            randnum = random.randrange(0, ns-1)
            
            ib_coords = s[randnum]
            try:
                nd, si_scm, si_ev, si_beams = si.getSCMatrix(ib_coords = ib_coords)
            except Exception:
                print(f'Error obtaining scattering matrix at random sampling points {ib_coords}')
            else:
                print(f'\n----Scattering matrix at a randomly selected sampling point {ib_coords}----:')
                print(f'Size of the scattering matrix: {nd}x{nd}')
                print(f'{si_scm}')
                print(f'\n----Eigen values at: {ib_coords}----')
                print(si_ev)
                print(f'\n----Diffracted beams at: {ib_coords}----')
                print(si_beams)

        # show a list of calculated beams for the session
        ncb, cbs = si.getCalculatedBeams(bPrint=True)
    # cleanup 
    si.endBloch()

if __name__ == "__main__":
    runSCMTests()
