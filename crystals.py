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

.. Author:             EMLab Solutions, Inc.
.. Date Created:       May 07, 2022 

'''

from enum import Enum
import os
import json
# from tkinter import N
    
import numpy as np
from numpy import asfortranarray as farray

from .errors import *
from .fileutils import *

class DW(Enum):
    """
    Debye-Waller (thermal) factor types that pyEMAPS supports.

    * **iso**: isotropic Debye-Waller factor *B*
    * **bij**: anisotropic temperature factors
    * **uij**: anisotropic displacement factors
    """
    iso = 1
    bij = 2
    uij = 3

iso = DW.iso
bij = DW.bij
uij = DW.uij

class Cell:
    """
    Unit cell constants: the lengths *a*, *b* and *c* (Å) and the angles *alpha*, *beta* and
    *gamma* (degrees). Each value must be a number or a string that converts to one.

    From a dictionary:

    .. code-block:: python

        from pyemaps import Cell

        data_dict = {
            "a": "5.4307",
            "b": "5.4307",
            "c": "5.4307",
            "alpha": "90.0",
            "beta": "90.0",
            "gamma": "90.0"
        }
        si_cell = Cell(data=data_dict)

    From a list, in the order a, b, c, alpha, beta, gamma:

    .. code-block:: python

        from pyemaps import Cell

        si_cell = Cell(data=[5.4307, 5.4307, 5.4307, 90.0, 90.0, 90.0])
        # strings work too: ["5.4307", "5.4307", "5.4307", "90.0", "90.0", "90.0"]

    Or by setting the attributes one at a time:

    .. code-block:: python

        from pyemaps import Cell

        si_cell = Cell()        # every value starts at 0.0
        si_cell.a = 5.4307
        si_cell.b = 5.4307
        si_cell.c = 5.4307
        si_cell.alpha = 90.0
        si_cell.beta = 90.0
        si_cell.gamma = 90.0
    """
    def __init__(self, data=None):
        """
        :param data: the six cell constants, either as a dictionary with the keys ``a``, ``b``,
            ``c``, ``alpha``, ``beta`` and ``gamma``, or as a list in that order. If omitted, all six
            values are 0.0.
        :type data: dict or list, optional
        :raise ~pyemaps.errors.CellDataError: if *data* doesn't have exactly six values, has an unknown key, or is
            neither a dictionary nor a list.
        :raise ~pyemaps.errors.CellValueError: if a value isn't a number or a numeric string.
        """
        self._session_controls = None

        if data is None:
            setattr(self, 'a', 0.0)
            setattr(self, 'b', 0.0)
            setattr(self, 'c', 0.0)
            setattr(self, 'alpha', 0.0)
            setattr(self, 'beta', 0.0)
            setattr(self, 'gamma', 0.0)
            return

        if len(data) != len(cell_keys):
            raise CellDataError(f"Cell constant data length must be {len(cell_keys)}")

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

    def __call__(self, session_controls=None):
        setattr(self, 'session_controls', session_controls)

    @property
    def session_controls(self):
        """
        Microscope controls attached to the cell, an :py:class:`~pyemaps.emcontrols.EMControl`.
        Set it by calling the cell with the controls, ``cell(emc)``, and clear it with ``cell()``.
        It's ``None`` until set. pyEMAPS doesn't use it.
        """
        return self._session_controls

    @property
    def a(self):
        """
        Cell length *a*, in Å.
        """
        return self._a
    @property
    def b(self):
        """
        Cell length *b*, in Å.
        """
        return self._b
    @property
    def c(self):
        """
        Cell length *c*, in Å.
        """
        return self._c
    @property
    def alpha(self):
        """
        Cell angle *alpha*, in degrees.
        """
        return self._alpha
    @property
    def beta(self):
        """
        Cell angle *beta*, in degrees.
        """
        return self._beta
    @property
    def gamma(self):
        """
        Cell angle *gamma*, in degrees.
        """
        return self._gamma

    @a.setter
    def a(self, v=None): 
        """
        Set cell length *a*.

        :param v: a number or a numeric string; ``None`` sets 0.0.
        :raise ~pyemaps.errors.CellValueError: if *v* isn't numeric.
        """
        av = 0.0 if v is None else v

        try:
            self._a = float(av)

        except ValueError as e:
            raise CellValueError(1, "a")

    @b.setter
    def b(self, v=None):
        """
        Set cell length *b*.

        :param v: a number or a numeric string; ``None`` sets 0.0.
        :raise ~pyemaps.errors.CellValueError: if *v* isn't numeric.
        """
        bv = 0.0 if v is None else v

        try:
            self._b = float(bv)

        except ValueError as e:
            raise CellValueError(1, "b")

    @c.setter
    def c(self, v=None):
        """
        Set cell length *c*.

        :param v: a number or a numeric string; ``None`` sets 0.0.
        :raise ~pyemaps.errors.CellValueError: if *v* isn't numeric.
        """
        cv = 0.0 if v is None else v
        try:
            self._c = float(cv)

        except ValueError as e:
            raise CellValueError(1, "c")


    @alpha.setter
    def alpha(self, v=None):
        """
        Set cell angle *alpha*.

        :param v: a number or a numeric string; ``None`` sets 0.0.
        :raise ~pyemaps.errors.CellValueError: if *v* isn't numeric.
        """
        av = 0.0 if v is None else v
        try:
            self._alpha = float(av)

        except ValueError as e:
            raise CellValueError(2, "alpha")

    @beta.setter
    def beta(self, v=0.0):
        """
        Set cell angle *beta*.

        :param v: a number or a numeric string; ``None`` sets 0.0.
        :raise ~pyemaps.errors.CellValueError: if *v* isn't numeric.
        """
        bv = 0.0 if v is None else v
        try:
            self._beta = float(bv)

        except ValueError as e:
            raise CellValueError(2, "beta")

    @gamma.setter
    def gamma(self, v=0.0):
        """
        Set cell angle *gamma*.

        :param v: a number or a numeric string; ``None`` sets 0.0.
        :raise ~pyemaps.errors.CellValueError: if *v* isn't numeric.
        """
        gv = 0.0 if v is None else v
        try:
            self._gamma = float(gv)

        except ValueError as e:
            raise CellValueError(2, "gamma")
    
    @session_controls.setter
    def session_controls(self, sv):
        from . import EMC

        if sv is not None and not isinstance(sv, EMC):
            raise CrystalClassError('Invalid session controls')

        self._session_controls = sv

    def __key__(self):
        return (self._a, self._b, self._c, self._alpha, self._beta, self._gamma)

    def __eq__(self, cello):
        if not isinstance(cello, Cell):
            return False
        
        return self.__key__() == cello.__key__()

    def __repr__(self):
        return str(f"cell: a: {self._a}, b: {self._b}, c : {self._c}, ") + \
               str(f"alpha: {self._alpha}, beta: {self._beta}, gamma: {self._gamma}") 

    def __str__(self):
        return str(f"cell: {self._a} {self._b} {self._c} ") + \
               str(f"{self._alpha} {self._beta} {self._gamma}") 

    def prepare(self):
        """
        Return the cell constants as a Fortran-ordered array of six floats, in the order a, b, c,
        alpha, beta, gamma, for the simulation backend. Used internally.

        :raise ~pyemaps.errors.CellDataError: if a cell constant is missing.
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
        for key in cell_keys:
            yield (key, getattr(self, key))

class Atom:
    """
    One atom in a crystal: its element symbol, fractional position (*x*, *y*, *z*), thermal
    factor(s) and occupancy.

    From a dictionary, for an isotropic atom:

    .. code-block:: python

        from pyemaps import Atom

        data_dict = {
            "x": "0.125",
            "y": "0.125",
            "z": "0.125",
            "d-w": "0.4668",
            "occ": "1.00"
        }
        si_atom = Atom(sym='Si', data=data_dict)

    From a list:

    .. code-block:: python

        from pyemaps import Atom

        si_atom = Atom(sym='Si', data=[0.125, 0.125, 0.125, 0.4668, 1.00])

    .. warning::

        A list must give the values in this order:

        .. code-block:: python

            ['x', 'y', 'z', 'd-w', 'occ']                                    # isotropic (iso)
            ['x', 'y', 'z', 'b11', 'b22', 'b33', 'b12', 'b13', 'b23', 'occ']  # anisotropic (bij, uij)

    .. note::

        The occupancy ``occ`` can be left out of a list or dictionary; it then defaults to 1.0.

    Or by setting the attributes one at a time:

    .. code-block:: python

        from pyemaps import Atom

        si_atom = Atom()
        si_atom.symb = 'Si'
        si_atom.loc = [0.125, 0.125, 0.125, 0.4668, 1.00]
    """
    def __init__(self, a_type=iso.value, sym = '', data=None):
        """
        :param a_type: thermal factor type: 1 (``iso``), 2 (``bij``) or 3 (``uij``).
        :type a_type: int, optional
        :param sym: element symbol, up to 10 characters.
        :type sym: str, optional
        :param data: position, thermal factor(s) and optional occupancy. A dictionary needs the keys
            ``x``, ``y``, ``z`` and ``d-w`` for an isotropic atom, or ``x``, ``y``, ``z``, ``b11``,
            ``b22``, ``b33``, ``b12``, ``b13`` and ``b23`` for an anisotropic one, plus an optional
            ``occ``. A list gives the same values in that order.
        :type data: dict or list, optional
        :raise ~pyemaps.errors.UCError: if *data* isn't a dictionary or list, has the wrong number of values or is
            missing a key, or if *a_type* or *sym* is invalid.
        """
        setattr(self, 'atype', a_type)
        setattr(self, 'symb', sym)

        if data is None or type(data) is list:
            setattr(self, 'loc', data)
            return
        
        if type(data) is not dict:
            raise UCError("Atom position property input must be a dictionary or a list")

        akey = at_iso_keys if a_type == iso.value else at_noniso_keys
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
        Element symbol.
        """
        return self._symb

    @property
    def atype(self):
        """
        Thermal factor type: 1 (``iso``), 2 (``bij``) or 3 (``uij``).
        """
        return self._atype

    @property
    def loc(self):
        """
        Position, thermal factor(s) and occupancy, as a list:
        ``[x, y, z, d-w, occ]`` for an isotropic atom, or
        ``[x, y, z, b11, b22, b33, b12, b13, b23, occ]`` for an anisotropic one.
        """
        return self._loc

    @atype.setter
    def atype(self, a_type=iso.value):
        """
        Set the thermal factor type.

        :param a_type: 1 (``iso``), 2 (``bij``) or 3 (``uij``).
        :raise ~pyemaps.errors.UCError: if *a_type* isn't 1, 2 or 3.
        """
        
        if type(a_type) is not int or a_type < iso.value or a_type > uij.value:
            raise UCError("Atom thermal property type must be greater or equial to 1")
        
        self._atype = a_type

    @symb.setter
    def symb(self, sb=''):
        """
        Set the element symbol.

        :param sb: up to 10 characters; an empty string is stored as blanks.
        :raise ~pyemaps.errors.UCError: if *sb* is longer than 10 characters.
        """
        MAX_ATOM_SYMBOL_LEN = 10
        if len(sb) == 0:
            sb='          '
        
        if len(sb) > MAX_ATOM_SYMBOL_LEN or len(sb) < 1:
            raise UCError("Invalid atom symbol length")

        self._symb = sb
    
    @loc.setter
    def loc(self, locdata=None):
        """
        Set the position, thermal factor(s) and occupancy.

        :param locdata: a list in the order given in :py:attr:`~pyemaps.crystals.Atom.loc`; the occupancy can be left out
            and defaults to 1.0. ``None`` or an empty list sets every value to 0.0, with occupancy 1.0.
        :raise ~pyemaps.errors.UCError: if *locdata* isn't a list or has the wrong number of values.
        """
        akeys = at_iso_keys if self.isISO() else at_noniso_keys
        keylen = len(akeys)

        if locdata is None or len(locdata) == 0:
            # defaults if location data is not provided
            self._loc = [0.0]*(keylen-1)
            self._loc[-1] = 1.0
            self._data = dict(zip(akeys[1:], self._loc))
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

        self._data = dict(zip(akeys[1:], self._loc))
                
    def __eq__(self, other):
        if not isinstance(other, Atom):
            return False

        if self._atype != other.atype: 
            return False

        if self._symb.lower() != other.symb.lower():  
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
        """
        Return ``True`` if the atom has an isotropic thermal factor.
        """
        return self._atype == iso.value

    def prepare(self):
       """
       Return the position, thermal factor(s) and occupancy as a list of floats, for the simulation
       backend. Used internally.
       """
       tloc=[float(l) for l in self._loc]
            
       return tloc   


class SPG:
    """
    Space group: its number in the International Tables for Crystallography and its setting.

    From a dictionary:

    .. code-block:: python

        from pyemaps import SPG

        spg_dict = {
            "number": "227",    # International Tables number
            "setting": "2"      # space group setting
        }
        si_spg = SPG(data=spg_dict)

    From a list ``[number, setting]``:

    .. code-block:: python

        from pyemaps import SPG

        si_spg = SPG(data=[227, 2])     # or ["227", "2"]

    Or by setting the attributes:

    .. code-block:: python

        from pyemaps import SPG

        si_spg = SPG()
        si_spg.number = 227
        si_spg.setting = 2
    """
    def __init__(self, data=None):
        """
        :param data: the space group number and setting, as a dictionary with the keys ``number``
            and ``setting``, or as a list ``[number, setting]``. If omitted, both are 0.
        :type data: dict or list, optional
        :raise ~pyemaps.errors.SPGInvalidDataInputError: if *data* isn't a two-item list or a dictionary with exactly
            those two keys, or if a value isn't an integer.
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
        """
        International Tables number of the space group.
        """
        return self._number

    @property
    def setting(self):
        """
        Space group setting.
        """
        return self._setting

    @number.setter
    def number(self, n = None):
        """
        Set the International Tables number.

        :param n: an integer or an integer string; ``None`` sets 0.
        :raise ~pyemaps.errors.SPGInvalidDataInputError: if *n* isn't an integer or an integer string.
        """
        num = 0 if n is None else n

        try:
           self._number = int(num)
        except ValueError as e:
            raise SPGInvalidDataInputError()
        
    @setting.setter
    def setting(self, s=None):
        """
        Set the space group setting.

        :param s: an integer or an integer string; ``None`` sets 0.
        :raise ~pyemaps.errors.SPGInvalidDataInputError: if *s* isn't an integer or an integer string.
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
        """
        Check that the number and setting form a valid space group, and return them as a
        Fortran-ordered integer array for the simulation backend. Used internally.

        :raise ~pyemaps.errors.SPGInvalidDataInputError: if the space group number and setting aren't valid.
        """
        from .spg.spg_dec import validateSPG
        
        if not validateSPG(self._number, self._setting):
            raise SPGInvalidDataInputError()

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
#       such as x-ray structure factor: generateCSF().  
# --------------------------------------------------------------------- 

#---Crystal structure factors---
from .diffract.csf_dec import add_csf
#   1) X-Ray Structure Factors
#   2) Electron Structure Factor in V (volts)
#   3) Electron Structure Factor in 1/Angstron^2
#   4) Electron Absorption Structure Factor in 1/Angstron^2 

#---Crystal constructor---
#   building atomic structure based on crystal data
from .diffract.mxtal_dec import add_mxtal

#---Powder diffraction Calculation and rendering---
from .diffract.powder_dec import add_powder

#---Kinematic diffraction patterns database generation (upcoming) 
from .diffract.dpgen_dec import add_dpgen

#---diffraction pattern indexing----
# from .stem4d.stem4d_dec import add_stem4d

#---Stereodiagram---
from .diffract.stereo_dec import add_stereo
#   generates and plots stereographic projections

#---Kinematic Diffraction Simulations---
from .diffract.dif_dec import add_dif

#---Dynamic Diffraction Simulations---
from .diffract.bloch_dec import add_bloch

# @add_stem4d
@add_dpgen    
@add_mxtal              
@add_stereo              
@add_bloch              
@add_powder
@add_csf     
@add_dif   
class Crystal:
    """
    A crystal: its name, unit cell, atoms, space group and thermal factor type. All pyEMAPS
    simulations and calculations are methods of this class.

    * **name**: crystal name
    * **cell**: unit cell constants, a :py:class:`~pyemaps.crystals.Cell`
    * **atoms**: the atoms, a list of :py:class:`~pyemaps.crystals.Atom`
    * **spg**: space group, an :py:class:`~pyemaps.crystals.SPG`
    * **dw**: Debye-Waller (thermal) factor type, see :py:class:`~pyemaps.crystals.DW`

    Ways to create a crystal:

    1. ``Crystal(name, data)``, from a dictionary.
    2. :py:meth:`~pyemaps.crystals.Crystal.from_builtin`, from the pyEMAPS built-in crystal database.
    3. :py:meth:`~pyemaps.crystals.Crystal.from_xtl`, from a pyEMAPS XTL crystal file.
    4. :py:meth:`~pyemaps.crystals.Crystal.from_cif`, from a Crystallographic Information File (CIF).
    5. :py:meth:`~pyemaps.crystals.Crystal.from_json`, from a JSON file.
    6. :py:meth:`~pyemaps.crystals.Crystal.from_dict`, from a dictionary that includes the name.
    7. From its parts: :py:class:`~pyemaps.crystals.Cell`, :py:class:`~pyemaps.crystals.Atom` and :py:class:`~pyemaps.crystals.SPG` objects.

    From a dictionary:

    .. code-block:: python

        from pyemaps import Crystal

        c_dict = {
            'cell': {                       # cell constants
                'a': '5.4307', 'b': '5.4307', 'c': '5.4307',
                'alpha': '90.0', 'beta': '90.0', 'gamma': '90.0'
            },
            'atoms': [                      # one dictionary per atom
                {'symb': 'si',              # element symbol
                 'x': '0.125',              # fractional coordinates
                 'y': '0.125',
                 'z': '0.125',
                 'd-w': '0.4668',           # Debye-Waller factor
                 'occ': 1.00}               # occupancy
            ],
            'spg': {                        # space group
                'number': '227',            # International Tables number
                'setting': '2'              # setting
            },
            'dw': 'iso'                     # Debye-Waller factor type
        }

        si = Crystal(name='Silicon', data=c_dict)

    From the built-in crystal database:

    .. code-block:: python

        from pyemaps import Crystal

        si = Crystal.from_builtin('Silicon')

    .. note::

        For the names of all built-in crystals, call :py:meth:`~pyemaps.crystals.Crystal.list_all_builtin_crystals`.

    From its parts:

    .. code-block:: python

        from pyemaps import Cell, Atom, SPG, Crystal

        si = Crystal(name='Silicon')
        si.cell = Cell(data=[5.4307, 5.4307, 5.4307, 90.0, 90.0, 90.0])
        si.atoms = [Atom(sym='Si', data=[0.125, 0.125, 0.125, 0.4668, 1.00])]
        si.spg = SPG(data=[227, 2])
        si.dw = 'iso'

    .. note::

        All atoms in a crystal must have the same thermal factor type as the crystal.
    """
    
    def __init__(self, name="Diamond", data=None):
        """
        :param name: crystal name.
        :type name: str, optional
        :param data: the crystal data, as a dictionary with the keys ``cell``, ``atoms``, ``spg``
            and ``dw`` (see the example below). If omitted, the crystal starts empty: a zero cell, no
            atoms, space group 0 and isotropic thermal factors.
        :type data: dict, optional
        :raise ~pyemaps.errors.CrystalClassError: if *data* isn't a dictionary, a required key is missing, or an
            atom has no ``symb``. Validation errors from the cell, atoms and space group, such as
            :py:class:`~pyemaps.errors.CellDataError` and :py:class:`~pyemaps.errors.UCError`, are
            raised as they are.

        The dictionary for Silicon:

        .. code-block:: python

            {
                'cell': {'a': '5.4307', 'b': '5.4307', 'c': '5.4307',
                         'alpha': '90.0', 'beta': '90.0', 'gamma': '90.0'},
                'atoms': [{'symb': 'si', 'x': '0.125', 'y': '0.125', 'z': '0.125',
                           'd-w': '0.4668', 'occ': 1.00}],
                'spg': {'number': '227', 'setting': '2'},
                'dw': 'iso'
            }
        """
         
        # initially nothing is loaded, no rvec and no load type
        self._loaded = False
        self._ltype = -1

        setattr(self, 'name', name)

        if data is None:

            setattr(self, 'dw', iso.value)     
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
            at = dict(at)
            sym = at.pop('symb')

            att = Atom(a_type = self._dw, sym=sym, data = at)
            catoms.append(att)
        
        setattr(self, 'atoms', catoms)

        spg = SPG(data = data['spg'])
        setattr(self, 'spg', spg)

    @property
    def cell(self):
        """
        Unit cell constants, a :py:class:`~pyemaps.crystals.Cell`.
        """
        return self._cell

    @property
    def dw(self):
        """
        Debye-Waller (thermal) factor type: 1 (``iso``), 2 (``bij``) or 3 (``uij``). It can be set
        with the number or the name; ``'par'`` is accepted for ``iso``.
        """
        return self._dw

    @property
    def spg(self):
        """
        Space group, an :py:class:`~pyemaps.crystals.SPG`.
        """
        return self._spg

    @property
    def atoms(self):
        """
        The atoms, a list of :py:class:`~pyemaps.crystals.Atom`.
        """
        return self._atoms

    @property
    def name(self):
        """
        Crystal name.
        """
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
                if vl == iso.name or vl == 'par':
                    self._dw = iso.value
                elif  vl == bij.name:
                    self._dw =bij.value
                elif vl == uij.name:
                    self._dw = uij.value
                else:
                    raise ValueError("Invalid Debye-Waller value")
        elif isinstance(v, int):
            if v < iso.value or v > uij.value:
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
        """
        Return ``True`` if the crystal has isotropic thermal factors.
        """
        return self._dw == iso.value

    def __del__(self):

        if getattr(self, '_loaded', False):
            self.unload()

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

        if len(self._atoms) != len(other.atoms):
            return False

        for a in self._atoms:
            if a not in other.atoms:
                return False

        return True
   
    def __str__(self) -> str:
        
        cstr = []
        sdw = ''
        if self._dw == iso.value:
            sdw = iso.name
        elif self._dw == bij.value:
            sdw = bij.name
        elif self._dw == uij.value:
            sdw = uij.name
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
                 yield('atoms', [dict(a) for a in self._atoms])

    def loaded(self):
        
        """
        Return whether the crystal's data is loaded into the simulation backend.

        :return: ``True`` if loaded, otherwise ``False``.
        :rtype: bool
        """
        return self._loaded

    @classmethod
    def from_builtin(cls, cn='Diamond'):
        
        """
        Create a crystal from the pyEMAPS built-in crystal database.

        :param cn: name of a built-in crystal, such as ``'Silicon'``.
        :type cn: str, optional
        :return: the crystal.
        :rtype: Crystal
        :raise ~pyemaps.errors.CrystalClassError: if there's no built-in crystal with that name, or its data
            doesn't validate.

        .. note::

            For the names of all built-in crystals, call :py:meth:`~pyemaps.crystals.Crystal.list_all_builtin_crystals`.
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
        Create a crystal from a pyEMAPS XTL crystal file.

        :param fn: XTL file name.
        :type fn: str, required
        :return: the crystal.
        :rtype: Crystal
        :raise ~pyemaps.errors.CrystalClassError: if the file isn't found, or its data doesn't validate.

        **XTL format example:**

        ::

            crystal Aluminium: dw = iso
            cell 4.0493 4.0493 4.0493 90.0000 90.0000 90.0000
            atom al 0.000000 0.000000 0.000000 0.7806 1.000000
            spg 225 1

        **Fields:**

        1. ``crystal``: the crystal name, then the Debye-Waller factor type after ``dw =``:
           ``iso`` (the default), ``bij`` or ``uij``.
        2. ``cell``: the six cell constants a, b, c (Å) and alpha, beta, gamma (degrees).
        3. ``atom``: one line per atom: the element symbol, then its values.
        4. ``spg``: the space group number and setting.

        **Atom values:**

        - ``iso``: at least 4 numbers, x, y, z and d-w, then optionally occ (default 1.0).
        - ``bij`` or ``uij``: at least 9 numbers, x, y, z, b11, b22, b33, b12, b13 and b23, then
          optionally occ.

        **Where the file is looked for:**

        1. *fn* as given: a full path, or a path relative to the current directory.
        2. The ``crystals`` folder in the pyEMAPS data folder.

        See :ref:`Environment Variables <Environment Variables>` for how the data folder is set.
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
            raise CrystalClassError(str(e)) from e
        else:
            return xtl
    
    @classmethod
    def from_cif(cls, fn):
        
        """
        Create a crystal from a Crystallographic Information File (CIF).

        :param fn: CIF file name. It's looked for as given (a full path or a path relative to the
            current directory), then in the ``crystals`` folder of the pyEMAPS data folder.
        :type fn: str, required
        :return: the crystal.
        :rtype: Crystal
        :raise ~pyemaps.errors.CrystalClassError: if the file isn't found, or its cell, atoms or space group don't
            validate.
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

        except (CIFError, CellError, UCError, SPGError) as e:
            raise CrystalClassError(e.message) from None
        except AttributeError as e:
            raise CrystalClassError(str(e)) from e
        else:
            return cif

    @classmethod 
    def from_json(cls, jfn):
        
        """
        Create a crystal from a JSON file.

        :param jfn: JSON file name. It's looked for as given (a full path or a path relative to the
            current directory), then in the ``crystals`` folder of the pyEMAPS data folder.
        :type jfn: str, required
        :return: the crystal.
        :rtype: Crystal
        :raise ~pyemaps.errors.CrystalClassError: if the file isn't found or can't be read, has no ``name``, or its
            data doesn't validate.

        Example file:

        .. code-block:: json

            {
                "cell": {
                    "a": "5.4307", "b": "5.4307", "c": "5.4307",
                    "alpha": "90.0", "beta": "90.0", "gamma": "90.0"
                },
                "atoms": [
                    {"symb": "si", "x": "0.125", "y": "0.125", "z": "0.125",
                     "d-w": "0.4668", "occ": "1.00"}
                ],
                "spg": {"number": "227", "setting": "2"},
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
        Create a crystal from a dictionary that includes its name.

        :param cdict: the crystal data: the keys ``name``, ``cell``, ``atoms``, ``spg`` and ``dw``.
        :type cdict: dict, required
        :return: the crystal.
        :rtype: Crystal
        :raise ~pyemaps.errors.CrystalClassError: if *cdict* has no ``name``, or its data doesn't validate.

        Example:

        .. code-block:: python

            {
                "cell": {"a": "5.4307", "b": "5.4307", "c": "5.4307",
                         "alpha": "90.0", "beta": "90.0", "gamma": "90.0"},
                "atoms": [{"symb": "si", "x": "0.125", "y": "0.125", "z": "0.125",
                           "d-w": "0.4668", "occ": "1.00"}],
                "spg": {"number": "227", "setting": "2"},
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
        List the names of all crystals in the pyEMAPS built-in crystal database, for use with
        :py:meth:`~pyemaps.crystals.Crystal.from_builtin`.

        :return: crystal names, such as ``'Silicon'``.
        :rtype: list of str
        """
        import glob
        base_dir = os.path.realpath(__file__)
        cbase_dir = os.path.join(os.path.dirname(base_dir), crystal_data_basedir)
        cbase_files = os.path.join(cbase_dir, '*.xtl')
        cfile_list = glob.glob(cbase_files)

        return [os.path.basename(name).split('.')[0] for name in cfile_list]
