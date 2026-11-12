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
product_name = "pyEMAPS"
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

    
def _getDateTimeString():
    '''
    Helper function to create a unique name for the image file name.

    '''
    from datetime import datetime

    # Get the current date and time
    current_time = datetime.now()

    # Format the date-time string (up to seconds); no characters that Windows file names reject
    return current_time.strftime("%Y%m%d_%H%M%S")

class StackImage():
    """
    An experimental diffraction image, or a stack of them, for 4D-STEM analysis with the
    licensed stem4d module:

    - indexing a diffraction pattern against a database
      (:py:meth:`~pyemaps.stackimg.StackImage.indexImage`);
    - bright field, dark field and annular images
      (:py:meth:`~pyemaps.stackimg.StackImage.generateBDF`);
    - images from a detector mask
      (:py:meth:`~pyemaps.stackimg.StackImage.generateMaskedImage`).

    An image is read from a file or taken from a numpy array, depending on *nformat*:

    - ``E_SH``: pyEMAPS' own small-header format (``.im3``). The 8-byte header holds four
      short integers: the width, the height, the number of stacks and the data type.
    - ``E_RAW``: a headered raw file. The pixel data starts *noffset* bytes into the file,
      stored row by row, and you give the data type and dimensions yourself.
    - ``E_NPY``: a 2-D numpy array, set through the
      :py:attr:`~pyemaps.stackimg.StackImage.data` property. The file name is ignored.

    The image is read into the backend by :py:meth:`~pyemaps.stackimg.StackImage.loadImage`,
    or by the analysis methods, which load it themselves.

    Images are 100 to 512 pixels per side (``MIN_IMAGESIZE``, ``MAX_IMAGESIZE``), with 1 to
    5000 stacks (``MIN_IMAGESTACK``, ``MAX_IMAGESTACK``).
    """
    def __init__(self, 
                 imgfn, 
                 nformat=E_SH,
                 ndtype = E_FLOAT,
                 dim = (MIN_IMAGESIZE,
                        MIN_IMAGESIZE,
                        MIN_IMAGESTACK),
                 noffset = 8):

        """
        :param imgfn: path of the image file. Ignored for ``E_NPY``.
        :type imgfn: str
        :param nformat: the image format: ``E_SH`` (the default), ``E_RAW`` or ``E_NPY``.
        :type nformat: int, optional
        :param ndtype: the pixel data type, used for ``E_RAW`` files. Defaults to ``E_FLOAT``.
            See :py:attr:`~pyemaps.stackimg.StackImage.ndtype`.
        :type ndtype: int, optional
        :param dim: the image dimensions ``(width, height, stacks)``, used for ``E_RAW`` files.
            Defaults to ``(100, 100, 1)``.
        :type dim: tuple of int, optional
        :param noffset: where the pixel data starts in an ``E_RAW`` file, in bytes. Defaults to 8.
        :type noffset: int, optional
        :raise ~pyemaps.errors.XDPImageError: if a parameter is invalid.
        """
        self._data = None                       # current image data
        self._npdata = None                     # numpy input image (E_NPY)
        setattr(self, 'nformat', nformat)       # image file type
        setattr(self, 'fname', imgfn)           # image file name
        setattr(self, 'noffset', noffset)       # image header offset to image data
        setattr(self, 'ndtype', ndtype)         # image data offset
        setattr(self, 'dim', dim)               # dimension of the image

    @property
    def fname(self):
        """
        Path of the image file. Ignored when the format is ``E_NPY``.
        """
        return self._fname

    @property
    def nformat(self):
        """
        The image format:

        - ``E_SH``: pyEMAPS' small-header format. The header is 8 bytes: the width, the height,
          the number of stacks and the data type, each a short integer.
        - ``E_RAW``: a raw file whose pixel data starts
          :py:attr:`~pyemaps.stackimg.StackImage.noffset` bytes into the file.
        - ``E_NPY``: a numpy array, set through :py:attr:`~pyemaps.stackimg.StackImage.data`.
        """
        return self._nformat

    @property
    def ndtype(self):
        """
        The pixel data type of a raw image:

        - ``E_INT`` (single image) or ``EM_INT`` (stack): 2-byte integers.
        - ``E_FLOAT`` or ``EM_FLOAT``: 4-byte floating-point numbers.
        - ``E_DOUBLE`` or ``EM_DOUBLE``: 8-byte floating-point numbers.
        """
        return self._ndtype

    @property
    def noffset(self):
        """
        Where the pixel data starts in a raw file, in bytes: usually the size of the file's
        header.
        """
        return self._noffset

    @property
    def dim(self):
        """
        The image dimensions ``(width, height, stacks)``. Width and height are 100 to 512 pixels,
        and there can be 1 to 5000 stacks. Loading an image replaces them with the loaded image's
        dimensions.
        """
        return self._dim

    @property
    def data(self):
        """
        The image data, as a numpy array.

        After :py:meth:`~pyemaps.stackimg.StackImage.loadImage`, it holds the loaded image; after
        :py:meth:`~pyemaps.stackimg.StackImage.generateBDF` or
        :py:meth:`~pyemaps.stackimg.StackImage.generateMaskedImage`, the generated image.

        With the format set to ``E_NPY``, set it to a 2-D numpy array of any boolean, integer or
        floating-point type, 100 to 512 pixels per side, before calling
        :py:meth:`~pyemaps.stackimg.StackImage.loadImage`. It's converted to float32 when loaded.
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

            raise XDPImageError(f'Image dimensions must be (width, height, stacks), with width and height '
                                f'from {MIN_IMAGESIZE} to {MAX_IMAGESIZE} pixels and {MIN_IMAGESTACK} to '
                                f'{MAX_IMAGESTACK} stacks')

        self._dim = d

    @data.setter
    def data(self, idata):
        if not isinstance(idata, np.ndarray):
            raise XDPImageError('Raw image data must be a numpy array')

        # loadImage reads the input from _npdata; _data is replaced by
        # whichever image is loaded or generated later
        self._npdata = idata
        self._data = idata

    def __del__(self):
        # At interpreter exit, the stem4d extension module can be torn down
        # before this object, leaving freeStem4d as None. The process is ending
        # then, so there is nothing left to free.
        free = getattr(stem4d, 'freeStem4d', None)
        if callable(free):
            free()

    def loadImage(self, rmode= EL_ONE, stack = 1):
        """
        Read the image into the stem4d backend for analysis. The image's
        :py:attr:`~pyemaps.stackimg.StackImage.dim` and
        :py:attr:`~pyemaps.stackimg.StackImage.data` are then updated from the loaded image.

        :param rmode: ``EL_ONE`` (the default) to read one stack, or ``EL_MORE`` to read them all.
        :type rmode: int, optional
        :param stack: which stack to read with ``EL_ONE``, counting from 1.
        :type stack: int, optional
        :raise ~pyemaps.errors.XDPImageError: if the image can't be loaded, for example because the
            file is missing or invalid, a numpy image is missing or invalid, or no valid license is
            found. A license problem is also explained in a printed message.
        """
        img_format = self.nformat
        if img_format != E_NPY and img_format != E_SH and img_format != E_RAW:
            raise XDPImageError("Invalid image file type")
        
        ximage = stem4d.cvar.ximg
        ret = -1
        if img_format == E_NPY:
            if self._npdata is None:
                raise XDPImageError("No image data: set the data property to a 2-D numpy array before loading")
            try:
                ret = ximage.setImage_from_numpy(self._npdata)
            except (TypeError, ValueError, MemoryError) as e:
                raise XDPImageError(f"Invalid numpy image: {e}") from e

        # load proprietory small header formatted image file
        if img_format == E_SH:
            ret = stem4d.loadXImage(self.fname, rmode = rmode, stack = stack)
                
        # load raw image file            
        if img_format == E_RAW:
            ret = stem4d.loadRawImage(self.fname, 
                          self.noffset, self.ndtype, 
                          self.dim[0], self.dim[1], self.dim[2], 
                          rmode = rmode, stack=stack)
            
        # spell out license issues here before bailing out
        if ret == stem4d.LICENSE_EXPIRED:
            print(f"Your {product_name} license has expired. ")
            print("Upgrade your license by purchasing a full license token by contacting support@emlabsoftware.com.")
            print("Contact support@emlabsoftware.com if you think you have a valid license and the problem persists.")
        elif ret == stem4d.LICENSE_NONEXISTENT:
            print(f"Fail to find {product_name} license.")
            print("Contact support@emlabsoftware.com if you think you have a valid license and the problem persists.")
            print(f"Run \"pyemaps -l trial\" to obtain a free 7-day trial {product_name} license.")
            print(f"Or, contact support@emlabsoftware.com to purchase a {product_name} license activation token.")
        elif ret == stem4d.LICENSE_OTHERS:
            print(f'Unknown error retrieving {product_name} license info!')
            print(f'If persists, contact support@emlabsoftware.com')

        if ret != 0:
            raise XDPImageError("Failed to import the image into pyEMAPS")
        
        self._dim = (ximage.h.ncol,ximage.h.nrow,ximage.h.nlayer)
        self._data = ximage.getImageData(stack)

    def viewExpImage(self, peakDP = False, iStack=1, title = "", iShow = False):      
        """
        Display the loaded image. After indexing, it can also draw the indexed diffraction
        peaks on top of it.

        :param peakDP: draw the diffraction peaks found by the last peak search or indexing.
        :type peakDP: bool, optional
        :param iStack: the stack number. It's only checked against the number of stacks: the image
            shown is the one in :py:attr:`~pyemaps.stackimg.StackImage.data`.
        :type iStack: int, optional
        :param title: the figure title.
        :type title: str, optional
        :param iShow: label the peaks with their Miller indices.
        :type iShow: bool, optional
        :raise ~pyemaps.errors.XDPImageError: if the image data can't be converted for display.

        If no image is loaded, or there are no peaks to draw, it prints a message and shows
        nothing.
        """
        
        xnc, xnr, nl = self._dim[0], self._dim[1], self._dim[2]
        
        if iStack < 1 or iStack > nl:
            print(f'The stack number of the image is invalid')
            return
        
        if self._data is None:
            print(f'Experimental image is not loaded or invalid')
            return
        
        try:
            yi = np.ascontiguousarray(self._data, 
                                      dtype=np.float32).reshape(xnr, xnc)
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
                          fsize=(xnr, xnc),  
                          iShow = iShow, 
                          ds = xkdisk,
                          suptitle = title)
    @staticmethod
    def showMatchedDBDP():        
        """
        Display the database diffraction pattern that best matches the experimental pattern in
        the last :py:meth:`~pyemaps.stackimg.StackImage.indexImage` call, with its diffraction
        peaks marked. Use it to check the match. See the sample ``al_ediom.py``.

        :return: -1 if the pattern can't be retrieved or displayed.
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
            return -1
        displayXImage(img1d, 
                      fsize=(nc,nr), 
                      iShow=True, 
                      ds=kdisk,
                      suptitle = 'Matching Database Diffraction Pattern')
        return 0
        
    @staticmethod
    def displayFitImage(nr, nc):
        """
        Display the fit image from peak search. Used internally for debugging.

        :param nr: number of rows in the image.
        :type nr: int
        :param nc: number of columns in the image.
        :type nc: int
        :return: 0 on success, otherwise the error code.
        :rtype: int
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
        Display the mask used in the peak search. Shown by
        :py:meth:`~pyemaps.stackimg.StackImage.indexImage` when *bDebug* is set.

        :param nr: number of rows in the mask.
        :type nr: int
        :param nc: number of columns in the mask.
        :type nc: int
        :return: 0.
        :rtype: int
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
        Display the kernel used in the peak search. Shown by
        :py:meth:`~pyemaps.stackimg.StackImage.indexImage` when *bDebug* is set.

        :param nr: number of rows in the kernel.
        :type nr: int
        :param nc: number of columns in the kernel.
        :type nc: int
        :return: 0 on success, -1 if the kernel can't be retrieved.
        :rtype: int
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
        Display the stereographic projection map of the loaded diffraction pattern database.
        Each point on the map is an orientation with a pattern in the database:

        .. image:: https://github.com/emlab-solutions/imagepypy/raw/main/stereoprojectionmap.png
            :width: 75%
            :align: center

        :param mr: the map's height, from :py:meth:`~pyemaps.stackimg.StackImage.loadDPDB`.
        :type mr: int
        :param mc: the map's width, from :py:meth:`~pyemaps.stackimg.StackImage.loadDPDB`.
        :type mc: int
        :return: -1 if the map can't be retrieved.
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
        Load a diffraction pattern database file into stem4d, for peak search and indexing.

        Create the database with :py:meth:`~pyemaps.crystals.Crystal.generateDPDB`; see the sample
        ``al_dpgen.py``. A database file can be kept and reused.

        :param dbfn: path of the database file.
        :type dbfn: str
        :param bShowDBMap: display the database's stereographic projection map after loading it.
        :type bShowDBMap: bool, optional
        :return: ``(code, height, width)``: 0 on success, and the height and width of the
            stereographic projection map. On failure, the code isn't 0 and both sizes are 0.
        :rtype: tuple

        The stereographic projection map represents the database: each point is an orientation
        with a pattern in it.

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
        Display the matching index map from the last
        :py:meth:`~pyemaps.stackimg.StackImage.indexImage` call: a heat map over the database's
        stereographic projection map. Its peak marks the orientation where the experimental and
        database patterns match best.

        :param fr: the map's height, from :py:meth:`~pyemaps.stackimg.StackImage.loadDPDB`.
        :type fr: int
        :param fc: the map's width, from :py:meth:`~pyemaps.stackimg.StackImage.loadDPDB`.
        :type fc: int
        :return: the error code if the map can't be retrieved, otherwise ``None``.
        """
        
        flen = fc*fr
        
        ret, fmask = ediom.getFitMap(flen)
        if ret != 0:
            print(f'Python ----Failed to get fit map')
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
        Find the diffraction peaks in the experimental image and index them against a diffraction
        pattern database. This is a licensed feature.

        The method loads the database and the image itself, one stack at a time. The database is
        made by :py:meth:`~pyemaps.crystals.Crystal.generateDPDB`; see the samples ``al_dpgen.py``
        and ``al_ediom.py``.

        :param dpdbfn: path of the diffraction pattern database file.
        :type dpdbfn: str
        :param cc: camera constant, in pixels per 1/Å.
        :type cc: float, optional
        :param sigma: estimated width of the diffraction peaks, in pixels.
        :type sigma: float, optional
        :param img_center: center of the diffraction pattern ``(column, row)``, in pixels.
        :type img_center: tuple of float, optional
        :param rmin: radius around the center, in pixels, excluded from the search. It removes the
            central beam and the diffuse intensity around it.
        :type rmin: float, optional
        :param search_box: size of the peak search box, in pixels. For selected area diffraction,
            3 to 4 times *sigma* is recommended.
        :type search_box: float, optional
        :param scaling_option: how the experimental and the database pattern intensities are scaled
            for matching: two integers, each 0 to 5, not both 0.
        :type scaling_option: tuple of int, optional
        :param filter_threshold: screening threshold for the database patterns, from 0.0 to 1.0. Use
            0 to search all of them.
        :type filter_threshold: float, optional
        :param peak_threshold: peak threshold, from 0.0 to 1.0, used to drop noisy peaks.
        :type peak_threshold: float, optional
        :param ssel: the stack to index, counting from 1.
        :type ssel: int, optional
        :param bDebug: also display the intermediate images: the search mask and kernel, and the
            peaks found before indexing.
        :type bDebug: bool, optional
        :return: 0 on success. -1, or the backend's error code, if the peak search or the indexing
            fails; fewer than four peaks found counts as a failure.
        :rtype: int
        :raise ~pyemaps.errors.XDPImageError: if *scaling_option* is out of range, or the database or
            the image can't be loaded.
        :raise ValueError: if *img_center* is outside the image.

        The image measurements, *cc* to *rmin*, need to be accurate: errors in them can spoil the
        peak search and the indexing. The remaining parameters tune the search and the indexing.

        A typical run displays:

        1. The stereographic projection map of the database, once it's loaded:

           .. image:: https://github.com/emlab-solutions/imagepypy/raw/main/stereoprojmap.png
               :width: 75%
               :align: center

        2. The experimental image, once it's loaded, so you can check it:

           .. image:: https://github.com/emlab-solutions/imagepypy/raw/main/expimagoriginal.png
               :width: 75%
               :align: center

        3. The indexing result, drawn on the experimental image:

           .. image:: https://github.com/emlab-solutions/imagepypy/raw/main/expimgindexed.png
               :width: 75%
               :align: center

        4. The matching index map
           (:py:meth:`~pyemaps.stackimg.StackImage.showMatchingIndexMap`). The best match between
           the database patterns and the experimental pattern is in red:

           .. image:: https://github.com/emlab-solutions/imagepypy/raw/main/matchingindexmap.png
               :width: 75%
               :align: center

           Afterwards, :py:meth:`~pyemaps.stackimg.StackImage.showMatchedDBDP` displays the best
           matching database pattern:

           .. image:: https://github.com/emlab-solutions/imagepypy/raw/main/matchingDPDB.png
               :width: 75%
               :align: center

        5. The results, printed to standard output:

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

        A reliability index above 5.0 means the indexing succeeded. If it doesn't, try adjusting
        *filter_threshold* and *peak_threshold*.
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
        
        self.viewExpImage(title='Experimental Diffraction Image - input')

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
        Generate a bright field (BF), dark field (DF), annular bright field (ABF) or annular
        dark field (ADF) image from a 4D-STEM image stack, with a virtual detector. Each stack is
        the diffraction pattern at one scan position. This is a licensed feature; see the sample
        ``adf.py``.

        :param center: center of the detector ``(column, row)``, in pixels of the diffraction
            patterns.
        :type center: tuple of float, optional
        :param rads: inner and outer radius of the detector, in pixels; they must differ. An inner
            radius of 0 gives a bright field image if the detector covers the central beam, or a
            dark field image if it doesn't. A positive inner radius gives an annular bright or dark
            field image.
        :type rads: tuple of float, optional
        :param scol: number of scan positions per row: the width of the output image. The number of
            stacks must be a multiple of it.
        :type scol: int or float
        :param bShow: display the image.
        :type bShow: bool, optional
        :return: ``(code, data)``. The code is 0 on success, and *data* is the image as a numpy
            array, also stored in :py:attr:`~pyemaps.stackimg.StackImage.data`. On failure, the code
            is negative, *data* is ``None`` and a message is printed.
        :rtype: tuple

        .. note::

            The image must have more than one stack. All stacks are loaded.
        """
        if not isinstance(scol, (int, float)) or scol <= 0:
            print(f'The size of the output image along column direction must be numeral and positive')
            return -1, None
        
        if not isinstance(center, tuple) or len(center) !=2 or \
           not all(isinstance(x, (int, float)) for x in center):
            print(f'Invalid annular dark or bright field detector center')
            return -2, None
        
        if not isinstance(rads, tuple) or len(rads) !=2 or \
           not all(isinstance(x, (int, float)) for x in rads) or \
           rads[0] == rads[1]:
            print(f'Invalid annular dark or bright field detector inner and outer radius, it must be a pair of numerals')
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
            print(f'Failed to generate annular dark or bright field image for experimental image {self.fname}')
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
        Generate an image from a 4D-STEM image stack with a detector mask: each pixel of the
        output is the sum of the masked pixels in one stack. This is a licensed feature; see the
        sample ``adf.py``.

        :param maskfn: path of the mask, an image file in pyEMAPS' small-header format, with the
            same width and height as the stacks, and integer or float data. Pixels above 0.5 are
            included. To convert a raw mask file, use
            :py:meth:`~pyemaps.stackimg.StackImage.convertImage`.
        :type maskfn: str
        :param scancol: number of scan positions per row: the width of the output image. The number
            of stacks must be a multiple of it.
        :type scancol: int or float
        :param bShow: display the image.
        :type bShow: bool, optional
        :return: ``(code, data)``. The code is 0 on success, and *data* is the image as a numpy
            array, also stored in :py:attr:`~pyemaps.stackimg.StackImage.data`. On failure, the code
            is negative and *data* is ``None``.
        :rtype: tuple
        """
        if not isinstance(scancol, (int, float)) or scancol <= 0:
            print(f'The scancol input must be numeral and positive')
            return -1, None
        
        if not isinstance(maskfn, str) or not maskfn.strip():
            print(f'The mask image file name must be string and not empty ')
            return -2, None
        
        try:
            self.loadImage(rmode = EL_MORE)
        except Exception as e:
            print(f'Error loading the experimental image with message: {e}')
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
    

    @staticmethod
    def convertImage(
                imgfn,
                nformat=E_RAW,
                ndtype = E_FLOAT,
                dim = (MIN_IMAGESIZE,
                        MIN_IMAGESIZE,
                        MIN_IMAGESTACK),
                noffset = 8):
        """
        Convert a raw image file, or a numpy image, to pyEMAPS' small-header format (``.im3``).

        The stem4d module needs auxiliary images, such as the masks for
        :py:meth:`~pyemaps.stackimg.StackImage.generateMaskedImage`, in this format. See the sample
        ``convert_image.py``.

        :param imgfn: path of the raw image file, or with ``nformat=E_NPY``, the image as a 2-D
            numpy array.
        :type imgfn: str or numpy.ndarray
        :param nformat: the input format: ``E_RAW`` (the default) or ``E_NPY``.
        :type nformat: int, optional
        :param ndtype: the pixel data type of a raw file. Defaults to ``E_FLOAT``. See
            :py:attr:`~pyemaps.stackimg.StackImage.ndtype`.
        :type ndtype: int, optional
        :param dim: the dimensions ``(width, height, stacks)`` of a raw file. Defaults to
            ``(100, 100, 1)``.
        :type dim: tuple of int, optional
        :param noffset: where the pixel data starts in a raw file, in bytes. Defaults to 8.
        :type noffset: int, optional
        :return: the path of the converted file.
        :rtype: str
        :raise ValueError: if *nformat* isn't ``E_RAW`` or ``E_NPY``, the file name is invalid, or
            the numpy image isn't a numpy array.
        :raise FileNotFoundError: if the file isn't found.
        :raise ~pyemaps.errors.XDPImageError: if the image can't be loaded or saved.

        A file name without a folder is looked for in the folder set by the ``PYEMAPS_DATA``
        environment variable, or else in the current working directory.

        The output is saved in a ``sh_converted`` folder next to the input file, with the same name
        and the extension ``.im3``. A numpy image is saved in a ``sh_converted`` folder in the
        ``PYEMAPS_DATA`` folder, or else in the current working directory, named
        ``numpy_image_`` followed by the date and time. That folder must be writable.
        """
        import os

        if nformat != E_RAW and nformat != E_NPY:
            raise ValueError('pyEmaps only converts raw and numpy images to its proprietory format.')

        oExt = '.im3'

        if nformat == E_NPY:
            if not isinstance(imgfn, np.ndarray):
                raise ValueError('A numpy image must be given as a numpy array')

            idir = os.environ.get('PYEMAPS_DATA') or os.getcwd()
            iname = "numpy_image_" + _getDateTimeString()
            source = 'numpy image'
            img = StackImage('', nformat=E_NPY)
            img.data = imgfn

        else:
            if not isinstance(imgfn, str) or not imgfn:
                raise ValueError("Input image file error!")

            # first, split the image path
            idir, ifile = os.path.split(imgfn)

            if not ifile:
                raise ValueError("Input image file error!")

            if not idir:
                idir = os.environ.get('PYEMAPS_DATA') or os.getcwd()

            imgFile = os.path.join(idir, ifile)
            if not os.path.exists(imgFile):
                raise FileNotFoundError("Input image file not found!")

            iname, inxt = os.path.splitext(ifile)

            if not iname or not inxt:
                raise ValueError('Input file name error!')

            source = f'image file {imgFile}'
            img = StackImage(imgFile,
                            nformat=nformat,
                            ndtype = ndtype,
                            dim = dim,
                            noffset = noffset)

        odir = os.path.join(idir, 'sh_converted')

        os.makedirs(odir, exist_ok=True)
        oImageFn = os.path.join(odir, f"{iname}{oExt}")

        try:
            img.loadImage()
            ret = stem4d.saveImage(oImageFn)
        except XDPImageError:
            raise
        except Exception as e:
            raise XDPImageError(f'Error converting the {source} to pyEMAPS image format: {e}') from e

        if ret != 0:
            raise XDPImageError(f'Error saving the {source} as {oImageFn}')

        print(f"The {source} was successfully converted to pyEMAPS image format and saved as {oImageFn}")
        return oImageFn
