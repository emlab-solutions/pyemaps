
"""
.. This file is part of pyemaps

Fileutils is a helper module in assisting pyemaps file i/o functions.
Its methods include reading crystal data files and writing simulation 
output files. 

It also detects pyemaps data home environment variables and directs
file i/o accoridng to the rule set in :ref:`Environment Variables <Environment Variables>`.

 
.. ----

.. pyemaps is free software. You can redistribute it and/or modify 
.. it under the terms of the GNU General Public License as published 
.. by the Free Software Foundation, either version 3 of the License, 
.. or (at your option) any later version..

.. pyemaps is distributed in the hope that it will be useful,
.. but WITHOUT ANY WARRANTY; without even the implied warranty of
.. MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
.. GNU General Public License for more details.

.. You should have received a copy of the GNU General Public License
.. along with pyemaps.  If not, see `<https://www.gnu.org/licenses/>`_.

.. Contact supprort@emlabsoftware.com for any questions and comments.

.. ----

.. Author:     EMLab Solutions, Inc.
.. Date:       September 26th, 2022    

"""


from pathlib import Path
import os
import re

# ------------------pyemaps data file and locations-------------
#             set by PYEMAPS_DATAHOME 
#             -- location to retrieve data and put darta
# 


pyemaps_datahome = None

def find_datahome():
    bLegacy = False
    if 'PYEMAPS_CRYSTALS' in os.environ:
        bLegacy = True

    env_name = 'PYEMAPS_CRYSTALS' if bLegacy else 'PYEMAPS_DATA'

    # defaults to current working directory
    datahome = os.getcwd()

    # but find pyeamsp home if exists
    if env_name in os.environ:
        pyemaps_home = os.getenv(env_name)
        
        if Path(pyemaps_home).exists(): 
            datahome = pyemaps_home
        else:
            try:
                os.mkdir(pyemaps_home)

            except OSError:
                # can't create the directory, fall back to current directory
                pass
            else:
                datahome = pyemaps_home
                   
    return datahome


def auto_fn(cn):
    '''
    Auto-generate file name based on crystal name and time stamp
    when file is generated from pyemaps simulations.

    This can be modified to tune the output to any other specific needs.

    :param cn: A crystal name.
    :type cn: string, required

    :return: file name composed of crytsal name and time stamp in yyyymmddmmss format
    rtype: string

    '''
    import datetime

    curr_time  = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    return cn + '-' + curr_time

def find_pyemaps_datahome(home_type='crystals'):
    '''
    Detects enviroment variable set by PYEMAPS_DATA and return the
    diretcory set by the variable or return current working directory.
    
    :param home_type: Type of home directory
    :type home_type: string, optional
    
    :return: data home path.
    :rtype: string

    Folder names depending by *home_type* input:

    1. **crystals**: all crystal data files.
    2. **bloch**: all dynamic simulation output files.
    3. **mxtal**: all .xyz files saved from crystal constructor.
    4. **stereo**: all .png files saved from stereodiagram plotting methods

    '''
    # pyemaps_datahome = ''
    # if home_type='crystals' and 'PYEMAPS_CRYSTALS' in os.environ:
    #     pyemaps_datahome = os.getenv('PYEMAPS_CRYSTALS')

    #
    # defaults to current working directory
    # bLegacy = False
    # if 'PYEMAPS_CRYSTALS' in os.environ:
    #     bLegacy = True
    
    # env_name = 'PYEMAPS_CRYSTALS' if bLegacy else 'PYEMAPS_DATA'

    # # defaults to current working directory
    # pyemaps_datahome = os.getcwd()

    # # but find pyeamsp home if exists
    # if env_name in os.environ:
    #     pyemaps_home = os.getenv(env_name)
        
    #     if Path(pyemaps_home).exists(): 
    #         pyemaps_datahome = pyemaps_home
    #     else:
    #         try:
    #             os.mkdir(pyemaps_home)

    #         except OSError:
    #             # can't create the directory, fall back to current directory
    #             pass
    #         else:
    #             pyemaps_datahome = pyemaps_home
    # from . import pyemaps_datahome
    global pyemaps_datahome
    if pyemaps_datahome is None:
        pyemaps_datahome = find_datahome()

    if 'PYEMAPS_CRYSTALS' in os.environ:
        return pyemaps_datahome # done when legacy

    # if the environment home folder does extists
    
    pyemaps_home = os.path.join(pyemaps_datahome, home_type)

    if Path(pyemaps_home).exists():
        return pyemaps_home

    try:
        os.mkdir(pyemaps_home)
    except OSError:
        print(f'failed to create {home_type} folder in pyemaps data home directory {pyemaps_datahome}')
        print(f'{pyemaps_datahome} will be used to host {home_type} data instead')
        return pyemaps_datahome
    else: 
        return pyemaps_home

