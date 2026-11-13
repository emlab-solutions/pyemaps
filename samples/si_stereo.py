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

"""Stereodiagrams for Silicon over a tilt series and a zone axis series.

For each of the two microscope controls, tilt and zone axis, this sample generates six
stereodiagrams, each with a different value of that control, and displays them with their
Miller indices. The stereodiagrams are generated in parallel processes.

Run it with:

    python si_stereo.py
"""
import concurrent.futures
import sys

from pyemaps import EMC, Crystal, showStereo

# The microscope controls this sample varies: tilt and zone axis.
CONTROLS = ('tilt', 'zone')

MAX_WORKERS = 4    # number of parallel processes


def stereodiagram(name, emc, control):
    """Return `emc` and the stereodiagram of crystal `name` at the `control` value in `emc`.

    This runs in a worker process, so it loads the crystal itself.
    """
    crystal = Crystal.from_builtin(name)
    if control == 'tilt':
        return emc, crystal.generateStereo(tilt=emc.tilt)
    return emc, crystal.generateStereo(zone=emc.zone)


def generate_stereodiagrams(control='tilt', name='Silicon'):
    """Generate stereodiagrams, one per value of a microscope control.

    :param control: the microscope control to vary: 'tilt' or 'zone'.
    :param name: the name of a built-in crystal.
    :return: a list of (EMC, stereodiagram) pairs, sorted by their microscope controls.
    """
    if control == 'tilt':
        emc_list = [EMC(tilt=(i * 0.5, 0.0)) for i in range(-3, 3)]
    else:
        emc_list = [EMC(zone=(i, -i, 1)) for i in range(-3, 3)]

    stereo_list = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(stereodiagram, name, emc, control) for emc in emc_list]

        for future in concurrent.futures.as_completed(futures):
            try:
                stereo_list.append(future.result())
            except Exception as e:
                sys.exit(f'Failed to generate a stereodiagram: {e}')

    stereo_list.sort(key=lambda pair: pair[0])
    return stereo_list


def main():
    # The tilt series as a table.
    showStereo(generate_stereodiagrams('tilt'), name='Silicon', layout='table',
               iShow=True, zLimit=1, bClose=True)

    # The zone axis series, one stereodiagram at a time.
    showStereo(generate_stereodiagrams('zone'), name='Silicon',
               iShow=True, zLimit=1, bClose=True)


if __name__ == '__main__':
    main()
