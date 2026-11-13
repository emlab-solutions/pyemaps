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

Contact support@emlabsoftware.com for any questions and comments.
___________________________

Author:     EMLab Solutions, Inc.
Date:       May 25, 2023  


This sample code generates large-angle CBED (LACBED) images for
Silicon, one image per diffracted beam, and displays them.


"""

from pyemaps import showBloch


def generate_lacbed_images(name = 'Silicon', bSave = False, bShow=False):

    from pyemaps import Crystal as cryst

    cr = cryst.from_builtin(name)
    
    try:
        imgs = cr.generateBloch( disk_size = 0.5,
                            sampling = 10,
                            nType = 1, 
                            sample_thickness=(1000,1000,100),
                            bSave=bSave)
    except Exception as e:
        print(f'Failed to obtain large angle CBED images: {e}')
        return
       
    imgs.sort()
    if bShow: 
        showBloch(imgs,bClose=True)
    return imgs

def main():
    generate_lacbed_images(bSave=True, bShow=True)


if __name__== '__main__':
    main()
        
