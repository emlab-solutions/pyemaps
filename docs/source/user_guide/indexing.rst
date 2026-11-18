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

Images from TIFF files
----------------------

pyEMAPS reads experimental patterns from TIFF files (``.tif``, ``.tiff``) itself, with no
other package: a single pattern, or a multi-page stack such as a 4D-STEM scan, one pattern per
page. Most microscope and detector software can save TIFF, and so can ImageJ and Fiji.

- Pixels: 8 to 64-bit integers, or 16 to 64-bit floating point, in either byte order.
- Compression: none, LZW, Deflate (zip) or PackBits. Large stacks read fastest uncompressed or
  with Deflate; LZW is decoded in Python, at a few MB per second.
- BigTIFF files, and ImageJ stacks over 4 GB.
- Colour, palette and black-and-white images, and other compressions such as JPEG, are refused
  with a message that says what the file holds.

:py:meth:`StackImage.from_file <pyemaps.stackimg.StackImage.from_file>` creates an image from
a TIFF file, ready for indexing or for bright and dark field imaging:

.. code-block:: python

   from pyemaps import StackImage

   pattern = StackImage.from_file('pattern.tif')
   pattern.indexImage(db_file, cc=29.0, img_center=(256.0, 256.0))

   scan = StackImage.from_file('scan.tif', scan_shape=(64, 64))
   ret, bf = scan.generateBDF(center=(128.0, 128.0), rads=(0.0, 20.0))   # scan width 64

A multi-page TIFF holds the patterns one after another, in scan order. When tifffile wrote the
file, it recorded the scan's shape, and pyEMAPS uses it. Otherwise, as for ImageJ stacks, give
it with *scan_shape*, or give the scan width to the imaging methods (*scol*, *scancol*).

The 4D-STEM features take patterns of 100 to 512 pixels per side and up to 5000 patterns.
pyEMAPS doesn't shrink larger data for you; it says what to ask for:

- *binning* averages square blocks of pixels: ``binning=2`` turns 1024 x 1024 patterns into
  512 x 512. Divide the camera constant *cc* and the pattern center *img_center* you give
  *indexImage* by the same factor.
- *scan_roi* reads part of a scan, and only that part of the file: ``scan_roi=(row, column,
  rows, columns)`` for a 2-D scan, ``(first, count)`` for a series of patterns.

.. code-block:: python

   scan = StackImage.from_file('big_scan.tif', scan_shape=(256, 256), binning=2,
                               scan_roi=(0, 0, 64, 64))

To keep a converted copy, for repeated use or as a mask for
:py:meth:`generateMaskedImage <pyemaps.stackimg.StackImage.generateMaskedImage>`,
:py:meth:`convertImage <pyemaps.stackimg.StackImage.convertImage>` with ``nformat=E_FILE``
writes pyEMAPS' ``.im3`` format.

Reading needs no license. :py:func:`pyemaps.read_image <pyemaps.expimage.read_image>` returns
the patterns as numpy arrays, with the scan shape and the file's metadata, to look at or to use
in your own code:

.. code-block:: python

   import matplotlib.pyplot as plt
   from pyemaps import read_image

   img = read_image('scan.tif')
   print(img)              # patterns, size, scan shape and reader
   print(img.metadata)     # the TIFF's description, software, compression ...
   plt.imshow(img.data[0], cmap='gray')
   plt.show()

Images from DigitalMicrograph files
-----------------------------------

pyEMAPS reads Gatan DigitalMicrograph files (``.dm3``, ``.dm4``) itself, with no other package:
the files that microscopes with Gatan cameras save, on JEOL, Thermo Fisher and other
instruments. It reads single patterns, stacks and 4D-STEM datacubes, in 8 to 32-bit integers
or 32 and 64-bit floats.

- A stack that DigitalMicrograph recorded as a 4D-STEM scan gets its scan shape from Gatan's
  scan tags, so the imaging methods know the scan width.
- :py:attr:`axes <pyemaps.expimage.ExperimentalImage.axes>` gives each pattern axis'
  calibration, such as 1/nm per pixel, and
  :py:attr:`metadata <pyemaps.expimage.ExperimentalImage.metadata>` the high voltage
  (``high_voltage_kV``) and camera length (``camera_length_mm``) DigitalMicrograph recorded,
  with all its tags under ``tags``.
- Thumbnails are skipped. Spectrum images (with an energy axis), colour and complex images
  aren't diffraction patterns, and are refused with a message saying so.
- A file can hold several images; pyEMAPS reads the one with the most patterns. Choose another
  with *dataset*, its number or its name.
- DM5 files, which are HDF5 underneath, aren't supported yet.

.. code-block:: python

   from pyemaps import StackImage, read_image

   scan = StackImage.from_file('scan.dm4', scan_roi=(0, 0, 20, 20))
   ret, bf = scan.generateBDF(center=(285.0, 268.0), rads=(0.0, 30.0))   # scan width 20

   img = read_image('pattern.dm3')
   print(img.axes[0], img.metadata['high_voltage_kV'])

Images from MRC, Merlin and other files
---------------------------------------

pyEMAPS also reads these formats itself, with no other package:

- **MRC** (``.mrc``, ``.mrcs``, ``.st``), the open MRC2014 standard: images and stacks from 3D
  electron diffraction (MicroED), SerialEM, Direct Electron cameras and Thermo Fisher software.
  Each section is a pattern. The pixel size, in Å, comes from the header when it's set.
