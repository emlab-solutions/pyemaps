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
def add_dif(target):
    import numpy as np
    from numpy import asfortranarray as farray

    from . import dif
    from .. import EMC, DP
    from .. import DEF_MODE, DEF_CBED_DSIZE, DEF_XAXIS
    from .. import EMCError,DPListError,CrystalClassError,DPError

    def load(self, cty=0):
        """
        Load the crystal's data into the simulation backend.

        The data stays in the backend's memory until :py:meth:`~pyemaps.crystals.Crystal.unload` is called or another crystal
        is loaded. The backend holds one crystal at a time for the whole process, so running
        simulations for different crystals concurrently in one process gives wrong results; use
        separate processes instead.

        :param cty: 0 for simulations, 1 for the crystal constructor (:py:meth:`~pyemaps.crystals.Crystal.generateMxtal`).
        :type cty: int, optional
        :raise ~pyemaps.errors.CrystalClassError: if an atom symbol is longer than 10 characters, or the backend
            can't load the crystal.

        .. note::

            The simulation methods call this themselves, and skip it when the crystal is already
            loaded, so you don't need to call it directly.
        """
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
            raise CrystalClassError('Failed to load crystal')

        self._loaded = True
        self._ltype = cty

    def unload(self):
        """
        Remove the crystal's data from the simulation backend's memory.
        """
        dif.crystaldelete()
        self._loaded = False

    def generateDP(self, mode = None, dsize = None, em_controls = None):
        """
        Simulate a kinematic diffraction pattern.

        :param mode: 1 for normal diffraction or 2 for convergent beam (CBED). Defaults to 1.
        :type mode: int, optional
        :param dsize: diffracted beam (disk) size, used only in CBED mode. Defaults to
            *DEF_CBED_DSIZE* (0.16).
        :type dsize: float, optional
        :param em_controls: microscope and simulation controls. Defaults to ``EMC()``.
        :type em_controls: :py:class:`~pyemaps.emcontrols.EMControl`, optional
        :return: ``(emc, dp)``: the controls used and the diffraction pattern, a
            :py:class:`~pyemaps.kdiffs.diffPattern`. *emc* is the same object as *em_controls*,
            updated with the mode, the disk size (CBED) and the x-axis the backend calculated if none
            was set.
        :rtype: tuple
        :raise ~pyemaps.errors.EMCError: if *mode* isn't 1 or 2, *dsize* isn't numeric, or a control is missing.
        :raise ~pyemaps.errors.DPError: if the simulation fails.
        """

        if em_controls is None:
            em_controls =EMC()

        # if not sim_controls:
        #     em_controls =SIMC()

        tx0, ty0 = em_controls.tilt
        dx0, dy0 = em_controls.defl
        cl, vt = em_controls.cl, em_controls.vt
        zone = em_controls.zone
        sc = em_controls.simc
        if em_controls.xaxis != DEF_XAXIS:
            xa = em_controls.xaxis
        else:
            xa = None

        if not mode:
            mode = DEF_MODE

        if mode == 2 and dsize is None:
            dsize = DEF_CBED_DSIZE

        ret, diffp = self._get_diffraction(zone,mode,tx0,ty0,dx0,dy0,cl,vt,dsize,xa,sc)
        
        
        if ret != 200:
            raise DPError('failed to generate diffraction patterns')

        # update the controls
        
        em_controls(mode=mode)
        if mode == 2:
            em_controls(dsize=dsize)
        
        # @70323 merge
        # update x-axis if it was set to (0,0,0)
        # and new xaxis is calculated by the backend

        if em_controls.xaxis == DEF_XAXIS:
            xa1 = 0
            xa2 = 2
            xa3 = 0
            xa1, xa2, xa3 = dif.get_xaxis()
            em_controls(xaxis = (xa1,xa2,xa3))

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
                              xa = None,
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
            print(f'tilt and deflection values: {tx0},{ty0}, {dx0}, {dy0}')
            raise EMCError('Control parameters invalid: tilt and deflection')

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
        if xa:
            dif.set_xaxis(1, xa[0], xa[1], xa[2])
        
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
            klines_arr = farray(np.zeros((num_klines, 5)), dtype=np.single)
            
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
            disks_arr = farray(np.zeros((num_disks, 6)), dtype=np.single)
            if dif.get_disks(disks_arr) == 0:
                # for i in range(num_disks):
                #     x1,y1,r,i1,i2,i3=disks_arr[i][0:]
                #     disk={}
                #     disk['c']=(x1,y1)
                #     disk['r']=r
                #     disk['idx']=(int(i1),int(i2),int(i3))
                #     disks.append(disk)
                for d in disks_arr:
                    x1,y1,r,i1,i2,i3=d
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
                hlines_arr = farray(np.zeros((num_hlines, 5)), dtype=np.single)
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
        Simulate a kinematic diffraction pattern and return it in a list.

        .. deprecated::
            Use :py:meth:`~pyemaps.crystals.Crystal.generateDP`, which returns the pattern and its controls directly.

        :param mode: 1 for normal diffraction or 2 for convergent beam (CBED). Defaults to 1.
        :type mode: int, optional
        :param dsize: diffracted beam (disk) size, used only in CBED mode.
        :type dsize: float, optional
        :param em_controls: microscope and simulation controls.
        :type em_controls: :py:class:`~pyemaps.emcontrols.EMControl`, optional
        :return: a list holding the one pattern, with its controls.
        :rtype: :py:class:`DPList <pyemaps.kdiffs.Diffraction>`
        :raise ~pyemaps.errors.CrystalClassError: if the simulation fails.
        """
        from .. import DPList
        if mode is None:
            mode = 1
        try:
            emc, cdp = self.generateDP(mode = mode, dsize=dsize, em_controls = em_controls)
            myDif = DPList(self._name, mode = mode)
            myDif.add(emc, cdp)

        except (DPListError, EMCError, DPError) as e:
            raise CrystalClassError('failed to generate diffraction')

        return myDif   

    def d2r(self, v = (0.0, 0.0, 0.0)):
        """
        Transform a vector from real space to reciprocal space, using the crystal's metric tensor.

        :param v: the vector's three components.
        :type v: tuple of float, optional
        :return: the transformed vector.
        :rtype: tuple of float
        """
        
        self.load()

        x, y, z = v
        rx, ry, rz = dif.drtrans(x, y, z, 0)

        # dif.crystaldelete()
        return rx, ry, rz

    def r2d(self, v = (0.0, 0.0, 0.0)):
        """
        Transform a vector from reciprocal space to real space, using the crystal's reciprocal
        metric tensor.

        :param v: the vector's three components.
        :type v: tuple of float, optional
        :return: the transformed vector.
        :rtype: tuple of float
        """
   
        self.load()

        x, y, z = v
        dx, dy, dz = dif.drtrans(x, y, z, 1)

        # dif.crystaldelete()
        return dx, dy, dz

    def angle(self, v1 =(1.0, 0.0, 0.0), \
                     v2 = (0.0, 0.0, 1.0),
                     ty = 0):
        """
        Calculate the angle between two vectors, both in real space or both in reciprocal space.

        :param v1: the first vector.
        :type v1: tuple of float, optional
        :param v2: the second vector.
        :type v2: tuple of float, optional
        :param ty: 0 for real-space vectors, 1 for reciprocal-space vectors.
        :type ty: int, optional
        :return: the angle, in degrees.
        :rtype: float
        :raise ValueError: if either vector is zero.
        """
        x1, y1, z1 = v1
        if x1 == 0.0 and y1 == 0.0 and z1 == 0.0:
            raise ValueError("Error: input vector can't be zero")
        
        x2, y2, z2 = v2
        if x2 == 0.0 and y2 == 0.0 and z2 == 0.0:
            raise ValueError("Error: input vector can't be zero")           
   
        self.load()

        a = dif.ang(x1, y1, z1, x2, y2, z2, ty)

        # dif.crystaldelete()
        return a

    def vlen(self, v = (1.0, 0.0, 0.0), ty = 0):
        
        """
        Calculate the length of a real-space or reciprocal-space vector.

        :param v: the vector's three components.
        :type v: tuple of float, optional
        :param ty: 0 for a real-space vector (length in Å), 1 for a reciprocal-space vector
            (length in 1/Å).
        :type ty: int, optional
        :return: the vector's length.
        :rtype: float
        """
              
        self.load()

        x, y, z = v
        ln = dif.vlen(x, y, z, ty)

        # dif.crystaldelete()
        return ln

    @staticmethod
    def wavelength(kv = 100):
        """
        Calculate the relativistic electron wavelength for an accelerating voltage.

        :param kv: accelerating voltage, in kV.
        :type kv: float or int, optional
        :return: the wavelength, in Å.
        :rtype: float
        :raise ValueError: if *kv* isn't positive.
        """
        import math

        if kv <= 0.0:
            raise ValueError("Error: input kv must be positive number")

        wlen = 0.3878314/math.sqrt(kv*(1.0+0.97846707e-03*kv))
        return wlen
	
    def set_sim_controls(self, simc = None):
        """
        Send the simulation controls to the backend. Values left at their defaults aren't sent,
        since the backend already has them.

        :param simc: simulation controls. If omitted, the backend defaults are used.
        :type simc: :py:class:`~pyemaps.emcontrols.SIMControl`, optional

        .. note::

            The simulation methods call this themselves; you don't need to call it directly.
        """
        # from pyemaps import 
        if not simc:
            # all defaults set in backend set by dif.initcontrols()
            return
                     
        if not simc._check_def('excitation'):
            sgmin, sgmax = simc.excitation
            dif.setexcitation(sgmin, sgmax)

        if not simc._check_def('gmax'):
            dif.setglen(simc.gmax)

        if not simc._check_def('bmin'):
            dif.setgcutoff(simc.bmin)

        if not simc._check_def('intensity'):
            intz0, intctl = simc.intensity
            dif.setintensities(intctl, intz0)

        if not simc._check_def('gctl'):
            dif.setgctl(simc.gctl)

        if not simc._check_def('zctl'):
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