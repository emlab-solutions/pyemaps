
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