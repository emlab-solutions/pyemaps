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

"""A Silicon supercell, saved as an .xyz file.

This sample builds a supercell of Silicon with pyEMAPS' mxtal module, prints its atoms, and
saves it as an .xyz file, which viewers such as Jmol can display.

Run it with:

    python si_constructor.py
"""
from pyemaps import Crystal, CrystalClassError, MxtalError


def build_supercell(name='Silicon', verbose=True, save=True):
    """Build a supercell of a crystal with the default cell box (3 x 3 x 3 unit cells).

    :param name: the name of a built-in crystal.
    :param verbose: print the crystal and the supercell's atoms.
    :param save: save the supercell as an .xyz file.
    :return: the supercell, or None if it couldn't be built.
    """
    crystal = Crystal.from_builtin(name)
    if verbose:
        print(f'Crystal data used to build the supercell:\n{crystal}')

    try:
        supercell = crystal.generateMxtal(bound=0.1)
    except (CrystalClassError, MxtalError) as e:
        print(f'Failed to build the supercell: {e.message}')
        return None

    if verbose:
        print(f'\nSupercell of {name}:')
        crystal.printXYZ(supercell)
    if save:
        crystal.writeXYZ(supercell)
    return supercell


def main():
    build_supercell()


if __name__ == '__main__':
    main()
