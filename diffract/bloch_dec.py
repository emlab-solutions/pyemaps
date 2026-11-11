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
def add_bloch(target):    
    """
    
    Dynamic Simulation Specific Controls Default Values:
    ---------------------------------------------------- 

    .. data:: DEF_APERTURE
        :value: 1.0

    .. data:: DEF_OMEGA
        :value: 10

    .. data:: DEF_SAMPLING
        :value: 8

    .. data:: DEF_PIXSIZE
        :value: 25

    .. data:: DEF_DETSIZE
        :value: 512

    .. data:: DEF_CBED_DSIZE
        :value: 0.16

    .. data:: DEF_THICKNESS
        :value: (200, 200, 100)

    .. data:: DEF_DSIZE_LIMITS
        :value: (0.01, 0.5)

    """
    from . import bloch, dif
    from .. import DEF_APERTURE, \
                   DEF_THICKNESS, \
                   DEF_SAMPLING, \
                   DEF_PIXSIZE, \
                   DEF_DETSIZE, \
                   MAX_DEPTH, \
                   DEF_OMEGA, \
                   DEF_CBED_DSIZE, \
                   DEF_MODE, \
                   DEF_DSIZE_LIMITS, \
                   DEF_XAXIS
    from .. import BImgList, EMC, SIMC

    def _default_bloch_controls():
        # a new object for each call: beginBloch updates the controls it's given
        return EMC(cl=200, # set smaller that 1000 default value
                   simc = SIMC(gmax=1.0, excitation=(0.3,1.0)))

    from ..fileutils import compose_ofn
    from .. import BlochError,BlochListError
    import numpy as np
    from numpy import asfortranarray as farray
    from .. import TY_NORMAL, TY_LACBED

    BIMG_EXT = '.im3'
    MAX_BIMGFN = 256
    CBED_MODE = DEF_MODE + 1

    def _getBlochFN(self):
        '''
        Constructs a bloch image output file name.
        
        Refer to :ref:`Environment Variables <Environment Variables>` 
        for how this file name is constructed.

        '''
        cfn = compose_ofn(None, self.name, ty='bloch')+BIMG_EXT

        l = len(cfn)
        if l > MAX_BIMGFN:
            raise BlochError('Bloch image file name too long, it cant excced 256')
        
        ffn = farray(np.empty((256), dtype='c'))
        for i in range(l):
            ffn[i] = cfn[i]

        return cfn, ffn, l
        
    def beginBloch(self, aperture = DEF_APERTURE,
                         omega = DEF_OMEGA,
                         sampling = DEF_SAMPLING,
                         dbsize = DEF_CBED_DSIZE,
                         em_controls = None
                    ):
        """
        Start a dynamic diffraction (Bloch wave) simulation session.

        The results stay in the backend until :py:meth:`~pyemaps.crystals.Crystal.endBloch`. Between the two calls you can
        retrieve them with:

        1. :py:meth:`~pyemaps.crystals.Crystal.getBlochImages`: the diffraction images, for one or more sample thicknesses;
        2. :py:meth:`~pyemaps.crystals.Crystal.getSCMatrix`: the scattering matrix, eigenvalues and diffracted beams at one
           sampling point;
        3. :py:meth:`~pyemaps.crystals.Crystal.getIBDetails`: the sampling points and their beam tilts;
        4. :py:meth:`~pyemaps.crystals.Crystal.getCalculatedBeams`: the diffracted beams used in the calculation.

        To get images in one call, use :py:meth:`~pyemaps.crystals.Crystal.generateBloch` instead.

        :param aperture: objective aperture. Defaults to *DEF_APERTURE* (1.0).
        :type aperture: float, optional
        :param omega: diagonalization cutoff. Defaults to *DEF_OMEGA* (10).
        :type omega: int, optional
        :param sampling: number of sampling points along the disk radius. Defaults to
            *DEF_SAMPLING* (8).
        :type sampling: int, optional
        :param dbsize: diffracted beam (disk) size, within *DEF_DSIZE_LIMITS* (0.01 to 1.0).
            Defaults to *DEF_CBED_DSIZE* (0.16).
        :type dbsize: float, optional
        :param em_controls: microscope and simulation controls. Defaults to a camera length of
            200 mm, ``gmax`` 1.0 and excitation error limits (0.3, 1.0). The object is updated with
            the settings used and kept as the crystal's session controls.
        :type em_controls: :py:class:`~pyemaps.emcontrols.EMControl`, optional
        :return: ``(n, points)``: the number of sampling points, and the points as a list of
            ``(i, j)`` tuples.
        :rtype: tuple
        :raise ~pyemaps.errors.BlochError: if an input is invalid, the backend's resource limit is reached, or the
            simulation fails.
        """
        if aperture is None or not isinstance(aperture, (int, float)):
            raise BlochError('Objective aperture must be valid numberal')

        if omega is None or not isinstance(omega, int):
            raise BlochError('Diagnization cutoff value must be valid numberal')

        if dbsize is None or not isinstance(dbsize, (int,float)) or \
            dbsize < DEF_DSIZE_LIMITS[0] or dbsize > DEF_DSIZE_LIMITS[1]:
            raise BlochError(f'Diffracted beam size must be in range {DEF_DSIZE_LIMITS}')

        if em_controls is None:
            em_controls = _default_bloch_controls()

        if not isinstance(em_controls, EMC):
            raise BlochError('Control object must be of EMControl type')


        dif.initcontrols()
        dif.setmode(CBED_MODE) # alway in CBED mode

        
        # setting default simulation controls
        self.set_sim_controls(em_controls.simc)

        dif.setdisksize(dbsize)
   
        self.load()

        tx, ty = em_controls.tilt[0], em_controls.tilt[1]
        dx, dy = em_controls.defl[0], em_controls.defl[1]
        z = em_controls.zone
        vt, cl = em_controls.vt,  em_controls.cl
        
        dif.setsamplecontrols(tx, ty, dx, dy)
        dif.setemcontrols(cl, vt)        
        dif.setzone(z[0], z[1], z[2])
        
        if em_controls.xaxis != DEF_XAXIS:
            xa = em_controls.xaxis
            dif.set_xaxis(1, xa[0], xa[1], xa[2])
        
        ret = dif.diffract(1)
        if ret == 0:
            dif.diff_internaldelete(1)
            raise BlochError('Error bloch runtime1')
        
        dif.diff_internaldelete(1)
        
        ret = bloch.dobloch(aperture,omega,sampling,0.0)
        
        if ret == 2:
            raise BlochError('Predefined Bloch computation resource limit reached')

        if ret != 0:
            raise BlochError('Error computing dynamic diffraction')
        
        nsampling = bloch.get_nsampling()
        sampling_points = farray(np.zeros((2, nsampling)), dtype=int)
        sampling_points, ret = bloch.get_samplingpoints(sampling_points)

        if ret != 0:
            raise BlochError('Failed to retrive sampling points used in scattering matrix run')
        
        spoints = np.transpose(sampling_points)

        # convert the np array to a array of python native tuple
        sp = [(list(p)[0].item(),list(p)[1].item()) for p in spoints]

        # updating controls with input params as optional attributes for easy handling
        em_controls(mode = 2, 
                    dsize = dbsize,
                    aperture = aperture)                      
        
        em_controls.simc(omega = omega, 
                         sampling = sampling
                        )
        # update x-axis if it was set to (0,0,0)
        # and new xaxis is calculated by the backend

        if em_controls.xaxis == DEF_XAXIS:
            xa1 = 0
            xa2 = 2
            xa3 = 0
            xa1, xa2, xa3 = dif.get_xaxis()
            em_controls(xaxis = (xa1,xa2,xa3))

        self.session_controls=em_controls
        return nsampling, sp

    def getBlochImages(self, 
                  sample_thickness = DEF_THICKNESS,
                  pix_size = DEF_PIXSIZE,
                  det_size = DEF_DETSIZE,
                  nType = TY_NORMAL,
                  bSave = False):
       """
       Get the dynamic diffraction images from the session started by :py:meth:`~pyemaps.crystals.Crystal.beginBloch`:
       one image per sample thickness, or, for large-angle CBED, one per thickness and calculated
       beam.

       :param sample_thickness: ``(start, end, step)``, in Å. Images are made at *start*,
           *start* + *step*, ... below *end*, and at *end*. At most *MAX_DEPTH* (200) thicknesses.
           Defaults to *DEF_THICKNESS*, ``(200, 200, 100)``: one image at 200 Å.
       :type sample_thickness: tuple of int, optional
       :param pix_size: detector pixel size, in µm. Defaults to *DEF_PIXSIZE* (25).
       :type pix_size: int, optional
       :param det_size: detector size in pixels; each image is *det_size* × *det_size*. Defaults
           to *DEF_DETSIZE* (512).
       :type det_size: int, optional
       :param nType: ``TY_NORMAL`` (0) for normal images, or ``TY_LACBED`` (1) for large-angle
           CBED images.
       :type nType: int, optional
       :param bSave: if ``True``, also save the images to a raw ``.im3`` file in the ``bloch``
           folder of the pyEMAPS data folder; see :ref:`Environment Variables <Environment Variables>`.
       :type bSave: bool, optional
       :return: the images, each with the controls and thickness it was made with.
       :rtype: :py:class:`~pyemaps.ddiffs.BlochImgs`
       :raise ~pyemaps.errors.BlochListError: if *sample_thickness*, *pix_size* or *det_size* is invalid, or there
           are too many thicknesses.
       :raise ~pyemaps.errors.BlochError: if the images can't be made or the file can't be written.

       .. warning::

           Dynamic diffraction needs a lot of memory, and large-angle CBED
           (``nType = TY_LACBED``) needs much more than normal images. To reduce it, lower:

           - the detector size *det_size*: 256 instead of the default 512, for example, uses a
             quarter of the image memory;
           - the number of sampling points *sampling*.
       """
       from copy import deepcopy

       if pix_size is None or not isinstance(pix_size, int):
            raise BlochListError('Pixel size input must be valid integert')

       if det_size is None or not isinstance(det_size, int):
            raise BlochListError('Pixel size input must be valid integert')

       if sample_thickness is None or \
          not all(isinstance(v, int) for v in sample_thickness) or \
          len(sample_thickness) !=3:
            raise BlochListError('Sample thickness input must be valid tuple of three integers')

       th_start, th_end, th_step = sample_thickness

       if th_start > th_end or th_step <= 0:
            raise BlochListError('Sample thickness input must be valid integers range')               

       thlist = []
       if th_start == th_end:
            thlist.append(th_start)
       else:
            thlist = list(range(th_start, th_end, th_step))
            thlist.append(th_end)

       ndep = len(thlist)

       if ndep > MAX_DEPTH:
            raise BlochListError(f'Number of sample thickness cannot exceed {MAX_DEPTH}')

       # save the input as optional control attributes
       imgfn =''
       if bSave: 
            imgfn, bfn, l = self._getBlochFN()
            if l > MAX_BIMGFN-1:
                raise BlochError(f'File name must not exceed {MAX_BIMGFN-1}')
            
            if bloch.openimgfile(det_size, ndep, bfn, l) != 0:
                raise BlochError('Error opening file for write, check if you have write permission')

       isLACBED = (nType == TY_LACBED)
    #    for th in thlist:
       nslices = ndep
       nout = 0
       if isLACBED:
           nout = bloch.getncalcbeams()
           nslices = ndep*nout
           
       bimg = farray(np.zeros((det_size, det_size, nslices), dtype=np.float32))
       thl = farray(np.array(thlist), dtype=int)

       bimg, ret = bloch.getimage(thl,
                                  bimg,
                                  teta = 0,
                                  pix = pix_size,
                                  det = det_size,
                                  blacbed = isLACBED,
                                  bsave = bSave)
       
       if(ret != 0):
            raise BlochError("bloch image generation failed!")
       
