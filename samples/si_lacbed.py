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

"""Large-angle CBED (LACBED) images for Silicon.

This sample runs a dynamic diffraction simulation in LACBED mode, which gives one image per
diffracted beam, and displays the images. It also saves them in a raw image file.

Run it with:

    python si_lacbed.py
"""
from pyemaps import TY_LACBED, Crystal, showBloch


def generate_lacbed_images(name='Silicon', save=False, show=False):
    """Generate LACBED images, one per diffracted beam.

    :param name: the name of a built-in crystal.
    :param save: also save the images in a raw image file.
    :param show: display the images.
    :return: the images as a BImgList, or None if the simulation failed.
    """
    crystal = Crystal.from_builtin(name)

    try:
        images = crystal.generateBloch(disk_size=0.5,
                                       sampling=10,
                                       nType=TY_LACBED,
                                       sample_thickness=(1000, 1000, 100),
                                       bSave=save)
    except Exception as e:
        print(f'Failed to generate LACBED images: {e}')
        return None

    images.sort()
    if show:
        showBloch(images, bClose=True)
    return images


def main():
    generate_lacbed_images(save=True, show=True)


if __name__ == '__main__':
    main()
