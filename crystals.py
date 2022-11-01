# '''
# This file is part of pyemaps
# ___________________________

# pyemaps is free software for non-comercial use: you can 
# redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either 
# version 3 of the License, or (at your option) any later version.

# pyemaps is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with pyemaps.  If not, see <https://www.gnu.org/licenses/>.

# Contact supprort@emlabsoftware.com for any questions and comments.
# ___________________________


# Author:             EMLab Solutions, Inc.
# Date Created:       May 07, 2022  

# '''
import os
import json
import pstats
from tkinter import N
    
import numpy as np
from numpy import asfortranarray as farray

from .errors import *
from .fileutils import *

class Cell:
    """

    Cell constant data class. 

    """
    def __init__(self, data=None):
        """
        :param data: Optional cell constant python dictionary or list
        :type data: dict or list
        :raise CellValueError: if cell data validations fail.

        Example of the cell constant input in dictionary:

        .. code-block:: json

            {
                "a": "5.4307",
                "b": "5.4307",
                "c": "5.4307",
                "alpha": "90.0",
                "beta": "90.0",
                "gamma": "90.0"
            }
        
        Example of the cell constant input in python list:

        .. code-block:: python

            ["5.4307", "5.4307", "5.4307", "90.0", "90.0", "90.0"]
            # or
            [5.4307, 5.4307, 5.4307, 90.0, 90.0, 90.0]

        """
        if data is None:
            setattr(self, 'a', 0.0)
            setattr(self, 'b', 0.0)
            setattr(self, 'c', 0.0)
            setattr(self, 'alpha', 0.0)
            setattr(self, 'beta', 0.0)
            setattr(self, 'gamma', 0.0)
            return

        if len(data) != len(cell_keys):
            raise CellDataError("Cell constant data length must be 6")

        if type(data) is list:

            c_dict = dict(zip(cell_keys, data))
            for k, v in c_dict.items():
                setattr(self, k, v)
            return

        if type(data) is dict:

            for k, v in data.items():
                if k not in cell_keys:
                    raise CellDataError("Unrecognized cell constant key")
                setattr(self, k, v)
            return

        raise CellDataError('Cell data validation failed')

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
    def a(self, v=None): 
        '''
        Sets b cell length.

        :param v: required, must be a numeral or numberal string
        
        ''' 
        av = 0.0 if v is None else v

        try:
            self._a = float(av)

        except ValueError as e:
            raise CellValueError(1, "b")

    @b.setter
    def b(self, v=None):
        '''
        Sets b cell length.

        :param v: required, must be a numeral or numberal string
        
        ''' 
        bv = 0.0 if v is None else v

        try:
            self._b = float(bv)

        except ValueError as e:
            raise CellValueError(1, "b")

    @c.setter
    def c(self, v=None):
        '''
        Sets c cell length.

        :param v: required, must be a numeral or numberal string
        
        ''' 
        cv = 0.0 if v is None else v
        try:
            self._c = float(cv)

        except ValueError as e:
            raise CellValueError(1, "c")


    @alpha.setter
    def alpha(self, v=None):
        '''
        Sets cell alpha angle.

        :param v: required, must be a numeral or numberal string
        
        ''' 
        av = 0.0 if v is None else v
        try:
            self._alpha = float(av)

        except ValueError as e:
            raise CellValueError("alpha")

    @beta.setter
    def beta(self, v=0.0):
        '''
        Sets cell beta angle.

        :param v: required, must be a numeral or numberal string
        
        ''' 
        bv = 0.0 if v is None else v
        try:
            self._beta = float(bv)

        except ValueError as e:
            raise CellValueError("beta")

    @gamma.setter
    def gamma(self, v=0.0):
        '''
        Sets cell gamma angle.

        :param v: required, must be a numeral or numberal string
        
        ''' 
        gv = 0.0 if v is None else v
        try:
            self._gamma = float(gv)

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
        """
        Prepare cell constant data for loading into backend modules
        
        """
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

