'''
# This file is part of pyemaps
# ___________________________
#
# pyemaps is free software for non-comercial use: you can 
# redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either 
# version 3 of the License, or (at your option) any later version.
#
# pyemaps is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyemaps.  If not, see <https://www.gnu.org/licenses/>.
#
# Contact supprort@emlabsoftware.com for any questions and comments.
# ___________________________


Author:             EMLab Solutions, Inc.
Date Created:       May 07, 2022  

'''

import numpy as np
from numpy import asfortranarray as farray
from functools import wraps
import os
import json

from . import dif
from . import sct
from . import spgseek as spgra
    
from .errors import *

from .emcontrols import DEF_CBED_DSIZE
from .emcontrols import EMControl as EMC

import re

# pyemaps scattering data 
SCT_SYM_LEN = sct.elmn #6

sct_symbtable = re.split(r'\s+', sct.elnams.tobytes().decode().strip())

sct_cifsymbtable = re.split(r'\s+', sct.cifelnams.tobytes().decode().strip())

# space group builtin data

SPG_SYMMETRY_MAXCOL = spgra.getsymmetrymaxlen() #48

SPG_SETTING_MAX = spgra.getspgallsettingmax() #6

SPG_SYMMETRY_MAXLEN = spgra.getsymmetryitemlen() #20

SPG_ITNUM_MAX = spgra.getspgitnum() #234

SPG_ENTRY_MAX = spgra.getspgentrynum() #310

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

def float_eq(a,b):
    return abs(a-b) < 0.000001

def getCIFFloats(sArr, fillval=0.0):
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

def getCIFFloat(s):
    '''
    input s: dictionary string from CIF file
    Return: float number
    '''
    import re
    
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

def getCIFInt(s):
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

def scrubCIFSymmXYZ(cf, maxlen):
    '''
    scrub off those items white space and longer than MAX_SPG_LEN

    '''
    import re
    
    res = []
    l = 0
    for c in cf:
        toks = re.split(r'\s+', c)
        s = ''.join(toks)
        if len(s) <= maxlen:
            l += 1
            res.append(s)
            
    return l, res

def simplifyCIF(str1, str2):
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

def isCIFEquivalent(c, cc):
    '''
    Compare two expressions of symmetry in the form of
    expr1,expr2,expr3
    If they are the same arithmetic expressions, return True
    otherwise False
    '''  
    import re
    import concurrent.futures
    
    ct = re.split(r',', c)
    cct = re.split(r',', cc)

    if len(ct) != 3 or len(cct) != 3: 
        return False

    sym_pairs = list(zip(ct, cct))
    for p in sym_pairs:
        res = simplifyCIF(p[0], p[1])
        if res != 0:
            return False
    return True

