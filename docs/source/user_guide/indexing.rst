4D-STEM pattern indexing
========================

Electron diffraction pattern (DP) indexing uses template matching: it compares an acquired DP
with the patterns in a database that pyEMAPS' DPGEN module generates. The crystal orientation
and phase come from the database pattern that fits best. This feature requires
:ref:`License Activation`.

First, generate a DP database for the crystal, here Aluminium:

.. code-block:: python

   from pyemaps import EMC, Crystal, StackImage

   aluminium = Crystal.from_builtin('Aluminium')
   ret, db_file = aluminium.generateDPDB(emc=EMC(zone=(0, 0, 1)), res=200, xa=(2, 0, 0))

*ret* is 0 on success, and *db_file* is the database file name.An optional *vertices* argument,
an array of 3 or 4 zone axis indexes, encloses the orientation area within which the
diffraction patterns are generated. For details, see
:py:obj:`generateDPDB <pyemaps.crystals.Crystal.generateDPDB>`.

Then load the experimental image and index it against the database. *indexImage* loads the
database itself. *al.img* is a sample experimental image that ships with pyEMAPS:
``pyemaps -cp samples`` copies it, with the sample scripts, into a *pyemaps_samples* folder in the
current directory (see :doc:`../examples`). Run the example from that folder.

.. code-block:: python

   image = StackImage('al.img')
   image.indexImage(db_file,
                    cc=29.0,                       # camera constant, pixels per 1/Å
                    sigma=3.0,                     # estimated peak width, in pixels
                    img_center=(99.923, 99.919),   # pattern center, in pixels
                    rmin=10,                       # radius excluded around the center
                    search_box=10.0,               # peak search box size, in pixels
                    scaling_option=(1, 2),         # intensity scaling for matching
                    filter_threshold=0.0,          # 0 searches every database pattern
                    peak_threshold=0.8)            # drops noisy peaks

   StackImage.showMatchedDBDP()

*indexImage* prints the indexed diffraction beams, and *showMatchedDBDP* shows the database
pattern that best matches the image. For all the parameters, see
:py:obj:`StackImage.indexImage <pyemaps.stackimg.StackImage.indexImage>`. The *al_ediom.py*
sample runs this whole example.

Images from microscopes and detectors
-------------------------------------

pyEMAPS reads experimental patterns from the files microscopes and detectors write, through
`RosettaSciIO <https://hyperspy.org/rosettasciio/>`_, HyperSpy's file reading library. Install
it with pyEMAPS' ``io`` extra:

.. code-block:: console

   pip install "pyemaps[io]"

The formats include Gatan DigitalMicrograph (``.dm3``, ``.dm4``), Quantum Detectors Merlin
(``.mib``), TIFF, Velox and NCEM EMD (``.emd``), TIA (``.ser``, ``.emi``), MRC (``.mrc``,
``.mrcz``), TopSpin (``.app5``), Dectris Arina (``.h5``), TVIPS (``.tvips``) and HyperSpy
(``.hspy``, ``.zspy``). :py:func:`pyemaps.image_readers <pyemaps.expimage.image_readers>` lists them all. On Python 3.15, the
formats stored in HDF5 or Zarr (EMD, Arina, TopSpin, HyperSpy) wait for their libraries' Python
3.15 releases; the others work.

:py:meth:`StackImage.from_file <pyemaps.stackimg.StackImage.from_file>` creates an image from
such a file, ready for indexing or for bright and dark field imaging:

.. code-block:: python

   from pyemaps import StackImage

   pattern = StackImage.from_file('pattern.dm4')
   pattern.indexImage(db_file, cc=29.0, img_center=(256.0, 256.0))

   scan = StackImage.from_file('scan.mib')
   ret, bf = scan.generateBDF(center=(128.0, 128.0), rads=(0.0, 20.0))   # scan width from the file

The 4D-STEM features take patterns of 100 to 512 pixels per side and up to 5000 patterns.
pyEMAPS doesn't shrink larger data for you; it says what to ask for:

- *binning* averages square blocks of pixels: ``binning=2`` turns 1024 x 1024 patterns into
  512 x 512. Divide the camera constant *cc* and the pattern center *img_center* you give
  *indexImage* by the same factor.
- *scan_roi* reads part of a scan: ``scan_roi=(row, column, rows, columns)`` for a 2-D scan,
  ``(first, count)`` for a series of patterns.

.. code-block:: python

   scan = StackImage.from_file('big_scan.mib', binning=2, scan_roi=(0, 0, 64, 64))

To keep a converted copy, for repeated use or as a mask for
:py:meth:`generateMaskedImage <pyemaps.stackimg.StackImage.generateMaskedImage>`,
:py:meth:`convertImage <pyemaps.stackimg.StackImage.convertImage>` with ``nformat=E_RSCIIO``
writes pyEMAPS' ``.im3`` format.

Reading needs no license. :py:func:`pyemaps.read_image <pyemaps.expimage.read_image>` returns the patterns as numpy arrays,
with the scan shape and the file's calibration, to look at or to use in your own code:

.. code-block:: python

   import matplotlib.pyplot as plt
   from pyemaps import read_image

   img = read_image('scan.mib')
   print(img)              # patterns, size, scan shape and reader
   print(img.axes)         # calibration of the pattern axes, from the file
   plt.imshow(img.data[0], cmap='gray')
   plt.show()

.. note::

   Diffraction pattern indexing supports crystals of any crystal system, with these limits:

   1. Experimental images must be 100 to 512 pixels in each dimension. Read larger ones with
      *binning*, as above.
   2. The database resolution (*res* in *generateDPDB*) can be 100 to 500 sampling points.

   We appreciate any comments and suggestions to improve this feature. Contact us at
   support@emlabsoftware.com.
