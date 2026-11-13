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

"""Kinematic diffraction patterns for Silicon, varying one microscope control at a time.

For each microscope control (tilt, zone axis, deflection, high voltage and camera length),
this sample generates six diffraction patterns, each with a different value of that control,
and displays them. The patterns are generated in parallel processes.

Run it with:

    python si_dif.py
"""
import concurrent.futures
import sys

from pyemaps import (DEF_CBED_DSIZE, DEF_MODE, EMC, SIMC, Crystal, DPError, DPList, EMCError,
                     showDif)

# The microscope controls this sample varies, by their EMC attribute names:
# tilt, zone axis, deflection, high voltage and camera length.
CONTROLS = ('tilt', 'zone', 'defl', 'vt', 'cl')

MAX_WORKERS = 4    # number of parallel processes


def make_controls(control, random_sim=False):
    """Return six microscope controls (EMC), each with a different value of `control`.

    With `random_sim=True`, all six also share one set of randomized simulation controls
    (SIMC) instead of the defaults.
    """
    sim = SIMC.from_random() if random_sim else None

    emc_list = []
    for i in range(-3, 3):
        emc = EMC()
        if control == 'tilt':
            emc.tilt = (i * 0.5, 0.0)
        elif control == 'zone':
            emc.zone = (0, i, 1)
        elif control == 'defl':
            emc.defl = (i * 0.5, 0.0)
        elif control == 'vt':
            emc.vt = 200 + i * 10
        elif control == 'cl':
            emc.cl = 1000 + i * 50

        if sim is not None:
            emc.simc = sim
        emc_list.append(emc)

    return emc_list


def generate_kinematic_patterns(control='tilt', mode=DEF_MODE, name='Silicon',
                                random_sim=False):
    """Generate kinematic diffraction patterns, one per value of a microscope control.

    :param control: the microscope control to vary, one of CONTROLS.
    :param mode: the diffraction mode: 1 for normal, 2 for CBED.
    :param name: the name of a built-in crystal.
    :param random_sim: use randomized simulation controls instead of the defaults.
    :return: the patterns as a DPList, sorted by their microscope controls.
    """
    crystal = Crystal.from_builtin(name)
    disk_size = DEF_CBED_DSIZE if mode == 2 else None

    patterns = DPList(name, mode=mode)
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(crystal.generateDP, mode=mode, dsize=disk_size,
                                   em_controls=emc)
                   for emc in make_controls(control, random_sim)]

        for future in concurrent.futures.as_completed(futures):
            try:
                emc, pattern = future.result()
            except (DPError, EMCError) as e:
                sys.exit(f'Failed to generate a diffraction pattern: {e.message}')
            except Exception as e:
                sys.exit(f'Failed to generate a diffraction pattern: {e}')
            patterns.add(emc, pattern)

    patterns.sort()
    return patterns


def main():
    # CBED patterns, without Kikuchi lines or Miller indices. The tilt and zone axis series
    # are shown as tables, and the zone axis table is also saved as an image.
    for control in CONTROLS:
        patterns = generate_kinematic_patterns(control, mode=2)
        layout = 'table' if control in ('tilt', 'zone') else 'individual'
        showDif(patterns, layout=layout, kShow=False, iShow=False,
                bSave=(control == 'zone'), bClose=True)

    # Normal-mode patterns with randomized simulation controls.
    for control in CONTROLS:
        patterns = generate_kinematic_patterns(control, random_sim=True)
        showDif(patterns, bClose=True)


if __name__ == '__main__':
    main()
