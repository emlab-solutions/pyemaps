4D-STEM pattern indexing
========================

Electron diffraction pattern (DP) indexing uses template matching: it compares an acquired DP
with the patterns in a database that pyEMAPS' DPGEN module generates. The crystal orientation
and phase come from the database pattern that fits best. This feature requires
:ref:`License Activation`.

First, generate a DP database for the crystal, here Aluminium:

.. code-block:: python

   from pyemaps import Crystal, EMC, StackImage

   al = Crystal.from_builtin('Aluminium')
   ret, dbfn = al.generateDPDB(emc=EMC(zone=(0, 0, 1)), res=200, xa=(2, 0, 0))

*ret* is 0 on success, and *dbfn* is the database file name. An optional *vertices* argument,
an array of 3 or 4 zone axis indexes, encloses the orientation area within which the
diffraction patterns are generated. For details, see
:py:obj:`generateDPDB <pyemaps.crystals.Crystal.generateDPDB>`.

Then load the experimental image and index it against the database. *indexImage* loads the
database itself. *al.img* is a sample experimental image that ships with pyEMAPS:
``pyemaps -cp`` copies it, with the sample scripts, into a *pyemaps_samples* folder in the
current directory (see :doc:`../examples`). Run the example from that folder.

.. code-block:: python

   img = StackImage('al.img')
   img.indexImage(dbfn,
                  cc               = 29.0,
                  sigma            = 3.0,
                  img_center       = (99.923, 99.919),
                  rmin             = 10,
                  search_box       = 10.0,
                  scaling_option   = (1, 2),
                  filter_threshold = 0.0,
                  peak_threshold   = 0.8)

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
