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

"""Electron powder diffraction for Silicon and Diamond.

This sample generates the powder diffraction profiles of Silicon, and of Diamond with
absorption, and plots them side by side.

Run it with:

    python powder.py
"""
from pyemaps import Crystal, plot2Powder


def generate_powder_profiles(verbose=True):
    """Generate the powder diffraction profiles of Silicon and Diamond.

    :param verbose: print the two crystals.
    :return: the Silicon profile and the Diamond profile (with absorption).
    """
    silicon = Crystal.from_builtin('Silicon')
    if verbose:
        print(silicon)
    silicon_profile = silicon.generatePowder()

    diamond = Crystal.from_builtin('Diamond')
    if verbose:
        print(diamond)
    diamond_profile = diamond.generatePowder(absp=1)

    return silicon_profile, diamond_profile


def main():
    silicon_profile, diamond_profile = generate_powder_profiles()
    plot2Powder(silicon_profile, diamond_profile,
                titles=('Silicon', 'Diamond'),
                ylabels=('Intensity', 'Intensity with absorption'))


if __name__ == '__main__':
    main()
