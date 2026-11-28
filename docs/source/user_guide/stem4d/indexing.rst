Indexing a diffraction pattern
==============================

Electron diffraction pattern (DP) indexing uses template matching: it compares an acquired DP
with the patterns in a database that pyEMAPS' DPGEN module generates. The crystal orientation
and phase come from the database pattern that fits best. This feature requires
:ref:`License Activation`.

.. seealso::

   The notebook :doc:`../../notebooks/al_ediom` indexes the sample image *al.img* end to end,
   shown here with its plots and output.

.. toctree::
   :hidden:

   ../../notebooks/al_ediom

First, generate a DP database for the crystal, here Aluminium:

.. code-block:: python

   from pyemaps import EMC, Crystal, StackImage

   aluminium = Crystal.from_builtin('Aluminium')
   ret, db_file = aluminium.generateDPDB(emc=EMC(zone=(0, 0, 1)), res=200, xa=(2, 0, 0))

*ret* is 0 on success, and *db_file* is the database file name.An optional *vertices* argument,
an array of 3 or 4 zone axis indexes, encloses the orientation area within which the
diffraction patterns are generated. For details, see
:py:obj:`generateDPDB <pyemaps.crystals.Crystal.generateDPDB>`.

The database must reach as far out as the experimental peaks that indexing uses: the
reflections' *gmax* (``EMC(simc=SIMC(gmax=...))``) must be at least the outer radius of those
peaks, in pixels, divided by the camera constant *cc*. By default the outer radius is two
thirds of the distance from the pattern center to the nearest edge; *rmax* in *indexImage* and
*mapOrientation* changes it. The default *gmax*, 3.5 1/Å, covers most patterns. With a smaller
one, the outer reflections are missing from the database and tilted orientations index worse;
*indexImage* and *mapOrientation* warn when that happens.

Then load the experimental image and index it against the database. *indexImage* loads the
database itself. *al.img* is a sample experimental image that ships with pyEMAPS:
``pyemaps -cp samples`` copies it, with the sample scripts, into a *pyemaps_samples* folder in the
current directory (see :doc:`../../examples`). Run the example from that folder. To read patterns
from TIFF, DigitalMicrograph, MRC, EMD and other files, see :doc:`data`.

.. code-block:: python

   image = StackImage('al.img')
   image.indexImage(db_file,
                    cc=29.0,                       # camera constant, pixels per 1/Å
                    sigma=3.0,                     # half the peaks' full width at half maximum
                    img_center=(99.923, 99.919),   # pattern center, in pixels
                    rmin=10,                       # radius excluded around the center
                    search_box=10.0,               # peak search box size, in pixels
                    scaling_option=(1, 2),         # intensity scaling for matching
                    filter_threshold=0.0,          # 0 searches every database pattern
                    peak_threshold=0.8)            # how closely a peak's shape must match

   StackImage.showMatchedDBDP()

*indexImage* prints the indexed diffraction beams, and *showMatchedDBDP* shows the database
pattern that best matches the image. For all the parameters, see
:py:obj:`StackImage.indexImage <pyemaps.stackimg.StackImage.indexImage>`. The *al_ediom.py*
sample runs this whole example.

*sigma* sets the width of a peak. pyEMAPS draws peaks as Gaussians whose full width at half
maximum is *sigma*, both for the starting kernel of the peak search and for the database
patterns, but the value that works is about half the width you measure across your peaks at
half their height. The peaks in *al.img* are about 6 pixels wide at half height, and *sigma* 3.0
indexes it best. From 3.5 to 5.0 it finds the same orientation with fewer peaks indexed, and
2.5 or 6.0 find too few peaks to index at all.

.. note::

   Diffraction pattern indexing supports crystals of any crystal system, with these limits:

   1. Experimental images must be 100 to 512 pixels in each dimension. Read larger ones with
      *binning*; see :doc:`data`.
   2. The database resolution (*res* in *generateDPDB*) can be 100 to 500 sampling points.

   We appreciate any comments and suggestions to improve this feature. Contact us at
   support@emlabsoftware.com.
