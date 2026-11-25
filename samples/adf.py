# This file is part of pyEMAPS.
# Copyright (C) 2021-2026 EMLab Solutions, Inc.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Additional permission under GPLv3 Section 7:
# See license-exception.txt for the exception permitting
# combination with the separately licensed backend, emaps.
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

# The direct beam, at column 263, row 263 of the 512 x 512 patterns: the brightest pixel of
# the patterns' average (the adf.ipynb notebook finds it). Detectors around the direct beam are
# centred on it, not on the middle of the pattern.
BEAM_CENTER = (263.0, 263.0)    # (column, row), in pixels


def annular_dark_field():
    """Generate and display an annular dark field image."""
    image = StackImage(IMAGE_FILE, ndtype=EM_INT)
    ret, _ = image.generateBDF(center=BEAM_CENTER,      # detector center, in pixels
                               rads=(50.0, 200.0),      # inner and outer radius, in pixels
                               scol=SCAN_COLUMNS,
                               bShow=True,
                               title='Annular Dark Field')
    if ret != 0:
        print('Failed to generate the annular dark field image')


def dark_field():
    """Generate and display a dark field image, with the detector off the central beam."""
    image = StackImage(IMAGE_FILE, ndtype=EM_INT)
    ret, _ = image.generateBDF(center=(1.0, 256.0),
                               rads=(0.0, 200.0),
                               scol=SCAN_COLUMNS,
                               bShow=True,
                               title='Dark Field')
    if ret != 0:
        print('Failed to generate the dark field image')


def masked_image():
    """Generate and display an image with the detector shape taken from a mask image."""
    image = StackImage(IMAGE_FILE, ndtype=EM_INT)
    ret, _ = image.generateMaskedImage(MASK_FILE, SCAN_COLUMNS, bShow=True,
                                       title='Masked Image')
    if ret != 0:
        print('Failed to generate the masked image')


def main():
    annular_dark_field()
    dark_field()
    masked_image()


if __name__ == '__main__':
    main()
