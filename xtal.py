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
.. Date:       Feb. 17, 2025    

'''

from . import MxtalError
import numpy as np

class ACoord:

    '''

    Coordinates of an atom with its symbol and 3-d real number coordinates in a crystal structure.
    
    '''
    def __init__(self, symb = "", coord=[0.0, 0.0, 0.0]):

        setattr(self, 'symb', symb)
        setattr(self, 'coord', coord)

    @property
    def symb(self):

        '''

        atom symbol

        '''
        return self._symb
    
    @property
    def coord(self):

        '''

        Atom coordinate in 3-d floating numbers

        '''
        return self._coord

    @symb.setter
    def symb(self, s):
        if s is None or not isinstance(s, str):
            raise MxtalError("Atomic symbol must be a string")
        self._symb=s

    @coord.setter
    def coord(self, v):
        
        if v is None or not isinstance(v, (list, np.ndarray)) or len(v) != 3 or not all(isinstance(x, (int, float)) for x in v):
            raise MxtalError("Atomic coordinates must be an array of three float or integer numerals")
        self._coord=v
    
    def __eq__(self, other):
        import numpy as np
        if not isinstance(other, ACoord):
            print(f'Comparing object must of type ACoord')
            return False
        
        if self._symb != other.symb:
            return False
        
        if not np.allclose(self._coord, other.coord, atol=1.0e-6):
            return False

        return True

    def __repr__(self):
        s, x, y, z = self._symb, self._coord[0], self._coord[1], self._coord[2]
        sx = '{0:<#014.10f}'. format(x)
        sy = '{0:<#014.10f}'. format(y)
        sz = '{0:<#014.10f}'. format(z)
        return str(f'{s:<10}\t{sx} {sy} {sz}')
    
    def __str__(self):
        return self.__repr__()
    
class Xtal:

    '''
    Crystal structure class cnostructed by the output from
    `generateMxtal <pyemaps.crystals.html#pyemaps.crystals.Crystal.generateMxtal>`_ method of any crystal object, which consists of a cell
    constant and a list of atomic coordinates.

    '''
    def __init__(self):
        
        setattr(self, 'cell', [0.0,0.0,0.0,90.0,90.0,90.0])
        setattr(self, 'acoordList', [])

    @property
    def cell(self):
        return self._cell

    @property
    def acoordList(self):
        return self._acoordList

    @cell.setter
    def cell(self, c):
        if c is None or not isinstance(c, (list, np.ndarray)) or len(c) != 6 or not all(isinstance(x, (int, float)) for x in c):  
            raise MxtalError('Invalid cell constants, it much be an array of six floats')

        self._cell = c

    @acoordList.setter
    def acoordList(self, al):
        if not isinstance(al, list):
            raise MxtalError('invalid input atomic structure coordinates, it must be a list')

        for a in al:
            if not isinstance(a, ACoord):
                raise MxtalError('invalid data found in atomic structure list')

        self._acoordList = al

    def add(self, symb, c):
        '''
        
        Append an atomc coordinate to existing list

        '''
        ac = ACoord(symb, c)
        self._acoordList.append(ac)
                
    def __getitem__(self, key):

        '''
        
        Array like method for retrieving atomic coordinates
        
        '''
        
        return self._acoordList[key]
    
    def __eq__(self, other):
        '''
        
        Overloading == operator for the atomic coordinates class

        '''
        import copy
        if not isinstance(other, Xtal):
            print("Comparing object of of invalid type")
            return False  
        
        nxtal1 = len(self._acoordList)
        nxtal2 = len(other.acoordList)

        if nxtal1 != nxtal2:
            return False
        
        if not np.allclose(self._cell, other.cell, atol=1.0e-6):
            return False
        
        clist = copy.deepcopy(self._acoordList)
        for ac in other.acoordList:
            if not ac in clist:
                return False
            clist.remove(ac)

        return True

    def __repr__(self):
        '''
        Present atomic stucture data in .xyz format in standard output. 
        Refer to `XYZ format <https://wiki.jmol.org/index.php/File_formats/Formats/XYZ>`_
        for its definition and usage.
        
        .. note:: An example of Silicon atomic structure by pyemaps:
            
        .. code-block:: console

            216
                50.0 50.0 50.0 90.0 90.0 90.0
            SI        	 0.6788375000   0.6788375000   0.6788375000 
            SI        	 3.3941875000   3.3941875000   0.6788375000 
            SI        	 4.7518625000   2.0365125000   2.0365125000 
            SI        	 2.0365125000   4.7518625000   2.0365125000 
            SI        	 3.3941875000   0.6788375000   3.3941875000 
            ...

        '''
        
        slines = []
        nxyz = len(self._acoordList)
        slines.append(str(nxyz))     

        c0, c1, c2, c3, c4, c5 = self._cell
        slines.append(str(f'\t {c0} {c1} {c2} {c3} {c4} {c5}'))

        for ac in self._acoordList:
            slines.append(str(ac))

        ret = '\n'.join(slines)
        return ret   

    def __str__(self):
        return self.__repr__()