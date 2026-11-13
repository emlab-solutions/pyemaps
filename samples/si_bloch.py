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

"""Dynamic (Bloch wave) CBED patterns for Silicon over a tilt series and a zone axis series.

For each of the two microscope controls, tilt and zone axis, this sample generates six
dynamic diffraction patterns, each with a different value of that control, and displays them.
The patterns are generated in parallel processes.

Run it with:

    python si_bloch.py
"""
import concurrent.futures
import sys

from pyemaps import DEF_CBED_DSIZE, EMC, SIMC, BImgList, Crystal, showBloch

# The microscope controls this sample varies: tilt and zone axis.
CONTROLS = ('tilt', 'zone')

MAX_WORKERS = 4    # number of parallel processes


def make_controls(control, random_sim=False):
    """Return six microscope controls (EMC), each with a different value of `control`.

    All six use a camera length of 200 and share one set of simulation controls (SIMC):
    randomized with `random_sim=True`, the defaults otherwise.
    """
    sim = SIMC.from_random() if random_sim else SIMC()

    emc_list = []
    for i in range(-3, 3):
        emc = EMC(cl=200, simc=sim)
        if control == 'tilt':
            emc.tilt = (i * 0.5, 0.0)
        elif control == 'zone':
            emc.zone = (0, i, 1)
        emc_list.append(emc)

    return emc_list


def generate_bloch_images(control='tilt', name='Silicon', disk_size=DEF_CBED_DSIZE,
                          random_sim=False):
    """Generate dynamic diffraction images, one per value of a microscope control.

    :param control: the microscope control to vary: 'tilt' or 'zone'.
    :param name: the name of a built-in crystal.
    :param disk_size: the diffracted beam (disk) size.
    :param random_sim: use randomized simulation controls instead of the defaults.
    :return: the images as a BImgList sorted by their microscope controls, or None if a
        simulation failed.
    """
    crystal = Crystal.from_builtin(name)

    images = BImgList(name)
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(crystal.generateBloch,
                                   disk_size=disk_size,
                                   sampling=20,
                                   sample_thickness=(1750, 1750, 100),
                                   em_controls=emc)
                   for emc in make_controls(control, random_sim)]

        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
            except Exception as e:
                print(f'Unable to generate a Bloch image: {e}')
                return None

            # Each simulation has one sample thickness, so it returns one image.
            emc, image = result[0]
            images.add(emc, image)

    images.sort()
    return images


def main():
    # The tilt and zone axis series, as tables, also saved as images.
    for control in CONTROLS:
        images = generate_bloch_images(control)
        if images is None:
            sys.exit(1)
        showBloch(images, layout='table', bSave=True, bClose=True)

    # The same series with randomized simulation controls, one image at a time.
    for control in CONTROLS:
        images = generate_bloch_images(control, random_sim=True)
        if images is None:
            sys.exit(1)
        showBloch(images, bClose=True)


if __name__ == '__main__':
    main()
