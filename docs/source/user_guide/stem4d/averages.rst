Average patterns and polar transforms
=====================================

Two views of a scan's patterns: their average, and their polar transform, which turns rings
about the center into straight rows. Like the methods in :doc:`similar`, they read the whole scan
into memory and return NumPy arrays. This feature requires :ref:`License Activation`.

.. seealso::

   Steps 7 and 12 of the notebook :doc:`../../notebooks/adf` run these methods on a real scan:
   they compare its average pattern with NumPy's, and measure each grain's rotation from the
   polar transforms.

- :py:meth:`~pyemaps.stackimg.StackImage.averagePattern`: the mean of all the patterns, the
  position-averaged pattern of the scan.
- :py:meth:`~pyemaps.stackimg.StackImage.polarTransform`, and
  :py:func:`~pyemaps.stackimg.polar_transform` for a single pattern: the pattern in polar
  coordinates about a center. Rows are radii in pixels, out to the pattern's nearest edge, and
  columns are angles. Rings about the center become straight rows, and a pattern's symmetry
  about the center shows as a repeat along the rows.

.. code-block:: python

   from pyemaps import StackImage, polar_transform

   scan = StackImage.from_file('scan.tif', scan_shape=(64, 64))
   center = (128.0, 128.0)                       # the direct beam, (column, row)

   mean = scan.averagePattern()                                 # 256 x 256
   polar = scan.polarTransform(center, dtheta=1.0, pattern=0)   # radii x 360 angles
   mean_polar = polar_transform(mean, center, dtheta=1.0)       # the same for one array

Every pattern's transform together can be large, patterns x radii x angles floats, so pass
*pattern* for one.

These are ports of functions from the DigitalMicrograph plug-in that pyEMAPS' 4D-STEM module
grew from, computed in emaps. As ported, the polar transforms reach the nearest edge in every
direction.
