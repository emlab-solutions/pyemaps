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

"""A first look at pyEMAPS with Silicon: the sample that ``pyemaps -s`` runs.

It loads Silicon from the built-in crystals, generates and displays its kinematic diffraction
pattern in normal and CBED modes, then generates and displays its dynamic (Bloch wave)
diffraction pattern, all with the default microscope controls.

See https://emlab-solutions.github.io/pyemaps/ for the pyEMAPS documentation.
"""
from pyemaps import Crystal, DPList, showBloch, showDif


def run_sample(name='Silicon'):
    """Generate and display a crystal's kinematic and dynamic diffraction patterns."""
    crystal = Crystal.from_builtin(name)

    # Kinematic diffraction in normal mode. generateDP also returns the microscope
    # controls it used, which DPList keeps with the pattern.
    patterns = DPList(name)
    emc, pattern = crystal.generateDP()
    patterns.add(emc, pattern)

    showDif(patterns, bClose=True)                  # everything
    showDif(patterns, kShow=False, bClose=True)     # without Kikuchi lines

    # Kinematic diffraction in CBED mode (mode 2).
    patterns = DPList(name, mode=2)
    emc, pattern = crystal.generateDP(mode=2)
    patterns.add(emc, pattern)

    # Without Kikuchi lines or Miller indices, then without Miller indices only.
    showDif(patterns, kShow=False, iShow=False, bClose=True)
    showDif(patterns, iShow=False, bClose=True)

    # Dynamic diffraction.
    try:
        images = crystal.generateBloch(sampling=20)
    except Exception as e:
        print(f'Failed to generate the dynamic diffraction pattern: {e}')
        return

    showBloch(images, bClose=True)                  # grey scale
    showBloch(images, bColor=True, bClose=True)     # with a color map


if __name__ == '__main__':
    run_sample()