class Atom:
    """
    Crystal atom descriptor class. 

    """
    def __init__(self, a_type=0, sym = '', data=None):
        """
        Internal representation of single atom in a crystal.
        a_type: atom thermal type
        symb:   atomic sybom
        loc:    atomic position, thermal properties and occupacy information

        :param a_type: Optional atom thermal factor type - 0 for isotropic and 1 for anisotropic.
        :type a_type: int
        :param data: Optional atoms data input. Default None
        :type data: dict or list
        :raise UCError: if data validation fails.

        Example of isotropic crystal atom data input for loc_dict:

        .. code-block:: json 
            
            {
                "symb": "Si",
                "x": "0.125",
                "y": "0.125",
                "z": "0.125",
                "d-w": "0.4668",
                "occ": "1.00" 
            }

        Example of isotropic crystal atom data input loc_dict in list object :

        .. code-block:: python 
            
            ["0.125", "0.125", "0.125", "0.4668", "1.00"]
            # or
            [0.125, 0.125, 0.125, 0.4668, 1.00]

        .. warning:: 

            When atom positional data is entered as a python list object
            the order of the elements must match their corresponding keys:

        .. code-block:: python 

            ['x','y','z','d-w','occ']       # for isotropic atom type
            ['x','y','z','b11','b22','b33','b12','b13','b23','occ']   #for anisotropic atome types

        .. note:: 
        
            The list input for atom positional data can have 'occ' data missing. In which case
            pyemaps will default its occupancy data to 1.0

        """
        setattr(self, 'atype', a_type)
        setattr(self, 'symb', sym)

        if data is None or type(data) is list:
            setattr(self, 'loc', data)
            return
        
        if type(data) is not dict:
            raise UCError("Atom position property input must be a dictionary or a list")

        akey = at_iso_keys if a_type == 1 else at_noniso_keys
        klen = len(akey)

        vloc = [0.0]*(klen-1)
        vloc[-1] = 1.0

        if len(data) > klen-1 or len(data) < klen-2:
            raise UCError("Atom position property input invalid")

        # check to see if required keys are present
        for i, k in enumerate(akey[1:klen-1]):
            if k not in data:
                raise UCError(f"Required key {k} missing from {akey[1:klen]}")
        
            vloc[i] = data[k]
        
        if 'occ' in data:
            vloc[-1] = data['occ']

        setattr(self, 'loc', vloc)   
        
    @property
    def symb(self):
        """
        Atom symbol

        """
        return self._symb

    @property
    def atype(self):
        """
        Atom dw type - isotropic or not

        """
        return self._atype

    @property
    def loc(self):
        """
        atomic position, thermal properties and occupacy information

        """
        return self._loc

    @symb.setter
    def atype(self, a_type=0):
        '''
        setting atomic thermal property
        1 - isotropic
        >1 - all other types (corresponding to anisotropic types, uij, bij)

        '''
        if type(a_type) is not int or \
        (a_type < 1 or a_type > 3):
            raise UCError("Atom thermal property type must be 0 for isotropic or 1 for other types")
        
        self._atype = a_type

    @symb.setter
    def symb(self, sb=''):
        MAX_ATOM_SYMBOL_LEN = 10
        if len(sb) == 0:
            sb='          '
        
        if len(sb) > MAX_ATOM_SYMBOL_LEN or len(sb) < 1:
            raise UCError("Invalid atom symbol length")

        self._symb = sb
    
    @loc.setter
    def loc(self, locdata=None):
        '''
        Atom position attribute.
        
        Must be a list of floats or None. In later case, this attribute
        will default to all 0.0.

        '''
        akeys = at_iso_keys if self.isISO() else at_noniso_keys
        keylen = len(akeys)

        if locdata is None or len(locdata) == 0:
            locdata = [0.0]*keylen
            locdata[-1] = 1.0
            self._loc = locdata
            # defaults if location data is not provided
            return


        if type(locdata) is not list:
            raise UCError("Invalid data type for atomic position entered!")

        inputlen = len(locdata)
        # akeys = at_iso_keys if self.isISO() else at_noniso_keys

        if inputlen < keylen-2 or inputlen > keylen-1:
            raise UCError(f"Input atom position data must have length of {keylen-1} or {keylen}")

        self._loc=[0.0]*(keylen-1)
        self._loc[-1] = 1.0 

        for i in range(len(locdata)):
            self._loc[i] = locdata[i]

        self._data = dict(zip(akeys, self._loc))
                
    def __eq__(self, other):
        if not isinstance(other, Atom):
            return False

        if self._atype != other.atype: 
            return False

        if self._symb.lower() != other._symb.lowder(): 
            return False

        if self._loc != other.loc:
            return False

        return True
    
    def __str__(self) -> str:
        atoms=[f"{self._symb}"]
        
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

    def isISO(self):
        return self._atype == 1

    def prepare(self, rvec = None):
       if rvec is None:
              return self._loc

       if len(rvec) != 3 and not all(isinstance(v, (int,float)) for v in rvec):
              raise UCError('R vector must be three integers tuple')

       tloc=[float(l) for l in self._loc]
       
       for i in range(3):
         tloc[i] += rvec[i]
            
       return tloc   


