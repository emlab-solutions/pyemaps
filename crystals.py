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


Author:     EMLab Solutions, Inc.
Date:       May 07, 2022    

'''

import numpy as np
from numpy import asfortranarray as farray
from functools import wraps
import os
import json

# from .kdiffs import DEF_MODE
from .emcontrols import DEF_CBED_DSIZE
from .emcontrols import EMControl as EMC


cell_keys=['a','b','c','alpha','beta','gamma']
at_iso_keys=['symb','x','y','z','d-w','occ']
at_noniso_keys=['symb','x','y','z','b11','b22','b33','b12','b13','b23','occ']
spg_keys=['number','setting']
crystal_data_basedir = 'cdata'

required_keys = ['cell', 'dw', 'atoms', 'spg']

def float_eq(a,b):
    return abs(a-b) < 0.000001

class Cell:
    def __init__(self, cell_dict=dict.fromkeys(cell_keys,0.0)):
        
        self.a = float(cell_dict["a"])
        self.b = float(cell_dict["b"])
        self.c = float(cell_dict["c"])
        
        self.alpha = float(cell_dict["alpha"])
        self.beta = float(cell_dict["beta"])
        self.gamma = float(cell_dict["gamma"])
        
        self._a = round(self.a, 6)
        self._b = round(self.b, 6)
        self._c = round(self.c, 6)
        self._alpha = round(self.alpha, 6)
        self._beta = round(self.beta, 6)
        self._gamma = round(self.gamma, 6)
    
    def __key__(self):
        return (self._a, self._b, self._c, self._alpha, self._beta, self._gamma)

    def __eq__(self, cello):
        if not isinstance(cello, Cell):
            return False
        
        return self.__key__() == cello.__key__()

    def __repr__(self):
        return str(f"cell: a: {self.a}, b: {self.b}, c: {self.c}, ") + \
               str(f"alpha: {self.alpha}, beta: {self.beta}, gamma: {self.gamma}") 

    def __str__(self):
        return str(f"cell: {self.a} {self.b} {self.c} ") + \
               str(f"{self.alpha} {self.beta} {self.gamma}") 


class SPG:
    def __init__(self, spg_dict):
        self.number = int(spg_dict["number"])
        self.setting = int(spg_dict["setting"])
    
    def __eq__(self, spgo):
         if not isinstance(spgo, SPG):
            return False

         return (self.number == spgo.number) and (self.setting == spgo.setting)

    def __str__(self):
        return str(f"spg: {self.number} {self.setting}")
    
    def __repr__(self):
        return str(f"spg: number: {self.number} setting: {self.setting}")

class Atom:
    def __init__(self, a_dict={}):
        # print(f"atom data: {a_dict.items()}")
        self.symb = a_dict["symb"]
        self._symb = self.symb.lower()

        acopy = a_dict.copy()
        acopy.pop("symb")
        self.atom = acopy

    def __eq__(self, other):
        if not isinstance(other, Atom):
            return False

        if self._symb != other._symb: 
            return False

        for key,val in self.atom.items():
            if not float_eq(float(val), float(other.atom[key])):
                return False

        return True
    
    def __str__(self) -> str:
        atoms=[str(f"{self.symb}")]
        
        for _ , val in self.atom.items():
            atoms.append(str(f"{val}"))

        return " ".join(atoms)

def add_dpgen(target):
    def dp_gen(self, res =1):
        try:
            from pyemaps import dif

        except ImportError as e:               
            print(f"Error: required module pyemaps.dif not found")
            return -1

        try:
            from pyemaps import dpgen

        except ImportError as e:               
            print(f"Error: required module pyemaps.dpgen not found")
            return -1

        ediom_dp_res_lookup = [('small', 0.01),
                 ('medium', 0.005),
                 ('large', 0.0025)]

        cell, atoms, atn, spg, dw = self._get_params()

        dif.initcontrols()
        
        dif.loadcrystal(cell, atoms, atn, spg, ndw=dw)

        dif.set_xaxis(1, 2, 0, 0)
        ret = dif.diffract(2)
        
        if ret == 0:
            print('Error running dif module')
            return -1

        vertices0 = np.array([[0,0,1],[1,1,1],[0,1,1]])
        vertices = farray(vertices0.transpose(), dtype=int)

        sres, fres = ediom_dp_res_lookup[res-1]
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
    ######INPUT#######
    # -------------kv-----------------------
    #   Accelaration Voltage in Kilo-Volts
    # --------------------------------------
    # -------------smax---------------------
    #   Limit of Sin(theta)/Wave length
    # --------------------------------------
    # -------------sftype-------------------
    #   Structure Factors Type:
    #   1 - x-ray structure factor (default)
    #   2 - electron structure factor in volts (KV)
    #   3 - electron structure factor in 1/angstrom^2 in (KV)
    #   4 - electron absorption structure factor in 1/angstrom^2 (KV)
    # --------------------------------------
    # -------------aptype-------------------
    #   Structure Factor in (Amplitude, Phase) or (Real, Imaginary):
    #   0 - in (Real, Imaginary) 
    #   1 - in (Amplitude, Phase) (default)
    # --------------------------------------

    #####OUTPUT########
    # The function returns an array of structure factors
    # Each item in the output array [sfs] is of a dictionary type
    # for each element:
    #   hkl: (h,k,l)    - Miller Indices 
    #   sw: s           - Sin(theta)/Wave length
    #   ds: d           - d-spacing
    #   amp_re          - Structure factor amplitude or rela part
    #   phase_im        - Structure factor phase or imaginary part

    sf_type_lookup = ['X-ray Structure Factors',
                  'Electron Strcture Factors in kV',
                  'Electron Structure Factor in 1/\u212B',
                  'Electron Absorption Structure Factor in 1/\u212B^2']

    sf_ap_flag = [('real', 'imaginary'), ('amplitude', 'phase')]

    def printCSF(self, sfs, kv, smax, sftype, aptype):
        if sftype < 1 or sftype > 4:
            print(f'Invalid structure factor type input: {sftype}')
            return sfs

        if aptype < 0 or aptype > 1:
            print(f'Invalid structure factor output data flag: {aptype}')
            return sfs

        subj = sf_type_lookup[sftype-1]
        print(f"-----{subj}----- ")

        # print(f"     by EMLab Solutions, Inc.     \n")

        mi = "     h k l \t\t: Miller Index"
        print(mi)
        ssw = str(f"     s-w   \t\t: (Sin(\u03F4)/Wavelength) <= {smax}")
        print(ssw )
        dss = "     d-s   \t\t: D-Spacing"
        print(dss)
        
        if sftype > 1:
            print(f"     high voltage\t: {kv} kV\n")
        else:
            print(f"\n")


        # sds = "D-Spacing"
        sap1 = sf_ap_flag[aptype][0]
        sap2 = sf_ap_flag[aptype][1]
        
        # print(f"{mi:<15}{ssw:<30}{'(D-Spacing)':<16}")
        print(f"{'h':^4}{'k':^4}{'l':^5}{'s-w':^16}{'d-s':^16}{sap1:^16}{sap2:^16}\n")
        
        # empty_mi = ' '*15
        # ssmax = str(f'< {smax}')
        # print(f"{empty_mi:<15}{ssmax:<25}\n")

        nb = len(sfs)
        for i in range(0, nb, 1):
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
            from pyemaps import dif

        except ImportError as e:               
            print(f"Error: required module pyemaps.dif not found")
            return []

        try:
            from pyemaps import csf

        except ImportError as e:               
            print(f"Error: required module pyemaps.csf not found")
            return []
        
        sfs = []

        cell, atoms, atn, spg, dw = self._get_params()

        dif.initcontrols()
        
        dif.loadcrystal(cell, atoms, atn, spg, ndw=dw)

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
            
            # print(f"{h:<4}{k:<4}{l:<7}{s:<25}{d:<25}{sf1:<25}{sf2:<25}")
            sf = dict(hkl = (h,k,l),
                       sw = s,
                       ds = d,
                       amp_re = sf1,
                       phase_im = sf2)
            sfs.append(sf)    

        #release the memory
        csf.delete_sfmem()
        dif.diff_internaldelete(0)
        dif.diff_delete()

        return sfs
    
    target.generateCSF = generateCSF
    target.printCSF = printCSF

    return target

@add_csf        
@add_dpgen      
class Crystal:
    def __init__(self, name="Diamond", data={}):
        
        self.name = name #save the original name
        self.data = data
        self._name = name.lower()

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
        dw = self.data["dw"]
        cellconst = Cell(self.data["cell"])
        atoms = ["atoms:"]
        for at in self.data["atoms"]:
            att = Atom(at)
            atoms.append(str(att))

        spg = SPG(self.data["spg"])
        return str(f"Crystal name: {self.name} dw: {dw}\n{cellconst}\n") + \
              "\n".join(atoms) + "\n" + str(spg)

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

        _, data = Crystal.loadCrystalData(fn, cn)

        for key in required_keys:
            if key not in data:
                print(f"Error: {key} data missing for {cn}")
                return None
        
#       Successfully imported crystal data
        return cls(name, data)
    @classmethod
    def from_xtl(cls, fn):
        """
        Loading crystal instance data from a user supplied xtl formtted data:
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
                print(f"Error finding the data file: {fn}")
                return None
        
        name, data = Crystal.loadCrystalData(cfn)
        
        for key in required_keys:
            if key not in data:
                print(f"Error: {key} data missing for {name}")
                return None
        
#       Successfully imported crystal data
        return cls(name, data)

    @staticmethod
    def loadCrystalData(fn, cn=None):
        """
        Base function for from_builtin and from_xtl
        """
        import re

        data = {}
        
        name=""
        occ="1.000" #default value for occ
            
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
                        print(f"Error: crystal name provided {name} does not match that in builtin data {cname}")
                        return name, data
                    
                    # parsing for dw and occ data
                    dwocc = re.split(' =+', token[1].strip())
                    owlen = len(dwocc)
                    

                    if owlen > 3:
                        print(f"Error: pasing data for {cname}")
                        return name, data

                    if owlen < 2:
                        print(f"Error: dw data retireval failure for {cname}")
                        return name, data
                        
                    dw = re.split(' +', dwocc[1].strip())[0]
                    # validating dw:
                    if dw != 'iso' and dw != 'uij' and dw != 'bij':
                        print(f"Invalid dw data: must be one of iso, bij and uij")
                        return name, data

                    data['dw'] = dw

                    if len(dwocc) == 3:
                        occ = dwocc[2].strip()

                # line = fline.strip()
                if ln.startswith('cell'):
                    # cell_line = line.strip('cell ')
                    cellStr = ln[4:].strip()
                    tokens = np.array([n for n in re.split(' +', cellStr)])
                    if tokens.size != len(cell_keys):
                        print("Error: adding atom: cell mismatch")
                        return name, data
                    cell = {}
                    for k, t in zip(np.array(cell_keys), tokens):
                        cell[k] = t
                    data['cell'] = cell

                if ln.startswith('atom'):
                    # atom_line = line.strip('atom ')
                    atomStr = ln[4:].strip()
                    token = [n for n in re.split(' +', atomStr)]
                    # print(token.size)
                    # print(self.get_atom_len())
                    if 'dw' not in data:
                        print("Error: dw data missing before atom data")
                        return name, data

                    alen = Crystal.get_atom_len(data['dw'])
                    tokenlen = len(token)
                    if tokenlen < alen - 1 or tokenlen > alen:
                        print("Error: parsing atom data")
                        return name, data

                    if tokenlen == alen - 1:
                        token.append(occ)
                        print(f'atom data with occ added: {token}')

                    atom = {}
                    keys = at_iso_keys if data['dw']== 'iso' else at_noniso_keys
                    
                    for k, t in zip(np.array(keys), token):
                        atom[k] = t
                    atoms.append(atom)

                if ln.startswith('spg'):
                    # spg_line = line.strip('spg ')
                    sStr = ln[3:].strip()
                    tokens = np.array([n for n in re.split(' +', sStr)])
                    if tokens.size != 2:
                        print(f"Error: parsing for space group data for {cn}")
                        return name, data
                    spg = {}
                    for k, t in zip(np.array(spg_keys), tokens):
                        spg[k] = t
                    data['spg'] = spg

            if len(atoms) == 0:
                print(f"Error: atom data missing")
                return name, data
                
            data['atoms'] = atoms

        return name, data
    
    @staticmethod
    def get_atom_len(dw):
        if dw == 'iso':
            return len(at_iso_keys)
        
        if dw == 'uij' or dw == 'bij':
            return len(at_noniso_keys)
        
        return -1 #error

    @classmethod
    def from_json_file(cls, jfn):
        with open(jfn) as jf:
            data=json.load(jfn)
            if "name" in data:
                name = data["name"]
                return cls(name, data)
            
            return cls()

    @classmethod
    def from_json(cls, jdata):
        if "name" in jdata:
            name = jdata["name"]
            return cls(name, jdata)

        return cls()            

    def _get_params(self):
        cell0 = self.data["cell"]
        celarr = np.zeros((6,))
        for i, key in enumerate(cell_keys):
            if key in cell0:
                celarr[i]=cell0[key]
            else:
                print('Error: missing cell data key!')
                os.exit()
        cell = farray(celarr, dtype=float)

        sdw = self.data['dw'].lower()
        keylen = 10
        dw = 1
        if sdw == 'iso' or sdw.lower() == 'par':
            keylen = 5
        elif sdw == 'bij':
            dw = 2
        elif sdw == 'uij':
            dw = 3
        else:
            dw = 0 #should error

        atKeys = at_noniso_keys
        if dw == 1:
            atKeys = at_iso_keys

        atarr=self.data['atoms']
        atomsarr = []
        atnarr =[]
        for a in atarr:
            atom = np.zeros((keylen,))
            for i, key in enumerate(atKeys):
                if key in a:
                    if i == 0:
                        atnarr.append(a[key])
                    else:
                        atom[i-1]=a[key]
                else:
                    print('Error: missing key atomic data!')
                    os.exit()
            atomsarr.append(atom)

        atoms = farray(atomsarr, dtype=float)
        
        spgdict = self.data["spg"]
        spgnum=-1
        if 'num1' in spgdict:
            spgnum = spgdict['num1']
        if 'number' in spgdict:
            spgnum = spgdict['number']
        spgset = -1
        if 'num2' in spgdict:
            spgset = spgdict['num2']
        if 'setting' in spgdict:
            spgset = spgdict['setting']

        spg = farray([spgnum,spgset], dtype=int)
        
        num_atoms = len(atoms)
        atn = farray(np.empty((num_atoms, 10), dtype='c'))
        k=0
        for an in atnarr:
            # print(an)
            for j in range(10):
                if j >= len(an):
                    an = an + ' '
            atn[k] = an
            k = k + 1

        return cell, atoms, atn, spg, dw

        
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
        from .kdiffs import diffPattern as DP

        if not em_controls:
            em_controls =EMC()

        tx0, ty0 = em_controls.tilt
        dx0, dy0 = em_controls.defl
        cl, vt = em_controls.cl, em_controls.vt
        zone = em_controls.zone

        ret, diffp = self._get_diffraction(zone,mode,tx0,ty0,dx0,dy0,cl,vt,dsize)
        if ret != 200:
            print(f'Error generating diffraction pattern')
            return None
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
        from .kdiffs import diffPattern as DP

        ret, diffp = self._get_diffraction(zone,mode,tx0,ty0,dx0,dy0,cl,vt,dsize)
        if ret != 200:
            print(f'Error generating diffraction pattern')
            return None
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
        This routine returns raw diffraction data from pyemaps dif extension

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
        from pyemaps import dif
        import copy

        cell, atoms, atn, spg, dw = self._get_params()

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
        
        dif.loadcrystal(cell, atoms, atn, spg, ndw=dw)

        ret = 1
        ret = dif.diffract()
        if ret == 0:
            return 500, ({})

        # print(f"tx, ty: {tx0}, {ty0}")
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
        







