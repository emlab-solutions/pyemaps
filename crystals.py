# from pymongo import MongoClient
import numpy as np
from numpy import asfortranarray as farray
# from numpy import array
import os
# from urllib.parse import urljoin
# import requests
import json


cell_keys=['a','b','c','alpha','beta','gamma']
at_iso_keys=['symb','x','y','z','d-w','occ']
at_noniso_keys=['symb','x','y','z','b11','b22','b33','b12','b13','b23','occ']
spg_keys=['number','setting']
crystal_data_basedir = 'cdata'

required_keys = ['cell', 'dw', 'atoms', 'spg']
# difModes = {"normal": 1,
#             "CBED":   2}
# API_BASEURL = "https://data.mongodb-api.com/app/data-svvat/endpoint/data/beta/action/"
# API_BASEPAYLOAD = {
#                 "collection": "crystals",
#                 "database": "clusterEMAPS",
#                 "dataSource": "ClusterEMAPS"
#                 }

# MONGO_URI = "mongodb+srv://xiurongz-emaps:jmrong01@clusteremaps.zfesp.mongodb.net/clusterEMAPS?retryWrites=true&w=majority"
# client = MongoClient(MONGO_URI)
# db = client['clusterEMAPS']

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
    
class Crystal:
    def __init__(self, name="Diamond", data={}):
        
        self.name = name #save the original name
        self.data = data
        self._name = name.lower()

    # def fillDiffPatterns(self):
    #     for mode in difModes:
    #         self.diff[mode] = Diffraction(self.name, mode)

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
    def from_builtin(cls, cn):
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
        """
        import os

        if not os.path.exists(fn):
            print(f"Error finding the data file: {fn}")
            return None

        name, data = Crystal.loadCrystalData(fn)
        
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
                    # print(token)
                    cname = re.split(' +', token[0].strip())[1].strip()
                    name = cname
                    # print(f'crystal name input: {name}')
                    if cn and name.lower() != cn.lower():
                        print(f"Error: crystal name provided {name} does not match that in builtin data {cname}")
                        return name, data
                    
                    # parsing for dw and occ data
                    dwocc = re.split(' =+', token[1].strip())
                    owlen = len(dwocc)
                    # print(f'dw occ data: {dwocc} with length: {owlen}')

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

    # @classmethod
    # def from_builtin_db(cls, name="Diamond", capi=True):

    #     data = Crystal.get_crystal_raw(name) if not capi else \
    #         Crystal.get_crystal_api_raw(name)
            
    #     return cls(name, data)

    @classmethod
    def from_json_file(cls, jfn):
        with open(jfn) as jf:
            data=json.load(jfn)
            if "name" in data:
                name = data["name"]
                return cls(name, data)
            
            return cls()

# TODO: need to validate the hson data
    @classmethod
    def from_json(cls, jdata):
        if "name" in jdata:
            name = jdata["name"]
            return cls(name, jdata)

        return cls()            

    # @classmethod #-- for testing only ----
    # def from_builtin_db_reverse(cls, name="Diamond", capi=True):

    #     data = Crystal.get_crystal_raw(name) if not capi else \
    #         Crystal.get_crystal_api_raw(name)
        
    #     data["atoms"] = data["atoms"][::-1]
    #     return cls(name, data)

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
        # print(dw)
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
                    # print(i,key)
                    if i == 0:
                        atnarr.append(a[key])
                    else:
                        atom[i-1]=a[key]
                    # cel.append(cell0[key])
                else:
                    print('Error: missing key atomic data!')
                    os.exit()
            atomsarr.append(atom)

        atoms = farray(atomsarr, dtype=float)
        # print(atoms)
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
        # print(spg)
        # zn = farray([0, 0, 1])
        # anames= array([atom['symb'] for atom in c_data["atoms"]])
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
        Wrapper for get_diffraction routine
        """
        from .kdiffs import diffPattern as DP

        ret, diffp = self.get_diffraction(zone,mode,tx0,ty0,dx0,dy0,cl,vt,dsize)
        if ret != 200:
            print(f'Error generating diffraction pattern')
            return None
        return DP(diffp)


    def get_diffraction(self, zone = None, 
                              mode = None, 
                              tx0 = None, 
                              ty0 = None, 
                              dx0 = None,
                              dy0 = None,
                              cl = None,
                              vt = None, 
                              dsize = None):
        """
        
        If none of the parameters are supplied, the routine will
        generate the diffraction patterns in default set in the fortran
        backend:
            zone = (0,0,1) zone axis
            mode = normal  kinematic diffraction mode (CBED is the other)
            (tx0,ty0) = (0.0,0.0) tilt angles
            (dx0,dy0) = (0.0,0.0) deflection move
            cl = 1000 EM length
            vt = 200  voltage
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
        if mode == 2:
            dif.setmode(mode)
            if dsize == None:
                return 500, ({})
            dif.setdisksize(float(dsize))
        
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

        #remove module internal memory
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

    def generate_test_diff(self,v, mode=1):        
        import kdiffs
        from test.baseline import MAX_PROCWORKERS
        import concurrent.futures
        import sys

        if mode == 2:
            dsize = 0.16
        else:
            dsize = None

        # cell, atoms, atn, spg, dw = self._get_params()
        
        fs=[]
        diff = kdiffs.Diffraction(self.name, mode = mode)

        with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_PROCWORKERS) as e:
            for tx,ty, z1, z2, z3 in v:
                fs.append((tx, ty, z1,z2,z3, \
                e.submit(self.get_diffraction, (z1,z2,z3), mode,tx,ty,0.0,0.0,None,None,dsize)))

        for tx, ty, z1, z2, z3, f in fs:
            ret, diff_dict = f.result()
            if ret != 200:
                print(f"Error: running diffraction module for {self.name}")
                sys.exit(1)
            # print(f"\n\n****Success****: generated diffraction patterns for tilt: ({tx},{ty})\n\n")

            cntrl = {}
            cntrl["tilt"]= (tx,ty)
            cntrl["zone"]= (z1, z2, z3)

            diffP = kdiffs.diffPattern(diff_dict)
            diff.add(cntrl,diffP)
        return diff

    def generate_baseline_diff(self, v, fn, mode=1):

        diff = self.generate_test_diff(v, mode=mode)
        ofn = diff.savebin(fn)
        # diff.readbin(ofn,True)
        return ofn

    def load_baseline_diff(self, mode=1):
        from test.baseline import DIFF_BASELINE_DIR
        import kdiffs
  
        fn = self.name + str("_CBED" if mode == 2 else "_normal") + ".bin"

        basefn = os.path.join(DIFF_BASELINE_DIR, fn)
        # print(f"inside base;ine loading: {basefn}")
        if not os.path.exists(basefn):
            return None

        diff = kdiffs.Diffraction(self.name, mode = mode)
        diff.readbin(basefn,False)

        return diff

    # def generate_ediom_dp(self, res=1):
    #     from pyemaps import dif, dpgen
    #     ediom_dp_res_lookup = [('small', 0.01),
    #              ('medium', 0.005),
    #              ('large', 0.0025)]
    #     # mode = 1; disksize = 0.05
    #     mode = 1

    #     cell, atoms, atn, spg, dw = self._get_params()

    #     dif.initcontrols()
        
    #     dif.loadcrystal(cell, atoms, atn, spg, ndw=dw)

    #     dif.set_xaxis(1, 2, 0, 0)
    #     ret = dif.diffract(2)
        
    #     if ret == 0:
    #         print('Error running dif module')
    #         return -1

    #     vertices0 = np.array([[0,0,1],[1,1,1],[0,1,1]])
    #     vertices = farray(vertices0.transpose(), dtype=int)

    #     sres, fres = ediom_dp_res_lookup[res-1]
    #     output_fn = self.name +'_' + sres

    #     print(f"input for do_gen: {vertices},{output_fn}")
    #     ret = dpgen.do_dpgen(fres, vertices, output_fn)
    #     if ret != 0:
    #         print(f'Error running generating diffraction patterns for {self.name}')
    #         return -1

    #     ret = dpgen.readbin_new(output_fn+' ', "bin"+' ')
    #     if ret != 0: 
    #         print(f'Error running generating diffraction patterns for {self.name}')
    #         return -1

    #     #release the memory
    #     dif.diff_internaldelete(0)
    #     dif.diff_delete()
    #     return 0

    # @staticmethod
    # def get_crystal_raw(name):
    #     query = {}
    #     query["name"] = name
        
    #     return db.crystals.find_one(query, {"_id":0})

    # @staticmethod
    # def get_crystal_api_raw(name):
    #     action_name = "findOne"
    #     # print(f"api baseURL: {API_BASEURL}")
    #     url = urljoin(API_BASEURL, action_name)
    #     # print(f"api URL: {url}")
    #     query={}
    #     query["name"] = name

    #     # payload dictionary
    #     payload_dict = API_BASEPAYLOAD.copy()
    #     payload_dict.update({"filter": query})
    #     payload_dict.update({"projection": {"_id":0}})

    #     payload = json.dumps(payload_dict)
    #     headers = {
    #         'Content-Type': 'application/json',
    #         'Access-Control-Request-Headers': '*',
    #         'api-key': 'Lt1mjy8jVolzveVTkTeepPDczjImLbhF8OPFIF4dPHhQa66y077b9UaOIhSmBucc'
    #     }

    #     response = requests.request("POST", url, headers=headers, data=payload)
    #     data = response.json()["document"]
    #     # print(f"Data retrieved for {name}: {data}")
    #     return data

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

    # @staticmethod
    # def get_all_builtin_crystal_names(capi=True):
    #     # 2/19/22
    #     # pass
    #     if not capi:
    #         crystCollection = db['crystals']
    #         crs = crystCollection.find({}, {"_id":0, "name":1})
    #         res = []
    #         for item in crs:
    #             res.append(item["name"])
    #         return res
        
    #     #api url
    #     action_name = "find"
    #     url = urljoin(API_BASEURL, action_name)

    #     # payload dictionary
    #     payload_dict = API_BASEPAYLOAD.copy()
    #     payload_dict.update({"filter": {}})
    #     payload_dict.update({"projection": {"_id":0, "name":1}})


    #     payload = json.dumps(payload_dict)
    #     headers = {
    #         'Content-Type': 'application/json',
    #         'Access-Control-Request-Headers': '*',
    #         'api-key': 'Lt1mjy8jVolzveVTkTeepPDczjImLbhF8OPFIF4dPHhQa66y077b9UaOIhSmBucc'
    #     }

    #     response = requests.request("POST", url, headers=headers, data=payload)
    #     res=[]
    #     for item in response.json()["documents"]:
    #         res.append(item["name"])

    #     return res
