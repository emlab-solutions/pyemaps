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
Date:       October 21, 2022    


This sample code is to demonstrate how to generate .xyz crystal 
construction data that can be visualized by Jmol and cloudEMAPS 2.0. 
'''
def test_mxtal(bPrint=True, bSave=True):
    
    from pyemaps import Crystal as cr
    from pyemaps import CrystalClassError
    from pyemaps import MxtalError
    mx=None
    try:
        si = cr.from_builtin('Silicon')
        if si and bPrint:
            print(f'crytsal data to generate mxtal: {si}')
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
