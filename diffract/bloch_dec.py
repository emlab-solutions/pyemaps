def add_bloch(target):    
    '''
    bloch module interfaces
    '''
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
                   DEF_DSIZE_LIMITS
    from .. import BImgList, EMC, SIMC

    from ..fileutils import compose_ofn
    from .. import BlochError,BlochListError
    import numpy as np
    from numpy import asfortranarray as farray

    BIMG_EXT = '.im3'
    MAX_BIMGFN = 256
    CBED_MODE = DEF_MODE + 1

    def getBlochFN(self):
        '''
        Construct a bloch image output file name.
        
        (TODO: ref to environment variable for construction of the file name)

        '''
        cfn = compose_ofn(None, self.name, ty='bloch')+BIMG_EXT

        l = len(cfn)
        if l > MAX_BIMGFN:
            raise BlochError('Bloch image file name too long, it cant excced 256')
        
        # fortran string
        ffn = farray(np.empty((256), dtype='c'))
        for i in range(l):
            ffn[i] = cfn[i]

        return cfn, ffn, l
        
    def generateBloch(self, aperture = DEF_APERTURE, 
                            omega = DEF_OMEGA,  
                            sampling = DEF_SAMPLING,
                            pix_size = DEF_PIXSIZE,
                            det_size = DEF_DETSIZE,
                            disk_size = DEF_CBED_DSIZE,
                            sample_thickness = DEF_THICKNESS,
                            em_controls = EMC(cl=200, # set smaller that 1000 default value
                                              simc = SIMC(gmax=1.0, excitation=(0.3,1.0))),
                            bSave = False):
        """
        Generate dynamic diffraction (Bloch) image(s).

        :param aperture: Optional. Objective aperture
        :type aperture: float

        :param omega: Optional. Diagnization cutoff value
        :type omega: float

        :param sampling: Optional. Number of sampling points
        :type sampling: int

        :param pix_size: Optional. Detector pixel size in microns
        :type pix_size: int

        :param det_size: Optional. Detector size or output image size
        :type det_size: int

        :param disk_size: Optional. Diffracted beams size in range set by DEF_DSIZE_LIMITS
        :type disk_size: float

        :param thickness: Optional. Sample thickness in (start, end, step) tuple
        :type thickness: tuple of int

        :param em_controls: Optional. electron microscope control object. (TODO, ref to the class)
        :type em_controls: pyemaps.EMC

        :param bSave: Optional. True - save the output to a raw image file (ext: im3)
        :type bSave: bool

        .. note::

            There will be one slice of image generated for each sample
            thickness specified by sample_thickness = (start, end, step) arguement:

            start, start+step ... start+N*step

            when start is not the same as end, end will not have image
            generated.

        """
        if disk_size < DEF_DSIZE_LIMITS[0] or disk_size > DEF_DSIZE_LIMITS[1]:
            raise BlochError('Diffracted beam size bust be in range {DEF_DSIZE_LIMITS}')

        th_start, th_end, th_step = sample_thickness

        if th_start > th_end or th_step <= 0:
            raise BlochListError('Sample thickness parameter invalid')               

        dep = (th_end-th_start) // th_step + 1
        if dep > MAX_DEPTH:
            raise BlochListError(f'Number of sample thickness cannot exceed {MAX_DEPTH}')

        dif.initcontrols()
        dif.setmode(CBED_MODE) # alway in CBED mode

        
        # setting default simulation controls
        self.set_sim_controls(em_controls.simc)

        dif.setdisksize(disk_size)
   
        self.load()

        tx, ty = em_controls.tilt[0], em_controls.tilt[1]
        dx, dy = em_controls.defl[0], em_controls.defl[1]
        z = em_controls.zone
        vt, cl = em_controls.vt,  em_controls.cl
        
        dif.setsamplecontrols(tx, ty, dx, dy)
        dif.setemcontrols(cl, vt)        
        dif.setzone(z[0], z[1], z[2])
        
        ret = dif.diffract(1)
        if ret == 0:
            raise BlochError('Error bloch runtime1')
        
        dif.diff_internaldelete(1)
        bloch.setsamplethickness(th_start, th_end, th_step)
        
        ret = bloch.dobloch(aperture,omega,sampling,0.0)
        
        if ret == 2:
            raise BlochError('Predefined Bloch computation resource limit reached')

        if ret != 0:
            raise BlochError('Error computing dynamic diffraction')

        # 
        #successful bloch runtime, then retreive bloch image
        #     
        
        slice_step = th_step 
        slice_num = 1 + (th_end-th_start) // slice_step
        th = th_start

        myBlochImgs = BImgList(self._name)
        imgfn =''
        if bSave: 
            imgfn, bfn, l = self.getBlochFN()
            if bloch.openimgfile(det_size, bfn, l) != 0:
                raise BlochError('Error opening file for write')

        for i in range(slice_num):
            ret = bloch.imagegen(th,0,pix_size,det_size, bSave)
            if(ret != 0):
                raise BlochError("bloch image generation failed!")

            raw_image = farray(np.zeros((det_size,det_size), dtype=np.double))
        
            bloch.get_rawimagedata(raw_image)
        
            myBlochImgs.add(em_controls, raw_image)

            th += slice_step

        if bSave:
            if (bloch.closeimgfile() != 0):
                raise BlochError('Error closing file')

            print(f'Raw Bloch images data has been successfully saved to: {imgfn}')
            print(f'To view, import the file into ImageJ or other tools')

