# This file is part of pyEMAPS.
# Copyright (C) 2021-2026 EMLab Solutions, Inc.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Additional permission under GPLv3 Section 7:
# See license-exception.txt for the exception permitting
# combination with the separately licensed backend, emaps.

'''
.. Author:             EMLab Solutions, Inc.
.. Date Created:       May 07, 2022  
'''
import re
from . import sct
sct_symbtable = re.split(r'\s+', sct.elnams.tobytes().decode().strip())
sct_cifsymbtable = re.split(r'\s+', sct.cifelnams.tobytes().decode().strip())

