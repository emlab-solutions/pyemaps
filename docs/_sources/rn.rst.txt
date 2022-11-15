Release Notes
=============

Version 0.4.7 Beta:
------------------- 
* **Date**: November 14th, 2022

* **New**

  Reorganized dynamic diffraction simulation into sessions with:
  
  1. `beginBloch <pyemaps.crystals.html#pyemaps.crystals.Crystal.beginBloch>`_. Starts a Bloch wave dynamic diffraction session.
  2. `endBloch <pyemaps.crystals.html#pyemaps.crystals.Crystal.endBloch>`_. Ends a dynamic diffraction session.

  These methods enable pyemaps to retain simulation in memory while preventing repeatitive computations, making
  pyemaps more efficient. Dynamic simulation data can be retrieved during session include:

  - `getBlochImages <pyemaps.crystals.html#pyemaps.crystals.Crystal.getBlochImages>`_. Retrieves bloch images and/or save the images into raw image files.
  - `getSCMatrix <pyemaps.crystals.html#pyemaps.crystals.Crystal.getEigen>`_. Gets scattering matrix at a selected sampling point.
  - `getEigen <pyemaps.crystals.html#pyemaps.crystals.Crystal.getSCMatrix>`_. Gets eigen values at a selected sampling point.
  - `getBeams <pyemaps.crystals.html#pyemaps.crystals.Crystal.getBeams>`_. Retrieves diagnization Miller indexes at each sampling point.
  - `printIBDetails <pyemaps.crystals.html#pyemaps.crystals.Crystal.printIBDetails>`_. Prints miscellenous data such as incidental beams and a list of sampling points etc. 

  .. note::

        `generateBloch <pyemaps.crystals.html#pyemaps.crystals.Crystal.generateBloch>`_ is kept for backward compatibility purposes.
        This function is now equivalent to calling:
          
        - `beginBloch <pyemaps.crystals.html#pyemaps.crystals.Crystal.beginBloch>`_ 
        - `getBlockImages <pyemaps.crystals.html#pyemaps.crystals.Crystal.getBlockImages>`_
        - `endBloch <pyemaps.crystals.html#pyemaps.crystals.Crystal.endBloch>`_
        