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
Date Created:       May 07, 2022  

'''
from . import spgseek as spgra

SPG_SYMMETRY_MAXCOL = spgra.getsymmetrymaxlen() #48

SPG_SETTING_MAX = spgra.getspgallsettingmax() #6

SPG_SYMMETRY_MAXLEN = spgra.getsymmetryitemlen() #20

SPG_ITNUM_MAX = spgra.getspgitnum() #234

SPG_ENTRY_MAX = spgra.getspgentrynum() #310

def get_settingmax(num):
    return spgra.getspgsettingmax(num)

def get_settingmax(num):
    return spgra.getspgsettingmax(num)

def lookuphm(inum):
    return(spgra.getspghm(inum))

def getsymmetryxyz(sp, coords):
    return spgra.getsymmetryxyz(sp[0], sp[1], coords)

def validateSPG(num, iset):
    if num < 1 or num > SPG_ITNUM_MAX:
        return False

    setting_max = get_settingmax(num)

    if iset <1 or iset > setting_max:    
        return False
    
    return True