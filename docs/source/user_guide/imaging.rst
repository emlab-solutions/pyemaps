4D-STEM imaging
===============

In 4D-STEM, a camera records the whole diffraction pattern at every position of a scanning
electron probe. A conventional STEM detector adds up the electrons that land on a fixed region of
the pattern; with the whole pattern recorded, you choose that region after the experiment. This
is a **virtual detector**: each scan position gives one pixel of the image. pyEMAPS makes bright
field, dark field and annular dark field images this way, and images with a detector of any
shape, from a mask. This feature requires :ref:`License Activation`.

.. seealso::

   The notebook :doc:`../notebooks/adf` runs these steps end to end on a real scan, shown here
   with its plots and output.

.. toctree::
   :hidden:

   ../notebooks/adf

The examples use *adftest900.im3*, a 4D-STEM test scan of 30 x 30 positions with 512 x 512
pixel patterns, published by EMLab Solutions on
`Zenodo <https://zenodo.org/records/14028793/files/adftest900.im3?download=1>`_ (472 MB).

Find the direct beam
--------------------

Detectors are placed relative to the direct beam, so find it first. Read the scan with
:py:func:`pyemaps.read_image <pyemaps.expimage.read_image>`, and take the brightest pixel of the
average pattern:

.. code-block:: python

   import numpy as np
   import pyemaps

   scan = pyemaps.read_image('adftest900.im3', scan_shape=(30, 30))
   mean = scan.data.mean(axis=0)                     # the average of the 900 patterns
   row, col = np.unravel_index(mean.argmax(), mean.shape)
   center = (float(col), float(row))                 # (column, row), as pyEMAPS expects

In *adftest900.im3* the direct beam is at column 263, row 263, not at the middle of the
pattern, and its intensity falls by a factor of ten within about 10 pixels of it. An *.im3*
file doesn't record the scan's shape, so *scan_shape* gives it.

Bright field, dark field and annular dark field
-----------------------------------------------

:py:meth:`StackImage.generateBDF <pyemaps.stackimg.StackImage.generateBDF>` adds up each
pattern's pixels inside a disk or ring: *center* is the detector's center, ``(column, row)``,
and *rads* its inner and outer radius, both in pixels. *scol* is the number of scan positions
per row, the width of the image.

.. code-block:: python

   from pyemaps import EM_INT, StackImage

   detectors = {
       'BF':  (center, (0.0, 8.0)),          # a disk on the direct beam
       'ADF': (center, (50.0, 200.0)),       # a ring around it
       'DF':  ((1.0, 256.0), (0.0, 200.0)),  # a disk off the direct beam
   }
   for name, (c, rads) in detectors.items():
       ret, data = StackImage('adftest900.im3', ndtype=EM_INT).generateBDF(
           center=c, rads=rads, scol=30)
       image = np.array(data, dtype=float).reshape(-1, 30)   # 30 x 30 pixels

*ret* is 0 on success. Pass ``bShow=True`` to display the image as well, and *title* to name
it, such as ``title='Annular Dark Field'``. Without *title*, the image is titled by its detector,
such as "Ring Detector, Radii 50-200 px, Center (263, 263)": whether a detector gives bright or
dark field depends on where the direct beam is, which pyEMAPS doesn't know.

- **Bright field (BF):** a disk on the direct beam, a little smaller than it. It records the
  electrons that pass the sample unscattered.
- **Annular dark field (ADF):** a ring around the direct beam. It records the electrons
  scattered to larger angles, so it shows the contrast of BF reversed: on *adftest900.im3* the
  two images have a correlation of -0.72.
- **Dark field (DF):** a disk that leaves out the direct beam, here one centred at the
  pattern's left edge. Its image depends on which part of the pattern it covers.

An inner radius of 0 gives a disk detector, and a positive one a ring. A virtual detector is
just a sum over pixels, so NumPy gives the same image; the notebook checks it.

A scan read with :py:meth:`StackImage.from_file <pyemaps.stackimg.StackImage.from_file>`
knows its scan shape, and *scol* defaults to its width:

.. code-block:: python

   scan = StackImage.from_file('scan.tif', scan_shape=(64, 64))
   ret, bf = scan.generateBDF(center=(128.0, 128.0), rads=(0.0, 20.0))

Detector masks
--------------

