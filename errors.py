

"""
.. This file is part of pyEMAPS

The exceptions pyEMAPS raises when input data is invalid or a calculation fails. Each one
has a ``message`` attribute with its error message.

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

.. Author:             EMLab Solutions, Inc.
.. Date Created:       June 28, 2022
"""

class pyemapsError(Exception):
    """
    Reserved for future use; not raised.
    """
    pass # reserved for later

    
class CrystalClassError(Exception):
    """
    Raised when a crystal can't be created, validated or loaded into the backend.
    """
    def __init__(self, message):
        self.message = str(f'Error creating pyemaps crystal object with message:\n{message}')
        super().__init__(self.message)

class XTLError(Exception):
    """
    Raised when a crystal data (``.xtl``) file can't be read or has invalid data.
    """
    def __init__(self, fn='', message=''):
        self.message = str(f'Error importing XTL file {fn}: {message}')
        super().__init__(self.message)

class CIFError(Exception):
    """
    Raised when a CIF file can't be read or has invalid data.
    """
    def __init__(self, fn='', message=''):
        self.message = str(f'Error importing CIF file {fn}: {message}')
        super().__init__(self.message)

class CellError(Exception): 
    """
    Base class for invalid cell constants.
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class CellValueError(CellError):
    """
    Raised when a cell length or angle is invalid.
    """
    def __init__(self, ty=0, cn=''):
        self.message = str(f'Invalid cell length value for {cn}') if ty ==1 else \
                       str(f'Invalid cell angle value for {cn}')
        super().__init__(self.message)

class CellDataError(CellError):
    """
    Raised when the cell constants as a whole are invalid.
    """
    def __init__(self, message = 'invalid cell data'):
        self.message = message
        super().__init__(self.message)

class SPGError(Exception):
    """
    Raised when space group data is invalid or can't be identified.
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class SPGITMumberNotInRangeError(SPGError):
    """
    Raised when a space group number is out of range.
    """
    def __init__(self, nummax):
        self.message = str(f'Space Group IT number is not in (1, {nummax}) range')
        super().__init__(self.message)

class SPGSettingNotInRangeError(SPGError):
    """
    Raised when a space group setting is out of range.
    """
    def __init__(self, setmax):
        self.set_max = setmax
        self.message = str(f'Space Group Setting is not in (1, {setmax}) range')
        super().__init__(self.message)

class SPGInvalidDataInputError(SPGError):
    """
    Raised when space group data has the wrong form.
    """
    def __init__(self, message = 'Invalid Space group data entered'):
        self.message = message
        super().__init__(self.message)

class UCError(Exception):
    """
    Raised when the atoms in the unit cell are invalid.
    """
    def __init__(self, message=''):
        self.message = str(f'Invalid unit cell data: {message}')
        super().__init__(self.message)

# Diffraction pattern errors
class DPError(Exception):
    """
    Raised when a kinematic diffraction pattern can't be generated or is invalid.
    """
    def __init__(self, message=''):
        self.message = str(f'Invalid diffraction pattern: {message}')
        super().__init__(self.message)

class PointError(DPError):
    """
    Raised when a :py:class:`~pyemaps.kdiffs.Point` is invalid.
    """
    def __init__(self, message=''):
        self.message = str(f'Error creating Point object: {message}')
        super().__init__(self.message)

class LineError(DPError):
    """
    Raised when a :py:class:`~pyemaps.kdiffs.Line` (Kikuchi or HOLZ line) is invalid.
    """
    def __init__(self, message=''):
        self.message = str(f'Error creating Line object: {message}')
        super().__init__(self.message)

class PIndexError(DPError):
    """
    Raised when an :py:class:`~pyemaps.kdiffs.Index` (Miller indices of a diffracted beam) is invalid.
    """
    def __init__(self, message=''):
        self.message = str(f'Error creating Index object: {message}')
        super().__init__(self.message)

class DiskError(DPError):
    """
    Raised when a :py:class:`~pyemaps.kdiffs.Disk` (diffracted beam) is invalid.
    """
    def __init__(self, message=''):
        self.message = str(f'Error creating Disk object: {message}')
        super().__init__(self.message)

class DPListError(Exception):
    """
    Raised when a list of diffraction patterns, :py:class:`DPList <pyemaps.kdiffs.Diffraction>`, is invalid.
    """
    def __init__(self, message=''):
        self.message = str(f'Error creating DP list: {message}')
        super().__init__(self.message)

class BlochError(Exception):
    """
    Raised when a dynamic diffraction simulation fails or its input is invalid.
    """
    def __init__(self, message=''):
        self.message = str(f'Error generating dynamic diffraction: {message}')
        super().__init__(self.message)

# EM controls

class EMCError(Exception):
    """
    Raised when microscope or simulation controls are invalid.
    """
    def __init__(self, message=''):
        self.message = str(f'Error creating EMC object: {message}')
        super().__init__(self.message)

class BlochListError(Exception):
    """
    Raised when a list of dynamic diffraction images, :py:class:`BImgList <pyemaps.ddiffs.BlochImgs>`, is invalid.
    """
    def __init__(self, message=''):
        self.message = str(f'Error creating blochList object: {message}')
        super().__init__(self.message)

class StereodiagramError(Exception):
    """
    Raised when a stereodiagram can't be generated.
    """
    def __init__(self, message=''):
        self.message = str(f'Error generating stereodiagram: {message}')
        super().__init__(self.message)

class MxtalError(Exception):
    """
    Raised when a crystal structure can't be built, or its data is invalid.
    """
    def __init__(self, message=''):
        self.message = str(f'Error generating mxtal: {message}')
        super().__init__(self.message)


class CSFError(Exception):
    """
    Raised when structure factors can't be calculated, or their input is invalid.
    """
    def __init__(self, message=''):
        self.message = str(f'Error generating structure factors: {message}')
        super().__init__(self.message)


class XDPImageError(Exception):
    """
    Raised when an experimental image (:py:class:`~pyemaps.stackimg.StackImage`) is invalid or can't be loaded or analyzed.
    """
    def __init__(self, message=''):
        self.message = str(f'{message}')
        super().__init__(self.message)