# build a image list
       bimgs = BImgList(self.name)

       self.session_controls(pix_size=pix_size, det_size=det_size)
       
       for i, th in enumerate(thlist):
          emc = deepcopy(self.session_controls)
          emc.simc(sth=th)
          if isLACBED:
                for j in range(nout):
                    bimgs.add(emc, bimg[:,:,i*nout + j])
          else:
              bimgs.add(emc, bimg[:,:,i])


       if bSave:
            if bloch.closeimgfile() != 0:
                raise BlochError('Error closing file')

            print(f'The raw bloch image(s) of dimensions {det_size}x{det_size}x{nslices} and an offset of 8 bytes successfully saved to: \n{imgfn}')
            print(f'To view, import the file into ImageJ or other raw image visualization tools')

       return bimgs
           
    def getIBDetails(self, bPrint=True):
        """
        Get the sampling points of the session started by :py:meth:`~pyemaps.crystals.Crystal.beginBloch`, with the incident
        beam tilt at each one.

        :param bPrint: also print them.
        :type bPrint: bool, optional
        :return: ``(n, details)``: the number of sampling points, and a list of dictionaries with
            the keys ``ib``, the point as an ``(i, j)`` tuple, and ``tilt``, the beam tilt in
            reciprocal space as three numbers.
        :rtype: tuple
        :raise ~pyemaps.errors.BlochError: if the session has no sampling points or they can't be retrieved.
        """
        nib = bloch.get_nsampling()
        if nib <=0:
            raise BlochError("Failed to retrieve number of incidental beams")

        if nib == 0:
            raise BlochError("No incidental beams found")
        
        
        net = farray(np.zeros((2, nib), dtype=int))
        tilt = farray(np.zeros((3, nib), dtype=float))

        net, tilt, ret = bloch.getibinfo(net, tilt)
        if ret != 0:
            raise BlochError("failed to retrieve incidental beams info")
        
        if bPrint:
            print(f'\n-------Dynamic Diffraction Simulation Session for {self._name}---------\n')
            print(f'Total Number of sampling points: {nib}\n')

            smp = "Sampling"
            stilt = "Beam Tilts In Reciprical Space"
            
            print(f"{smp:^11}{stilt:^48}")
            print(f"{'Points':^11}\n")
            
        ibnet = np.transpose(net)
        ibtilt = np.transpose(tilt)
        
        # if bPrint:
        ibs_list =[]
        for i in range(1, nib+1, 1):
            net1, net2 = ibnet[i-1]
            t1,t2,t3 = ibtilt[i-1]
            ibs_list.append(dict(ib=(net1, net2), tilt=ibtilt[i-1]))
            if bPrint:
                sn1 = '{0: < #06d}'. format(int(net1))
                sn2 = '{0: < #06d}'. format(int(net2))
                st1 = '{0: < #016.10f}'. format(float(t1))
                st2 = '{0: < #016.10f}'. format(float(t2))
                st3 = '{0: < #016.7g}'. format(float(t3))

                print(f"{sn1}{sn2}{st1}{st2}{st3}")  

        return nib, ibs_list

    def getCalculatedBeams(self, bPrint=False):
        """
        Get the diffracted beams used in the session started by :py:meth:`~pyemaps.crystals.Crystal.beginBloch`.

        :param bPrint: also print them.
        :type bPrint: bool, optional
        :return: ``(n, beams)``: the number of beams, and their Miller indices as an n × 3 array.
        :rtype: tuple
        :raise ~pyemaps.errors.BlochError: if the beams can't be retrieved.
        """
        ncalcbeams = bloch.getncalcbeams()
        if ncalcbeams <= 0:
            raise BlochError("failed to retrieve diffracted beams info")

        cb = farray(np.zeros((3, ncalcbeams), dtype=int))
        
        cb, ret = bloch.getcalcbeams(cb)

        if ret != 0:
            raise BlochError("failed to retrieve incidental beams info")

        cbms = np.transpose(cb) 
        
        if bPrint:
            print('---------Calculated Beams in Miller Indexes---------')
            shkl = "h   K   l"
            print(f"{shkl:^12}")

            for cbm in cbms:
                h,k,l = cbm
                sh = '{0: < #04d}'. format(int(h))
                sk = '{0: < #04d}'. format(int(k))
                sl = '{0: < #04d}'. format(int(l))

                print(f"{sh}{sk}{sl}") 

        return ncalcbeams, cbms  
     
