

'''
.. This file is part of pEMAPS

Error module for handling various pyemaps data validation and calculation
failures.

.. note:: 

    This module is still in active development and improvements.

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

'''

class pyemapsError(Exception):
    pass # reserved for later

    
class CrystalClassError(Exception):
    '''
    Crystal object creation, validation and loading errors.
        
    '''
    def __init__(self, message):
        self.message = str(f'Error creating pyemaps crystal object with message:\n{message}')
        super().__init__(self.message)

class XTLError(Exception):
    '''
    XTL crystal data import errors.

    '''
    def __init__(self, fn='', message=''):
        self.message = str(f'Error importing XTL file {fn}: {message}')
        super().__init__(self.message)

class CIFError(Exception):
    '''
    CIF crystal data import errors.
    
    '''
    def __init__(self, fn='', message=''):
        self.message = str(f'Error importing CIF file {fn}: {message}')
        super().__init__(self.message)

class CellError(Exception): 
    '''
    Cell constant data validation errors.
    
    '''
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class CellValueError(CellError):
    '''
    Details of cell constant data validation errors.
    
    '''
    def __init__(self, ty=0, cn=''):
        self.message = str(f'Invalid cell length value for {cn}') if ty ==1 else \
                       str(f'Invalid cell angle value for {cn}')
        super().__init__(self.message)

class CellDataError(CellError):
    '''
    Details of cell constant data validation errors.
    
    '''
    def __init__(self, message = 'invalid cell data'):
        self.message = message
        super().__init__(self.message)

class SPGError(Exception):
    '''
    Space group data validation errors.
    
    '''
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class SPGITMumberNotInRangeError(SPGError):
    '''
    Space group IT number validation errors.
    
    '''
    def __init__(self, nummax):
        self.message = str(f'Space Group IT number is not in (1, {nummax}) range')
        super().__init__(self.message)

class SPGSettingNotInRangeError(SPGError):
    '''
    Space group setting validation errors.
    
    '''
    def __init__(self, setmax):
        self.set_max = setmax
        self.message = str(f'Space Group Setting is not in (1, {setmax}) range')
        super().__init__(self.message)

class SPGInvalidDataInputError(SPGError):
    '''
    Space group setting validation errors. Duplicate of SPGError.
    
    '''
    def __init__(self, message = 'Invalid Space group data entered'):
        self.message = message
        super().__init__(self.message)

class UCError(Exception):
    '''
    Atomc data validation errors.
    
    '''
    def __init__(self, message=''):
        self.message = str(f'Invalid unit cell data: {message}')
        super().__init__(self.message)

# Diffraction pattern errors
class DPError(Exception):
    '''
    Kinematic diffraction pattren object creation errors.
    
    '''
    def __init__(self, message=''):
        self.message = str(f'Invalid diffraction pattern: {message}')
        super().__init__(self.message)

class PointError(DPError):
    '''
    Detailed kinematic diffraction pattren object creation errors on 
    Point object creation.
    
    '''
    def __init__(self, message=''):
        self.message = str(f'Error creating Point object: {message}')
        super().__init__(self.message)

class LineError(DPError):
    '''
    Detailed kinematic diffraction pattren object creation errors on 
    Line (Kikuchi or HOLZ) object creation.
    
    '''
    def __init__(self, message=''):
        self.message = str(f'Error creating Line object: {message}')
        super().__init__(self.message)

class PIndexError(DPError):
    '''
    Detailed kinematic diffraction pattren object creation errors on 
    Dfffracted beams Miller index object creation.
    
    '''
    def __init__(self, message=''):
        self.message = str(f'Error creating Index object: {message}')
        super().__init__(self.message)

class DiskError(DPError):
    '''
    Detailed kinematic diffraction pattren object creation errors on 
    Dfffracted beams object creation.
    
    '''
    def __init__(self, message=''):
        self.message = str(f'Error creating Disk object: {message}')
        super().__init__(self.message)

class DPListError(Exception):
    '''
    List of diffraction patterns create errors.
    
    '''
    def __init__(self, message=''):
        self.message = str(f'Error creating DP list: {message}')
        super().__init__(self.message)

class BlochError(Exception):
    '''
    Dynamic diffraction pattern generation, creation and validation errors.
    
    '''
    def __init__(self, message=''):
        self.message = str(f'Error generating dynamic diffraction: {message}')
        super().__init__(self.message)

# EM controls

class EMCError(Exception):
    '''
    Microscope controls objects creation and validation errors.
    
    '''
    def __init__(self, message=''):
        self.message = str(f'Error creating EMC object: {message}')
        super().__init__(self.message)

class BlochListError(Exception):
    '''
    List of yynamic diffraction patterns errors.
    
    '''
    def __init__(self, message=''):
        self.message = str(f'Error creating blochList object: {message}')
        super().__init__(self.message)

class StereodiagramError(Exception):
    '''
    Stereodiagram generation errors.
    
    '''
    def __init__(self, message=''):
        self.message = str(f'Error generating stereodiagram: {message}')
        super().__init__(self.message)

class MxtalError(Exception):
    '''
    Crystal construction simulation errors.
    
    '''
    def __init__(self, message=''):
        self.message = str(f'Error generating mxtal: {message}')
        super().__init__(self.message)


class XDPImageError(Exception):
    '''
    Experimental diffraction pattern image object errors.
    
    '''
    def __init__(self, message=''):
        self.message = str(f'{message}')
        super().__init__(self.message)