def compose_ofn(fn, name, ty='diffraction'):
    '''
    Compose output file name based file name and file type.

    '''
    pyemaps_datahome=find_pyemaps_datahome(home_type=ty)

    if fn is None:
        fn = auto_fn(name)
        return os.path.join(pyemaps_datahome, fn)
    
    # valid input fn
    fpath, fname = os.path.split(fn)
    
    # can't write any file to a path that does not exist  
    if fpath and not Path(fpath).exists():
        raise FileNotFoundError('Error: file path not found')

    if not fpath: # if no path compose fn 
        if not fname:
            fn = auto_fn(name, ty=ty)
        else:
            fn = fname
        return os.path.join(pyemaps_datahome, fn)

    # left with both path not empty and exists, then go with the input
    return fn
# -----------------crystal data loading and saving -----------------
#                  from/to data files on disks
#       
#                   CIF files


import numpy as np
from numpy import asfortranarray as farray
from .spg.spg_dec import *

from . import (XTLError, SPGError, CIFError, 
               SPGSettingNotInRangeError,SPGITMumberNotInRangeError)


cell_keys=['a','b','c','alpha','beta','gamma']

at_iso_keys=['symb','x','y','z','d-w','occ']

at_noniso_keys=['symb','x','y','z','b11','b22','b33','b12','b13','b23','occ']

spg_keys=['number','setting']

crystal_data_basedir = 'cdata'

negative_infinity = float(-np.inf)

required_keys = ['cell', 'dw', 'atoms', 'spg']
# CIF_NUM_TOKENS = r"[\(\+]"

NUMERIC_PATTERN = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
RX = re.compile(NUMERIC_PATTERN, re.VERBOSE)

HM_CORE_PATTERN = '[A-Za-z0-9 /\-+]+'
HM_RX = re.compile(HM_CORE_PATTERN, re.VERBOSE)

# HM_PATTERN ='[][ \t_(),.;:"&<>/\{\}\'`~!@#$%?+=*A-Za-z0-9|^-]*' not used 


def _float_eq(a,b):
    return abs(a-b) < 0.000001

def _getCIFFloats(sArr, fillval=0.0):
    '''
    input sArr: dictionary string array from CIF file
    Return: float array
    handling cases: 
    1) with () symbols in the input
    2) with ? in the input
    3) with . in the input
    ...
    '''

    sl = len(sArr)

    retArr = [0.0]*sl

    for i, w in enumerate(sArr):
        
        ww = RX.findall(w)

        try:
            fel = float(ww[0])

        except (IndexError, ValueError):
            fel = fillval

        retArr[i] = fel

    return retArr

def _getCIFFloat(s):
    '''
    input s: dictionary string from CIF file
    Return: float number
    '''
    
    digits = RX.findall(s)
    if len(digits) == 0:
        return negative_infinity

    sw = RX.findall(s)[0]
    
    ret = negative_infinity
    try:
        ret = float(sw)
        
    except (IndexError, ValueError):
        return negative_infinity
    
    return ret

def _getCIFInt(s):
    '''
    input s: dictionary string from CIF file
    Return: int number
    '''
    
    digits = RX.findall(s)
    if len(digits) == 0:
        return -np.inf

    sw = RX.findall(s)[0]
    try:
        int(sw)
    except (IndexError, ValueError):
        return -np.inf
    
    return int(sw)

def _scrubCIFSymmXYZ(cf, maxlen):
    '''
    scrub off those items white space and longer than MAX_SPG_LEN

    '''
    
    res = []
    l = 0
    for c in cf:
        toks = re.split(r'\s+', c)
        s = ''.join(toks)
        if len(s) <= maxlen:
            l += 1
            res.append(s)
            
    return l, res

