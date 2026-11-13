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
``pyemaps -cp`` copies it, with the sample scripts, into a *pyemaps_samples* folder in the
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

.. note::

   Diffraction pattern indexing supports crystals of any crystal system, with these limits:

   1. Experimental images must be 100 to 512 pixels in each dimension.
   2. The database resolution (*res* in *generateDPDB*) can be 100 to 500 sampling points.

   We appreciate any comments and suggestions to improve this feature. Contact us at
   support@emlabsoftware.com.
