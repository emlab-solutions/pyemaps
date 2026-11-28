Reading 4D-STEM data files
==========================

Every 4D-STEM feature starts from diffraction patterns read from a file: one pattern to index,
or a whole scan. pyEMAPS reads TIFF, DigitalMicrograph, MRC, Merlin, EMD, NumPy and picture
files itself, with no other package, and reading needs no license.
:py:meth:`StackImage.from_file <pyemaps.stackimg.StackImage.from_file>` makes an image ready for
indexing and imaging, and :py:func:`pyemaps.read_image <pyemaps.expimage.read_image>` returns the
patterns as NumPy arrays.

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
it with *scan_shape*, or give the scan width to the imaging methods (*scol*, *scancol*). For
the imaging methods, see :doc:`imaging`.

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
- A file can hold several images; pyEMAPS reads diffraction patterns first (see
  :ref:`diffraction-or-not`), and among those the one with the most patterns. Choose another
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
  voltage (``high_voltage_kV``), the camera length (``camera_length_m``), the ``detector``
  Velox recorded and the ``title`` Velox shows the image under (such as ``DF-S``), and
  :py:attr:`axes <pyemaps.expimage.ExperimentalImage.axes>` the pixel size. Spectra in the
  same file, such as EDS and EELS, aren't images and are skipped; the elemental maps Velox
  computes from them are images, marked by ``spectrum_map``.
- **Berkeley EMD** files (versions 0.x and 1.0), including the 4D-STEM datacubes of py4DSTEM:
  the scan shape and the calibration of each axis come from the file.

A file can hold several images, such as a 4D-STEM scan and an overview image. pyEMAPS reads
diffraction patterns first, and among those the one with the most patterns; choose another
with *dataset*: its number, its name, or for a Velox file its title:

.. code-block:: python

   from pyemaps import StackImage, read_image

   series = StackImage.from_file('diffraction.emd')
   img = read_image('diffraction.emd')
   print(img.metadata['high_voltage_kV'], img.metadata['camera_length_m'])

   overview = read_image('scan.emd', dataset=1)
   stem = read_image('spectrum_image.emd', dataset='DF-S')

.. _diffraction-or-not:

Does a file hold diffraction patterns?
--------------------------------------

The 4D-STEM features index diffraction patterns, but microscope files also hold images of the
sample, such as STEM images, and maps computed from spectra. A file's calibration tells them
apart: diffraction patterns are calibrated in reciprocal lengths or angles (1/nm, mrad …),
images of the sample in lengths (nm, Å …).
:py:attr:`ExperimentalImage.kind <pyemaps.expimage.ExperimentalImage.kind>` gives what an
image read is: ``'diffraction'``, ``'real-space'``, ``'spectrum map'``, or ``'unknown'`` when
the file doesn't tell, as for TIFF, MRC, Merlin, picture and NumPy files and uncalibrated
images. :py:func:`pyemaps.image_datasets <pyemaps.expimage.image_datasets>` lists a file's
images and their kinds without reading them:

.. code-block:: python

   from pyemaps import image_datasets

   for d in image_datasets('spectrum_image.emd'):
       print(d['dataset'], d['title'], d['kind'], d['pattern_shape'], d['default'])

When none is named, pyEMAPS reads diffraction patterns first, then images of unknown kind,
then images of the sample, then spectrum maps, passing over single images that are all zero.
If the image :py:meth:`StackImage.from_file <pyemaps.stackimg.StackImage.from_file>` reads
is an image of the sample or a spectrum map, it warns, and says which dataset holds the file's
diffraction patterns, if any. A Velox spectrum-imaging file, for example, holds STEM images and
elemental maps but no diffraction patterns, so it has nothing to index.