def _simplifyCIF(str1, str2):
    s1 = str1.replace('-', '+-').strip('+')
    s2 = str2.replace('-', '+-').strip('+')
    
    l1 = re.split(r'[+]', s1)
    l2 = re.split(r'[+]', s2)

    if len(l1) != len(l2):
        
        return 1

    exp1 = set(l1)
    exp2 = set(l2)
    
    if exp1 == exp2:
        return 0

    return 1

def _isCIFEquivalent(c, cc):
    '''
    Compare two expressions of symmetry in the form of
    expr1,expr2,expr3
    If they are the same arithmetic expressions, return True
    otherwise False
    '''  
    # import concurrent.futures
    
    ct = re.split(r',', c)
    cct = re.split(r',', cc)

    if len(ct) != 3 or len(cct) != 3: 
        return False

    sym_pairs = list(zip(ct, cct))
    for p in sym_pairs:
        res = _simplifyCIF(p[0], p[1])
        if res != 0:
            return False
    return True

def _compareCIFSymmetry(n, coords, cf_coords):
    '''
    compare two symmrety array if:
    1. coords contained in cf_coords, return 0
    2. otherwise return 1
    the comparison is done using sympy module with expression equivalence
    ''' 
    count = 0
    for c in coords:
        count += 1
        if count > n:
            break
        cstr = ''.join([c[i].decode() for i in range(SPG_SYMMETRY_MAXLEN)]).strip()
        
        found = False
        for cfc in cf_coords: 
            if _isCIFEquivalent(cstr, cfc):
                found = True
                break
        if not found:
            return 1
    return 0

def _matchCIFHM(l1, l0):
    '''
    Compare two Space Group H-M strings and find the longest match length
    '''
    
    res = 0
    for i in range(len(l1)):
        if l1[i].upper() == l0[i].upper():
            res +=1
        else:
            break
    return res

def _validAtomSiteLabel(l):
    try:
        from .scattering.sct_dec import sct_symbtable, sct_cifsymbtable
    except:
        raise CIFError(f"pyemaps scattering database module must be available")
    
    ll = l.strip().upper()

    # cover most of the cases hopefully      
    if ll in sct_symbtable or ll in sct_cifsymbtable:
        return True, ll

    # remove one character from the back until it appears in pyemaps element table
    ellen = len(ll)
    
    for i in range(ellen-2, -1, -1):
        lll = ll[0:i+1]
        
        if lll in sct_symbtable or lll in sct_cifsymbtable:
            return True, lll
    
    return False, l

    
