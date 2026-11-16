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

"""Crystal structure factors for Silicon.

This sample calculates Silicon's structure factors of every type, at 100 kV and for
reflections with sin(θ)/λ up to 1.0 1/Å, in both output formats, and prints them.

Run it with:

    python si_csf.py
"""
from pyemaps import Crystal

# Structure factor types (the sftype argument of generateCSF).
SF_TYPES = {
    1: 'X-ray structure factors',
    2: 'electron structure factors, in volts',
    3: 'electron structure factors, in 1/Å²',
    4: 'electron absorption structure factors, in 1/Å²',
}

# Output formats (the aptype argument of generateCSF).
AP_TYPES = {
    1: 'amplitude and phase',
    0: 'real and imaginary parts',
}


def generate_structure_factors(name='Silicon', verbose=True):
    """Calculate a crystal's structure factors of every type, in both output formats.

    :param name: the name of a built-in crystal.
    :param verbose: print the crystal and each set of structure factors.
    :return: a dictionary of the structure factors, keyed by (sftype, aptype).
    """
    crystal = Crystal.from_builtin(name)
    if verbose:
        print(crystal)

    results = {}
    for sftype in SF_TYPES:
        for aptype in AP_TYPES:
            sfs = crystal.generateCSF(kv=100, smax=1.0, sftype=sftype, aptype=aptype)
            results[(sftype, aptype)] = sfs
            if verbose:
                crystal.printCSF(sfs)

    return results


def main():
    generate_structure_factors()


if __name__ == '__main__':
    main()
