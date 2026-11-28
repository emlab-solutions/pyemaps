Orientation mapping of a 4D-STEM scan
=====================================

An orientation map indexes every pattern of a 4D-STEM scan against a database, as *indexImage*
does for one pattern (see :doc:`indexing`), and shows the crystal orientation at each scan
position. This feature requires :ref:`License Activation`.

.. seealso::

   The notebook :doc:`al_orientmap.ipynb <../../notebooks/al_orientmap>` maps the orientations of a
   synthetic scan step by step, shown here with its plots and output.

.. toctree::
   :hidden:

   ../../notebooks/al_orientmap

.. admonition:: Experimental
   :class: warning

   Orientation mapping is experimental. It finds the right orientations on simulated scans and
   gives the same result as *indexImage* on *al.img*, but it hasn't yet been validated against an
   independent orientation map of real data, and its results depend on the peak search settings.
   Check a map against patterns you can index by hand before relying on it. Its parameters,
   defaults and results may change in later releases.

:py:meth:`StackImage.mapOrientation <pyemaps.stackimg.StackImage.mapOrientation>` indexes every
pattern of a scan against a database, and returns the crystal orientation at each scan point as
an :py:class:`~pyemaps.orientmap.OrientationMap`. It takes the same parameters as
*indexImage*, so try them on a few patterns with *indexImage* first (see :doc:`indexing`):

.. code-block:: python

   from pyemaps import StackImage

   scan = StackImage.from_file('scan.dm4', scan_roi=(0, 0, 20, 20))
   omap = scan.mapOrientation(db_file, cc=29.0, sigma=3.0, img_center=(99.9, 99.9),
                              rmin=10, search_box=10.0, filter_threshold=0.0,
                              peak_threshold=0.6, min_snr=3.0)
   print(omap)              # how many patterns were indexed, and how many reliably
   omap.show()              # the orientation map, coloured by beam direction, with its key
   omap.show('rindex')      # the reliability index at each scan point
   omap.save('scan_map.npz')

Indexing uses all the computer's cores. On a 6-core laptop it takes about 0.03 seconds per
pattern of 200 x 200 to 256 x 256 pixels, so a 64 x 64 scan takes about 2 minutes; larger
patterns and databases take longer. Read part of a large scan with *scan_roi*. Pressing Ctrl+C stops the run and returns the patterns done so far.

The sample *al_orientmap.py* shows a whole run on a synthetic scan: four Aluminium grains of known
orientation, with counting noise. Its Aluminium is a refined crystal structure from the
`Crystallography Open Database <https://www.crystallography.net>`_ (COD entry 4004108, public
domain), in a CIF file that comes with the sample. It maps the scan and compares the map with the
truth. Most patterns come out within 1 degree of their true orientation; the few the map can't index
reliably are black. The notebook :doc:`al_orientmap.ipynb <../../notebooks/al_orientmap>` walks
through the same run step by step, with the choice of settings and how to read the map. It's shown
here with its results; ``pyemaps -cp notebooks`` copies it to run yourself.

*peak_threshold* tests how closely a peak's shape matches the search kernel, not how bright it
is. The default (0.825) suits clean patterns such as selected area diffraction, but in a scan
the spots are often fainter and noisier, and it can miss them all. Try 0.6 to 0.7, with
*min_snr* 3 to keep the background out of the peak list. A higher *min_snr*, such as 5, starts
dropping weak real peaks.

The best *scaling_option* and *peak_threshold* depend on the data, so try a few on some patterns
first, and check the map against patterns you can index by hand. ``(2, 2)`` compares intensities
on a logarithmic scale, and ``(5, 5)`` compares peak positions only. On simulated patterns of
Aluminium and Silicon, with their intensities randomly changed as dynamical diffraction changes
them, both found the right orientation for 75 to 80% of the patterns, against 25 to 30% for the
default ``(1, 2)``. The reliability index depends on the settings and the data, so compare it
only between maps made the same way.

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