def compareCIFSymmetry(n, coords, cf_coords):
    '''
    compare two symmrety array if:
    1) coords contained in cf_coords, return 0
    2) otherwise return 1
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
            if isCIFEquivalent(cstr, cfc):
                found = True
                break
        if not found:
            return 1
    return 0

def matchCIFHM(l1, l0):
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
  

def validAtomSiteLabel(l):
    
    import re

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

class Cell:

    def __init__(self, cell_dict=dict.fromkeys(cell_keys,0.0)):

        if not cell_dict or not isinstance(cell_dict, dict) or len(cell_dict) != len(cell_keys):
            raise CellDataError()

        for k in cell_keys:
            if k not in cell_dict:
                dataerr = str(f'Missing cell key {k} from input cell data')
                raise CellDataError(dataerr)

        for k, v in cell_dict.items():
            setattr(self, k, v)

    @property
    def a(self):
        ''' a cell length '''
        return self._a
    @property
    def b(self):
        ''' b cell length '''
        return self._b
    @property
    def c(self):
        ''' c cell length '''
        return self._c
    @property
    def alpha(self):
        ''' alpha cell angle '''
        return self._alpha
    @property
    def beta(self):
        ''' beta cell angle '''
        return self._beta
    @property
    def gamma(self):
        ''' gamma cell angle '''
        return self._gamma

    @a.setter
    def a(self, v):  
        try:
            self._a = float(v)
        except ValueError as e:
            raise CellValueError(1, "a")

    @b.setter
    def b(self, v):
        
        try:
            self._b = float(v)
        except ValueError as e:
            raise CellValueError(1, "b")


    @c.setter
    def c(self, v):
        
        try:
            self._c = float(v)
        except ValueError as e:
            raise CellValueError(1, "c")


    @alpha.setter
    def alpha(self, v):
        
        try:
            self._alpha = float(v)
        except ValueError as e:
            raise CellValueError("alpha")

    @beta.setter
    def beta(self, v):
        
        try:
            self._beta = float(v)
        except ValueError as e:
            raise CellValueError("beta")

    @gamma.setter
    def gamma(self, v):
        
        try:
            self._gamma = float(v)
        except ValueError as e:
            raise CellValueError("gamma")

    def __key__(self):
        return (self._a, self._b, self._c, self._alpha, self._beta, self._gamma)

    def __eq__(self, cello):
        if not isinstance(cello, Cell):
            return False
        
        return self.__key__() == cello.__key__()

    def __repr__(self):
        return str(f"cell: a: {self._a}, b: {self._b}, c: {self._c}, ") + \
               str(f"alpha: {self._alpha}, beta: {self._beta}, gamma: {self._gamma}") 

    def __str__(self):
        return str(f"cell: {self._a} {self._b} {self._c} ") + \
               str(f"{self._alpha} {self._beta} {self._gamma}") 

    def prepareDif(self):
        cell0 = self.__dict__
        celarr = np.zeros((6,))
        for i, key in enumerate(cell_keys):
            sk = '_' + key
            if sk in cell0:
                celarr[i]=cell0[sk]
            else:
               raise CellDataError("Unrecognized cell length or angle data")
        
        return farray(celarr, dtype=float)

class SPG:
    def __init__(self, spg_dict):
        if not spg_dict or not isinstance(spg_dict, dict):
            raise SPGInvalidDataInputError()

        if len(spg_dict) != 2 or 'number' not in spg_dict or 'setting' not in spg_dict:
            raise SPGInvalidDataInputError()

        # make sure that 'number' attribute is set first
        setattr(self, 'number', spg_dict['number'])
        
        setattr(self, 'setting', spg_dict['setting'])  

    @property
    def number(self):
        ''' The first number in Space Group lookup'''
        return self._number

    @property
    def setting(self):
        ''' The second number in Space Group lookup'''
        return self._setting

    @number.setter
    def number(self, num):
        
        number = 0
        try:
            number = int(num)
        except ValueError as e:
            raise SPGInvalidDataInputError()
        
        if number < 1 or number > SPG_ITNUM_MAX:
            raise SPGITMumberNotInRangeError(SPG_ITNUM_MAX)

        self._number = number

    @setting.setter
    def setting(self, s):

        iset = 0
        try:
            iset = int(s)
        except ValueError:
            raise SPGInvalidDataInputError()

        if iset < 1 or iset > SPG_SETTING_MAX:
            raise SPGSettingNotInRangeError(SPG_SETTING_MAX)   

        inum = 0
        try:
            inum = self._number #already validated
        except AttributeError:
            raise SPGError("Space group number missing in creation of SPG object")
            
        set_max = spgra.getspgsettingmax(inum)
        if iset > set_max:    
            raise SPGSettingNotInRangeError(set_max)


        self._setting = iset
        

    def __eq__(self, spgo):
         if not isinstance(spgo, SPG):
            return False

         return (self._number == spgo.number) and (self._setting == spgo.setting)

    def __str__(self):
        return str(f"spg: {self._number} {self._setting}")
    
    def __repr__(self):
        return str(f"spg: number: {self._number} setting: {self._setting}")

    def prepareDif(self):
         return farray([self._number, self._setting], dtype=int)

class Atom:
    def __init__(self, a_dict={}):
        
        if not a_dict or not isinstance(a_dict, dict) or len(a_dict) == 0:
            raise UCError()

        if 'symb' not in a_dict:
            raise UCError("missing symbol")

        setattr(self, 'symb', a_dict["symb"])

        acopy = a_dict.copy()
        acopy.pop("symb")
        
        setattr(self, 'loc', acopy)

    @property
    def symb(self):
        return self._symb

    @property
    def loc(self):
        return self._loc

    @symb.setter
    def symb(self, sb):
        if not isinstance(sb, str):
            raise UCError("symbol must be string")
        
        self._symb = sb
    
    @loc.setter
    def loc(self, vloc_dict):
        if not vloc_dict:
            raise UCError("unit cell coordinates missing")

        ln = len(vloc_dict)
        if ln != 4 and ln != 5 and \
           ln != 9 and ln != 10:
            raise UCError("invalid unit cell coordinates length")

        akeys = at_iso_keys
        if ln == 9 or ln == 10:
            akeys = at_noniso_keys
            
        klen = len(akeys)
        self._loc = [0.0]*(klen-1)
        for i in range(klen):
            k = akeys[i]
            if k == 'symb':
                continue

            if k in vloc_dict:
                self._loc[i-1] = vloc_dict[k]
                
            else:
               raise UCError(str(f"unrecognized key {k}"))
                
    def __eq__(self, other):
        if not isinstance(other, Atom):
            return False

        if self._symb.lower() != other._symb.lowder(): 
            return False

        if self._loc != other.loc:
            return False

        return True
    
    def __str__(self) -> str:
        atoms=[str(f"{self._symb}")]
        
        for v in self._loc:
            atoms.append(str(v))

        return " ".join(atoms)

def add_dpgen(target):
    def dp_gen(self, res =1):

        try:
            from . import dpgen

        except ImportError as e:               
            print(f"Error: required module pyemaps.dpgen not found")
            return -1

        dp_res_lookup = [('small', 0.01),
                        ('medium', 0.005),
                        ('large', 0.0025)]

        dif.initcontrols()
        
        cell, atoms, atn, spg = self.prepareDif()
        dif.loadcrystal(cell, atoms, atn, spg, ndw=self._dw)

        dif.set_xaxis(1, 2, 0, 0)
        ret = dif.diffract(2)
        
        if ret == 0:
            print('Error running dif module')
            return -1

        vertices0 = np.array([[0,0,1],[1,1,1],[0,1,1]])
        vertices = farray(vertices0.transpose(), dtype=int)

        sres, fres = dp_res_lookup[res-1]
        output_fn = self.name +'_' + sres

        print(f"input for do_gen: {vertices},{output_fn}")
        ret = dpgen.do_dpgen(fres, vertices, output_fn)
        if ret != 0:
            print(f'Error running generating diffraction patterns for {self.name}')
            return -1

        ret = dpgen.readbin_new(output_fn+' ', "bin"+' ')
        if ret != 0: 
            print(f'Error running generating diffraction patterns for {self.name}')
            return -1

        #release the memory
        dif.diff_internaldelete(0)
        dif.diff_delete()

        return 0
    
    target.dp_gen = dp_gen

    return target

def add_csf(target):
    '''
    #####INPUT#######
    -------------kv-----------------------
      Accelaration Voltage in Volts
    --------------------------------------
    -------------smax---------------------
      Limit of Sin(theta)/Wave length
    --------------------------------------
    -------------sftype-------------------
      Structure Factors Type:
      1 - x-ray structure factor (default)
      2 - electron structure factor in volts (V)
      3 - electron structure factor in 1/angstrom^2 in (V)
      4 - electron absorption structure factor in 1/angstrom^2 (V)
    --------------------------------------
    -------------aptype-------------------
      Structure Factor in (Amplitude, Phase) or (Real, Imaginary):
      0 - in (Real, Imaginary) 
      1 - in (Amplitude, Phase) (default)
    --------------------------------------

    ####OUTPUT########
    The function returns an array of structure factors
    Each item in the output array [sfs] is of a dictionary type
    for each element:
      hkl: (h,k,l)    - Miller Indices 
      sw: s           - Sin(theta)/Wave length
      ds: d           - d-spacing
      amp_re          - Structure factor amplitude or rela part
      phase_im        - Structure factor phase or imaginary part
