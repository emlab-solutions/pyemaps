'''
This file is part of pyemaps
___________________________

pyemaps is free software for non-comercial use: you can 
redistribute it and/or modify it under the terms of the GNU General 
Public License as published by the Free Software Foundation, either 
version 3 of the License, or (at your option) any later version.

pyemaps is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pyemaps.  If not, see <https://www.gnu.org/licenses/>.

Contact supprort@emlabsoftware.com for any questions and comments.
___________________________



Author:     EMLab Solutions, Inc.
Date:       July 17, 2022    
'''

from . import EMC
from . import BlochListError
class BlochImgs:
    '''
    list of Bloch image objects and its associated controls 
    '''
    def __init__(self, name):
        
        setattr(self, 'name', name)
        setattr(self, 'blochList', [])

    @property
    def name(self):
        return self._name

    @property
    def blochList(self):
        return self._blochList

    @name.setter
    def name(self, n):
        if not isinstance(n, str) or len(n) == 0:
            raise BlochListError('crystal name invalid')
        
        self._name = n

    @blochList.setter
    def blochList(self, bl):
        if not isinstance(bl, list):
            raise BlochListError('invalid input DP list')

        for emc, b in bl:
            if not isinstance(emc, EMC) or \
                not hasattr(b, "__len__") or \
                b.ndim != 2:
                raise BlochListError('invalid data found in bloch imgage list')

        self._blochList = bl

    # Adding new diffraction patterns
    def add(self, emc, b):
        if not isinstance(emc, EMC) or \
           not hasattr(b, "__len__") or \
           b.ndim != 2:
            raise BlochListError('failed to add Bloch image object')

        self._blochList.append((emc, b))
    
            
    def __getitem__(self, key):
        '''
        Array like method for retrieving DP
        '''
        return self._blochList[key]