def loadCrystalCIFData(fn):
    """
    Reads a .cif file for crystal data.

    :param fn: cif file name
    :type: string, required

    :return: tuple of crystal name and crystal data as dict object
    :rtype: dict

    .. note:: 

        This method is still in active development. 
    
    """
    from .CifFile import ReadCif

    SPG_NUMBER_CIFKEY=['_symmetry_Int_Tables_number', 
                        '_symmetry_IT_number',
                        '_space_group_IT_number']

    # check for full path
    cfn = fn
    if not os.path.exists(fn):
        
        # pyemaps_home = os.getenv('PYEMAPS_CRYSTALS')
        datahome = find_pyemaps_datahome(home_type = 'crystals')
        cfn = os.path.join(datahome, fn)
        
        if not os.path.exists(cfn):
            raise CIFError('Failed to find the crystal data file', cfn)
    
    cf = None
    try:
        cf =  ReadCif(cfn)
    except IOError as e:
        raise CIFError(cfn, e.message)

    if len(cf.keys()) == 0:
        raise CIFError(cfn, 'missing required data keys')

    name = cf.keys()[0]
    if not isinstance(name, str) or len(name) == 0:
        raise CIFError(cfn, 'missing required data name')

    # retirving cell constants data
    data = {}

    cell = {}
    
    c_dict = cf[name]
    
    if '_cell_length_a' not in c_dict or \
        '_cell_length_b' not in c_dict or \
        '_cell_length_c' not in c_dict or \
        '_cell_angle_alpha' not in c_dict or \
        '_cell_angle_beta' not in c_dict or \
        '_cell_angle_gamma' not in c_dict:
        raise CIFError(cfn, 'missing required cell parameters data keys')

    lp = _getCIFFloat( c_dict['_cell_length_a'])
    
    if lp ==  negative_infinity:
        raise CIFError(cfn, 'missing or invalid cell parameters value for _cell_length_a')

    cell['a'] = lp

    lp = _getCIFFloat( c_dict['_cell_length_b'])
    if lp ==  negative_infinity:
        raise CIFError(cfn, 'missing or invalid cell parameters value for _cell_length_b')
    cell['b'] = lp
    
    lp = _getCIFFloat( c_dict['_cell_length_c'])
    if lp ==  negative_infinity:
        raise CIFError(cfn, 'missing or invalid cell parameters value for _cell_length_c')
    cell['c'] = lp
    
    lp = _getCIFFloat( c_dict['_cell_angle_alpha'])
    if lp ==  negative_infinity:
        raise CIFError(cfn, 'missing or invalid cell parameters value for _cell_angle_alpha')
    cell['alpha'] = lp
    
    lp = _getCIFFloat( c_dict['_cell_angle_beta'])
    if lp ==  negative_infinity:
        raise CIFError(cfn, 'missing or invalid cell parameters value for _cell_angle_beta')
    cell['beta'] = lp
    
    lp = _getCIFFloat( c_dict['_cell_angle_gamma'])
    if lp ==  negative_infinity:
        raise CIFError(cfn, 'missing or invalid cell parameters value for _cell_angle_gamma')
    cell['gamma'] = lp

    data['cell'] = cell

    # retrieving unitcell data
    if '_atom_site_fract_x' not in c_dict or \
        '_atom_site_fract_y' not in c_dict or \
        '_atom_site_fract_z' not in c_dict:
        raise CIFError(cfn, 'missing unit cell keys _atom_site_fract_x[y|z]')
    
    if '_atom_site_label' not in c_dict and '_atom_site_type_symbol' not in c_dict:
        raise CIFError(cfn, 'missing unit cell keys for atom site label')

    atlabels=[]
    
    if '_atom_site_type_symbol' in c_dict:
        atlabels = c_dict['_atom_site_type_symbol']
        
    else:
        atlabels = c_dict['_atom_site_label']
        

    at_len = len(atlabels)

    xs = c_dict['_atom_site_fract_x']
    if not xs and len(xs) != at_len:
        raise CIFError(cfn, 'invalid unit cell value for _atom_site_fract_x')
        
    xx = _getCIFFloats(xs)

    ys = c_dict['_atom_site_fract_y']
    if not ys and len(ys) != at_len:
        raise CIFError(cfn, 'invalid unit cell value for _atom_site_fract_y')
        
    yy = _getCIFFloats(ys)

    zs = c_dict['_atom_site_fract_z']
    if not zs and len(zs) != at_len:
        raise CIFError(cfn, 'invalid unit cell value for _atom_site_fract_z')
        
    zz = _getCIFFloats(zs)

    # Occupancy data
    occ = [1.0]*at_len
    if '_atom_site_occupancy' in c_dict:
        occ_raw = _getCIFFloats(c_dict['_atom_site_occupancy'])
        if not occ_raw or len(occ_raw) != at_len:
            raise CIFError(cfn, 'invalid unit cell value for _atom_site_occupancy')
        occ = occ_raw

    atoms = [dict(symb=atlabels[i], x=xx[i], y=yy[i], z=zz[i], occ=occ[i]) for i in range(at_len)]

    # thermal display type, dw = Uiso, Biso, Uani, Uovl?
    # dw = 'iso'
    # if '_atom_site_thermal_displace_type' in c_dict or \
    #     '_atom_site_adp_type' in c_dict:
    #     dw_cif =''
    #     if '_atom_site_adp_type' in c_dict:
    #         dw_cif = c_dict['_atom_site_adp_type'].strip().lower()
    #     else:
    #         dw_cif = c_dict['_atom_site_thermal_displace_type'].strip().lower()

    #     if dw_cif == 'biso':
    #         dw = 'iso'
    #     elif dw_cif == 'uovl':
    #         dw = 'iso'
    #     elif dw_cif == 'uiso':
    #         dw = 'uij'  
    #     elif dw_cif == 'uani':
    #         dw = 'uij'
    #     elif dw_cif == 'bani':
    #         dw = 'bij'  
    #     elif dw_cif == 'umpe':
    #         dw = ''          

    if '_atom_site_aniso_label' in c_dict:
        if '_atom_site_aniso_U_11' not in c_dict and \
            '_atom_site_aniso_U_22' not in c_dict and \
            '_atom_site_aniso_U_33' not in c_dict and \
            '_atom_site_aniso_U_12' not in c_dict and \
            '_atom_site_aniso_U_13' not in c_dict and \
            '_atom_site_aniso_U_23' not in c_dict and \
            '_atom_site_aniso_B_11' not in c_dict and \
            '_atom_site_aniso_B_22' not in c_dict and \
            '_atom_site_aniso_B_33' not in c_dict and \
            '_atom_site_aniso_B_12' not in c_dict and \
            '_atom_site_aniso_B_13' not in c_dict and \
            '_atom_site_aniso_B_23' not in c_dict:
            raise CIFError(cfn, 'missing required unit cell keys such as _atom_site_aniso_U_NN or _atom_site_aniso_B_NN')
        
        for i in range(at_len):
            atoms[i]['b11'] = 0.0
            atoms[i]['b22'] = 0.0
            atoms[i]['b33'] = 0.0
            atoms[i]['b12'] = 0.0
            atoms[i]['b13'] = 0.0
            atoms[i]['b23'] = 0.0

        if '_atom_site_aniso_U_11' in c_dict:
            dw = 'uij'
            u11 = _getCIFFloats(c_dict['_atom_site_aniso_U_11'])

            for i, uf11 in enumerate(u11):
                atoms[i]['b11'] = uf11
        
        if '_atom_site_aniso_U_22' in c_dict:
            dw = 'uij'
            u22 = _getCIFFloats(c_dict['_atom_site_aniso_U_22'])

            for i, uf22 in enumerate(u22):
                atoms[i]['b22'] = uf22

        if '_atom_site_aniso_U_33' in c_dict:
            dw = 'uij'
            u33 = _getCIFFloats(c_dict['_atom_site_aniso_U_33'])
            for i, uf33 in enumerate(u33):
                atoms[i]['b33'] = uf33
        
        if '_atom_site_aniso_U_12' in c_dict:
            dw = 'uij'
            u12 = _getCIFFloats(c_dict['_atom_site_aniso_U_12'])

            for i, uf12 in enumerate(u12):
                atoms[i]['b12'] = uf12
    
        if '_atom_site_aniso_U_13' in c_dict:
            dw = 'uij'
            u13 = _getCIFFloats(c_dict['_atom_site_aniso_U_13'])
            for i, uf13 in enumerate(u13):
                atoms[i]['b13'] = uf13

        if '_atom_site_aniso_U_23' in c_dict:
            dw = 'uij'
            u23 = _getCIFFloats(c_dict['_atom_site_aniso_U_23'])
            for i, uf23 in enumerate(u23):
                atoms[i]['b23'] = uf23

        if '_atom_site_aniso_B_11' in c_dict:
            b11 = [0.0]*at_len
            dw = 'bij'
            b11 = _getCIFFloats(c_dict['_atom_site_aniso_B_11'])
            for i, bf11 in enumerate(b11):
                atoms[i]['b11'] = bf11
        
        if '_atom_site_aniso_B_22' in c_dict:
            b22 = [0.0]*at_len
            dw = 'bij'
            b22 = _getCIFFloats(c_dict['_atom_site_aniso_B_22'])
            for i, bf22 in enumerate(b22):
                atoms[i]['b22'] = bf22
            
        if '_atom_site_aniso_B_33' in c_dict:
            b33 = [0.0]*at_len
            dw = 'bij'
            b33 = _getCIFFloats(c_dict['_atom_site_aniso_B_33'])
            for i, bf33 in enumerate(b33):
                atoms[i]['b33'] = bf33
        
        if '_atom_site_aniso_B_12' in c_dict:
            b12 = [0.0]*at_len
            dw = 'bij'
            b12 = _getCIFFloats(c_dict['_atom_site_aniso_B_12'])
            for i, bf12 in enumerate(b12):
                atoms[i]['b12'] = bf12
        
        if '_atom_site_aniso_B_13' in c_dict:
            b13 = [0.0]*at_len
            dw = 'bij'
            b13 = _getCIFFloats(c_dict['_atom_site_aniso_B_13'])
            for i, bf13 in enumerate(b13):
                atoms[i]['b13'] = bf13

        if '_atom_site_aniso_B_23' in c_dict:
            b23 = [0.0]*at_len
            dw = 'bij'
            b23 = _getCIFFloats(c_dict['_atom_site_aniso_B_23'])
            for i, bf23 in enumerate(b23):
                atoms[i]['b23'] = bf23
        
    elif '_atom_site_U_iso_or_equiv' in c_dict or '_atom_site_Uiso_or_equiv' in c_dict:
        
        dw = 'uij'
        bxx = _getCIFFloats(c_dict['_atom_site_U_iso_or_equiv'])
        for i, b in enumerate(bxx):
            atoms[i]['b11'] = atoms[i]['b22'] = atoms[i]['b33'] = b
            atoms[i]['b12'] = atoms[i]['b13'] = atoms[i]['b23'] = 0.0


    elif '_atom_site_B_iso_or_equiv' in c_dict:
        dw = 'iso'
    
        d_w = _getCIFFloats(c_dict['_atom_site_B_iso_or_equiv'], 0.05)
        for i, d in enumerate(d_w):
            atoms[i]['d-w'] = d
    else:
        # assuming iso with default values of d-w
        dw = 'iso'
        for i in range(at_len):
            atoms[i]['d-w'] = 0.05
            
    vatoms = []
    for at in atoms:  
        symb = at['symb']  
        v, vsymb = _validAtomSiteLabel(symb)        
        if not v:
            print(f'Warning: unrecognized unit cell site label: {symb}, removing the corresponding unit cell')
        else:
            at['symb'] = vsymb
            vatoms.append(at)

    if len(vatoms) == 0:
        raise CIFError(cfn, 'invalid unit cells')

    data['dw'] = dw
    data['atoms'] = vatoms  
    
        
    spgInCIF = False
    spg = {}
    for k in SPG_NUMBER_CIFKEY:
        if k in c_dict:
            spgInCIF = True
            break
        
    spg_num = 0
    spg_setting = 0
    
    spg_pairs =[(0,0)]

    if  spgInCIF:
        spg_num = _getCIFInt(c_dict[k]) 

    if spgInCIF and spg_num >= 1 and  spg_num <= SPG_ITNUM_MAX:
        
        spg_pairs.clear()
        spg_smax = get_settingmax(spg_num)
        for i in range(1, spg_smax+1):
            spg_pairs.append((spg_num, i))
    else:
        if not '_symmetry_space_group_name_H-M' in c_dict and \
            not '_space_group_name_H-M_alt' in c_dict and \
            not '_cod_original_sg_symbol_H-M' in c_dict:
            raise CIFError(cfn, 'missing required space group keys. ' + 
                                        'it must be on of:\n' + 
                                        '_symmetry_Int_Tables_number\n' +  
                                        '_symmetry_IT_number\n' + 
                                        '_space_group_IT_number\n' + 
                                        'or, one of:\n' + 
                                        '_symmetry_space_group_name_H-M\n' + 
                                        '_space_group_name_H-M_alt\n' + 
                                        '_cod_original_sg_symbol_H-M'
                                        )

        hm = None
        if '_symmetry_space_group_name_H-M' in c_dict:
            hm0 = c_dict['_symmetry_space_group_name_H-M']
            
            hm00 = HM_RX.findall(hm0)
        
            if len(hm00) > 0:
                hm = hm00[0]
                
        if not hm and '_space_group_name_H-M_alt' in c_dict:

            hm0 = c_dict['_space_group_name_H-M_alt']
            
            hm00 = HM_RX.findall(hm0)
        
            if len(hm00) > 0:
                hm = hm00[0]

        if not hm and '_cod_original_sg_symbol_H-M' in c_dict:
            hm0 = c_dict['_cod_original_sg_symbol_H-M']
            
            hm00 = HM_RX.findall(hm0)
        
            if len(hm00) > 0:
                hm = hm00[0]
        

        if not hm:
            raise CIFError(cfn, 'invalid space group H-M value')

        spgHM = re.split(r'\s+', hm)
        maxMatched = 0
        mIndex = -1
        for i in range(SPG_ENTRY_MAX):
            emaps_spghm, spgnum, spgsetting = loouphm(i+1)

            cemaps_spghm = emaps_spghm.decode().strip()

            emaps_spghm_list = re.split(r'\s+', cemaps_spghm)

            nmatched = _matchCIFHM(emaps_spghm_list, spgHM)
            
            if nmatched > maxMatched: 
                maxMatched = nmatched
                mIndex = i + 1
                spg_pairs.clear()
                spg_pairs.append((spgnum, spgsetting))

            elif nmatched == maxMatched and mIndex >= 0:
                spg_pairs.append((spgnum, spgsetting))


        if mIndex == -1:
            raise CIFError(cfn, 'no match found in pyemaps space group database')
    
    if '_symmetry_space_group_setting' in c_dict:
        spg_setting = _getCIFInt(c_dict['_symmetry_space_group_setting'])

        if spg_setting < 1 or spg_setting > SPG_SETTING_MAX:
            raise SPGSettingNotInRangeError()

        spg_num = 0
        spg_tmppairs = []
        for sp in spg_pairs:
            if sp[1] == spg_setting:
                spg_tmppairs.append(sp)

        spg_pairs = spg_tmppairs

    if '_symmetry_equiv_pos_as_xyz' in c_dict or \
        '_space_group_symop_operation_xyz' in c_dict:

        cif_coords = []
        if '_symmetry_equiv_pos_as_xyz' in c_dict:
            cif_coords = c_dict['_symmetry_equiv_pos_as_xyz']
        elif '_space_group_symop_operation_xyz' in c_dict:
            cif_coords = c_dict['_space_group_symop_operation_xyz']
        
        l, pact = _scrubCIFSymmXYZ(cif_coords, SPG_SYMMETRY_MAXLEN)
        
        max_match = -1
        new_pairs = []
        for sp in spg_pairs:
            coords = farray(np.empty((SPG_SYMMETRY_MAXCOL, SPG_SYMMETRY_MAXLEN), dtype='c'))
            coords, n = getsymmetryxyz(sp, coords)
            
            
            if n == -1:
                # This should not happen but check for it anyway
                raise CIFError(cfn, 'symmetry lookup in pyemaps space group failed')
            if n > l:
                # no match
                continue

            if _compareCIFSymmetry(n, coords, pact) == 0:
                if max_match < n:
                    max_match = n
                    new_pairs.append(sp)
        
        if max_match == -1:
            raise CIFError(cfn, 'symmetry data provided does match any in pyemaps database')

        spg_pairs.clear()
        spg_pairs = new_pairs
    else:
        print(f'Info: no symmetry infomation provided in {cfn}')

    if len(spg_pairs) == 1:
        print(f'\nInfo: closest matching space group information found in pyemaps: {spg_pairs}')
    else:
        errmsg = str(f'Multiple sets of space group match found: {spg_pairs}, retry with _symmetry_space_group_setting field in {cfn}')
        raise SPGError(errmsg)

    # make sure the spg pair is not empty
    if len(spg_pairs) == 0:
        raise SPGError('No space group info found')

    spg_num = spg_pairs[0][0]
    spg_setting = spg_pairs[0][1]                           
                    
    if spg_setting <= 0 or spg_setting > SPG_SETTING_MAX:
        raise SPGSettingNotInRangeError()

    if  spg_num <= 0 or spg_num > SPG_ITNUM_MAX:            
        raise SPGITMumberNotInRangeError()
        
    spg['number'] = spg_num
    spg['setting'] = spg_setting

    data['spg'] = spg
    
    for key in required_keys:
        if key not in data:
            raise CIFError(cfn, 'parsing and extraction failed to produce valid crystal data')

    return name, data
 
