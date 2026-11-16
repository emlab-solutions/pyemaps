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

"""Converting a raw image into pyEMAPS' small-header image format.

This sample converts raw.img, a 256 x 256 raw image of 4-byte floats with no header, into
pyEMAPS' small-header format. The converted image is saved in a folder named sh_converted
next to the input image, so that folder must be writable.

It needs an activated pyEMAPS license; see the License page of the pyEMAPS documentation.
Contact support@emlabsoftware.com for license information.

Run it with:

    python convert_image.py
"""
import os

from pyemaps import StackImage

# The raw image, next to this script. To convert your own image, change this path, and the
# dimensions and offset below to match it.
RAW_IMAGE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'raw.img')


def convert_image(raw_file=RAW_IMAGE_FILE):
    """Convert a raw image file into pyEMAPS' small-header format."""
    StackImage.convertImage(raw_file,
                            dim=(256, 256, 1),   # width, height and number of stacks
                            noffset=0)           # bytes before the image data
    # The image format (raw) and data type (float) are the defaults.


def main():
    convert_image()


if __name__ == '__main__':
    main()