class SPG:
    """
    Space Group class. This class includes: 
    
    1. Symmetry International Tables Number, and
    2. Symmetry Space Group Setting

    required by Crystal class

    """
    def __init__(self, data=None):
        """
        :param data: optional space group data input.
        :type data: dict or list
        :raise SPGInvalidDataInputError: if cell data validations fail.

        Example of space group input:
        
        .. code-block:: json

            {
                "number": "227", // <---Symmetry International Tables Number
                "setting": "2"   // <---Symmetry Space Group Setting  
            } 
        
        .. code-block:: python

            ["227", "2"] 
            # or
            [227, 2]

        """
        if data is None:
            setattr(self, 'number', 0)
            setattr(self, 'setting', 0)
            return
        
        if type(data) is list:
            if len(data) != 2:
                raise SPGInvalidDataInputError()
            setattr(self, 'number', data[0])
            setattr(self, 'setting', data[1])
            return

        if type(data) is dict:
            if len(data) != 2:
                raise SPGInvalidDataInputError()

            if 'number' not in data or 'setting' not in data:
                raise SPGInvalidDataInputError()

            setattr(self, 'number', data['number'])
            setattr(self, 'setting', data['setting'])
            return

        raise SPGInvalidDataInputError()
            
    @property
    def number(self):
        ''' Symmetry International Tables Number'''
        return self._number

    @property
    def setting(self):
        ''' Symmetry Space Group Setting'''
        return self._setting

    @number.setter
    def number(self, n = None):
        """
        Setting Symmetry Space Group Setting Number
        
        :param num: required integer number that is in the range of spg backend data module
        :type num: int
        :raise SPGInvalidDataInputError: if the input is not in the range in spg data module.

        """
        num = 0 if n is None else n

        try:
           self._number = int(num)
        except ValueError as e:
            raise SPGInvalidDataInputError()
        
    @setting.setter
    def setting(self, s=None):
        """
        Symmetry setting data., provided IT number is set first
        :param s: required integer number that is in the range of spg backend data module
        :type s: int or string
        :raise SPGInvalidDataInputError: if the input is not in the range in spg data module.

        """
        if s is None:
            sn = 0
        else:
            sn = s

        try:
            self._setting = int(sn)
        except ValueError:
            raise SPGInvalidDataInputError()


    def __eq__(self, spgo):
         if not isinstance(spgo, SPG):
            return False

         return (self._number == spgo.number) and (self._setting == spgo.setting)

    def __str__(self):
        return str(f"spg: {self._number} {self._setting}")
    
    def __repr__(self):
        return str(f"spg: number: {self._number} setting: {self._setting}")

    def prepare(self):
        
        # validating here
        if self._number < 1 or self._number > SPG_ITNUM_MAX:
            raise SPGITMumberNotInRangeError(SPG_ITNUM_MAX)
        
        setting_max = get_setmaxbynumber(self._number)

        if self._setting > setting_max:    
            raise SPGSettingNotInRangeError(setting_max)

        return farray([self._number, self._setting], dtype=int)

    def __iter__(self):
        for key in self.__dict__:
            yield key[1:], getattr(self, key)     

