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

"""A diffraction pattern database for Aluminium.

This sample uses pyEMAPS' dpgen module to generate a database of diffraction patterns for
Aluminium, around the [001] zone axis. The stem4d module searches such a database to index
experimental diffraction pattern images; see al_ediom.py.

It needs an activated pyEMAPS license; see the License page of the pyEMAPS documentation.
Contact support@emlabsoftware.com for license information.

Run it with:

    python al_dpgen.py
"""
import os

from pyemaps import EMC, SIMC, Crystal


def generate_database(name='Aluminium'):
    """Generate a diffraction pattern database for a crystal.

    :param name: the name of a built-in crystal.
    :return: the database file name, or None if the database couldn't be generated.
    """
    crystal = Crystal.from_builtin(name)
    emc = EMC(zone=(0, 0, 1), simc=SIMC(gmax=3.9))

    ret, db_file = crystal.generateDPDB(emc=emc,
                                        xa=(2, 0, 0),   # the x-axis of the patterns
                                        res=200)        # the database resolution

    if ret != 0 or db_file is None or not os.path.exists(db_file):
        print('Failed to generate the diffraction pattern database')
        return None
    return db_file


def main():
    generate_database()


if __name__ == '__main__':
    main()
