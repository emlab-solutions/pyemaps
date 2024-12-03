"""
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

An example of using pyemaps crystal and diffraction modules to 
1) create a crystal from built-in data for Silicon 
2) generate kinematical diffraction patterns
3) display the diffraction pattern using pyemaps's built-in plot function 

See https://emlab-solutions.github.io/pyemaps/ for pemaps usage

Author:     EMLab Solutions, Inc.
Date:       May 07, 2022    

"""
if __name__ == '__main__':
    
    from pyemaps import Crystal as cr
    from pyemaps import CrystalClassError
    from pyemaps import BlochError
    try:
        si = cr.from_builtin('Silicon')

        bimgs = si.generateBloch(sample_thickness=(200, 1000, 100), bSave=True)

    except (CrystalClassError, BlochError) as e:
        print(f'error: generate and write bloch image data: {e.message}')
    except Exception as e:
        print(f'error: generate and write bloch image data: ' + str(e))
   
   