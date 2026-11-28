4D-STEM
=======

In 4D-STEM, a camera records the whole diffraction pattern at every position of a scanning
electron probe. pyEMAPS indexes those patterns against simulated databases to find the crystal
orientation and phase, makes images with virtual detectors, and groups, averages and transforms
the patterns themselves. The 4D-STEM features are licensed and computed in emaps; they require
:ref:`License Activation`. Reading data files needs no license.

.. grid:: 1 2 3 3
   :gutter: 2

   .. grid-item-card:: Indexing a diffraction pattern
      :link: indexing
      :link-type: doc

      Generate a pattern database for a crystal and find a pattern's orientation from it.

   .. grid-item-card:: Orientation mapping of a 4D-STEM scan
      :link: orientation
      :link-type: doc

      Index every pattern of a scan and map the crystal orientation. Experimental.

   .. grid-item-card:: Phase mapping of a 4D-STEM scan
      :link: phase
      :link-type: doc

      Find which of several crystal phases each pattern belongs to. Experimental.

   .. grid-item-card:: Virtual detector imaging
      :link: imaging
      :link-type: doc

      Bright field, dark field and annular dark field images, and detectors of any shape.

   .. grid-item-card:: Grain maps from similar patterns
      :link: similar
      :link-type: doc

      Correlation maps, groups of similar patterns, their averages and labels, without a
      database.

   .. grid-item-card:: Average patterns and polar transforms
      :link: averages
      :link-type: doc

      A scan's average pattern, and patterns in polar coordinates about their center.

   .. grid-item-card:: Reading 4D-STEM data files
      :link: data
      :link-type: doc

      TIFF, DigitalMicrograph, MRC, Merlin, EMD and other files, and whether a file holds
      diffraction patterns.

.. toctree::
   :hidden:

   indexing
   orientation
   phase
   imaging
   similar
   averages
   data