# ----------------deprecated and folded into getSCMatrix call----------------
    # def getEigen(self, ib_coords=(0,0)):
    #     '''
    #     Returns eigen values for given sampling point.
    #     It must be called during a dynamic diffraction simulation session
    #     marked by
    #     `beginBloch <pyemaps.crystals.html#pyemaps.crystals.Crystal.beginBloch>`_ and 
    #     `endBloch <pyemaps.crystals.html#pyemaps.crystals.Crystal.endBloch>`_.   
    #     :param ib_coords: Sampling point coordinates tuple
    #     :type ib_coords: tuple, optional, default (0,0)
    #     :return: a list of complex eigen values at sampling point location
    #     :rtype: numpy.ndarray

    #     Example of the eigen vales:
    #     .. code-block:: console
    #         Eigen values at: (0, 0):
    #         [ 0.04684002-0.00218389j -0.2064669 -0.00147516j -0.30446348+0.00055009j
    #         -0.27657617+0.00023512j -0.2765751 +0.00023515j  0.00539041-0.00382443j
    #         -0.535879  -0.00023585j -0.5612881 +0.00045343j -0.55369247+0.00026236j
    #         -0.55368818+0.00026249j -0.19093572+0.00066419j -0.1550311 +0.00045471j
    #         -0.15503166+0.00045471j -0.58842399-0.00202841j -0.67850191+0.00042728j
    #         -0.72713566+0.00060655j -0.70972681+0.00052279j -0.72092338+0.0005903j
    #         -0.72093237+0.00059052j -0.64608335-0.0001983j  -0.64607544-0.00019853j]
    #     '''
    #     #  validate the input values

    #     if ib_coords is None or not all(isinstance(v, int) for v in ib_coords) or len(ib_coords) != 2:
    #          raise BlochError("Invalid incident beam coordinates input, must be tuple of two integers")

    #     scmdim = bloch.get_scmdim(ib_coords)
    #     if scmdim <= 0:
    #         raise BlochError("Error finding corresponding scattering matrix, use getIBDetails to find potential input for ib_coords")
        
    #     ev = farray(np.zeros(scmdim, dtype=np.complex64))
    #     ev, ret = bloch.geteigenvalues(ib_coords, ev)
    #     if ret < 0 or ret > scmdim:
    #         raise BlochError("failed to retrieve incidental beams info")
        
    #     return ev

    def getSCMatrix(self,
                    ib_coords = (0,0), 
                    sample_thickness = DEF_THICKNESS[0],
                    rvec = (0.0,0.0,0.0)
                    ):
        """
        Get the scattering matrix at one sampling point of the session started by
        :py:meth:`~pyemaps.crystals.Crystal.beginBloch`, with its eigenvalues and diffracted beams. For the session's sampling
        points, call :py:meth:`~pyemaps.crystals.Crystal.getIBDetails`.

        :param ib_coords: the sampling point, as an ``(i, j)`` tuple of integers.
        :type ib_coords: tuple, optional
        :param sample_thickness: sample thickness, in Å. Defaults to 200.
        :type sample_thickness: int, optional
        :param rvec: the R vector, three numbers between 0.0 and 1.0, that shifts the atom
            positions in the crystal.
        :type rvec: tuple of float, optional
        :return: ``(n, scm, ev, beams)``: the matrix dimension; the n × n complex scattering matrix;
            the n complex eigenvalues; and the diffracted beams' Miller indices as an n × 3 array.
        :rtype: tuple
        :raise ~pyemaps.errors.BlochError: if an input is invalid, or there's no scattering matrix for that point.

        Example eigenvalues:

        .. code-block:: console

            [ 0.04684002-0.00218389j -0.2064669 -0.00147516j -0.30446348+0.00055009j
             -0.27657617+0.00023512j -0.2765751 +0.00023515j  0.00539041-0.00382443j
             ...]
        """

        #  validate the input values
        if ib_coords is None or len(ib_coords) != 2 or not all(isinstance(v, int) for v in ib_coords):  
            raise BlochError("Invalid incident beam coordinates input, must be tuple of two integers2")   

        if sample_thickness is None or not isinstance(sample_thickness, int):
            raise BlochError("Sample thickness ")

        if rvec is None or not all(isinstance(v, (int,float)) for v in rvec) or len(rvec) != 3:
            raise BlochError("Invalid R-vector input, must be tuple of three floats")

        # get the dimension of the scattering matrix
        scmdim, RET = bloch.compute_scm([ib_coords[0], ib_coords[1]])
        
        if RET != 0 or scmdim <= 0:
            raise BlochError("Error finding corresponding scattering matrix")

        scm = farray(np.zeros((scmdim, scmdim)), dtype=np.complex64)
        ev = farray(np.zeros(scmdim), dtype=np.complex64)
        bms = farray(np.zeros((3, scmdim), dtype=int))
        scm, ev, bms, ret = bloch.getscm(sample_thickness, rvec, scm, ev, bms)
        if ret != 0:
            raise BlochError('Error retieving scattering matrix, input matrix dimension too small, use getIBDetails to find extact dimentsion')

        return scmdim, scm, ev, np.transpose(bms)

    def endBloch(self):
       """
       End the dynamic diffraction session started by :py:meth:`~pyemaps.crystals.Crystal.beginBloch`, and free the
       backend's memory for it.
       """
       dif.diff_delete()
       bloch.free_bloch()
        
    def generateBloch(self, aperture = DEF_APERTURE,                    
                            omega = DEF_OMEGA,                          
                            sampling = DEF_SAMPLING,                    
                            pix_size = DEF_PIXSIZE,                     
                            det_size = DEF_DETSIZE,                     
                            disk_size = DEF_CBED_DSIZE,                 
                            sample_thickness = DEF_THICKNESS,           
                            em_controls = None,
                            nType = TY_NORMAL,
                            bSave = False):
        """
        Simulate dynamic diffraction (Bloch wave) images in one call. It's the same as calling
        :py:meth:`~pyemaps.crystals.Crystal.beginBloch`, :py:meth:`~pyemaps.crystals.Crystal.getBlochImages` and :py:meth:`~pyemaps.crystals.Crystal.endBloch`.

        :param aperture: objective aperture. Defaults to *DEF_APERTURE* (1.0).
        :type aperture: float, optional
        :param omega: diagonalization cutoff. Defaults to *DEF_OMEGA* (10).
        :type omega: int, optional
        :param sampling: number of sampling points along the disk radius. Defaults to
            *DEF_SAMPLING* (8).
        :type sampling: int, optional
        :param pix_size: detector pixel size, in µm. Defaults to *DEF_PIXSIZE* (25).
        :type pix_size: int, optional
        :param det_size: detector size in pixels; each image is *det_size* × *det_size*. Defaults
            to *DEF_DETSIZE* (512).
        :type det_size: int, optional
        :param disk_size: diffracted beam (disk) size, within *DEF_DSIZE_LIMITS* (0.01 to 1.0).
            Defaults to *DEF_CBED_DSIZE* (0.16).
        :type disk_size: float, optional
        :param sample_thickness: ``(start, end, step)``, in Å: one image at *start*,
            *start* + *step*, ... below *end*, and at *end*. Defaults to *DEF_THICKNESS*,
            ``(200, 200, 100)``.
        :type sample_thickness: tuple of int, optional
        :param em_controls: microscope and simulation controls. Defaults to a camera length of
            200 mm, ``gmax`` 1.0 and excitation error limits (0.3, 1.0).
        :type em_controls: :py:class:`~pyemaps.emcontrols.EMControl`, optional
        :param nType: ``TY_NORMAL`` (0) for normal images, or ``TY_LACBED`` (1) for large-angle
            CBED images, one per thickness and calculated beam.
        :type nType: int, optional
        :param bSave: if ``True``, also save the images to a raw ``.im3`` file in the ``bloch``
            folder of the pyEMAPS data folder.
        :type bSave: bool, optional
        :return: the images, each with the controls and thickness it was made with.
        :rtype: :py:class:`~pyemaps.ddiffs.BlochImgs`
        :raise ~pyemaps.errors.BlochError: if an input is invalid or the simulation fails.
        :raise ~pyemaps.errors.BlochListError: if *sample_thickness*, *pix_size* or *det_size* is invalid.

        .. warning::

            Dynamic diffraction needs a lot of memory, and large-angle CBED
            (``nType = TY_LACBED``) needs much more than normal images. To reduce it, lower:

            - the detector size *det_size*: 256 instead of the default 512, for example, uses a
              quarter of the image memory;
            - the number of sampling points *sampling*.
        """
        try:
           
            _, _ = self.beginBloch(aperture=aperture, 
                            omega=omega, 
                            sampling=sampling, 
                            dbsize = disk_size,
                            em_controls=em_controls)

        except BlochError as e:
            # re-raise the same error, so that the caller can handle it
            raise e

        except Exception as e:
            # Any other exception will be handled by the callers as BlochError from this point on
            raise BlochError(f'Something went wrong in starting bloch simulation') from e
        
        else:
            try:
                bimgs = self.getBlochImages(
                    sample_thickness = sample_thickness,
                    pix_size = pix_size,
                    det_size = det_size,
                    nType = nType,
                    bSave = bSave)

            except (BlochError, BlochListError) as e:
                raise

            except Exception as e:
                raise BlochError(f'Something went wrong when retrieving bloch image {e}') from e

            else:
                return bimgs

            finally:
                self.endBloch()

        finally:
            self.endBloch()

                

    target.beginBloch = beginBloch
    target._getBlochFN = _getBlochFN

    # ---These calls must be between beginBloch and endBloch calls
    target.getIBDetails = getIBDetails
    # target.getBeams = getBeams     <-------deprecate
    target.getSCMatrix = getSCMatrix
    target.getBlochImages = getBlochImages
    target.getCalculatedBeams = getCalculatedBeams
    # target.getLACBEDImage = getLACBEDImage
    # ---These calls must be between beginBloch and endBloch calls

    target.endBloch = endBloch

    target.generateBloch = generateBloch

    return target