def _get_atom_len(dw):
    if dw == 'iso':
        return len(at_iso_keys)
    
    if dw == 'uij' or dw == 'bij':
        return len(at_noniso_keys)
    
    return -1 #error

def loadCrystalData(fn, cn=None):
    """
    Reading built-in datbase or a .xtl file for crystal data.

    :param fn: XTL formatted Crystal file name
    :type: string, required

    :param cn: Crystal name
    :type: string, optional

    :return: tuple of crystal name and crystal data as dict object
    :rtype: dict

    """

    data = {}
    
    name=""
    
    try:
        with open(fn) as f:
            lines = f.readlines()
            atoms = []
            for line in lines:
                ln = line.strip().lower()
                if ln.startswith('crystal'):
                    token = line.split(':')
                    
                    cname = re.split(' +', token[0].strip())[1].strip()
                    name = cname
                    
                    if cn and name.lower() != cn.lower():
                        raise XTLError(fn, 'mismatch of input name with builtin crystal name, only in builtin files')
                    
                    # parsing for dw and occ data
                    dwocc = re.split(' =+', token[1].strip())
                    owlen = len(dwocc)
                    
                    # dw = iso or
                    # dw = iso occ = 1

                    if owlen > 3 or owlen < 2:
                        raise XTLError(fn, 'invalid dw and occ data input')

                    dwkey = dwocc[0].strip().lower()
                    if dwkey != 'dw':
                        raise XTLError(fn, 'missing dye-waller factor key')

                    dw = re.split(' +', dwocc[1].strip())[0]

                    occ = 1.0 #default
                    if owlen == 3:
                        occkey = re.split(' +', dwocc[1].strip())[1].lower()
                        if occkey and occkey != 'occ':
                            raise XTLError(fn, 'missing occupancy key')
                        
                        occ = int(dwocc[2].strip())

                    # validating dw:
                    if dw != 'iso' and dw != 'uij' and dw != 'bij': 
                        raise XTLError(fn, 'invalid dye-Waller facttor data: must be one of iso, bij and uij')

                    data['dw'] = dw

                    # if len(dwocc) == 3:
                    #     occ = dwocc[2].strip()


                if ln.startswith('cell'):
                    
                    cellStr = ln[4:].strip()
                    tokens = np.array([n for n in re.split(' +', cellStr)])
                    if tokens.size != len(cell_keys):
                        raise XTLError(fn, 'invalid cell parameters input')

                    cell = {}
                    for k, t in zip(np.array(cell_keys), tokens):
                        cell[k] = t
                    data['cell'] = cell

                if ln.startswith('atom'):
                    
                    atomStr = ln[4:].strip()

                    token = [n for n in re.split(' +', atomStr)]

                    alen = _get_atom_len(data['dw'])
                    tokenlen = len(token)
                    if tokenlen < alen - 1 or tokenlen > alen:
                        raise XTLError(fn, 'invalid unit cell input')

                    if tokenlen == alen - 1:
                        token.append(occ)

                    atom = {}
                    keys = at_iso_keys if data['dw']== 'iso' else at_noniso_keys
                    
                    for k, t in zip(np.array(keys), token):
                        atom[k] = t
                    atoms.append(atom)

                if ln.startswith('spg'):

                    sStr = ln[3:].strip()
                    if not sStr:
                        raise ValueError("Space group data missing")

                    tokens = np.array([n for n in re.split(' +', sStr)])
                    if tokens.size != 2:
                        raise XTLError(fn, 'invalid space group input')
                        
                    spg = {}
                    for k, t in zip(np.array(spg_keys), tokens):
                        spg[k] = t
                    
                    # validateSPG(tokens)

                    data['spg'] = spg
            new_atoms = []
            for a in atoms:
                symb = a['symb']
                valided, new_symb = _validAtomSiteLabel(symb)
                if not valided:
                    print(f'Warning: invalid unit cell symbol {symb}, removing corresponding unit cell')
                    continue
                a['symb'] = new_symb
                new_atoms.append(a)

            if len(new_atoms) == 0:
                raise XTLError(fn, 'missing unit cell data')

            data['atoms'] = new_atoms
            
            for key in required_keys:
                if key not in data:
                    raise XTLError(fn, str(f'missing data for {key}'))

    except (FileNotFoundError,IOError) as e:
        raise XTLError(fn, str(e))

    return name, data

    
       
