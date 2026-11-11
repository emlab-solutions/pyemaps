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

BLOCH_TOLERANCE = 1.0e-04

class BlochImgs:

    """
    A list of dynamic diffraction (Bloch) images, each paired with the microscope controls it
    was simulated with, including its sample thickness. Returned by
    :py:meth:`~pyemaps.crystals.Crystal.generateBloch` and
    :py:meth:`~pyemaps.crystals.Crystal.getBlochImages`, and displayed by
    :py:func:`~pyemaps.display.showBloch`. It's also available as ``BImgList``.

    .. code-block:: python

        for emc, img in bloch_imgs:
            print(emc.simc.sth, img.shape)     # thickness (Å) and image size
    """
    def __init__(self, name):
        
        """
        :param name: the crystal's name.
        :type name: str, required
        :raise ~pyemaps.errors.BlochListError: if *name* is empty.
        """
        setattr(self, 'name', name)
        setattr(self, 'blochList', [])

    @property
    def name(self):
        """
        The crystal's name.
        """
        return self._name

    @property
    def blochList(self):
        """
        The images, as a list of ``(controls, image)`` tuples; each image is a 2-D numpy array.
        """
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
        """
        Add an image, with the controls it was simulated with.

        :param emc: the controls.
        :type emc: :py:class:`~pyemaps.emcontrols.EMControl`, required
        :param b: the image.
        :type b: 2-D numpy.ndarray, required
        :raise ~pyemaps.errors.BlochListError: if *emc* isn't an EMControl or *b* isn't a 2-D array.
        """
        if not isinstance(emc, EMC) or \
           not hasattr(b, "__len__") or \
           b.ndim != 2:
            raise BlochListError('failed to add Bloch image object')

        self._blochList.append((emc, b))
    
    def sort(self):

        """
        Sort the images by their controls.
        """
        self._blochList.sort(key=lambda x: x[0])
                
    def __getitem__(self, key):

        """
        Return the ``(controls, image)`` tuple at *key*.
        """
        
        return self._blochList[key]
    
    def __contains__(self, emc, b):
        """
        Return ``True`` if the list has an image with controls equal to *emc* and pixels within
        1e-4 of *b*. Used by ``==``.
        """
        if not isinstance(emc, EMC) or \
           not hasattr(b, "__len__") or \
           b.ndim != 2:
            raise BlochListError('invalid Bloch image object')
        
        import numpy as np
        
        shape_given = b.shape
        
        for (e,c) in self._blochList:
            if e != emc or c.shape != shape_given:
                continue
            if np.allclose(c, b, atol=BLOCH_TOLERANCE): 
                return True
        
        return False
    
    def __eq__(self, other):
        """
        Return ``True`` if both lists have the same name and matching images.
        """
        if len(self._blochList) != len(other.blochList):
            print(f'Dimension of bloch image differs')
            return False
        
        if self._name != other._name:
            print(f'Name of bloch image differs')
            return False
        
        if len(self._blochList) != len(other.blochList):
            return False
        
        for (e,b) in self._blochList:
            if not other.__contains__(e,b):
                print(f'Current bloch image differs from baseline')
                return False
        return True
