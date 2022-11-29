def add_dif(target):
    
        
    import numpy as np
    from numpy import asfortranarray as farray

    from . import dif
    from .. import EMC, DP
    from .. import DEF_MODE, DEF_CBED_DSIZE
    from .. import EMCError,DPListError,CrystalClassError,DPError

    def load(self, cty=0):
        '''
        Prepare and load crystal data into backend simulation module.

        Once loaded into simulation modules, the crystal data will be
        in backend module's memory until unload() method is called or 
        another crystal object calls this method. 
        
        Since all crystal objects use this method to load its data into
        the shared silmulation modules, data races need to be avoided. 

        One way to prevent data races is to guard all simulations for 
        one crystal object between its load() and unload() methods.

        :param cty: 0 - normal crystal loading, 1 - loading for crystal constructor 
        :type cty: int, optional

        .. note::

            This routine is designed to minimize trips to the backend simulation modules
            and therefore miximizing the performance. Users do not need to handle this calls
            directly.

        '''
        if self.loaded() and cty == self._ltype:
            return

        diff_cell = self._cell.prepare() #cell constant
        
        num_atoms = len(self._atoms)
        atn = farray(np.empty((num_atoms, 10), dtype='c'))
        
        atnarr = [at.symb for at in self._atoms]
        for i, an in enumerate(atnarr):
            if len(an) > 10:
                raise CrystalClassError(f"Atomic symbol {an} length cannot exceed 10")
            atn[i] = an.ljust(10)

        diff_atoms = farray([at.prepare() for at in self._atoms], dtype=float)
        
        diff_spg = self._spg.prepare()

        ret = dif.loadcrystal(diff_cell, diff_atoms, atn, diff_spg, ndw=self._dw, cty=cty)
        
        if ret != 0:
            self.unload() #remove any memory from backend module
            raise CrystalClassError('Failed to load cystal to backend module')

        self._loaded = True
        self._ltype = cty

    def unload(self):
        '''
        Remove crystal data from the memory in the backend simulation modules.
        
        '''
        dif.crystaldelete()
        self._loaded = False

    def generateDP(self, mode = None, dsize = None, em_controls = None):
        """
        Kinematic diffraction simulation.

        :param mode: Mode of kinemetic diffraction - normal(1) or CBED(2).
        :type mode: int, optional

        :param dsize: diffractted beam size, only applied to CBED mode.
        :type dsize: float, optional
        
        :param em_controls: `Microscope control <pyemaps.emcontrols.html#module-pyemaps.emcontrols>`_ object. 
        :type em_controls: pyemaps.EMC, optional

        :return: A tuple (emc, dp) where emc is the microscope control and dp is a `diffPattern <pyemaps.kdiffs.html#pyemaps.kdiffs.diffPattern>`_ object .
        :rtype: tuple.
 
        """

        if not em_controls:
            em_controls =EMC()

        # if not sim_controls:
        #     em_controls =SIMC()

        tx0, ty0 = em_controls.tilt
        dx0, dy0 = em_controls.defl
        cl, vt = em_controls.cl, em_controls.vt
        zone = em_controls.zone
        sc = em_controls.simc
        

        if not mode:
            mode = DEF_MODE

        if mode == 2 and dsize is None:
            dsize = DEF_CBED_DSIZE

        ret, diffp = self._get_diffraction(zone,mode,tx0,ty0,dx0,dy0,cl,vt,dsize,sc)
        
        
        if ret != 200:
            raise DPError('failed to generate diffraction patterns')

        # update the controls
        
        em_controls.simc(mode=mode)
        if mode == 2:
            em_controls.simc(dsize=dsize)
            
        return em_controls, DP(diffp)

    def _get_diffraction(self, zone = None, 
                              mode = None, 
                              tx0 = None, 
                              ty0 = None, 
                              dx0 = None,
                              dy0 = None,
                              cl = None,
                              vt = None, 
                              dsize = None,
                              simc = None):
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

        # if not mode:
        #     mode = DEF_MODE
        
        if mode != DEF_MODE and mode != DEF_MODE + 1:
            raise EMCError('Simulation mode is invalid: 1 = normal (default), 2 = CBED')

        dif.initcontrols()
        # mode defaults to DEF_MODE, in which dsize is not used
        # Electron Microscope controls defaults - DEF_CONTROLS
        
        if mode == 2:
            dif.setmode(mode)
            try:
                fd = float(dsize)
            except ValueError:
                raise EMCError('Invalid diffracted beams disk size')
            else: 
                dif.setdisksize(fd)

        if tx0 is not None and \
           ty0 is not None and \
           dx0 is not None and \
           dy0 is not None:
            
            dif.setsamplecontrols(tx0, ty0, dx0, dy0)
        else:
            print(f'tilt and def values: {tx0},{ty0}, {dx0}, {dy0}')
            raise EMCError('Control parameters invalid: tilt and deflections')

        if cl is not None and vt is not None:
            dif.setemcontrols(cl, vt)
        else:
            raise EMCError('Control parameters invalid: cl and vt')

        if zone is not None:
            dif.setzone(zone[0], zone[1], zone[2])
        else:
            raise EMCError('Control parameters invalid: zone')

        # setting simulation parameters
        self.set_sim_controls(simc)
        
        self.load()
        
        ret = dif.diffract()
        if ret == 0:
            return 500, ({})

        shiftx, shifty = dif.get_shifts()
        bounds = (shiftx, shifty)
        
        # dif.diff_printall()
        #remove module internal global memory
        dif.diff_internaldelete(0)

        klines=[]
        num_klines = dif.getknum()
        
        if (num_klines > 0):
            klines_arr = farray(np.zeros((num_klines, 5)), dtype=np.double)
            if dif.get_klines(klines_arr) == 0:
                for i in range(num_klines):
                    j=i+1
                    x1,y1,x2,y2,intensity=klines_arr[i][0:]
                    klines.append((x1,y1,x2,y2,intensity))
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
            
            if (num_hlines > 0):
                hlines_arr = farray(np.zeros((num_hlines, 5)), dtype=np.double)
                if dif.get_hlines(hlines_arr) == 0:
                    for i in range(num_hlines):
                        x1,y1,x2,y2,intensity = hlines_arr[i][0:]
                        hlines.append((x1,y1,x2,y2,intensity))
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

    def generateDif(self, mode = None, dsize = None, em_controls = None):
        """
         Another kinematic diffraction simulation method to be deprecated in
         stabel production soon. Its replacement is:
         `generateDP <pyemaps.crystals.html#pyemaps.crystals.Crystal.generateDP>`_.

        :param mode: mode of kinemetic diffraction - normal(1) or CBED(2).
        :type mode: int

        :param dsize: diffractted beam size, only applied to CBED mode.
        :param dsize: float

        :param em_controls: electron microscope controls object.
        :type em_controls: pyemaps.EMC

        :return: myDif.
        :rtype: pyemaps.DPList.

        """
        from . import DPList
        
        try:
            emc, cdp = self.generateDP(mode = mode, dsize=dsize, em_controls = em_controls)
            myDif = DPList(self._name, mode = mode)
            myDif.add(emc, cdp)

        except (DPListError, EMCError, DPError) as e:
            raise CrystalClassError('failed to generate diffraction')

        return myDif   

    def d2r(self, v = (0.0, 0.0, 0.0)):
        '''
        Transform vector from real to recriprocal space
        
        :param v: A vector of float coordinates
        :type v: tuple, optional

        :return: a transformed vector
        :rtype: tuple

        '''           
        
        self.load()

        x, y, z = v
        rx, ry, rz = dif.drtrans(x, y, z, 0)

        dif.crystaldelete()
        return rx, ry, rz

    def r2d(self, v = (0.0, 0.0, 0.0)):
        '''
        Transform vector from recriprocal to real space
        
        :param v: A vector of float coordinates
        :type v: tuple, optional

        :return: Tranformed vector
        :rtype: tuple of floats
        
        '''          
   
        self.load()

        x, y, z = v
        dx, dy, dz = dif.drtrans(x, y, z, 1)

        dif.crystaldelete()
        return dx, dy, dz

    def angle(self, v1 =(1.0, 0.0, 0.0), \
                     v2 = (0.0, 0.0, 1.0),
                     ty = 0):
        '''
        Calculates angle between two real space vectors or 
        two reciprocal space vectors
        
        :param v1: A vector of float coordinates
        :type v1: tuple, optional

        :param v2: A vector of float coordinates
        :type v2: tuple, optional

        :param ty: 0 real space, 1 reciprocal space
        :type ty: int, optional

        :return: an angle between v1 and v2.
        :rtype: float


        '''
        x1, y1, z1 = v1
        if x1 == 0.0 and y1 == 0.0 and z1 == 0.0:
            raise ValueError("Error: input vector can't be zero")
        
        x2, y2, z2 = v2
        if x2 == 0.0 and y2 == 0.0 and z2 == 0.0:
            raise ValueError("Error: input vector can't be zero")           
   
        self.load()

        a = dif.ang(x1, y1, z1, x2, y2, z2, ty)

        dif.crystaldelete()
        return a

    def vlen(self, v = (1.0, 0.0, 0.0), ty = 0):
        
        '''
        Calculates vector length real space vectors or in reciprocal 
        space vectors.
        
        :param v: A vector of float coordinates
        :type v: tuple, optional

        :param ty: 0 real space, 1 reciprocal space
        :type ty: int, optional

        :return: vector length in reciprical space or in reciprocal space
        :rtype: float

        '''        
              
        self.load()

        x, y, z = v
        ln = dif.vlen(x, y, z, ty)

        dif.crystaldelete()
        return ln

    @staticmethod
    def wavelength(kv = 100):
        '''
        Calculates electron wavelength.

        :param kv: High voltage
        :type kv: float or int, optional

        return: wave length
        rtype: float

        '''
        import math

        if kv <= 0.0:
            raise ValueError("Error: input kv must be positive number")

        wlen = 0.3878314/math.sqrt(kv*(1.0+0.97846707e-03*kv))
        return wlen
	
    def set_sim_controls(self, simc = None):
        '''
        Sets simulation controls in the backend. 

        This method also tries to minimize the trip to the backend 
        simulation module by skipping the call to the backend if
        default values are given.

        :param simc: `Simulation control <pyemaps.emcontrols.html#pyemaps.emcontrols.SIMControl>`_ objects
        :type simc: pyemaps.SIMC, optional
        
        .. note::

            *pyemaps" assumes that attributes in sim_control class are
            rarely changed. 

        '''
        # from pyemaps import 
        if not simc:
            # all defaults set in backend set by dif.initcontrols()
            return
                    
        if not simc._isDefExcitation():
            sgmin, sgmax = simc.excitation
            dif.setexcitation(sgmin, sgmax)

        if not simc._isDefGmax():
            dif.setglen(simc.gmax)

        if not simc._isDefBmin():
            dif.setgcutoff(simc.bmin)

        if not simc._isDefIntensity():
            intz0, intctl = simc.intensity
            dif.setintensities(intctl, intz0)

        if not simc._isDefXaxis():
            x0,x1,x2 = simc.xaxis
            dif.set_xaxis(1, x0, x1, x2)

        if not simc._isDefGctl():
            dif.setgctl(simc.gctl)

        if not simc._isDefZctl():
            dif.setzctl(simc.zctl)

    target.generateDP = generateDP
    target._get_diffraction = _get_diffraction
    target.generateDif=generateDif
    target.d2r = d2r
    target.r2d = r2d
    target.angle = angle
    target.vlen = vlen
    target.wavelength = wavelength
    target.set_sim_controls = set_sim_controls
    target.load = load
    target.unload = unload
    

    return target