- **Quantum Detectors Merlin** (``.mib``): 4D-STEM frames from Medipix3 detectors, single-chip
  or quad, in counting mode. Merlin files don't record the scan shape, so give it with
  *scan_shape*. The settings in the ``.hdr`` file next to the ``.mib`` (counter depth, chip
  mode …) are in :py:attr:`metadata <pyemaps.expimage.ExperimentalImage.metadata>` under
  ``hdr``. Raw-mode (R64) files aren't supported; save in counting mode.
- **PNG, BMP and JPEG** pictures, 8 or 16-bit grayscale. RGB pictures whose channels are all
  equal are read as grayscale; colour pictures are refused. JPEG is lossy: fine for a quick
  look, not for measurements.
- **NumPy arrays** saved with ``numpy.save`` (``.npy``): 2-D for one pattern, 3-D for a series,
  4-D for a scan (scan rows, scan columns, rows, columns).

.. code-block:: python

   from pyemaps import StackImage

   scan = StackImage.from_file('scan.mib', scan_shape=(256, 256), scan_roi=(0, 0, 32, 32))
   series = StackImage.from_file('tilt_series.mrc')

Images from EMD files
---------------------

pyEMAPS also reads EMD files (``.emd``), which need the h5py package. Install it with
pyEMAPS' ``emd`` extra:

.. code-block:: console

   pip install "pyemaps[emd]"

On Python 3.15, h5py has no Windows release yet, so EMD files can't be read there for now;
TIFF files can.

Two unrelated layouts share the ``.emd`` extension, and pyEMAPS reads both:

- **Thermo Fisher Velox** files: the images and image series Velox saves, such as diffraction
  patterns. :py:attr:`metadata <pyemaps.expimage.ExperimentalImage.metadata>` gives the high
  voltage (``high_voltage_kV``), the camera length (``camera_length_m``) and the ``detector``
  Velox recorded, and :py:attr:`axes <pyemaps.expimage.ExperimentalImage.axes>` the pixel
  size. Spectra in the same file, such as EDS and EELS, aren't images and are skipped.
- **Berkeley EMD** files (versions 0.x and 1.0), including the 4D-STEM datacubes of py4DSTEM:
  the scan shape and the calibration of each axis come from the file.

A file can hold several images, such as a 4D-STEM scan and an overview image. pyEMAPS reads
the one with the most patterns; choose another with *dataset*, its number or its name:

.. code-block:: python

   from pyemaps import StackImage, read_image

   series = StackImage.from_file('diffraction.emd')
   img = read_image('diffraction.emd')
   print(img.metadata['high_voltage_kV'], img.metadata['camera_length_m'])

   overview = read_image('scan.emd', dataset=1)

Orientation maps
----------------

:py:meth:`StackImage.mapOrientation <pyemaps.stackimg.StackImage.mapOrientation>` indexes every
pattern of a scan against a database, and returns the crystal orientation at each scan point as
an :py:class:`~pyemaps.orientmap.OrientationMap`. It takes the same parameters as
*indexImage*, so try them on a few patterns with *indexImage* first:

.. code-block:: python

   from pyemaps import StackImage

   scan = StackImage.from_file('scan.dm4', scan_roi=(0, 0, 20, 20))
   omap = scan.mapOrientation(db_file, cc=29.0, sigma=3.0, img_center=(99.9, 99.9),
                              rmin=10, search_box=10.0, scaling_option=(1, 2),
                              filter_threshold=0.0, peak_threshold=0.8)
   print(omap)              # how many patterns were indexed, and how many reliably
   omap.show()              # the orientation map, coloured by beam direction, with its key
   omap.show('rindex')      # the reliability index at each scan point
   omap.save('scan_map.npz')

Indexing takes about a second per pattern, so a 64 x 64 scan takes over an hour. Read part of
a large scan with *scan_roi*. Pressing Ctrl+C stops the run and returns the patterns done so far.

The map holds, for each pattern:

- *status*: ``OM_INDEXED``, or ``OM_FEW_PEAKS`` or ``OM_FAILED`` when the pattern couldn't be
  indexed, such as a pattern from vacuum.
- *dp* and *rotation*: the best matching database pattern and its in-plane rotation, as
  *indexImage* reports them; *correlation*, *rindex* (the reliability index), *npeaks* and
  *nindexed*.
- *orientation*: the orientation matrix U, which turns a vector's components in the crystal
  frame into its components in the image frame: x along the image columns, y down the rows and
  z into the image, along the beam. The crystal frame has x along a, and y in the plane of a and
  b. :py:meth:`~pyemaps.orientmap.OrientationMap.euler_angles` gives the same orientations as
  Bunge Euler angles, and :py:meth:`~pyemaps.orientmap.OrientationMap.beam_indices` the beam
  direction as a zone axis [u v w].

:py:meth:`~pyemaps.orientmap.OrientationMap.ipf_colors` colours each pattern by its beam
direction within the database's orientation region: for a cubic crystal, [001] is red, [011]
green and [111] blue. Patterns that aren't
:py:meth:`~pyemaps.orientmap.OrientationMap.reliable`, with a reliability index below 5 or
fewer than 3 peaks indexed, are black.

A diffraction pattern from the zero-order Laue zone looks the same for an orientation and for
the same orientation turned 180 degrees about the beam, so the map can't tell those two apart.

.. note::

   Diffraction pattern indexing supports crystals of any crystal system, with these limits:

   1. Experimental images must be 100 to 512 pixels in each dimension. Read larger ones with
      *binning*, as above.
   2. The database resolution (*res* in *generateDPDB*) can be 100 to 500 sampling points.

   We appreciate any comments and suggestions to improve this feature. Contact us at
   support@emlabsoftware.com.
