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

    """
    An atom in a crystal structure: its element symbol and position.
    """
    def __init__(self, symb = "", coord=[0.0, 0.0, 0.0]):

        """
        :param symb: the element symbol.
        :type symb: str, optional
        :param coord: the position ``[x, y, z]``, in Å.
        :type coord: list or numpy.ndarray of three numbers, optional
        :raise ~pyemaps.errors.MxtalError: if *symb* isn't a string, or *coord* isn't three numbers.
        """
        setattr(self, 'symb', symb)
        setattr(self, 'coord', coord)

    @property
    def symb(self):

        """
        The element symbol.
        """
        return self._symb
    
    @property
    def coord(self):

        """
        The position ``[x, y, z]``, in Å.
        """
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
        r"""
        Two atoms are equal if they have the same symbol and their positions agree within
        10\ :sup:`-6`.
        """
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

    """
    A crystal structure, as built by :py:meth:`~pyemaps.crystals.Crystal.generateMxtal`: the
    cell constants of the block and a list of atoms.

    Index it like a list to get an atom, an :py:class:`~pyemaps.xtal.ACoord`. Printing it gives
    the structure in `XYZ format <https://wiki.jmol.org/index.php/File_formats/Formats/XYZ>`_.
    """
    def __init__(self):
        
        """
        Create an empty structure, with cell constants ``[0, 0, 0, 90, 90, 90]`` and no atoms.
        """
        setattr(self, 'cell', [0.0,0.0,0.0,90.0,90.0,90.0])
        setattr(self, 'acoordList', [])

    @property
    def cell(self):
        """
        The cell constants ``[a, b, c, alpha, beta, gamma]``: lengths in Å, angles in degrees.
        """
        return self._cell

    @property
    def acoordList(self):
        """
        The atoms, a list of :py:class:`~pyemaps.xtal.ACoord`.
        """
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
        """
        Add an atom to the structure.

        :param symb: the element symbol.
        :type symb: str
        :param c: the position ``[x, y, z]``, in Å.
        :type c: list or numpy.ndarray of three numbers
        :raise ~pyemaps.errors.MxtalError: if *symb* or *c* is invalid.
        """
        ac = ACoord(symb, c)
        self._acoordList.append(ac)
                
    def __getitem__(self, key):

        """
        Return the atom, or list of atoms, at *key*.
        """
        
        return self._acoordList[key]
    
    def __eq__(self, other):
        r"""
        Two structures are equal if their cell constants agree within 10\ :sup:`-6` and they have
        the same atoms, in any order.
        """
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
        """
        Return the structure in `XYZ format <https://wiki.jmol.org/index.php/File_formats/Formats/XYZ>`_:
        the number of atoms, the cell constants, then one line per atom with its symbol and
        position. For example, for silicon:

        .. code-block:: console

            216
                50.0 50.0 50.0 90.0 90.0 90.0
            SI        	 0.6788375000   0.6788375000   0.6788375000
            SI        	 3.3941875000   3.3941875000   0.6788375000
            SI        	 4.7518625000   2.0365125000   2.0365125000
            SI        	 2.0365125000   4.7518625000   2.0365125000
            SI        	 3.3941875000   0.6788375000   3.3941875000
            ...
        """
        
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