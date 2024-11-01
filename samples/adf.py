

"""
.. This file is part of pyEMAPS
 
.. ----

.. pyEMAPS is free software. You can redistribute it and/or modify 
.. it under the terms of the GNU General Public License as published 
.. by the Free Software Foundation, either version 3 of the License, 
.. or (at your option) any later version..

.. pyEMAPS is distributed in the hope that it will be useful,
.. but WITHOUT ANY WARRANTY; without even the implied warranty of
.. MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
.. GNU General Public License for more details.

.. You should have received a copy of the GNU General Public License
.. along with pyEMAPS.  If not, see `<https://www.gnu.org/licenses/>`_.

.. Contact supprort@emlabsoftware.com for any questions and comments.

.. ----


.. Author:     EMLab Solutions, Inc.
.. Date:       May 27, 2023  

This sample code is to demostrate basic usage of pyemaps' stem4d
module to obtain annular dark and bright field image from 
an experimental diffraction image input.

This script is only available in with a license activation. 

Contact: support@emlabsoftware.com for license information.

"""

import os
from pathlib import Path
from pyemaps import StackImage, EM_INT, E_RAW

current_file = Path(os.path.abspath(__file__))
samples_path = current_file.parent.absolute()

def getDFFn():
    '''
    Imports sample experimental diffraction pattern image
    with pyEMAPS preprietory 8-bytes header of integer data
    type. 

    To use your own image file, modify this call to retrieve 
    the file and specify the image format and data type in 
    StackImage object creation. See document on StackImage class.

    '''
    return os.path.join(samples_path, 'adftest30x30.im3')

def getMaskFn():
    '''
    Imports sample experimental diffraction pattern image
    with pyEMAPS preprietory 8-bytes header of integer data
    type.  

    To use your own image file, modify this call to retrieve 
    the file.

    '''
    return os.path.join(samples_path, 'mask.im3')

def test_adf():
    '''
    Generate and display annular dark field for input image.

    '''
    
    adfn = getDFFn()

    img = StackImage(adfn, 
                    #  nformat = E_SH,    <-------- use E_RAW or E_NPY for raw or numpy array image format, 
                    #                               default to pyEMAPS proprietory format E_SH
                    #  noffset = 8,       <-------- image head size or offset to image data, default 8
                    #  dim,               <-------- image dimensions in 3 integer tuple.
                    ndtype = EM_INT,     #<-------- image data type, default to float type EM_FLOAT.
                                        #           supports double type also.
                    
                    )
    
    ret, _ = img.generateBDF(center = (256.0, 256.0), 
                    rads = (50.0,200.0), 
                    scol = 30,
                    bShow = True)

    if ret != 0:
        print(f'Annular bright or dark field image generation failed ')
        

def test_df():
    '''

    Generate and display bright or dark field for input image

    '''
    
    adfn = getDFFn()
    
    img = StackImage(adfn, ndtype = EM_INT)
    
    ret, _ = img.generateBDF(center = (1.0, 256.0), 
                    rads = (0.0,200.0), 
                    scol = 30,
                    bShow = True)

    if ret != 0:
        print(f'Annular bright field image generation failed ')
        
def test_maskedimage():
    imgfn = getDFFn()
    maskfn = getMaskFn()
    
    img = StackImage(imgfn, ndtype = EM_INT)
    
    scancol = 30
    ret, _ = img.generateMaskedImage(maskfn,
                                scancol,
                                # bViewOriginal = True,   <---- display the input image
                                bShow = True)

    if ret != 0:
        print(f'Masked image generation failed ')
    
if __name__ == '__main__':
    
    test_adf()                      # <---------- annular bright or dark field image
    test_df()                      # <---------- bright or dark field image
    test_maskedimage()
    