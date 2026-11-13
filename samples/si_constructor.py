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

Contact support@emlabsoftware.com for any questions and comments.
___________________________

Author:     EMLab Solutions, Inc.
Date:       October 21, 2022    


This sample code demonstrates how to build a crystal supercell with
pyEMAPS' mxtal module and save it as an .xyz file, which viewers such
as Jmol can display.
'''
def test_mxtal(bPrint=True, bSave=True):
    
    from pyemaps import Crystal as cr
    from pyemaps import CrystalClassError
    from pyemaps import MxtalError
    mx=None
    try:
        si = cr.from_builtin('Silicon')
        if bPrint:
            print(f'crystal data to generate mxtal: {si}')
        mx = si.generateMxtal(bound=0.1)
    except (CrystalClassError, MxtalError) as e:
        print(f'error: generating crystal structure data: {e.message}')
    except Exception as e:
        print(f'error: generating crystal structure data: {e}')
    else:
        if bPrint:
            print(f'\nCrystal Structure Data Generated for {si.name}:')
            si.printXYZ(mx)
        if bSave:
            si.writeXYZ(mx)
        return mx
if __name__ == "__main__":
    test_mxtal()
