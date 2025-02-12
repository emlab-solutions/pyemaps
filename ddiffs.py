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

.. Author:     EMLab Solutions, Inc.
.. Date:       July 17, 2022    

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
    
    def sort(self):

        '''

        Sort the bloch simulation results by controls

        '''
        self._blochList.sort(key=lambda x: x[0])
                
    def __getitem__(self, key):

        '''

        Array like method for retrieving DP
        
        '''
        
        return self._blochList[key]
    
    def __contains__(self, emc, b):
        '''

        Given a dynamic image in 2-d array and corresponding simulation controls,
        test if the pair is part of dynamic diffraction paterns list. Internal
        function used for == operator overload.

        '''
        if not isinstance(emc, EMC) or \
           not hasattr(b, "__len__") or \
           b.ndim != 2:
            raise BlochListError('failed to add Bloch image object')
        
        import numpy as np
        for (e,c) in self._blochList:
            if e == emc and np.allclose(c, b, atol=1e-6): return True
        return False
    
    def __eq__(self, other):
        '''
        
        Overloading == operator for the class

        '''
        if self._name != other._name:
            return False
        for (e,b) in self._blochList:
            if not other.__contains__(e,b):
                return False
        for (e,b) in other._blochList:
            if not self.__contains__(e,b):
                return False
        return True
