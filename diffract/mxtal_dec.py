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


Author:             EMLab Solutions, Inc.
Date Created:       May 07, 2022  

'''
def add_mxtal(target):
    from . import dif
    from .. import (ID_MATRIX, MLEN, DEF_CELLBOX, 
                   DEF_XZ, DEF_ORSHIFT, DEF_TRSHIFT,
                   DEF_LOCASPACE)
    from .. import MxtalError
    from ..fileutils import compose_ofn
    from ..xtal import Xtal
    
    @staticmethod
    def printXYZ( mx):
        """
        Print a crystal structure from :py:meth:`~pyemaps.crystals.Crystal.generateMxtal` in XYZ format. See
        `XYZ format <https://wiki.jmol.org/index.php/File_formats/Formats/XYZ>`_.

        :param mx: the crystal structure.
        :type mx: :py:class:`~pyemaps.xtal.Xtal`, required
        :raise ~pyemaps.errors.MxtalError: if *mx* isn't an Xtal.

        Example output for Silicon:

        .. code-block:: console

            216
                50.0 50.0 50.0 90.0 90.0 90.0
            SI        	 0.6788375000   0.6788375000   0.6788375000
            SI        	 3.3941875000   3.3941875000   0.6788375000
            SI        	 4.7518625000   2.0365125000   2.0365125000
            ...
        """
        if not isinstance(mx, Xtal): 
            raise MxtalError("The print object is not valid atomic structure object.")
        print(f'{str(mx)}')

    def writeXYZ(self, mx, fn=None):
        """
        Save a crystal structure from :py:meth:`~pyemaps.crystals.Crystal.generateMxtal` to an XYZ file, which tools such as
        Jmol can open.

        :param mx: the crystal structure.
        :type mx: :py:class:`~pyemaps.xtal.Xtal`, required
        :param fn: file name, without the ``.xyz`` extension, which is added. If omitted, a name is
            composed from the crystal name. Without a directory, the file goes in the ``mxtal``
            folder of the pyEMAPS data folder; see :ref:`Environment Variables <Environment Variables>`.
        :type fn: str, optional
        :return: 0 on success, -1 if the file can't be written.
        :rtype: int
        :raise ~pyemaps.errors.MxtalError: if *mx* isn't an Xtal.
        """
        
        if not isinstance(mx, Xtal): 
            raise MxtalError("The print object is not valid atomic structure object.")
        

        xyzfn = compose_ofn(fn, self.name, ty='mxtal') +'.xyz'
        
        try:
            with open(xyzfn, 'w') as f:
                f.writelines(str(mx))
        except (FileNotFoundError, IOError, PermissionError) as e:
            print(f'Error writing xyz data file {fn}')
            return -1
        except Exception:
            return -1
        else:
            print(f'Successfully saved mxtal data in file: {xyzfn}')
            return 0

    def generateMxtal(self, 
                      trMatrix = ID_MATRIX, 
                      trShift = DEF_TRSHIFT, #Transformation shift
                      cellbox = DEF_CELLBOX,
                      xz = DEF_XZ,
                      orShift = DEF_ORSHIFT, #Origin shift
                      locASpace = DEF_LOCASPACE,
                      bound = None): #location in A Space
        """
        Build a block of the crystal's atomic structure (a supercell) from its unit cell.

        :param trMatrix: 3 × 3 matrix that transforms the unit cell into the new cell. Defaults to
            the identity matrix.
        :type trMatrix: list or array, optional
        :param trShift: origin shift of the transformation, three numbers. Defaults to
            ``[0, 0, 0]``.
        :type trShift: list or array, optional
        :param cellbox: the range of cells to fill, as ``[[x0, y0, z0], [x1, y1, z1]]`` in cell
            units. Defaults to ``[[0, 0, 0], [3, 3, 3]]``.
        :type cellbox: list or array, optional
        :param xz: two real-space directions, ``[x_direction, z_direction]``, to align with the
            output's x and z axes. Defaults to ``[[1, 0, 0], [0, 0, 1]]``.
        :type xz: list or array, optional
        :param orShift: shift added to the atom positions in cell coordinates, before they're
            oriented. Defaults to ``[0, 0, 0]``.
        :type orShift: list or array, optional
        :param locASpace: shift added to the final atom positions, in Å. Defaults to ``[0, 0, 0]``.
        :type locASpace: list or array, optional
        :param bound: if given, also include atoms up to this distance, in Å, outside the cell
            range.
        :type bound: float, optional
        :return: the atomic structure.
        :rtype: :py:class:`~pyemaps.xtal.Xtal`
        :raise ~pyemaps.errors.MxtalError: if the structure can't be built or retrieved.

        To print or save the result, use :py:meth:`~pyemaps.crystals.Crystal.printXYZ` or :py:meth:`~pyemaps.crystals.Crystal.writeXYZ`.
        """
        import numpy as np
        from numpy import asfortranarray as farray
        from . import mxtal as MX

        dif.initcontrols()
        
        self.load(cty=1)
            
        tmat = farray(np.array(trMatrix))
        
        pxz = farray(np.array(xz))

        if bound is not None:
            ret = MX.do_mxtal(tmat, trShift, cellbox[0], cellbox[1],
                            pxz[0], pxz[1], orShift, locASpace, bound)
        else:
            ret = MX.do_mxtal(tmat, trShift, cellbox[0], cellbox[1],
                            pxz[0], pxz[1], orShift, locASpace)
        
        if ret != 1:
            raise MxtalError('Failed to starting mxtal module')
        
        na = MX.get_nxyz()
        
        if na <=0:
            raise MxtalError('Failed to generate data')

        xyz, ret = MX.get_xyzdata(na)
    
        if ret != 1:
            raise MxtalError('Failed to retrieve data')

        sym = farray(np.empty((MLEN, na), dtype='c'))
        sym, ret = MX.get_symdata(sym)
    
        if ret != 1:
            raise MxtalError('Failed to retrieve data')

        tsym = np.transpose(sym)
        txyz = np.transpose(xyz)
        
        mx = Xtal()
        for i in range(na):          
            s = bytearray(tsym[i]).decode('utf-8').strip(" \x00")
            
            mx.add(s, txyz[i])

        nc = 6
        cell, ret = MX.get_cellconst(nc)
        
        mx.cell = cell

        if ret !=0:
            raise MxtalError(f'Failed to retrieve cell constants: {ret}')

        # clean up
        MX.cleanup()
        return mx

    target.generateMxtal = generateMxtal
    target.printXYZ = printXYZ
    target.writeXYZ =writeXYZ
    return target
