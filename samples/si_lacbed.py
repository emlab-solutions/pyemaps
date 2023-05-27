"""
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
Date:       May 25, 2023  


This sample code is to demostrate using pyemaps to generate and render
dynamic diffraction patterns. 


"""

def generate_lacbed_images(name = 'Silicon', bShow=False):
    
    from pyemaps import Crystal as cryst

    cr = cryst.from_builtin(name)
    
    try:
        imgs = cr.generateBloch( disk_size = 0.5,
                            sampling = 10,
                            nType = 1, 
                            sample_thickness=(1000,1000,100),
                            bSave=True)
    except Exception as e:
        print(f'Faild to obtain large angle CBED images: {e}') 
        return

    if bShow:        
        imgs.sort()
        showBloch(imgs,bClose=True)


from pyemaps import showBloch

if __name__ == '__main__':
    
    generate_lacbed_images(bShow=True)
        
