# This file is part of pyEMAPS.
#
# pyEMAPS is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# pyEMAPS is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with pyEMAPS.
# If not, see <https://www.gnu.org/licenses/>.
#
# Author: EMLab Solutions, Inc. Questions and comments: support@emlabsoftware.com

"""Bright field, dark field and masked images from an experimental 4D-STEM image.

This sample uses pyEMAPS' stem4d module on adftest900.im3, a 4D-STEM image with one
diffraction pattern per scan position, 30 scan positions per row. From it, the sample
generates and displays:

1. an annular dark field image, with a detector centered on the central beam;
2. a dark field image, with a detector off the central beam;
3. a masked image, with the detector shape taken from the mask image mask.im3.

adftest900.im3 is available from Zenodo:
https://zenodo.org/records/14028793/files/adftest900.im3?download=1
Save it in the same folder as this script.

It needs an activated pyEMAPS license; see the License page of the pyEMAPS documentation.
Contact support@emlabsoftware.com for license information.

Run it with:

    python adf.py
"""
import os

from pyemaps import EM_INT, StackImage

SAMPLES_DIR = os.path.dirname(os.path.abspath(__file__))

# The 4D-STEM image and the mask, in pyEMAPS' small-header format with integer data.
# To use your own image, change IMAGE_FILE, and pass its format, data type, header size and
# dimensions to StackImage below; see the StackImage documentation.
IMAGE_FILE = os.path.join(SAMPLES_DIR, 'adftest900.im3')
MASK_FILE = os.path.join(SAMPLES_DIR, 'mask.im3')

SCAN_COLUMNS = 30    # scan positions per row: the width of the output images


def annular_dark_field():
    """Generate and display an annular dark field image."""
    image = StackImage(IMAGE_FILE, ndtype=EM_INT)
    ret, _ = image.generateBDF(center=(256.0, 256.0),   # detector center, in pixels
                               rads=(50.0, 200.0),      # inner and outer radius, in pixels
                               scol=SCAN_COLUMNS,
                               bShow=True)
    if ret != 0:
        print('Failed to generate the annular dark field image')


def dark_field():
    """Generate and display a dark field image, with the detector off the central beam."""
    image = StackImage(IMAGE_FILE, ndtype=EM_INT)
    ret, _ = image.generateBDF(center=(1.0, 256.0),
                               rads=(0.0, 200.0),
                               scol=SCAN_COLUMNS,
                               bShow=True)
    if ret != 0:
        print('Failed to generate the dark field image')


def masked_image():
    """Generate and display an image with the detector shape taken from a mask image."""
    image = StackImage(IMAGE_FILE, ndtype=EM_INT)
    ret, _ = image.generateMaskedImage(MASK_FILE, SCAN_COLUMNS, bShow=True)
    if ret != 0:
        print('Failed to generate the masked image')


def main():
    annular_dark_field()
    dark_field()
    masked_image()


if __name__ == '__main__':
    main()
