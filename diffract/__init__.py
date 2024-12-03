'''
.. This file is part of pyEMAPS
 
.. ----

.. pyEMAPS is free software. You can redistribute it and/or modify 
.. it under the terms of the GNU General Public License as published 
.. by the Free Software Foundation, either version 3 of the License, 
.. or (at your option) any later version..

.. pyEMAPS is distributed in the hope that it will be useful,
.. but WITHOUT ANY WARRANTY; without even the implied warranty of
.. MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
.. GNU General Public License for more details.

.. You should have received a copy of the GNU General Public License
.. along with pyEMAPS.  If not, see `<https://www.gnu.org/licenses/>`_.

.. Contact supprort@emlabsoftware.com for any questions and comments.

.. ----

'''

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
    