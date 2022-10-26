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
                   DEF_KV, \
                   DEF_DSIZE_LIMITS
    from .. import BImgList, EMC, SIMC

    from ..fileutils import compose_ofn
    from .. import BlochError,BlochListError
    import numpy as np
    from numpy import asfortranarray as farray

    BIMG_EXT = '.im3'
    MAX_BIMGFN = 256

    def getbfilename(self):
        '''
        The file name of intended bloch image is constructed:
        1) if environment variavle PYEMAPS_HOME is set then
            the file will be in $PYEMAPS_HOME/bloch folder
        2) otherwise, the file will be save in current working directory
        3) The file name of the image will be composed as follows:
            <crystal_name>-<current_time>.im3
        4) The generated raw image file can be imported and viewed in 
            ImageJ and Gatan Digital Micrograph (GDM)
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
        
    def generateBlochImgs(self, *, aperture = DEF_APERTURE, 
                            omega = DEF_OMEGA,  
                            sampling = DEF_SAMPLING,
                            pix_size = 25,
                            det_size = DEF_DETSIZE,
                            disk_size = DEF_CBED_DSIZE,
                            sample_thickness = (200, 1000, 100),
                            em_controls = EMC(cl=200, 
                                              simc = SIMC(gmax=1.0, excitation=(0.3,1.0))),
                            bSave = False
                          ):
        
        th_start, th_end, th_step = sample_thickness

        if th_start > th_end or th_step <= 0:
            raise BlochListError('Sample thickness parameter invalid')               

        dep = (th_end-th_start) // th_step + 1
        if dep > MAX_DEPTH:
            raise BlochListError('Too many sample slices')

        dif.initcontrols()
        dif.setmode(2) # alway in CBED mode

        
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
            imgfn, bfn, l = self.getbfilename()
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
            print(f'Import the file into ImageJ or other tools to view images: ')

# ------- clean up ---------
        bloch.imgmemdelete()
        dif.diff_delete()

        return myBlochImgs

    @staticmethod
    def printIBDetails():
        '''
        print beams details after bloch scattering matrix run
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
        must follow scattering matrix run: generateSCMatrix().

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
        This method returns eigen values for given sample point.
        must be called between beginSCMatrix(...) and endSCMatrix().

        '''
        scmdim = bloch.get_scmdim(ib_coords)
        if scmdim <= 0:
            raise BlochError("Error finding corresponding scattering matrix, use printIBDetails to find potential input for ib_coords")
        
        ev, ret = bloch.geteigenvalues(ib_coords, scmdim)
        if ret < 0 or ret != scmdim:
            raise BlochError("failed to retrieve incidental beams info")
        
        return ev

    def beginSCMatrix(self, *, 
                        aperture = DEF_APERTURE, 
                        omega = DEF_OMEGA,  
                        sampling = DEF_SAMPLING,
                        disk_size = DEF_CBED_DSIZE,
                        rvec = (0.0,0.0,0.0),
                        thickness = 200,
                        em_controls = EMC(cl=200, 
                                          simc = SIMC(gmax=1.0, 
                                          excitation=(0.3,1.0))
                        )
                     ):
        '''
        This function begins to run dynamic diffraction simulation and prepare to retieve scattering matrix 
        with sampling point coordinates and sample thickness
        

        aperture = 1.0,                 #  Objective aperture
        omega = 10,                     #  Diagnization cutoff                            
        sampling = 8,                   #  Number of sampling points
        pix_size = 25,                  #  Detector pixel size in microns
        thickness = 200,                #  Sample thickness
        det_size = 512,                 #  Detector size (it's also resulting bloch image array dimension)
        disk_size = 0.16,               #  Diffraction disk rdius in 1/A\
        rvec = (0.0,0.0,0.0)            #  R vector shifting atom coordinates in crystal, 
                                        #  all components of R vector are floating numbers between 0.0 and 1.0
        Returns:                         
        A tuple (ns, s)                 #  ns = number of sampling points
                                           s = a list of sampling points in (x,y) coordiantes
        '''
        

        dif.initcontrols()
        dif.setmode(2) # alway in CBED mode

        dif.setdisksize(disk_size)
        
        # setting default simulation controls
        # print(f'simulation parameters: {em_controls.simc}')
        self.set_sim_controls(em_controls.simc)

        # Load crystal data to backend modules 
        self.load(rvec=rvec)
  
        tx, ty = em_controls.tilt
        dx, dy = em_controls.defl
        z = em_controls.zone
        # print(f'zone input from generateSCMatrix: {z}:{em_controls.zone}')
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
        # Crystal.printIBDetails()
        nsampling = bloch.get_nsampling()
        sampling_points, ret = bloch.get_samplingpoints(nsampling)

        if ret != 0:
            raise BlochError('Failed to retrive sampling points used in scattering matrix run')
        
        print(f'# of sampling points: {nsampling}')
        
        spoints = np.transpose(sampling_points)

        sp = [tuple(p) for p in spoints]
        print(f'List of sampling points: {sp}')
        return nsampling, sp


    @staticmethod
    def endSCMatrix():
        # freeing backend bloch module memory 
        bloch.cleanup()

    @staticmethod
    def getSCMatrix(ib_coords = (0,0)):
        '''
        This function retieves scattering matrix by sampling point coordinates,
        this call must be between:
        1) beginSCMatrix(...), and
        2) endSCMatrix() 
        All available input for ib_coords are output from beginSCMatrix call
        '''
        
        # get the dimension of the scm
        scmdim = bloch.get_scmdim(ib_coords)
        
        if scmdim <= 0:
            raise BlochError("Error finding corresponding scattering matrix,  to find potential input for ib_coords")

        scm, ret = bloch.getscm(ib_coords, scmdim)
        if ret <= 0:
            raise BlochError('Error retieving scattering matrix, input matrix dimention too small, use printIBDetails to find extact dimentsion')
        return np.transpose(scm)

    def generateBloch(self, *, aperture = DEF_APERTURE, 
                            omega = DEF_OMEGA,  
                            sampling = DEF_SAMPLING,
                            pix_size = 25,
                            det_size = DEF_DETSIZE,
                            disk_size = DEF_CBED_DSIZE,
                            thickness = 200,
                            em_controls = EMC(cl=200, 
                                              simc = SIMC(gmax=1.0, excitation=(0.3,1.0))
                                              )
                     ):
        '''
        aperture = 1.0,                 #  Objective aperture
        omega = 10,                     #  Diagnization cutoff                            
        sampling = 8,                   #  Number of sampling points
        pix_size = 25,                  #  Detector pixel size in microns
        thickness = 200,                #  Sample thickness
        det_size = 512,                 #  Detector size (it's also resulting bloch image array dimension)
        disk_size = 0.16,               #  Diffraction disk rdius in 1/A
        '''
                   
        dif.initcontrols()
        dif.setmode(2) # alway in CBED mode

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

        ret = bloch.dobloch(aperture,omega,sampling,0.0)
        
        if ret == 2:
            print('Contact support@emlabsoftware.com for how to register for ' +
            'a full and accelerated version of pyemaps')
            raise BlochError('Bloch computation resource limit reached')

        if ret != 0:
            raise BlochError('Error computing dynamic diffraction')

        #successful bloch runtime, then retreive bloch image
        # 
        #     
        ret = bloch.imagegen(thickness,0,pix_size,det_size)
        if(ret != 0):
            raise BlochError("bloch image generation failed!")

        raw_image = farray(np.zeros((det_size,det_size), dtype=np.double))
        bloch.get_rawimagedata(raw_image)
        bloch.imgmemdelete()
        dif.diff_delete()

        return em_controls, raw_image
    
    target.generateBloch = generateBloch
    target.generateBlochImgs = generateBlochImgs
    target.getbfilename = getbfilename

    target.beginSCMatrix = beginSCMatrix
    # These calls must be between the above and endSCMartix calls
    target.printIBDetails = printIBDetails
    target.getSCMatrix = getSCMatrix
    target.getEigen = getEigen
    target.getBeams = getBeams
    # These calls must be between the above and endSCMartix calls
    target.endSCMatrix = endSCMatrix

    return target