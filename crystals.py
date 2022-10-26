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

import os
import json
    
from .errors import *
from .fileutils import *
from . import XTLError, CellError, UCError, SPGError
from .diffract.bloch_dec import add_bloch
from .diffract.csf_dec import add_csf
from .diffract.mxtal_dec import add_mxtal
from .diffract.powder_dec import add_powder
from .diffract.dpgen_dec import add_dpgen
from .diffract.stereo_dec import add_stereo
from .diffract.dif_dec import add_dif

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

    def prepare(self):
        cell0 = self.__dict__
        celarr = np.zeros((6,))
        for i, key in enumerate(cell_keys):
            sk = '_' + key
            if sk in cell0:
                celarr[i]=cell0[sk]
            else:
               raise CellDataError("Unrecognized cell length or angle data")
        
        return farray(celarr, dtype=float)

    def __iter__(self):
        for key in self.__dict__:
            yield (key[1:], getattr(self, key))

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
            
        set_max = get_setmaxbynumber(inum)
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

    def prepare(self):
         return farray([self._number, self._setting], dtype=int)

    def __iter__(self):
        for key in self.__dict__:
            yield key[1:], getattr(self, key)

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
        self._data = vloc_dict
                
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

    def __iter__(self):
        for key in self.__dict__:
            if key == '_symb':
                yield 'symb', getattr(self, key)
            else:
                for key in self._data:
                    yield key, self._data[key]

    def prepare(self, rvec = None):
       if rvec is None:
              return self._loc

       if len(rvec) != 3 and not all(isinstance(v, [int,float]) for v in rvec):
              raise UCError('R vector must be three integers tuple')

       tloc=[float(l) for l in self._loc]
       
       for i in range(3):
         tloc[i] += rvec[i]
            
       return tloc   
       
# ---------------adding these features to Crystal class when correspoding
#                backend extension module is available
# ------------------------------------------------------------------------  
@add_mxtal
@add_stereo
@add_bloch
@add_powder
@add_csf    
@add_dpgen      
@add_dif   
class Crystal:
    def __init__(self, name="Diamond", data={}):

        if not data or not isinstance(data, dict):
            raise ValueError("Error constructing crytsal object")

        # print(f'In crystal creating by a dict: {data.items()}')
        if 'dw' not in data:
            raise CrystalClassError("Debye-Waller factor or thermal data missing")

        setattr(self, 'dw', data['dw'])

        for k, v in data.items():
           if k != 'dw' and k != 'name':
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
        if isinstance(v, str):
            if not len(v) == 3:
                raise ValueError("Invalid Debye-waller type")
            else:
                vl = v.lower()
                if vl == 'iso' or vl == 'par':
                    self._dw = 1
                elif  vl.lower() == 'bij':
                    self._dw = 2
                elif vl == 'uij':
                    self._dw = 3
                else:
                    raise ValueError("Invalid Debye-Waller value")
        elif isinstance(v, int):
            if v not in [1,2, 3]:
                raise ValueError("Invalid Debye-Waller value")
            else:
                self._dw = v
        else:
            raise ValueError("Invalid Debye-waller type")


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
        return self._dw == 1

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
    
    def __iter__(self):
        for k in self.__dict__:
            if k == '_name' or k == '_dw':
                yield (k[1:], getattr(self, k))
            if k == "_cell":
                 yield('cell', dict(self._cell))
            if k == "_spg":
                 yield('spg', dict(self._spg))
            if k == "_atoms":
                 yield('atoms', [dict(a) for a in self.atoms])

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

        # name = cn.lower().capitalize()

        base_dir = os.path.realpath(__file__)
        cbase_dir = os.path.join(os.path.dirname(base_dir), crystal_data_basedir)
        fn = os.path.join(cbase_dir, cn+'.xtl')
              
#       Successfully imported crystal data
        try:
            name, data = loadCrystalData(fn)
            xtl = cls(name, data)

        except (XTLError, CellError, UCError, SPGError) as e:
            raise CrystalClassError(e.message)
        except (FileNotFoundError, IOError) as e:
            raise CrystalClassError('Error creating crystal: ' + str(e))
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

        cfn = fn
        if not os.path.exists(fn):
            # find it in pyemaps data home or current directory
            pyemaps_datahome = find_pyemaps_datahome(home_type = 'crystals')
            cfn = os.path.join(pyemaps_datahome, fn)
            
            if not os.path.exists(cfn):
                err_msg = str(f"Error finding the data file: {cfn}")
                raise CrystalClassError(err_msg)
        # otherwise it is a full path file that exists
        try:
            name, data = loadCrystalData(cfn)
            xtl = cls(name, data)

        except (XTLError, CellError, UCError, SPGError) as e:
            raise CrystalClassError(e.message)
        except (FileNotFoundError, AttributeError) as e:
            raise CrystalClassError(e.message)
        else:
            return xtl
    
    @classmethod
    def from_cif(cls, fn):
        """
        import crystal data from a cif file
        """
        from . import CIFError, CellError, UCError, SPGError

        cfn = fn
        if not os.path.exists(fn): # exists full path or file name in current working directory
            # find it in pyemaps data home or current directory
            pyemaps_datahome = find_pyemaps_datahome(home_type = 'crystals')
            cfn = os.path.join(pyemaps_datahome, fn)
            
            if not os.path.exists(cfn):
                err_msg = str(f"Error finding the data file: {cfn}")
                raise CrystalClassError(err_msg)

        # otherwise it is a full path file that exists
        try:
            name, data = loadCrystalCIFData(cfn)
            cif = cls(name, data)

        except (CIFError, AttributeError, CellError, UCError, SPGError) as e:
            raise CrystalClassError(e.message) from None
        else:
            return cif

    @classmethod 
    def from_jsonfile(cls, jfn):
        try:
            with open(jfn) as jf:
                data=json.load(jf)
        except:
            raise CrystalClassError('Failed to open the json file')
        else:
            if 'name' not in data:
                raise CrystalClassError('Failed to create crystal object with input dictionary')

            return cls(data['name'], data)

    @classmethod
    def from_dict(cls, cdict):
        if 'name' not in cdict:
            raise CrystalClassError('Failed to create crystal object with input dictionary')
        
        name = cdict["name"]
        return cls(name, cdict)           

    @staticmethod
    def list_all_builtin_crystals():
        """
        
        List of all builtin crystals provided by pyemaps
        use this routine to determine which crystal to load
        """
        import glob
        base_dir = os.path.realpath(__file__)
        cbase_dir = os.path.join(os.path.dirname(base_dir), crystal_data_basedir)
        cbase_files = os.path.join(cbase_dir, '*.xtl')
        cfile_list = glob.glob(cbase_files)

        return [os.path.basename(name).split('.')[0] for name in cfile_list]