# -------------------------PYEMAPS EXTENSIONS--------------------------
#       add new features and methods to Crystal class when 
#       correspoding backend extension module becomes available. 
# 
#       These new methods extend the existing Crystal class
#       methods by wrapping the extension's backend module 
#       (e.g. csf - crystal structure factor module) that provide 
#       interfaces with the new extension to extract module data 
#       such as x-ray structure factor in the above example.  
# --------------------------------------------------------------------- 

#---Crystal structure factors---
#   1) X-Ray Structure Factors
#   2) Electron Structure Factor in V (volts)
#   3) Electron Structure Factor in 1/Angstron^2
#   4) Electron Absorption Structure Factor in 1/Angstron^2 
from .diffract.csf_dec import add_csf

#---Crystal constructor---
#   building atomic structure based on crystal data
from .diffract.mxtal_dec import add_mxtal

#---Powder diffraction Calculation---
#   TODO
from .diffract.powder_dec import add_powder

#---Kinematic diffraction patterns database generation (upcoming) 
from .diffract.dpgen_dec import add_dpgen

#---Stereodiagram---
#   generates and plots stereographic projections
from .diffract.stereo_dec import add_stereo

#---Kinematic Diffraction Simulations---
from .diffract.dif_dec import add_dif

#---Dynamic Diffraction Simulations---
from .diffract.bloch_dec import add_bloch