'''
    sf_type_lookup = ['X-ray Structure Factors',
                  'Electron Strcture Factors in kV',
                  'Electron Structure Factor in 1/\u212B',
                  'Electron Absorption Structure Factor in 1/\u212B^2']

    sf_ap_flag = [('real', 'imaginary'), ('amplitude', 'phase')]

    def printCSF(self, sfs):

        sftype =sfs[0]['sftype']
        aptype =sfs[0]['aptype']
        if sftype < 1 or sftype > 4:
            print(f'Invalid structure factor type input: {sftype}')
            return sfs

        if aptype < 0 or aptype > 1:
            print(f'Invalid structure factor output data flag: {aptype}')
            return sfs

        subj = sf_type_lookup[sftype-1]
        print(f"-----{subj}----- ")
        print(f"     crystal\t\t: {self.name}")

        # print(f"     by EMLab Solutions, Inc.     \n")

        mi = "     h k l \t\t: Miller Index"
        print(mi)
        ssw = str(f"     s-w   \t\t: Sin(\u03F4)/Wavelength <= {sfs[0]['smax']}")
        print(ssw )
        dss = "     d-s   \t\t: D-Spacing"
        print(dss)
        
        if sftype > 1:
            print(f"     high voltage\t: {sfs[0]['kv']} V\n")
        else:
            print(f" ")


        sap1 = sf_ap_flag[aptype][0]
        sap2 = sf_ap_flag[aptype][1]
        
        print(f"{'h':^4}{'k':^4}{'l':^5}{'s-w':^16}{'d-s':^16}{sap1:^16}{sap2:^16}\n")
        
        nb = len(sfs)
        for i in range(1, nb, 1):
            h,k,l = sfs[i]['hkl']
            sw,ds = sfs[i]['sw'], sfs[i]['ds']
            sf1,sf2 = sfs[i]['amp_re'], sfs[i]['phase_im']
            
            sh = '{0: < #04d}'. format(int(h))
            sk = '{0: < #04d}'. format(int(k))
            sl = '{0: < #05d}'. format(int(l))

            ssw = '{0: < #016.10f}'. format(float(sw))
            sds = '{0: < #016.10f}'. format(float(ds))
            ssf1 = '{0: < #016.7g}'. format(float(sf1))

            if aptype == 1:
                ssf2 = '{0: < #016.6f}'. format(float(sf2))
            else:
                ssf2 = '{0: < #016.6g}'. format(float(sf2))

            print(f"{sh}{sk}{sl}{ssw}{sds}{ssf1}{ssf2}")    

        print('\n')          

    def generateCSF(self, kv = 100, smax = 0.5, sftype = 1, aptype = 0):
       
        try:
            from . import csf

        except ImportError as e:               
            print(f"Error: required module pyemaps.csf not found")
            return []
        
        sfs = [dict(kv = kv, smax = smax, sftype = sftype, aptype = aptype)]

        cell, atoms, atn, spg = self.prepareDif()
        dif.loadcrystal(cell, atoms, atn, spg, ndw=self._dw)

        nb, ret = csf.generate_sf(kv, smax, sftype, aptype)

        if ret != 0 and nb <= 0:
            print(f'Error running generating structure factor for {self.name}')
            return sfs

        for i in range(2, nb+1):
            ret = 0
            ret,h,k,l,s,d,sf1,sf2 = csf.get_sf(i)
            if ret != 0: 
                print(f'Error running generating sructure factor for {self.name}')
                return sfs
            
            sf = dict(hkl = (h,k,l),
                       sw = s,
                       ds = d,
                       amp_re = sf1,
                       phase_im = sf2
                     )
            sfs.append(sf)    

        #release the memory
        csf.delete_sfmem()

        return sfs
    
    target.generateCSF = generateCSF
    target.printCSF = printCSF

    return target

def add_powder(target):
    '''
    #####INPUT#######
    -------------kv-----------------------
      Accelaration Voltage in Kilo-Volts
    --------------------------------------
    -------------t2max---------------------
      Maximum scattering angle 
    --------------------------------------
    -------------smax---------------------
      Maximum Sin(theta)/Wavelength
    --------------------------------------
    -------------eta, gamma---------------
      Eta - the mixing coefficient between gaussian and lorentzian 
            in a pseudo-Voight peak function
      Gamma - diffraction peaks half maximum half width
    --------------------------------------
    -------------absp---------------------
      With Absoption structure factor or not 
      values - 0, or 1 (default 0)
    --------------------------------------
    -------------isbgdon---------------------
      Background on or not (default no background)
    --------------------------------------
    -------------bamp---------------------
      Background amplitude
    --------------------------------------
    -------------bgamma---------------------
      Background width
    --------------------------------------
    -------------bmfact---------------------
      Background exponential damping factor
    --------------------------------------

    ####OUTPUT########
     The function returns an array of 2 x 1000 containing 
     the powder diffraction for the loaded crystal
     
     The first 1000 is the scattering angle 2theta and the second 
     the intensity    
    '''
    def plotPowder(self, pw):
        """
        plot one powder diffraction
        """

        import matplotlib.pyplot as plt

        xdim, _ = np.shape(pw)
        if xdim !=2:
            raise ValueError("Failed to plot: data error")
        
        fig, ax = plt.subplots()
        fig.canvas.set_window_title('PYEMAPS')    
        fig.suptitle("Electron Powder Diffraction", fontsize=14, fontweight='bold')

        ax.set_title(self.name)
        
        ax.set_ylabel('Intensity')
        ax.set_xlabel('Scattering Angle 2\u03F4 (Rad)')
        ax.plot(pw[0], pw[1], 'b')

        plt.show()

    def generatePowder(self,
            kv = 100, 
            t2max = 0.05, 
            smax = 1.0, 
            eta = 1.0, 
            gamma = 0.001, 
            absp = 0, 
            bg = False,
            bamp = 0.35, 
            bgamma = 0.001, 
            bmfact = 0.02):
        try:
            from . import powder

        except ImportError as e:               
            print(f"Error: required module pyemaps.powder not found")
            return []

        cell, atoms, atn, spg = self.prepareDif()
        dif.loadcrystal(cell, atoms, atn, spg, ndw=self._dw)

        rawP = farray(np.zeros((2,1000), dtype=np.double))
       
        ret = powder.generate_powder(rawP, kv=kv, t2max=t2max, 
                smax = smax, eta=eta, gamma=gamma, isab = absp, 
                isbgdon = bg, bamp = bamp, bgamma = bgamma, 
                bmfact = bmfact)

        if ret != 0:
            print(f'Error generating powder data for {self.name}')

        return rawP
    
    target.generatePowder = generatePowder
    target.plotPowder = plotPowder

    return target

@add_powder
@add_csf    
@add_dpgen   
class Crystal:
    def __init__(self, name="Diamond", data={}):

        if not data or not isinstance(data, dict):
            raise ValueError("Error constructing crytsal object")

        for k, v in data.items():
            
           setattr(self, k, v)

        setattr(self, 'name', name)

    @property
    def cell(self):
        ''' Cell constants '''
        return self._cell

    @property
    def dw(self):
        ''' Debye-Waller factor or thermal '''
        return self._dw

    @property
    def spg(self):
        ''' Space group '''
        return self._spg

    @property
    def atoms(self):
        ''' atom list '''
        return self._atoms

    @property
    def name(self):
        ''' crystal name '''
        return self._name

    @cell.setter
    def cell(self, cc):

        for i, key in enumerate(cell_keys):
            if key in cc:
                try:
                    c = float(cc[key])
                except ValueError:
                    raise ValueError("Error: cell constant must be numeric")
            else:
                raise KeyError("Invaid cell constant key")

        self._cell = Cell(cc)

    @dw.setter
    def dw(self, v):

        if not isinstance(v, str) and not len(v) == 3:
            raise ValueError("Invalid Debye-waller type")

        vl = v.lower()
        if vl == 'iso' or vl == 'par':
            self._dw = 1
        elif  vl.lower() == 'bij':
            self._dw = 2
        elif vl == 'uij':
            self._dw = 3
        else:
            raise ValueError("Invalid Debye-Waller value")

    @name.setter
    def name(self, cn):

        if not isinstance(cn, str):
               raise ValueError("crystal name invalid")
        
        self._name = cn

    @atoms.setter
    def atoms(self, ats):

       if not hasattr(ats, "__len__"):
            raise ValueError("atom list invalid")
       
       akeys = at_iso_keys if self.isISO() else at_noniso_keys

       self._atoms = []
       for a in ats:          
           for k in akeys:
               if k not in a:
                   raise ValueError(str(f"Invalid atom keys {k}"))
           try:
                at = Atom(a)
           except ValueError as ve:
                raise ValueError('Invalid atom data')
            
           self._atoms.append(at)

    @spg.setter
    def spg(self, v):
        
        if not 'number' in v or not 'setting' in v or len(v) != 2:
            raise ValueError("Invalid Space Group data input") 

        self._spg = SPG(v)

    def isISO(self):
        return self.dw == 1

    def __eq__(self, other):

        if not isinstance(other, Crystal):
            return False
        
        if self._name != other._name:
            return False
        
        if not isinstance(other.data, dict) or len(self.data) != len(other.data):
            return False

        cell = Cell(self.data["cell"])
        other_cell = Cell(other.data["cell"])

        if not cell == other_cell:
            return False
        
        if self.data["dw"] != other.data["dw"]:
            return False

        spg = SPG(self.data["spg"])
        other_spg = SPG(other.data["spg"])
        if not spg == other_spg:
            return False

        atoms = []
        for at in self.data["atoms"]:
            atom = Atom(at)
            atoms.append(atom)

        other_atoms = []
        for at in other.data["atoms"]:
            atom = Atom(at)
            other_atoms.append(atom)
        
        if len(atoms) != len(other_atoms):
            return False
        
        for at in atoms:
            if at not in other_atoms:
                return False

        return True
   
    def __str__(self) -> str:
        
        cstr = []
        sdw = ''
        if self._dw == 1:
            sdw = 'iso'
        elif self._dw == 2:
            sdw = 'bij'
        elif self._dw == 3:
            sdw = 'uij'
        else:
            raise ValueError("Invalid dw value out side of (1,2 3)")

        chead = str(f"Crystal name: {self._name}") + str(f' dw {sdw}')
        cstr.append(chead)

        cstr.append(str(self._cell))

        for at in self._atoms:
            cstr.append(str(at))

        cstr.append( str(self._spg))
        
        return '\n'.join(cstr)

    def prepareDif(self):
        '''
        prepare crystal data to be loaded into dif module
        This routine is designed to fit python crystal structure
        into the ones accepted by Fortran backend modules
        
        '''
        diff_cell = self._cell.prepareDif() #cell constant
        
        num_atoms = len(self._atoms)
        atn = farray(np.empty((num_atoms, 10), dtype='c'))
        
        atnarr = [at.symb for at in self._atoms]
        for i, an in enumerate(atnarr):
            if len(an) > 10:
                raise ValueError(f"Atomic symbol too long: {an}")
            atn[i] = an.ljust(10)

        diff_atoms = farray([at.loc for at in self._atoms], dtype = float)
            
        diff_spg = self._spg.prepareDif()
        return diff_cell, diff_atoms, atn, diff_spg

    @classmethod
    def from_builtin(cls, cn='Diamond'):
        """
        import crystal data from .XLT or .DAT file
        The example format:

        crystal Aluminium: dw = iso
        cell 4.0493 4.0493 4.0493 90.0000 90.0000 90.0000
        atom al 0.000000 0.000000 0.000000 0.7806 1.000000
        spg 225 1

        required fields:
        1) Dw = iso by default, other values: uij, bij
        2) Crystal name
        3) Cell constants: 6 floating point values following "cell"
        4) Atoms: one or two lines of atoms positions along with element symbol
            validation:
                a) if dw == iso, atoms line must have at least 4 floating numbers
                in (x,y,x,d-w,occ) where occ defaults to 1.00 if not provided
                b) if dw == uij,bij, atoms line must have at least 9 floating points
                in (x,y,z,b11,b22,b33,b12,b13,b23,occ)

        5) Spg: space group data. Two positive digits: [number, setting]

        """
        import os

        name = cn.lower().capitalize()

        base_dir = os.path.realpath(__file__)
        cbase_dir = os.path.join(os.path.dirname(base_dir), crystal_data_basedir)
        fn = os.path.join(cbase_dir,name+'.xtl')
              
#       Successfully imported crystal data
       
        try:
            _, data = Crystal.loadCrystalData(fn)
            xtl = cls(name, data)

        except (XTLError, AttributeError, CellError, UCError, SPGError) as e:
            raise CrystalClassError(e.message)
        else:
            return xtl

    @classmethod
    def from_xtl(cls, fn):
        """
        Loading crystal instance data from a user supplied xtl formtted data:
         The example format:

        crystal Aluminium: dw = iso [occ = 1.0]
        cell 4.0493 4.0493 4.0493 90.0000 90.0000 90.0000
        atom al 0.000000 0.000000 0.000000 0.7806 1.000000
        spg 225 1

        required fields:
        1) Dw = iso by default, other values: uij, bij
        2) Crystal name
        3) Cell constants: 6 floating point values following "cell"
        4) Atoms: one or two lines of atoms positions along with element symbol
            validation:
                a) if dw == iso, atoms line must have at least 4 floating numbers
                in (x,y,x,d-w,occ) where occ defaults to 1.00 if not provided
                b) if dw == uij,bij, atoms line must have at least 9 floating points
                in (x,y,z,b11,b22,b33,b12,b13,b23,occ)

        5) Spg: space group data. Two positive digits: [number, setting]

        input:
        fn - crystal data file name in above XTL format
            1) If fn is gigen in full path and exists, it will congest it and import the data in fn 
            into the crystal instance
            2) if fn exists in current dictory where python is run
            3) otherwise, it is expect to exist in PYEMAPSHOME directory
            where:
                PYEMAPSHOME is an environment variable defined by user 
                after successful installation
        """
        import os

        cfn = fn
        if not os.path.exists(fn):
            
            pyemaps_home = os.getenv('PYEMAPS_CRYSTALS')
            cfn = os.path.join(pyemaps_home, fn)
            
            if not os.path.exists(cfn):
                # error
                err_msg = str(f"Error finding the data file: {fn}")
                raise XTLError(err_msg)
                # return None
        
#       Successfully imported crystal data
        try:
            name, data = Crystal.loadCrystalData(cfn)
            xtl = cls(name, data)

        except (XTLError, AttributeError, CellError, UCError, SPGError) as e:
            raise CrystalClassError(e.message)
        else:
            return xtl
    
    @classmethod
    def from_cif(cls, fn):
        """
        import crystal data from a cif file
        """
        import os

        cfn = fn
        if not os.path.exists(fn):
            
            pyemaps_home = os.getenv('PYEMAPS_CRYSTALS')
            cfn = os.path.join(pyemaps_home, fn)
            
            if not os.path.exists(cfn):
                err_msg = str(f"Error finding the data file: {cfn}")
                raise XTLError(err_msg)
        
#       Successfully imported crystal data
        try:
            name, data = Crystal.loadCrystalCIFData(cfn)
            cif = cls(name, data)

        except (CIFError, AttributeError, CellError, UCError, SPGError) as e:
            raise CrystalClassError(e.message) from None
        else:
            return cif

    @staticmethod
    def loadCrystalCIFData(fn):
        """
        Loading crystal instance data from a user supplied .cif file:
        
        """
        import os, re
        from CifFile import ReadCif

        SPG_NUMBER_CIFKEY=['_symmetry_Int_Tables_number', 
                           '_symmetry_IT_number',
                           '_space_group_IT_number']

        cfn = fn
        if not os.path.exists(fn):
            
            pyemaps_home = os.getenv('PYEMAPS_CRYSTALS')
            cfn = os.path.join(pyemaps_home, fn)
            
            if not os.path.exists(cfn):
                raise CIFError(cfn, 'file does not exist')
        
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

        lp = getCIFFloat( c_dict['_cell_length_a'])
        
        if lp ==  negative_infinity:
           raise CIFError(cfn, 'missing or invalid cell parameters value for _cell_length_a')

        cell['a'] = lp

        lp = getCIFFloat( c_dict['_cell_length_b'])
        if lp ==  negative_infinity:
           raise CIFError(cfn, 'missing or invalid cell parameters value for _cell_length_b')
        cell['b'] = lp
        
        lp = getCIFFloat( c_dict['_cell_length_c'])
        if lp ==  negative_infinity:
           raise CIFError(cfn, 'missing or invalid cell parameters value for _cell_length_c')
        cell['c'] = lp
        
        lp = getCIFFloat( c_dict['_cell_angle_alpha'])
        if lp ==  negative_infinity:
           raise CIFError(cfn, 'missing or invalid cell parameters value for _cell_angle_alpha')
        cell['alpha'] = lp
        
        lp = getCIFFloat( c_dict['_cell_angle_beta'])
        if lp ==  negative_infinity:
           raise CIFError(cfn, 'missing or invalid cell parameters value for _cell_angle_beta')
        cell['beta'] = lp
        
        lp = getCIFFloat( c_dict['_cell_angle_gamma'])
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
            
        xx = getCIFFloats(xs)

        ys = c_dict['_atom_site_fract_y']
        if not ys and len(ys) != at_len:
           raise CIFError(cfn, 'invalid unit cell value for _atom_site_fract_y')
            
        yy = getCIFFloats(ys)

        zs = c_dict['_atom_site_fract_z']
        if not zs and len(zs) != at_len:
           raise CIFError(cfn, 'invalid unit cell value for _atom_site_fract_z')
            
        zz = getCIFFloats(zs)

        # Occupancy data
        occ = [1.0]*at_len
        if '_atom_site_occupancy' in c_dict:
            occ_raw = getCIFFloats(c_dict['_atom_site_occupancy'])
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
                u11 = getCIFFloats(c_dict['_atom_site_aniso_U_11'])

                for i, uf11 in enumerate(u11):
                    atoms[i]['b11'] = uf11
            
            if '_atom_site_aniso_U_22' in c_dict:
                dw = 'uij'
                u22 = getCIFFloats(c_dict['_atom_site_aniso_U_22'])

                for i, uf22 in enumerate(u22):
                    atoms[i]['b22'] = uf22

            if '_atom_site_aniso_U_33' in c_dict:
                dw = 'uij'
                u33 = getCIFFloats(c_dict['_atom_site_aniso_U_33'])
                for i, uf33 in enumerate(u33):
                    atoms[i]['b33'] = uf33
            
            if '_atom_site_aniso_U_12' in c_dict:
                dw = 'uij'
                u12 = getCIFFloats(c_dict['_atom_site_aniso_U_12'])

                for i, uf12 in enumerate(u12):
                    atoms[i]['b12'] = uf12
        
            if '_atom_site_aniso_U_13' in c_dict:
                dw = 'uij'
                u13 = getCIFFloats(c_dict['_atom_site_aniso_U_13'])
                for i, uf13 in enumerate(u13):
                    atoms[i]['b13'] = uf13
    
            if '_atom_site_aniso_U_23' in c_dict:
                dw = 'uij'
                u23 = getCIFFloats(c_dict['_atom_site_aniso_U_23'])
                for i, uf23 in enumerate(u23):
                    atoms[i]['b23'] = uf23

            if '_atom_site_aniso_B_11' in c_dict:
                b11 = [0.0]*at_len
                dw = 'bij'
                b11 = getCIFFloats(c_dict['_atom_site_aniso_B_11'])
                for i, bf11 in enumerate(b11):
                    atoms[i]['b11'] = bf11
            
            if '_atom_site_aniso_B_22' in c_dict:
                b22 = [0.0]*at_len
                dw = 'bij'
                b22 = getCIFFloats(c_dict['_atom_site_aniso_B_22'])
                for i, bf22 in enumerate(b22):
                    atoms[i]['b22'] = bf22
               
            if '_atom_site_aniso_B_33' in c_dict:
                b33 = [0.0]*at_len
                dw = 'bij'
                b33 = getCIFFloats(c_dict['_atom_site_aniso_B_33'])
                for i, bf33 in enumerate(b33):
                    atoms[i]['b33'] = bf33
            
            if '_atom_site_aniso_B_12' in c_dict:
                b12 = [0.0]*at_len
                dw = 'bij'
                b12 = getCIFFloats(c_dict['_atom_site_aniso_B_12'])
                for i, bf12 in enumerate(b12):
                    atoms[i]['b12'] = bf12
            
            if '_atom_site_aniso_B_13' in c_dict:
                b13 = [0.0]*at_len
                dw = 'bij'
                b13 = getCIFFloats(c_dict['_atom_site_aniso_B_13'])
                for i, bf13 in enumerate(b13):
                    atoms[i]['b13'] = bf13

            if '_atom_site_aniso_B_23' in c_dict:
                b23 = [0.0]*at_len
                dw = 'bij'
                b23 = getCIFFloats(c_dict['_atom_site_aniso_B_23'])
                for i, bf23 in enumerate(b23):
                    atoms[i]['b23'] = bf23
            
        elif '_atom_site_U_iso_or_equiv' in c_dict or '_atom_site_Uiso_or_equiv' in c_dict:
            
            dw = 'uij'
            bxx = getCIFFloats(c_dict['_atom_site_U_iso_or_equiv'])
            for i, b in enumerate(bxx):
                atoms[i]['b11'] = atoms[i]['b22'] = atoms[i]['b33'] = b
                atoms[i]['b12'] = atoms[i]['b13'] = atoms[i]['b23'] = 0.0


        elif '_atom_site_B_iso_or_equiv' in c_dict:
            dw = 'iso'
        
            d_w = getCIFFloats(c_dict['_atom_site_B_iso_or_equiv'], 0.05)
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
            v, vsymb = validAtomSiteLabel(symb)        
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
            spg_num = getCIFInt(c_dict[k]) 

        if spgInCIF and spg_num >= 1 and  spg_num <= SPG_ITNUM_MAX:
            
            spg_pairs.clear()
            spg_smax = spgra.getspgsettingmax(spg_num)
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

            # TODO: custome exception for SPG, Atom and cell?
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
                emaps_spghm, spgnum, spgsetting = spgra.getspghm(i+1)

                cemaps_spghm = emaps_spghm.decode().strip()

                emaps_spghm_list = re.split(r'\s+', cemaps_spghm)

                nmatched = matchCIFHM(emaps_spghm_list, spgHM)
                
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
            spg_setting = getCIFInt(c_dict['_symmetry_space_group_setting'])

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
            
            l, pact = scrubCIFSymmXYZ(cif_coords, SPG_SYMMETRY_MAXLEN)
            
            max_match = -1
            new_pairs = []
            for sp in spg_pairs:
                coords = farray(np.empty((SPG_SYMMETRY_MAXCOL, SPG_SYMMETRY_MAXLEN), dtype='c'))
                coords, n = spgra.getsymmetryxyz(sp[0], sp[1], coords)
                
                if n == -1:
                    # This should not happen but check for it anyway
                    raise CIFError(cfn, 'symmetry lookup in pyemaps space group failed')
                if n > l:
                    # no match
                    continue

                if compareCIFSymmetry(n, coords, pact) == 0:
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

    @staticmethod
    def loadCrystalData(fn, cn=None):
        """
        Base function for from_builtin and from_xtl
        """
        import re

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

                        # if owlen < 1:
                        #     print(f"Error: dw data retireval failure for {cname}")
                        #     return name, data
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
                        if dw != 'iso' and dw != 'uij' and dw != 'bij': #TODO message on dw
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

                        alen = Crystal.get_atom_len(data['dw'])
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
                    valided, new_symb = validAtomSiteLabel(symb)
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

        except IOError as e:
            raise XTLError(fn, e.message)

        return name, data
    
    @staticmethod
    def get_atom_len(dw):
        if dw == 'iso':
            return len(at_iso_keys)
        
        if dw == 'uij' or dw == 'bij':
            return len(at_noniso_keys)
        
        return -1 #error

    @classmethod ####TODO
    def from_json_file(cls, jfn):
        with open(jfn) as jf:
            data=json.load(jf)
            if "name" in data:
                name = data["name"]
                return cls(name, data)
            
            return cls()

    @classmethod ####TODO
    def from_json(cls, jdata):
        if "name" in jdata:
            name = jdata["name"]
            return cls(name, jdata)

        return cls()            

    @staticmethod
    def list_all_builtin_crystals():
        """
        
        List of all builtin crystals provided by pyemaps
        use this routine to determine which crystal to load
        """
        import os, glob
        base_dir = os.path.realpath(__file__)
        cbase_dir = os.path.join(os.path.dirname(base_dir), crystal_data_basedir)
        cbase_files = os.path.join(cbase_dir, '*.xtl')
        cfile_list = glob.glob(cbase_files)

        return [os.path.basename(name).split('.')[0] for name in cfile_list]
            
    def generateDP(self, mode = None, dsize = None, em_controls = None):
        """
        This routine returns a DP object.

        New DP generation based on the crystal data and Microscope control 
        parameters. We will add more controls as we see fit.  

        :param mode: Optional mode of diffraction mode - normal(1) or CBED(2)
        :param dsize: Optional of CBED circle size - defaults to dif.DEF_DSIZE = 0.16
        :param: Optional em_controls of electron microscope controls dictionary - defaults to DEF_CONTROLS
        :return: a DP object
        :rtype: diffPattern
        """
        from . import DP
        from . import DPError


        if not em_controls:
            em_controls =EMC()

        tx0, ty0 = em_controls.tilt
        dx0, dy0 = em_controls.defl
        cl, vt = em_controls.cl, em_controls.vt
        zone = em_controls.zone

        ret, diffp = self._get_diffraction(zone,mode,tx0,ty0,dx0,dy0,cl,vt,dsize)
        if ret != 200:
            raise DPError('failed to generate diffraction patterns')

        return em_controls, DP(diffp)
        
    def gen_diffPattern(self, zone = None,
                              mode = None,
                              tx0 = None,
                              ty0 = None,
                              dx0 = None,
                              dy0 = None,
                              cl = None,
                              vt = None,
                              dsize = None):
        """
        Wrapper for get_diffraction routine for pyemaps version <= 0.3.4
        use generateDP call for pyemaps version > 0.3.4
        """
        from . import DP
        from . import DPError

        ret, diffp = self._get_diffraction(zone,mode,tx0,ty0,dx0,dy0,cl,vt,dsize)
        if ret != 200:
            raise DPError('failed to generate diffraction patterns')

        return DP(diffp)

    def _get_diffraction(self, zone = None, 
                              mode = None, 
                              tx0 = None, 
                              ty0 = None, 
                              dx0 = None,
                              dy0 = None,
                              cl = None,
                              vt = None, 
                              dsize = None):
        """
        This routine returns raw diffraction data from emaps dif extension

        If none of the parameters are supplied, the routine will
        generate the diffraction patterns in default set in the fortran
        backend indicated below:
            zone = (0,0,1) zone axis
            mode = normal  kinematic diffraction mode (CBED is the other)
            (tx0,ty0) = (0.0,0.0) tilt angles
            (dx0,dy0) = (0.0,0.0) deflection move
            cl = 1000 EM length
            vt = 200  voltage
            cl and vt must be set togather
            dsize = 0.05 spot disk size in nm
        If any of the values are set, the following tuples must be set togather
            (tx0,ty0,dx0,dy0) 
            (cl,vt)
            if mode == 2 (CBED), then dsize must be set

        """
        import copy

        dif.initcontrols()
        # mode defaults to DEF_MODE, in which dsize is not used
        # Electron Microscope controls defaults - DEF_CONTROLS

        if mode == 2:
            dif.setmode(mode)
            if dsize == None:
                ds = DEF_CBED_DSIZE          
            else:
                ds = dsize
            dif.setdisksize(float(ds))

        if tx0 != None and ty0 != None and dx0 != None and dy0 != None:
            dif.setsamplecontrols(tx0, ty0, dx0, dy0)

        if cl != None and vt != None:
            dif.setemcontrols(cl, vt)
        
        if zone != None:
            dif.setzone(zone[0], zone[1], zone[2])
        
        cell, atoms, atn, spg = self.prepareDif()
        dif.loadcrystal(cell, atoms, atn, spg, ndw=self._dw)

        ret = 1
        ret = dif.diffract()
        if ret == 0:
            return 500, ({})

        shiftx, shifty = dif.get_shifts()
        bounds = (shiftx, shifty)

        #remove module internal global memory
        dif.diff_internaldelete(0)

        klines=[]
        num_klines = dif.getknum()
        
        if (num_klines > 0):
            klines_arr = farray(np.zeros((num_klines, 4)), dtype=np.double)
            if dif.get_klines(klines_arr) == 0:
                for i in range(num_klines):
                    j=i+1
                    x1,y1,x2,y2=klines_arr[i][0:]
                    line=[]
                    line.append((x1,y1))
                    line.append((x2,y2))
                    klines.append(line)
            else:
                print(f"Error: retrieving klines!")
                return 500, ({})

        disks=[]
        num_disks = dif.getdnum()
        if (num_disks > 0):
            disks_arr = farray(np.zeros((num_disks, 6)), dtype=np.double)
            if dif.get_disks(disks_arr) == 0:
                for i in range(num_disks):
                    x1,y1,r,i1,i2,i3=disks_arr[i][0:]
                    disk={}
                    disk['c']=(x1,y1)
                    disk['r']=r
                    disk['idx']=(int(i1),int(i2),int(i3))
                    disks.append(disk)
            else:
                print(f"Error: retrieving disks!")
                return 500, ({})

        hlines=[]
        num_hlines = 0
        if (mode == 2):
            num_hlines = dif.gethnum()
            # print(f"hline number: {num_hlines}")
            if (num_hlines > 0):
                hlines_arr = farray(np.zeros((num_hlines, 4)), dtype=np.double)
                if dif.get_hlines(hlines_arr) == 0:
                    for i in range(num_hlines):
                        x1,y1,x2,y2 = hlines_arr[i][0:]
                        line=[]
                        line.append((x1,y1))
                        line.append((x2,y2))
                        hlines.append(line)
                else:
                    print(f"Info: no hlines detected!")
                    return 500, ({})

        nums = {"nklines" : num_klines, "ndisks" : num_disks, "nhlines" : num_hlines}
        data = {"nums" : copy.deepcopy(nums), "bounds": copy.deepcopy(bounds), \
                    "klines": copy.deepcopy(klines), "hlines": copy.deepcopy(hlines), \
                    "disks": copy.deepcopy(disks), "name" : self.name}

        # delete diff pattern memory
        dif.diff_delete()
        return 200, data

    def d2r(self, v = (0.0, 0.0, 0.0)):
        '''
        Transform from real to recriprocal space
        '''           

        cell, atoms, atn, spg = self.prepareDif()
        
        dif.loadcrystal(cell, atoms, atn, spg, ndw=self.dw)

        x, y, z = v
        rx, ry, rz = dif.drtrans(x, y, z, 0)

        dif.crystaldelete()
        return rx, ry, rz

    def r2d(self,  v = (0.0, 0.0, 0.0)):
        '''
        Transform from recriprocal to real space
        '''          

        cell, atoms, atn, spg = self.prepareDif()
        
        dif.loadcrystal(cell, atoms, atn, spg, ndw=self.dw)

        x, y, z = v
        dx, dy, dz = dif.drtrans(x, y, z, 1)

        dif.crystaldelete()
        return dx, dy, dz

    def angle(self, v1 =(1.0, 0.0, 0.0), \
                     v2 = (0.0, 0.0, 1.0),
                     type = 0):
        '''
        Type = 0: Calculate angle between two real space vectors
	    Type = 1: Calculate angle between two reciprocal space vectors
        '''
        x1, y1, z1 = v1
        if x1 == 0.0 and y1 == 0.0 and z1 == 0.0:
            raise ValueError("Error: input vector can't be zero")
        
        x2, y2, z2 = v2
        if x2 == 0.0 and y2 == 0.0 and z2 == 0.0:
            raise ValueError("Error: input vector can't be zero")           

        cell, atoms, atn, spg = self.prepareDif()
        
        dif.loadcrystal(cell, atoms, atn, spg, ndw=self.dw)

        a = dif.ang(x1, y1, z1, x2, y2, z2, type)

        dif.crystaldelete()
        return a

    def vlen(self, v = (1.0, 0.0, 0.0), type = 0):
        
        '''
        Type = 0: Calculate length of a real space vector
	    Type = 1: Calculate length of a reciprocal space vector
        '''        
           
        cell, atoms, atn, spg = self.prepareDif()
        
        dif.loadcrystal(cell, atoms, atn, spg, ndw=self.dw)

        x, y, z = v
        ln = dif.vlen(x, y, z, type)

        dif.crystaldelete()
        return ln

    def wavelength(self, kv = 100):
        '''
        Calculate electron wavelength
        '''
        import math

        if kv <= 0.0:
            raise ValueError("Error: input kv must be positive number")

        return 0.3878314/math.sqrt(kv*(1.0+0.97846707e-03*kv))
	