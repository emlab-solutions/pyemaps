Grain maps from similar patterns
================================

A grain map groups the patterns of a 4D-STEM scan that look alike, without a database: the
patterns from one grain share its orientation, so they correlate with each other. These methods
look at the patterns themselves rather than at sums over a detector. They work on the whole scan,
which they read into memory, and return NumPy arrays. A scan read with
:py:meth:`StackImage.from_file <pyemaps.stackimg.StackImage.from_file>` knows its shape;
otherwise pass *scan_shape*, ``(rows, columns)``, and the results come in that shape. This
feature requires :ref:`License Activation`.

.. seealso::

   Steps 8 to 11 of the notebook :doc:`../../notebooks/adf` run these methods on a real scan:
   they find its grains, then average and label them.

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

Leaving the direct beam out of the mask keeps it from dominating the correlations:

.. code-block:: python

   import numpy as np
   from pyemaps import StackImage, read_image

   scan = StackImage.from_file('scan.tif', scan_shape=(64, 64))
   center = (128.0, 128.0)                       # the direct beam, (column, row)

   yy, xx = np.indices((256, 256))
   mask = np.hypot(xx - center[0], yy - center[1]) > 10

   first = read_image('scan.tif').data[0]        # the first pattern, as an array
   corr = scan.correlationMap(first, mask=mask)  # 64 x 64: how like the first pattern
   labels, corr = scan.findSimilar(threshold=0.7, mask=mask)
   averages, groups, counts = scan.averageByLabel(labels)
   big = averages[counts >= 20]                  # the groups of 20 patterns or more
   classes, match = scan.classifyPatterns(big, mask=mask)

These are ports of functions from the DigitalMicrograph plug-in that pyEMAPS' 4D-STEM module
grew from, computed in emaps. As ported, the correlations are true correlation coefficients over
the mask's pixels.