@add_mxtal              
@add_stereo              
@add_bloch              
@add_powder
@add_csf    
@add_dpgen      
@add_dif   
class Crystal:
    """
    This class is defined to capture and to validate crystal data. It is composed of
    the following data:
    
    * **Cell**: cell constants object
    * **A list of Atoms**: list of Atom objects
    * **spg**: Space Group SPG object
    * **dw**: Debye-waller factor type - isotropic or not 
    * **name**: Crystal name

    Crystal class constructors include:

    1. Crystal(name, data)                          //python dictionary object (default)
    2. Crystal.from_builtin(name)                   //from pyemaps' own built-in crystal database
    3. Crystal.from_xtl(xtl_filename)               //from a proprietory crystal data file
    4. Crystal.from_cif(cif_filename)               //from Crystallographic Information File
    
    In addition to standard methods for getting and setting each components of 
    the crystal class, interfaces and methods to generate simulation data using the crystal
    data attributes from backend modules are added as the corresponding modules become available.

    """
    def __init__(self, name="Diamond", data=None):
        """
        Default constructor taking a python dictionary of the followign format    
        
        :param name: Optional name of the crystal or default to 'Diamond'
        :type name: string
        :param data: Optional data of the crystal. Default to dictionary with just dw value of 'iso'
        :type data: dict
        :raise CrystalClassError: If data validations fail.

        
        The dictionary object example for Silicon:

        .. code-block:: json

            {'cell':                                       //Cell constants
                {'a': '5.4307',
                'b': '5.4307',
                'c': '5.4307',
                'alpha': '90.0',
                'beta': '90.0',
                'gamma': '90.0'},
            'atoms':                                        //atomic info.
                [
                    {'symb': 'si',                          //atom symbol
                    'x': '0.125',                           //atom coordinates
                    'y': '0.125',  
                    'z': '0.125',
                    'd-w': '0.4668',                        //Debye-waller factor
                    'occ': 1.00},                           //occupancy
                ],
            'spg':                                          //space group info
                {'number': '227'                            //symmetry international table(IT) number
                'setting': '2'                              //symmetry space group setting
                },
            'dw': 'iso'                                     //Debye-waller factor

            }

        """
         
        setattr(self, 'name', name)

        if data is None:

            setattr(self, 'dw', 1)     
            setattr(self, 'cell', Cell())
            setattr(self, 'atoms', [])
            setattr(self, 'spg', SPG())
            return
        
        if not isinstance(data, dict):
            raise CrystalClassError("Error constructing crytsal object")

        for k in required_keys:
            if k not in data:
                raise CrystalClassError(f"Required key {k} missing")

        setattr(self, 'dw', data['dw'])
        c = Cell(data = data['cell'])
        setattr(self, 'cell', c)
        
        ats = data['atoms']
        catoms = []
        for at in ats:
            
            if 'symb' not in at:
                raise CrystalClassError("Atom data input must have symbol")
            sym = sym=at['symb']
            del at['symb']

            att = Atom(a_type = self._dw, sym=sym, data = at)
            catoms.append(att)
        
        setattr(self, 'atoms', catoms)

        spg = SPG(data = data['spg'])
        setattr(self, 'spg', spg)

    @property
    def cell(self):
        ''' Cell constants '''
        return self._cell

    @property
    def dw(self):
        ''' Debye-Waller factor or thermal factor'''
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
    def cell(self, c):
        
        if c is None or not isinstance(c, Cell):
            raise CrystalClassError("Error: cell constant invalid")
        
        self._cell = c

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
        if ats is None:
            raise CrystalClassError('Atoms positional data missing')

        if type(ats) is not list:
            raise CrystalClassError('Atoms positional data invalid')

        for at in ats:
            if not isinstance(at, Atom):
                raise CrystalClassError("Atoms positional data invalid")

        self._atoms = ats

    @spg.setter
    def spg(self, vspg):
        
        if vspg is None or not isinstance(vspg, SPG):
            raise CrystalClassError('Invalid space group data')

        self._spg = vspg

    def isISO(self):
        return self._dw == 1

    def __eq__(self, other):

        if not isinstance(other, Crystal):
            return False
        
        if self._name != other._name:
            return False

        if not self._cell == other.cell:
            return False
        
        if self._dw != other.dw:
            return False

        if not self.spg == other.spg:
            return False

        for a in self._atoms:
            if a not in other.atoms:
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
        creates imports crystal data from pyemaps build-in crystal database
        
        :param cn: Optional. Name of the crystal in pyemaps's builtin database.
        :type cn: string
        :raise CrystalClassError: If reading database fails or any of its components 
                                  (cell, atoms, spg) fail to validate.

        For a list of pyemaps builtin crystal names, call:
        Crystal.list_all_builtin_crystals() method
        
        """

        base_dir = os.path.realpath(__file__)
        cbase_dir = os.path.join(os.path.dirname(base_dir), crystal_data_basedir)
        fn = os.path.join(cbase_dir, cn+'.xtl')
              
#       Successfully imported crystal data
        try:
            name, data = loadCrystalData(fn)
            xtl = cls(name=name, data=data)

        except (XTLError, CellError, UCError, SPGError) as e:
            raise CrystalClassError(e.message)
        except (FileNotFoundError, IOError) as e:
            raise CrystalClassError('Error creating crystal: ' + str(e))
        else:
            return xtl

    @classmethod
    def from_xtl(cls, fn):
        """
        To create a crystal object by importing data from xtl formtted file.

        :param fn: Required. Crystal data file name in pyemaps propietory format.
        :type fn: string
        :raise CrystalClassError: file reading fails or any of its components fail to validate.

        **XTL Format Example:**

        :: 

            crystal Aluminium: dw = iso
            cell 4.0493 4.0493 4.0493 90.0000 90.0000 90.0000
            atom al 0.000000 0.000000 0.000000 0.7806 1.000000
            spg 225 1

        **Required Fields:**

        1. dw = iso by default, other values: uij, bij
        2. name: crystal name.
        3. cell constants: six floating point values defining crystal cell.
        4. atoms: one or two lines of atoms positions along with element symbol
        5. spg: space group data. Two positive digits: [number, setting]
            
        **Validation**:

        - if dw == iso, atoms line must have at least 4 floating numbers in 
          (x,y,x,d-w,occ) where occ defaults to 1.00 if not provided.
        - if dw == uij,bij, atoms line must have at least 9 floating points in 
          (x,y,z,b11,b22,b33,b12,b13,b23,occ)
        
        **Input File Name Search**:

        - Full path and exists.
        - Current working directory.
        - *PYEMAPSHOME*/crystals directory, where
          *PYEMAPSHOME* is an environment variable pointing to pyemaps data home directory.

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
            xtl = cls(name=name, data=data)

        except (XTLError, CellError, UCError, SPGError) as e:
            raise CrystalClassError(e.message)
        except (FileNotFoundError, AttributeError) as e:
            raise CrystalClassError(e.message)
        else:
            return xtl
    
    @classmethod
    def from_cif(cls, fn):
        """
        import crystal data from a cif (Crystallographic Information File).

        :param fn: required crystal data file name in JSON format.
        :type fn: string
        :raise CrystalClassError: If file reading fails or any of its components 
                                  (cell, atoms, spg) fail to validate.
        """

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
            cif = cls(name=name, data=data)

        except (CIFError, AttributeError, CellError, UCError, SPGError) as e:
            raise CrystalClassError(e.message) from None
        else:
            return cif

    @classmethod 
    def from_json(cls, jfn):
        """
        Import crystal data from a .json file.

        :param jfn: required crystal data file name in JSON format.
        :type jfn: string
        :raise CrystalClassError: If file reading fails or any of its components fail to validate.

        An example of a json file content:

        .. code-block:: json

            {
                "cell": 
                    {"a": "5.4307",
                    "b": "5.4307",
                    "c": "5.4307",
                    "alpha": "90.0",
                    "beta": "90.0",
                    "gamma": "90.0"
                    },
                "atoms":
                    [
                        {"symb": "si",
                        "x": "0.125",  
                        "y": "0.125", 
                        "z": "0.125",
                        "d-w": "0.4668", 
                        "occ": "1.00"
                        } 
                    ],
                "spg":
                    {"number": "227",
                    "setting": "2" 
                    },
                "dw": "iso",
                "name": "Silicon"
            }
        
        """
        cfn = jfn
        if not os.path.exists(cfn):
            # find it in pyemaps data home or current directory
            pyemaps_datahome = find_pyemaps_datahome(home_type = 'crystals')
            cfn = os.path.join(pyemaps_datahome, cfn)
            
            if not os.path.exists(cfn):
                err_msg = str(f"Error finding the data file: {cfn}")
                raise CrystalClassError(err_msg)

        try:
            with open(cfn) as jf:
                data=json.load(jf)
        except:
            raise CrystalClassError('Failed to open the json file')
        else:
            if 'name' not in data:
                raise CrystalClassError('Json data must have name field')

            return cls(name = data['name'], data = data)

    @classmethod
    def from_dict(cls, cdict):
        """
        Import crystal data from a python dictionary object.
        
        :param cdict: required crystal data file name in as a python dictionary object.
        :type cdict: dict
        :raise CrystalClassError: If any of its components import fails.

        An example of a json file content:

        .. code-block:: python

            {
                "cell": 
                    {"a": "5.4307",
                    "b": "5.4307",
                    "c": "5.4307",
                    "alpha": "90.0",
                    "beta": "90.0",
                    "gamma": "90.0"
                    },
                "atoms":
                    [
                        {"symb": "si",
                        "x": "0.125",  
                        "y": "0.125", 
                        "z": "0.125",
                        "d-w": "0.4668", 
                        "occ": "1.00"
                        } 
                    ],
                "spg":
                    {"number": "227",
                    "setting": "2" 
                    },
                "dw": "iso",
                "name": "Silicon"
            }

        """

        if 'name' not in cdict:
            raise CrystalClassError('Failed to create crystal object with input dictionary')
        
        name = cdict["name"]
        return cls(name=name, data = cdict)           

    @staticmethod
    def list_all_builtin_crystals():
        """
        To list all builtin crystals available in pyemaps built-in crystal database,
        use this routine to determine the name of the crystal to load using from_builtin().

        """
        import glob
        base_dir = os.path.realpath(__file__)
        cbase_dir = os.path.join(os.path.dirname(base_dir), crystal_data_basedir)
        cbase_files = os.path.join(cbase_dir, '*.xtl')
        cfile_list = glob.glob(cbase_files)

        return [os.path.basename(name).split('.')[0] for name in cfile_list]
