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

'''
    
from . import stem4d, send, ediom

from . import (E_INT, EM_INT,
               E_FLOAT, EM_FLOAT,
               E_DOUBLE, EM_DOUBLE,
               
               MAX_IMAGESIZE, MIN_IMAGESIZE, 
               MAX_IMAGESTACK, MIN_IMAGESTACK,
               DEF_FILTER_THRESHOLD, DEF_SEARCH_THRESHOLD,
               
               DEF_RMIN, DEF_BOXSIZE,
               DEF_CC, DEF_SIGMA, DEF_ICENTER, 
               DEF_XSCALE, DEF_TSCALE,
               
               E_SH,
               E_RAW,
               E_NPY,
               # imageloading mode
               EL_ONE, #STEM4D image loading only one particular stack
               EL_MORE #STEM4D image loading all stacks
            )
import numpy as np


from .errors import XDPImageError

from .display import normalizeImage, displayXImage

class StackImage():
    """

    Simple wrapper class for experimental images used in pyemaps 
    Stem4d analysis:
    
    - Diffraction pattern indexing
    - Annular Drak Field image generation
    - Masked images

    All image files must be of raw bitmap format, or known as headered raw format:

    - **Header**: stores metadata about the image, often including three numbers 
        for dimensions (e.g. width, height, and number of bit depth, or stacks).

    - **Data Offset**: After the header, the actual image or pixel data starts.

    - **Pixel Data**: Stored in a row-major order, meaning pixels are arranged 
        row-byrow across columns.
    
    
    The image can also be represented by a numpy array directly. In this case,
    the StackImage object created will ignore its file name member.

    and more to come.

    """
    def __init__(self, 
                 imgfn, 
                 nformat=E_SH,
                 ndtype = E_FLOAT,
                 dim = (MIN_IMAGESIZE,
                        MIN_IMAGESIZE,
                        MIN_IMAGESTACK),
                 noffset = 8):
        
        setattr(self, 'nformat', nformat)       # image file type
        setattr(self, 'fname', imgfn)           # image file name
        setattr(self, 'noffset', noffset)       # image header offset to image data
        setattr(self, 'ndtype', ndtype)         # image data offset
        setattr(self, 'dim', dim)               # dimension of the image

    @property
    def fname(self):
        """
        Experimental diffraction pattern image input file full path.
        In case of numpy array, this field is ignored.
        """
        return self._fname

    @property
    def nformat(self):
        """
        The type of the image file 

        - E_RAW: raw image files with image data at an `noffset` from the beginning of the file. 
        - E_SH: small header (pyemaps propietory). Header is a tuple of three short integers 
          and data type represented also by a short integer. Total bytes of the header or the offset
          is 8)
        - E_NPY: numpy array.

        """
        return self._nformat

    @property
    def ndtype(self):
        """
        The type of the image data - int, float, double are supported.
        The constants to used to represent the types are:

        - E_INT and EM_INT: single and multiple stack integral image data type.
        - E_FLOAT and EM_FLOAT: single and multiple stack real image data type.  
        - E_DOUBLE and EM_DOUBLE: single and multiple stack 8-byte real image data type. 
         
        """
        return self._ndtype

    @property
    def noffset(self):
        """
        
        image data offset from start of the file. Normally, it is the size of the 
        header in bytes.

        """
        return self._noffset

    @property
    def dim(self):
        """

        image dimension, support 3 dimensional images with input of 
        3 integer tuple of integers (width, height, stack).

        """
        return self._dim

    @property
    def data(self):
        """

        Raw image data in numpy ndarray when it is read from a numpy array
        Otherwise, the data will be generated from Stem4d when the input image
        file is loaded.

        """
        return self._data

    @fname.setter
    def fname(self, fn):
        if self._nformat != E_NPY:
            if not isinstance(fn, str) or len(fn) == 0:
                raise XDPImageError('Input image file name invalid')
        
        self._fname = fn

    @nformat.setter
    def nformat(self, fmt):
        if not isinstance(fmt, int):
            raise XDPImageError('Invalid image file type')
        
        if fmt != E_SH and fmt != E_RAW and fmt != E_NPY:
            raise XDPImageError("Unsuported image file type")

        self._nformat = fmt

    @ndtype.setter
    def ndtype(self, dty):
        if not isinstance(dty, int):
            raise XDPImageError('Invalid image data type')
        
        if dty != E_INT and dty != EM_INT and \
           dty != E_FLOAT and dty != EM_FLOAT and \
           dty != E_DOUBLE and dty != EM_DOUBLE:
            raise XDPImageError("Unsuported image data type")

        self._ndtype = dty

    @noffset.setter
    def noffset(self, offset):
        if not isinstance(offset, int):
            raise XDPImageError('Invalid image data offset')

        self._noffset = offset

    @dim.setter
    def dim(self, d):
        if not isinstance(d, tuple) or len(d) !=3 or \
            not all(isinstance(x, (int, float)) for x in d) or \
            d[0] < MIN_IMAGESIZE or d[1] < MIN_IMAGESIZE or d[2] < MIN_IMAGESTACK or \
            d[0] > MAX_IMAGESIZE or d[1] > MAX_IMAGESIZE or d[2] > MAX_IMAGESTACK:

            raise XDPImageError('Invalid image data offset')

        self._dim = d

    @data.setter
    def data(self, idata):
        if not isinstance(idata, np.ndarray()):
            raise XDPImageError('Raw image data must be an numpy array')

        self._data = idata

    def __del__(self):
        
        stem4d.freeStem4d()

    def loadImage(self, rmode= EL_ONE, stack = 1):
        """
        Loads image into stem4d module for analysis.
        """
        img_format = self.nformat
        if img_format != E_NPY and img_format != E_SH and img_format != E_RAW:
            raise XDPImageError("Invalid image file type")
        
        ximage = stem4d.cvar.ximg
        ret = -1
        if img_format == E_NPY:
            ret = ximage.setImage_from_numpy(self.data)

# load proprietory small header formatted image file

        if img_format == E_SH:
            ret = stem4d.loadXImage(self.fname, rmode = rmode, stack = stack)
# load raw image file            
        if img_format == E_RAW:
            ret = stem4d.loadRawImage(self.fname, 
                          self.offset, self.ndtype, 
                          self.dim[0], self.dim[1], self.dim[2], 
                          rmode = rmode, stack=stack)

        if ret != 0:
            raise XDPImageError("Failed to import the image into stem4d module")
        
        self._dim = (ximage.h.ncol,ximage.h.nrow,ximage.h.nlayer)
        self._data = ximage.getImageData(stack)

    def viewExpImage(self, peakDP = False, iStack=1, title = "", iShow = False):      
        """
        Helper function in stem4d module to display experimental diffraction database 
        diffraction pattern currently loaded.

        :param peakDP: kinematic diffraction with miller index. This parameter is only valid for EDIOM operations
        :type peakDP: Boolean, optional

        :param Indexed: show the kinematic patterns after indexing is completed.
        :type Indexed: boolean, optional, default to `False`

        :param iStack: Image stack number to show. For single stack image, this parameter takes default value of 1
        :type iStack: integer, optional, default to 1

        :param iShow: whether to show miller indexes
        :type iShow: boolean, optional, default to `False`
        
        :return:  
        :rtype: None
        
        This function is typically used to display experimental image after diffraction 
        patterns matched and indexed. It can also be used to display intermediate
        search results after peaks are found but before indexes are matched. The latter
        display is turned on only by *bDebug* flag in 
        `loadDPDB <pyemaps.crystals.html#pyemaps.crystals.Crystal.loadDPDB>`_ call.

        """
        
        xnc, xnr, nl = self._dim[0], self._dim[1], self._dim[2]
        
        if iStack < 1 or iStack > nl+1:
            print(f'The stack number of the image is invalid')
            return
        
        if self._data is None:
            print(f'Experimental image is not loaded or invalid')
            return
        
        try:
            yi = np.ascontiguousarray(self._data, 
                                      dtype=np.float32).reshape(xnc, xnr)
        except Exception as e:
            print("Error converting image data to numpy array")
            raise XDPImageError from e
        else:
            xkdisk = None
            if peakDP:
                nps = ediom.getExpImagePeaks()
                
                if nps <= 0:
                    print(f'Image is not indexed or indexing data is invalid')
                    return
                
                ret, xkdisk = ediom.getXKDif(nps+1)
                
                if ret != 0:
                    print(f'Python ----Failed to get diffraction patterns for the experimental image')
                    return ret
                
            displayXImage(yi, 
                          fsize=(xnc, xnr), 
                          iShow = iShow, 
                          ds = xkdisk,
                          suptitle = title)
    @staticmethod
    def showMatchedDBDP():        
        """
        Helper function in stem4d module to display diffraction database diffraction pattern 
        that best matches that of the experimental diffraction image pattern.

        This function is typically used to confirm its match with experimental diffraction 
        pattern. See sample code *al_ediom.py* for usage of this function.

        """
        nr, nc = MAX_IMAGESIZE, MAX_IMAGESIZE
        
        img1d = np.ascontiguousarray(np.zeros(shape=(nc,nr)), dtype=np.float32)
       
        nPeaks = ediom.DPGetCurrentImage(img1d)
        if nPeaks <=0:
            print(f'Python ----Failed to get selected database image')
            return -1

        if not normalizeImage(img1d):
            print("Python ----Error normalizing the image for display")
            return -1
       
        knum = nPeaks+1
        ret, kdisk = ediom.getDPListKDif(knum) 
        
        if ret != 0:
            print(f'Python ----Failed to get diffraction disks list')
            exit(1)
        displayXImage(img1d, 
                      fsize=(nc,nr), 
                      iShow=True, 
                      ds=kdisk,
                      suptitle = 'Matching Database Diffraction Pattern')
        
    staticmethod
    def displayFitImage(nr, nc):
        """
        Internal intermediate helper function for display fit images.
        """
       
        filen = nr*nc
        ret, fimg = ediom.getFitImage(filen)
        if ret != 0:
            print(f'Python ----Failed to get fit image')
            return ret
            
        displayXImage(fimg.reshape(nr, nc), fsize=(nr, nc))
        return 0 
    
    @staticmethod
    def displaySearchMask(nr, nc):    
        """
        Internal stem4d helper function displaying image mask image 
        generated in peak search.

        :return:  
        :rtype: None
        
        """
        len = nr*nc
        ret = 1


        ret, img1d = ediom.getXMask(len)

        if ret != 0 :
            print(f'Python ----Error getting current image slice')

        displayXImage(img1d.reshape((nr,nc)), fsize = (nr,nc), suptitle='Search Mask')
        return 0
    
    @staticmethod
    def displaySearchKernel(nr, nc):     
        """
        Internal stem4d helper function displaying image kernel image 
        generated in peak search.

        :return:  
        :rtype: None
        
        """
        len = nr*nc
        ret = -1


        ret, img1d = ediom.getXTemplateMask(len)

        if ret != 0 :
            print(f'Python ----Error getting current image slice')
            return -1
        
        displayXImage(img1d.reshape((nr,nc)), 
                      fsize = (nr,nc), 
                      isMask=True, 
                      suptitle = 'Search Kernel')
        return 0   
        
    @staticmethod
    def showDPDBMMask(mr, mc):

        """
        Internal function to display loaded DP database stereo projection map
        as explained in the following
        
        .. image:: https://github.com/emlab-solutions/imagepypy/raw/main/stereoprojectionmap.png
            :width: 75%
            :align: center

        """
        len = mr*mc
        
        mask = np.ascontiguousarray(np.zeros(len), dtype=np.short)
        
        ret= ediom.DPGetMask(mask)
        
        if ret != 0:
            print(f'Python ----Error getting the mask data')
            return -1

        displayXImage(mask.reshape(mr,mc), 
                        fsize =(mr, mc), 
                        isMask = True,
                        suptitle="Stereo Projection Map") 
    
    @staticmethod    
    def loadDPDB(dbfn, bShowDBMap=False):
        """
        Loads the diffraction database file *dbfn* into stem4d for diffraction peak searching and indexing.

        See sample code *si_dpgen.py* for how to generate a diffraction pattern database with
        pyemaps `generateDPDB <pyemaps.crystals.html#pyemaps.crystals.Crystal.generateDPDB>`_.

        The database file can also be saved and reused.

        :param dbfn: DP database file name.
        :type dbfn: string, required
        
        :param bShowDBMap: weather to display the stereodigram project map after successful 
                           loading of the database file

        :type bShowDBMap: boolean, optional, default to `False`

        :return: status code, stereo projection map dimension - two integers tuple 
        :rtype: tuple

        See the following for stereo projection map representing the DP database:
        
        .. image:: https://github.com/emlab-solutions/imagepypy/raw/main/stereoprojectionmap.png
           :width: 75%
           :align: center

        """
        # load DP database into stem4d and return database fitmap dimensions
        ret, mrow, mcol = ediom.readDPDB(dbfn)
        if ret != 0:            #need to replace this with stem4d return value
            print(f'Error loading image file')
            return ret, 0, 0

        print(f'Diffraction Database loaded successfully.')
        print(f'Dimension of stereo projection map: width ={mcol}, height={mrow}')
        
        if bShowDBMap:
            StackImage.showDPDBMMask(mrow, mcol)

        return ret, mrow, mcol
    
    @staticmethod
    def showMatchingIndexMap(fr, fc):
            
        """
        Helper function in stem4d module to display matching indexes map. The colored
        heat map with the peak indicates the orientation in which experimental and 
        database diffraction patterns best match.

        :param fr: stereo projection map height. This number is obtained from 
                   `loadDPDB <pyemaps.crystals.html#pyemaps.crystals.Crystal.loadDPDB>`_ call. 
        :type fr: int, required

        :param fc: stereo projection map width. This number is obtained from 
                   `loadDPDB <pyemaps.crystals.html#pyemaps.crystals.Crystal.loadDPDB>`_ call.
        :type: int, required

        :return: status code 
        :rtype: int
        
        """
        
        flen = fc*fr
        
        ret, fmask = ediom.getFitMap(flen)
        if ret != 0:
            print(f'Python ----Failed to get for map')
            return ret

        displayXImage(fmask.reshape(fr,fc), 
                      fsize =(fr, fc), 
                      isMask = True, 
                      bColor=True,
                      suptitle = 'Matching Index Map')
        
    def indexImage(self, 
                   dpdbfn,                    
                   cc                      = DEF_CC,
                   sigma                   = DEF_SIGMA,
                   img_center              = DEF_ICENTER,
                   rmin                    = DEF_RMIN,
                   search_box              = DEF_BOXSIZE,
                   scaling_option          = (DEF_XSCALE, DEF_TSCALE),
                   filter_threshold        = DEF_FILTER_THRESHOLD,
                   peak_threshold          = DEF_SEARCH_THRESHOLD,   
                   ssel                    = 1,    
                   bDebug                  = False
              ):
        """
        Searches and indexes an experimental diffraction image. The experimental diffraction image will be loaded
        with StackImage class constructor and its `loadImage <pyemaps.stackimg.html#pyemaps.stackimg.StackImage.loadImage>`_
        method before the search and indexes are performed.

        In addition, a diffraction database also needs to be loaded preceeding this call with
        `loadDPDB <pyemaps.crystals.html#pyemaps.crystals.Crystal.loadDPDB>`_ 

        :param dpdbfn: diffraction pattern database file name. The file is generated by pyemaps dp_gen module 
        or database file name saved from previous runs.
        :type dpdbfn: string, required
        
        :param cc: Camera constant in 1/Angstrom/pixel.
        :type cc: float, optional

        :param sigma: Diffraction peak width - estimated image peak width.
        :type sigma: float, optional.

        :param img_center: diffraction pattern center in (col, row) coordinate.
        :type img_center: float tuple, optional

        :param rmin: low cutoff radius for excluding center beam and diffuse intensities.
        :type rmin: float, optional

        :param search_box: Parameter in pixels used to define peak search. Recommended value 
                           of 3 to 4 times of sigma value for selected area diffraction.
        :type search_box: float, optional

        :param filter_threshold: Diffraction pattern screening threshold. Between 0.0 and 1.0 
                                 use 0 to include all database patterns for search.
        :type filter_threshold: float, optional

        :param peak_threshold: Peak threshold. value between 0.0 and 1.0. used to remove noisy peaks.
        :type peak_threshold: float, optional

        :param ssel: image stack selection. The value must be in range of the input image layers.
        :type ssel: integer, optional. Default value to 1, the first image layer in the input image stack.

        :param bDebug: debug option. This is for displaying intermediate searching and masking images used. 
        :type bDebug: Boolean, optional. Default value to `False`.

        :return: status code, 0 for successful run
        :rtype: integer

        
        The image control parameters cc - rmin above are image meaurements controls. The accuraccies
        of these measurements can greatly affect the peak search and eventually indexing results.

        The remaining input parameters directly control the search and indexing functions and its results.
        Use these parameters to tune your results.

        The following is a typical sequence of displays during the execution:

        1. Once the DP database is loaded successfully, the steoreo projection map associated
        with the DP database will be shown.
        
        .. image:: https://github.com/emlab-solutions/imagepypy/raw/main/stereoprojmap.png
            :width: 75%
            :align: center

        2. Successful experimental DP image importing will also show the image. This gives users
        the opportunity to verify the image:

        .. image:: https://github.com/emlab-solutions/imagepypy/raw/main/expimagoriginal.png
            :width: 75%
            :align: center

        3. Following the display of the experimental DP image and if *bDebug* is not set (by default), 
        the indexing result will be displayed on top of the experimental image:

        .. image:: https://github.com/emlab-solutions/imagepypy/raw/main/expimgindexed.png
            :width: 75%
            :align: center

        4. Once the indexing results are generated, users have the option to call more display
        *STEM4D* functions to show other results generated by this call. For examples, 
        the matching database DP image and DP database matching index map as shown below:

        .. image:: https://github.com/emlab-solutions/imagepypy/raw/main/matchingDPDB.png
            :width: 75%
            :align: center

        .. image:: https://github.com/emlab-solutions/imagepypy/raw/main/matchingindexmap.png
            :width: 75%
            :align: center

        The latter map presents the likely matching location  (in red) between the DP in database, 
        also considered the theoretical diffraction patterns, and the experimental DP image. 

        5. Finally, in addition to the above visual representation of the run and results, 
        more verbose results are also shown in standard output:

        .. code-block:: console

            Number of peaks found: 45

            -----------------Diffraction Pattern(DP) Indexing Results--------------------
            ***** DP stack loaded and indexed: 1
            ***** Best matching database DP: 1715
            ***** DP rotation angle: 284.191 (degrees)
            ***** Number of diffraction peaks indexed: 11
            ***** Experimental and database DP correlation maximum: 0.988308
            ***** Beam direction: 0.0575418 0.0599394 0.232559
            ***** Reliability index (> 5.0): 30.5407


            -----------------Indexed Diffraction Pattern Details------------------
            DP #   Miller Index     Distance            DP Loc          Intensity
                1     2    -2     0   18.805359  114.912613  109.021492   14.05505
                2    -2     2     0   20.888754   81.346603   87.833191  100.00000
                3     3     1    -1   22.201900   95.978333  120.995316   28.63353
                4    -1    -3     1   22.830843  117.979164   86.309898    9.12775
                5    -3    -1     1   23.202806  101.336617   75.915146   17.33628
                6     1     3    -1   23.803307   78.843224  111.661034   97.01090
                7     5    -1    -1   36.265705  112.098000  132.817802    2.99402
                8    -5     1     1   36.616173   85.120682   65.116249    4.92946
                9    -1     5    -1   36.805595   62.239502  100.821404   33.52511
                10   -4     4     0   39.269745   66.114388   77.537254   18.77301
                11    4     4    -2   42.499973   76.063011  134.779076    2.83128

        where Reliability index greater than 5.0 is considered successful run. DP stands for
        diffraction pattern. If your results do not fit in a run, adjusting search and indexing paramemers
        such as filter_threshold and peak threshold can also help stem4d module to search and match peaks.

        .. note::

            When *bDebug* flag is set (to 'True'), users are offered to chance to display more information of 
            stem4d's intermediate execution steps. For example, peak discovery step will show results
            of all found peaks by image peak matching algorithms before indexing is done. 
            These intermediate images are mainly for debugging purposes.

        """ 
        
        if scaling_option[0] < 0 or scaling_option[0] > 5:
            raise XDPImageError('Experimental scaling factor out of range')
        
        if scaling_option[1] < 0 or scaling_option[1] > 5:
            raise XDPImageError('Theoretical scaling factor out of range')
        
        soption = scaling_option[0] * 10 + scaling_option[1]
        if soption == 0:
             raise XDPImageError('Both scaling factors out of range')

        # loading theoretical diffraction image database 
        # generated from pyemaps dpgen module
        ret, mr, mc = StackImage.loadDPDB(dpdbfn, bShowDBMap=True)
        if ret != 0:
            raise XDPImageError("Error loading theoretical diffraction pattern datanase")
        
        try:
            self.loadImage(rmode = 1, stack = ssel) #indexing one stack image at a time
        except Exception as e:
            raise XDPImageError(f"Error loading image for stem4d analysis: {e}") from e
        
        # print(f'debug:experimental image depth: {self._dim}')
        self.viewExpImage(title='Experimental Diffraction Image - Indexed')

        edc = stem4d.cvar.edc
        
        # setting image control parameters
        edc.cc = cc
        edc.sigma = sigma

        # validate image center
        
        if img_center[0] < 0 or img_center[0] > self.dim[0] or \
            img_center[1] < 0 or img_center[1] >self.dim[1]:
            raise ValueError('Point of interest on Experimental image invalid')
        
        edc.set_center(img_center[0], img_center[1])

        # load stem4d control parameters with which the image is generated
        # and search and return search kernel dimensions
        ret, kc, kr = stem4d.prepareSearch(img_center[0], img_center[1], rmin)
        if ret != 0 or kc <= 0 or kr <= 0:
            print(f'Error preparing for experimental image peak search')
            return -1
        
        if bDebug:
            StackImage.displaySearchMask(self._dim[1], self._dim[0])
            StackImage.displaySearchKernel(kr, kc) 

        # Start peaks search...
        xpeaks = ediom.searchXPeaks(search_box, threshold=peak_threshold)

        if xpeaks == -1:
            print(f'Peaks search failed')
            return -1
        
        if xpeaks <= 3:
            print(f'Insufficient number of peaks found for indexing')
            return -1
        
        if bDebug:
            self.viewExpImage(peakDP=True, title = 'Experimental Diffraction Image', iShow = False)
        
        ret = ediom.indexXPeaks(rmin, soption, filter_threshold)
        
        if ret != 0:
            print(f'Error indexing experimental image for DP')
            return ret
        
        self.viewExpImage(peakDP=True, title = 'Experimental Diffraction Image - Indexed', iShow = True)

        StackImage.showMatchingIndexMap(mr,mc)
        
        print("\n")
        print("-----------------Indexed Diffraction Pattern Details------------------")

        print(f"""{'DP #':^7}{'Miller Index':^15}{'Distance':^15}{'DP Loc':^23}{'Intensity':^11}""")
    
        ediom.printIndexDetails()
        return 0
    
    def generateBDF(self,
                    center=(0.0, 0.0), 
                    rads = (0.0, 0.0),
                    scol = 0.0,
                    bShow=False):
        """
        This method generates an (Annular) Bright/Dark Field image from an experimental stack image.
        It is a wrapper for the function `getBDF`function in the new SEND module.

        :param center: The center of detector.
        :type center: tuple of floating point numbers

        :param rads: a pair of radius for inner and outer field detectors. 
         When the inner radius is set to zero, the resulting image will be either 
         Bright Field(BF) or Dark Field(DF) depending on if the center is on 
         the bright spot of the image or not. Otherwise, a positive inner radius
         will result in Annular Bright Field (ABF) or Annular Dark Field (ADF).
        :type rads: tuple, optional.

        :param scol: The size of the output image along column direction.
        :type scol: floating point numbers, optional

        :param bShow: whether to display the resulting image.
        :type bShow: boolean, optional, default `False`

        :return: (status code, image data), status code of 0 successful, otherwise failed
        :rtype: tuple of a short integer and image data array.

.. note::

        The experimental image loaded must have more than one stack.
        
        """
        if not isinstance(scol, (int, float)) or scol <= 0:
            print(f'The size of the output image along column direction must be numeral and positive')
            return -1, None
        
        if not isinstance(center, tuple) or len(center) !=2 or \
           not all(isinstance(x, (int, float)) for x in center):
            print(f'Invalid ADF detector center')
            return -2, None
        
        if not isinstance(rads, tuple) or len(rads) !=2 or \
           not all(isinstance(x, (int, float)) for x in rads) or \
           rads[0] == rads[1]:
            print(f'Invalid ADF detector inner and outer radius, it must be a pair of numerals')
            return -3, None
               
        try:
            self.loadImage(rmode = EL_MORE) 
        except Exception as e:
            print(f'Error loading the experimental image with message: {e}')
            return -4, None
    
        ret = send.getBDF(center[0], center[1], 
                           rads[0], rads[1], 
                           scol)
        if ret != 0:
            print(f'Failed to generate ADF image for experimental image {self.fname}')
            return -4, None
        
        adfimg = stem4d.cvar.ximg
        self._dim = (adfimg.h.ncol, adfimg.h.nrow, 1)
        self._data = adfimg.getImageData(1)

        if bShow:
            self.viewExpImage(title='Annular Dark or Bright Field Image' if rads[0] > 0.0 else \
                              'Dark or Bright Field Image')

        return 0, self._data
    
    def generateMaskedImage(self,
                   maskfn,
                   scancol = 0.0,
                   bShow=False):
        """
        generates an Bright Field(ADF) image from an experimental stack image input.
        and a mask image.

        :param maskfn: mask image file name. 
        :type maskfn: string, required
        
        :param scancol: The center of ADF detector. default value 0.0
        :type scancol: float

        :param bShow: whether to display the resulting ADF image.
        :type bShow: boolean, optional, default `False`

        :return: status code, 0 successful, otherwise failed
        :rtype: integer

        .. note::
        """
        if not isinstance(scancol, (int, float)) or scancol <= 0:
            print(f'The scancol input must be numeral and positive')
            return -1, None
        
        if not isinstance(maskfn, str) and maskfn.strip():
            print(f'The mask image file name must be string and not empty ')
            return -2, None
        
        try:
            self.loadImage(rmode = EL_MORE) 
        except Exception as e:
            return -4, None

        ret = send.getMaskedImage(maskfn, scancol)
        
        if ret != 0:
            print(f'Failed to generate masked image for experimental image {self.fname}')
            return -3, None
        
        maskedimg = stem4d.cvar.ximg
        self._dim = (maskedimg.h.ncol, maskedimg.h.nrow, 1)
        self._data = maskedimg.getImageData(1)

        if bShow:
            self.viewExpImage(title = "Experimental Diffraction Image - Masked")

        return 0, self._data
