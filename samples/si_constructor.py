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
