

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
.. Date:       Oct 31, 2024  

This sample code is to demostrate pyEMAPS helper tool to convert
a raw image to a pyEMAPS propietory small header image format.

This script is only available in with a license activation. 

Contact: support@emlabsoftware.com for license information.

"""

import os
from pathlib import Path
from pyemaps import StackImage

current_file = Path(os.path.abspath(__file__))
samples_path = current_file.parent.absolute()

def getRawImageFn():
    '''
    retrieves sample experimental diffraction pattern image
    in raw image format of dimension (256, 256, 1), 4-bytes 
    real image data type and offset of 0, to be converted to
    pyEMAPS proprietory image format.  

    To use your own image file, modify this call to retrieve 
    the file.

    '''
    return os.path.join(samples_path, 'raw.img')

def test_conversion():
    '''
    
    retrieves the raw image file and convert it to a pyEMAPS
    small header image file.

    If the input raw image file name does not contain directory,
    this method will search the file in pyEMAPS data diretcory
    set by the environment variable PYEMAPS_DATA or current 
    working directory in that order. 
    
    If the input file contains the fully qualified file path, 
    pyEMAPS will be using the folder that contains the file
    to place the output image file. So, please make sure that
    the input directory is writable.
    
    The result pyEMAPS image file with small header will be saved 
    in a folder name `sh_converted` in the dierctory that
    contains the original raw image file.

    '''
    rawfn = getRawImageFn()
    StackImage.convertImage(rawfn,
                            # nformat=E_RAW, default
                            dim = (256, 256, 1),
                            # ndtype = E_FLOAT,  default
                            noffset = 0
    )    

if __name__ == '__main__':
    test_conversion()