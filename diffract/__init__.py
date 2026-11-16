# This file is part of pyEMAPS.
# Copyright (C) 2021-2026 EMLab Solutions, Inc.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Additional permission under GPLv3 Section 7:
# See license-exception.txt for the exception permitting
# combination with the separately licensed backend, emaps.
# import all pyemaps simulation modules
try:
    from emaps import dif
except ImportError as e:
    print(f'Failed to find pyemas simulation modules')
    print(f'Please make sure emaps python package is installed')
    raise ValueError('')

#check other modules existence
try:
    from emaps import dpgen

except ImportError as e:
    pass

try:
    from emaps import csf

except ImportError as e:
    pass

try:
    from emaps import powder

except ImportError as e:
    pass

try:
    from emaps import bloch

except ImportError as e:
    pass

try:
    from emaps import stereo

except ImportError as e:
    pass


try:
    from emaps import mxtal

except ImportError as e:
    print(f'no mxtal module found in simulation module')
    