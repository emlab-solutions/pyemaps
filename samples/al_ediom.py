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

"""Indexing an experimental Aluminium diffraction pattern.

This sample uses pyEMAPS' dpgen and stem4d modules. It generates a diffraction pattern
database for Aluminium, searches it for the pattern that best matches the experimental image
al.img, prints the indexing results and displays the best match.

It needs an activated pyEMAPS license; see the License page of the pyEMAPS documentation.
Contact support@emlabsoftware.com for license information.

Run it with:

    python al_ediom.py
"""
import os

from pyemaps import EMC, Crystal, StackImage, XDPImageError

# The experimental image, in pyEMAPS' small-header format, next to this script.
# To index your own image, change this path.
IMAGE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'al.img')


def index_image(image_file=IMAGE_FILE, name='Aluminium'):
    """Index an experimental diffraction pattern image against a generated database.

    :param image_file: the experimental image file.
    :param name: the name of the built-in crystal in the image.
    :return: 0 on success, -1 on failure.
    """
    crystal = Crystal.from_builtin(name)
    ret, db_file = crystal.generateDPDB(emc=EMC(zone=(0, 0, 1)), xa=(2, 0, 0), res=200)
    if ret != 0:
        print('Failed to generate the diffraction pattern database')
        return -1

    image = StackImage(image_file)
    try:
        image.indexImage(db_file,
                         cc=29.0,                       # camera constant, pixels per 1/Å
                         sigma=3.0,                     # estimated peak width, in pixels
                         img_center=(99.923, 99.919),   # pattern center, in pixels
                         rmin=10,                       # radius excluded around the center
                         search_box=10.0,               # peak search box size, in pixels
                         scaling_option=(1, 2),         # intensity scaling for matching
                         filter_threshold=0.0,          # 0 searches every database pattern
                         peak_threshold=0.8)            # drops noisy peaks
    except XDPImageError as e:
        print(f'Failed to index the image: {e.message}')
        return -1

    # Display the pattern in the database that best matches the image.
    StackImage.showMatchedDBDP()
    return 0


def main():
    index_image()


if __name__ == '__main__':
    main()