# ------- clean up ---------
        bloch.imgmemdelete()
        dif.diff_delete()

        return myBlochImgs

    @staticmethod
    def printIBDetails():
        '''
        Print beams details after bloch scattering matrix run

        Useful before retrieving the scattering matrix with incident 
        beam details as parameters

        '''
        nib = bloch.get_nsampling()
        if nib <=0:
            raise BlochError("Failed to retrieve number of incidental beams")

        if nib == 0:
            raise BlochError("No incidental beams found")
        
        net, tilt, dimscm, ret = bloch.getibinfo(nib)
        if ret != 0:
            raise BlochError("failed to retrieve incidental beams info")
        
        print(f'Total Number of Beams: {nib}\n')

        smp = "Sampling"
        stilt = "Beam Tilts In Reciprical Space"
        sscdim = "Scattering Matrix Dimensions"
        print(f"{smp:^11}{stilt:^48}{sscdim:^4}")
        print(f"{'Points':^11}\n")
        
        ibnet = np.transpose(net)
        ibtilt = np.transpose(tilt)
        ibnscm = np.transpose(dimscm)

        for i in range(1, nib+1, 1):
            net1, net2 = ibnet[i-1]
            t1,t2,t3 = ibtilt[i-1]
            d=ibnscm[i-1]
        
            sn1 = '{0: < #06d}'. format(int(net1))
            sn2 = '{0: < #06d}'. format(int(net2))
            st1 = '{0: < #016.10f}'. format(float(t1))
            st2 = '{0: < #016.10f}'. format(float(t2))
            st3 = '{0: < #016.7g}'. format(float(t3))

            sd = '{0: < #04d}'. format(int(d))

            print(f"{sn1}{sn2}{st1}{st2}{st3}{sd}")   

    @staticmethod
    def getBeams(ib_coords=(0,0), bPrint=False):
        '''
        print diffracted beams for given sample coordinates 
        must be called between beginSCMatrix(...) and endSCMatrix().

        :param ib_coords: Optional. Sampling point coordinates tuple
        :type ib_coords: tuple

        :param bPrint: Optional. True - print beams info on standard output
        :type bPrint: bool

        '''
        
        scmdim = bloch.get_scmdim(ib_coords)
        if scmdim <= 0:
            raise BlochError("Error finding corresponding scattering matrix, use printIBDetails to find potential input for ib_coords")
        
        ev, ret = bloch.getbeams(ib_coords, scmdim)

        if ret < 0 or ret != scmdim:
            raise BlochError("failed to retrieve incidental beams info")
        evv = np.transpose(ev) 
        if bPrint:
            print(f'Total Diffracted Beams In Diagonalization: {scmdim}\n')

            shkl = "h   K   l"
            print(f"{shkl:^12}")

            for e in evv:
                h,k,l = e
                sh = '{0: < #04d}'. format(int(h))
                sk = '{0: < #04d}'. format(int(k))
                sl = '{0: < #04d}'. format(int(l))

                print(f"{sh}{sk}{sl}") 
        return evv   

    @staticmethod
    def getEigen(ib_coords=(0,0)):
        '''
        This method returns eigen values for given sampling point.
        must be called between beginSCMatrix(...) and endSCMatrix().

        :param ib_coords: Optional. Sampling point coordinates tuple
        :type ib_coords: tuple

        :return: a vector of complex numbers
        :rtype: array

        Example of the eigen vales:

        .. code-block:: console

            Eigen values at: (0, 0):
            [ 0.04684002-0.00218389j -0.2064669 -0.00147516j -0.30446348+0.00055009j
            -0.27657617+0.00023512j -0.2765751 +0.00023515j  0.00539041-0.00382443j
            -0.535879  -0.00023585j -0.5612881 +0.00045343j -0.55369247+0.00026236j
            -0.55368818+0.00026249j -0.19093572+0.00066419j -0.1550311 +0.00045471j
            -0.15503166+0.00045471j -0.58842399-0.00202841j -0.67850191+0.00042728j
            -0.72713566+0.00060655j -0.70972681+0.00052279j -0.72092338+0.0005903j
            -0.72093237+0.00059052j -0.64608335-0.0001983j  -0.64607544-0.00019853j]

        '''
        scmdim = bloch.get_scmdim(ib_coords)
        if scmdim <= 0:
            raise BlochError("Error finding corresponding scattering matrix, use printIBDetails to find potential input for ib_coords")
        
        ev, ret = bloch.geteigenvalues(ib_coords, scmdim)
        if ret < 0 or ret != scmdim:
            raise BlochError("failed to retrieve incidental beams info")
        
        return ev

    def beginSCMatrix(self, 
                        aperture = DEF_APERTURE, 
                        omega = DEF_OMEGA,  
                        sampling = DEF_SAMPLING,
                        disk_size = DEF_CBED_DSIZE,
                        thickness = DEF_THICKNESS[0],
                        em_controls = EMC(cl=200, 
                                          simc = SIMC(gmax=1.0, 
                                          excitation=(0.3,1.0))
                        )
                     ):
        '''
        This function begins to run dynamic diffraction simulation and prepare to retieve scattering matrix 
        with sampling point coordinates and sample thickness
        
        :param aperture: Optional. Objective aperture
        :type aperture: float

        :param omega: Optional. Diagnization cutoff value
        :type omega: float

        :param sampling: Optional. Number of sampling points
        :type sampling: int

        :param disk_size: Optional. Diffracted beams size in range set by DEF_DSIZE_LIMITS
        :type disk_size: float

        :param thickness: Optional. sample thickness
        :type thickness: int

        :return: (ns, s). ns = number of sampling points; s - a list of sampling points in (x,y) coordiantes
        :rtype: tuple


        '''
        if disk_size < DEF_DSIZE_LIMITS[0] or disk_size > DEF_DSIZE_LIMITS[1]:
            raise BlochError('Diffracted beam size bust be in range {DEF_DSIZE_LIMITS}')

        dif.initcontrols()
        dif.setmode(CBED_MODE) # alway in CBED mode

        dif.setdisksize(disk_size)
        
        # setting default simulation controls
        
        self.set_sim_controls(em_controls.simc)

        # Load crystal data to backend modules 
           
        self.load()
  
        tx, ty = em_controls.tilt
        dx, dy = em_controls.defl
        z = em_controls.zone
        vt, cl = em_controls.vt,  em_controls.cl
        
        dif.setsamplecontrols(tx, ty, dx, dy)
        dif.setemcontrols(cl, vt)        
        dif.setzone(z[0], z[1], z[2])
        
        ret = dif.diffract(1)
        if ret == 0:
            raise BlochError('Error bloch runtime1')
            
        dif.diff_internaldelete(1)
        bloch.setsamplethickness(thickness, thickness, 100)

        ret = bloch.dobloch(aperture,omega,sampling,0.0,scm=1)
        if ret == 2:
            print('Contact support@emlabsoftware.com for how to register for ' +
            'a full and accelerated version of pyemaps')
            raise BlochError('Bloch computation resource limit reached')

        if ret != 0:
            raise BlochError('Error computing dynamic diffraction')

        print(f'---Scattering matrix data now available for the following sampling points---')
        print(f'call getSCMartix to retrive the scattering matrix at any of the following samplign points')
       
        nsampling = bloch.get_nsampling()
        sampling_points, ret = bloch.get_samplingpoints(nsampling)

        if ret != 0:
            raise BlochError('Failed to retrive sampling points used in scattering matrix run')
        
        print(f'# of sampling points: {nsampling}')
        
        spoints = np.transpose(sampling_points)

        sp = [tuple(p) for p in spoints]
        
        return nsampling, sp


    @staticmethod
    def endSCMatrix():
        """
        Ends scattering matrix runs started by BeginSCMatrix().

        Backend bloch module will no longers retain the scattering 
        matrix, Eigen values, sampling points etc in its memory, 
        unless a new call to beginSCMatrix().

        """
        bloch.cleanup()

    @staticmethod
    def getSCMatrix(ib_coords = (0,0), rvec = None):
        '''
        This function retieves scattering matrix by sampling point coordinates,
        this call must be between:
        1. beginSCMatrix(...), and
        2. endSCMatrix() 
        All available input for ib_coords are captured in standard output from beginSCMatrix()

        :param ib_coords: Optional. Sampling point coordinates tuple
        :type ib_coords: tuple

        :param rvec: Optional. R vector shifting atom coordinates in crystal, value between 0.0 and 1.0
        :type rvec: tuple

        '''
        
        # get the dimension of the scm
        scmdim = bloch.get_scmdim(ib_coords)
        
        if scmdim <= 0:
            raise BlochError("Error finding corresponding scattering matrix,  to find potential input for ib_coords")

        if rvec is None:
            rvec = (0.0,0.0,0.0)

        elif not all(isinstance(v, (int,float)) for v in rvec) or len(rvec) != 3:
            raise BlochError("Invalid R vector input, must be tuple of three floats")

        scm, ret = bloch.getscm(ib_coords, rvec, scmdim)
        if ret <= 0:
            raise BlochError('Error retieving scattering matrix, input matrix dimention too small, use printIBDetails to find extact dimentsion')
        return np.transpose(scm)
    
    target.generateBloch = generateBloch
    # target.generateBlochImgs = generateBlochImgs
    target.getBlochFN = getBlochFN

    target.beginSCMatrix = beginSCMatrix
    # ---These calls must be between the above and endSCMartix calls
    
    target.printIBDetails = printIBDetails
    target.getSCMatrix = getSCMatrix
    target.getEigen = getEigen
    target.getBeams = getBeams

    # ---These calls must be between the above and endSCMartix calls
    target.endSCMatrix = endSCMatrix

    return target