A detector doesn't have to be a disk or a ring.
:py:meth:`StackImage.generateMaskedImage <pyemaps.stackimg.StackImage.generateMaskedImage>`
takes a **mask**: an image file the size of a pattern, in pyEMAPS' *.im3* format, whose pixels
above 0.5 belong to the detector.

.. code-block:: python

   ret, data = StackImage('adftest900.im3', ndtype=EM_INT).generateMaskedImage('mask.im3', 30)

*mask.im3*, which comes with the samples, covers six spots on the ring around 60 pixels from the
direct beam, a hexagon from one grain's pattern. Only that grain lights up in the image: a mask
on chosen diffraction spots gives a dark field image of the crystal regions that produce them.

To use a mask of your own, draw it as a NumPy array and convert it with
:py:meth:`StackImage.convertImage <pyemaps.stackimg.StackImage.convertImage>`, which saves it in
the ``sh_converted`` folder of the :ref:`data folder <Environment Variables>` and returns its
path:

.. code-block:: python

   from pyemaps import E_NPY

   yy, xx = np.indices((512, 512))
   radius = np.hypot(xx - center[0], yy - center[1])
   ring = ((radius >= 55) & (radius <= 70)).astype(np.float32)   # a narrow ring
   mask_file = StackImage.convertImage(ring, nformat=E_NPY)

   ret, data = StackImage('adftest900.im3', ndtype=EM_INT).generateMaskedImage(mask_file, 30)

The sample *adf.py* makes the annular dark field, dark field and masked images of this page, and
*convert_image.py* converts a raw image file; see :doc:`../examples`.

Averages, similar patterns and polar transforms
-----------------------------------------------

These methods look at the patterns themselves rather than at sums over a detector. They work
on the whole scan, which they read into memory, and return NumPy arrays. A scan read with
:py:meth:`StackImage.from_file <pyemaps.stackimg.StackImage.from_file>` knows its shape;
otherwise pass *scan_shape*, ``(rows, columns)``, and the results come in that shape. Like the
other 4D-STEM features, they require :ref:`License Activation`.

- :py:meth:`~pyemaps.stackimg.StackImage.averagePattern`: the mean of all the patterns, the
  position-averaged pattern of the scan.
- :py:meth:`~pyemaps.stackimg.StackImage.correlationMap`: how closely each pattern matches a
  template, such as one of the scan's patterns. The template is compared over a *mask*'s pixels,
  those above 0.5 or ``True``. The comparison is the correlation coefficient, from -1 to 1, so
  the patterns' brightness and background don't affect it.
- :py:meth:`~pyemaps.stackimg.StackImage.findSimilar`: groups similar patterns, without a
  database. Seed patterns, chosen at random, collect the patterns along the scan that correlate
  with them above a *threshold*. Each pattern's label is its group's seed.
- :py:meth:`~pyemaps.stackimg.StackImage.averageByLabel`: one mean pattern per label, such as
  per group. Averaging brings out weak reflections that the noise hides in each pattern.
- :py:meth:`~pyemaps.stackimg.StackImage.classifyPatterns`: labels every pattern with the
  template it matches best, such as the groups' averages.
- :py:meth:`~pyemaps.stackimg.StackImage.polarTransform`, and
  :py:func:`~pyemaps.stackimg.polar_transform` for a single pattern: the pattern in polar
  coordinates about a center. Rows are radii in pixels, out to the pattern's nearest edge, and
  columns are angles. Rings about the center become straight rows.

Leaving the direct beam out of the mask keeps it from dominating the correlations:

.. code-block:: python

   scan = StackImage.from_file('scan.tif', scan_shape=(64, 64))
   center = (128.0, 128.0)                       # the direct beam, (column, row)

   yy, xx = np.indices((256, 256))
   mask = np.hypot(xx - center[0], yy - center[1]) > 10

   labels, corr = scan.findSimilar(threshold=0.7, mask=mask)
   averages, groups, counts = scan.averageByLabel(labels)
   big = averages[counts >= 20]                  # the groups of 20 patterns or more
   classes, match = scan.classifyPatterns(big, mask=mask)

   polar = scan.polarTransform(center, dtheta=1.0, pattern=0)   # radii x 360 angles

These are ports of functions from the DigitalMicrograph plug-in that pyEMAPS' 4D-STEM module
grew from, computed in emaps. As
ported, the correlations are true correlation coefficients over the mask's pixels, and the polar
transforms reach the nearest edge in every direction.
