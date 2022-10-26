def add_dif(target):
    
        
    import numpy as np
    from numpy import asfortranarray as farray

    from . import dif
    from .. import EMC, DP
    from .. import DEF_MODE, DEF_CBED_DSIZE
    from .. import EMCError,DPListError,CrystalClassError,DPError

    def load(self, rvec=None, cty=0):
        '''
        prepare crystal data to be loaded into backend module
        This routine is designed to fit python crystal structure
        into the ones accepted by Fortran backend modules
        10/19/2022:
        Combining Crystal.prepareDif() and load the crystal to 
        backend module memory  
        '''
        diff_cell = self._cell.prepare() #cell constant
        
        num_atoms = len(self._atoms)
        atn = farray(np.empty((num_atoms, 10), dtype='c'))
        
        atnarr = [at.symb for at in self._atoms]
        for i, an in enumerate(atnarr):
            if len(an) > 10:
                raise CrystalClassError(f"Atomic symbol {an} length cannot exceed 10")
            atn[i] = an.ljust(10)

        diff_atoms = farray([at.prepare(rvec=rvec) for at in self._atoms], dtype=float)
        
        diff_spg = self._spg.prepare()

        ret = dif.loadcrystal(diff_cell, diff_atoms, atn, diff_spg, ndw=self._dw, cty=cty)
        
        if ret != 0:
            self.unload() #remove any memory from backend module
            raise CrystalClassError('Failed to load cystal to backend module')
        
    def unload():
        '''
        Remove crystal from backend emaps modules memory
        '''
        dif.crystaldelete()

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

        if not em_controls:
            em_controls =EMC()

        # if not sim_controls:
        #     em_controls =SIMC()

        tx0, ty0 = em_controls.tilt
        dx0, dy0 = em_controls.defl
        cl, vt = em_controls.cl, em_controls.vt
        zone = em_controls.zone
        sc = em_controls.simc
        
        # self.set_simulation_controls()

        ret, diffp = self._get_diffraction(zone,mode,tx0,ty0,dx0,dy0,cl,vt,dsize,sc)
        
        
        if ret != 200:
            raise DPError('failed to generate diffraction patterns')

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

        if not mode:
            mode = DEF_MODE
        
        if mode != DEF_MODE and mode != DEF_MODE + 1:
            raise EMCError('Simulation mode is invalid: 1 = normal (default), 2 = CBED')

        dif.initcontrols()
        # mode defaults to DEF_MODE, in which dsize is not used
        # Electron Microscope controls defaults - DEF_CONTROLS
        
        if mode == 2:
            dif.setmode(mode)
            if dsize and isinstance(dsize, (int,float)) and dsize != DEF_CBED_DSIZE:
                dif.setdisksize(float(dsize))
            else:
                dif.setdisksize(DEF_CBED_DSIZE)

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

    def generateDif(self, mode = None, dsize = None, em_controls = None):
        """
        This routine returns a DPList object.

        New DP generation based on the crystal data and Microscope control 
        parameters. We will add more controls as we see fit.  

        :param mode: Optional mode of diffraction mode - normal(1) or CBED(2)
        :param dsize: Optional of CBED circle size - defaults to dif.DEF_DSIZE = 0.16
        :param: Optional em_controls of electron microscope controls dictionary - defaults to DEF_CONTROLS
        :return: a DP object
        :rtype: diffPattern
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
        Transform from real to recriprocal space
        '''           

        self.load()
        x, y, z = v
        rx, ry, rz = dif.drtrans(x, y, z, 0)

        dif.crystaldelete()
        return rx, ry, rz

    def r2d(self,  v = (0.0, 0.0, 0.0)):
        '''
        Transform from recriprocal to real space
        '''          

        self.load()
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

        self.load()

        a = dif.ang(x1, y1, z1, x2, y2, z2, type)

        dif.crystaldelete()
        return a

    def vlen(self, v = (1.0, 0.0, 0.0), type = 0):
        
        '''
        Type = 0: Calculate length of a real space vector
	    Type = 1: Calculate length of a reciprocal space vector
        '''        
           
        self.load()

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
	
    def set_sim_controls(self, simc = None):

        # from pyemaps import 
        if not simc:
            # all defaults set in backend
            return
                    
        if not simc.isDefExcitation():
            sgmin, sgmax = simc.excitation
            dif.setexcitation(sgmin, sgmax)

        if not simc.isDefGmax():
            dif.setglen(simc.gmax)

        if not simc.isDefBmin():
            dif.setgcutoff(simc.bmin)

        if not simc.isDefIntensity():
            intz0, intctl = simc.intensity
            dif.setintensities(intctl, intz0)

        if not simc.isDefXaxis():
            x0,x1,x2 = simc.xaxis
            dif.set_xaxis(1, x0, x1, x2)

        if not simc.isDefGctl():
            dif.setgctl(simc.gctl)

        if not simc.isDefZctl():
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