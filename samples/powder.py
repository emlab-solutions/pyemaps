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
