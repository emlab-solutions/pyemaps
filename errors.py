

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


Author:             EMLab Solutions, Inc.
Date Created:       June 28th, 2022  

'''
class pyemapsError(Exception):
    pass # reserved for later

    
class CrystalClassError(Exception):
    def __init__(self, message):
        self.message = str(f'Error creating pyemaps crystal object with message:\n{message}')
        super().__init__(self.message)

class XTLError(Exception):
    def __init__(self, fn='', message=''):
        self.message = str(f'Error importing XTL file {fn}: {message}')
        super().__init__(self.message)

class CIFError(Exception):
    def __init__(self, fn='', message=''):
        self.message = str(f'Error importing CIF file {fn}: {message}')
        super().__init__(self.message)

class CellError(Exception): 
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class CellValueError(CellError):
    def __init__(self, ty=0, cn=''):
        self.message = str(f'Invalid cell length value for {cn}') if ty ==1 else \
                       str(f'Invalid cell angle value for {cn}')
        super().__init__(self.message)

class CellDataError(CellError):
    def __init__(self, message = 'invalid cell data'):
        self.message = message
        super().__init__(self.message)

class SPGError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class SPGITMumberNotInRangeError(SPGError):
    def __init__(self, nummax):
        self.message = str(f'Space Group IT number is not in (1, {nummax}) range')
        super().__init__(self.message)

class SPGSettingNotInRangeError(SPGError):
    def __init__(self, setmax):
        self.set_max = setmax
        self.message = str(f'Space Group Setting is not in (1, {setmax}) range')
        super().__init__(self.message)

class SPGInvalidDataInputError(SPGError):
    def __init__(self, message = 'Invalid Space group data entered'):
        self.message = message
        super().__init__(self.message)

class UCError(Exception):
    def __init__(self, message=''):
        self.message = str(f'Invalid unit cell data: {message}')
        super().__init__(self.message)

# Diffraction pattern errors
class DPError(Exception):
    def __init__(self, message=''):
        self.message = str(f'Invalid diffraction pattern: {message}')
        super().__init__(self.message)

class PointError(DPError):
    def __init__(self, message=''):
        self.message = str(f'Error creating Point object: {message}')
        super().__init__(self.message)

class LineError(DPError):
    def __init__(self, message=''):
        self.message = str(f'Error creating Line object: {message}')
        super().__init__(self.message)

class PIndexError(DPError):
    def __init__(self, message=''):
        self.message = str(f'Error creating Index object: {message}')
        super().__init__(self.message)

class DiskError(DPError):
    def __init__(self, message=''):
        self.message = str(f'Error creating Disk object: {message}')
        super().__init__(self.message)

class DPListError(Exception):
    def __init__(self, message=''):
        self.message = str(f'Error creating DP list: {message}')
        super().__init__(self.message)

class BlochError(Exception):
    def __init__(self, message=''):
        self.message = str(f'Error generating dynamic diffraction: {message}')
        super().__init__(self.message)

# EM controls

class EMCError(Exception):
    def __init__(self, message=''):
        self.message = str(f'Error creating EMC object: {message}')
        super().__init__(self.message)

class EMSIMError(Exception):
    def __init__(self, message=''):
        self.message = str(f'Error creating simulation control object: {message}')
        super().__init__(self.message)


class BlochListError(Exception):
    def __init__(self, message=''):
        self.message = str(f'Error creating blochList object: {message}')
        super().__init__(self.message)