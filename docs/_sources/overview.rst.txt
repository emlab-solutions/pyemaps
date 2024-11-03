Overview
========

**pyEMAPS** package is a collection of python modules and libraries designed 
for transmission electron diffraction simulations and related crystallographic 
calculations for all crystal systems. The simulation is based on the theories 
of kinematical and dynamical electron diffraction, as described by Spence and Zuo 
in the book of Electron Microdiffraction (Plenum, New York, 1992).

PyEMAPS serves as the backbone of `cloudEMAPS on premise <https://www.emlabsolutions.com/software/#cloudemapsop>`_
and can also be used as a fully functional standalone Python package.

The base version is free for personal and commercial use, while additional licensed features in 4DSTEM are available for enhanced functionality.

Features
--------------

Free base features:

* Crystallography

  * Crystal constructor
  * Loading from a built-in crystal library
  * CIF import
  * Crystallographic transformations
  * Real and reciprocal vector calculations
  * Stereodiagram plotting
  * Crystal Structure Factors Calculations

* Electron diffraction pattern, dynamical

  * Convergent beam electron diffraction
  * Electron scattering Matrix
  * Electron dispersion

* Electron diffraction pattern, kinematical

  * Selected area diffraction
  * Kikuchi and high order Laue zone line geometry
  * Convergent beam electron diffraction
  * Electron powder diffraction simulations

**Extended features** (requires :ref:`License Activation`):

  * Electron diffraction patterns database builder and explore
  * Electron diffraction pattern indexing 
  * Annular bright and dark field
  * Masked images 

In development
--------------
* Coherent convergent beam electron diffraction
* Electron image simulation
* Pendellösung calculation
* Electron diffraction orientation mapping

Implementation
--------------

*pyEMAPS* is implemented as the object-oriented python modules supported 
by compiled Fortran 90 libraries that handle the backend computations. 

Check out the :doc:`usage` section for further information, including how to
:ref:`install <installation>` pyEMAPS package.

.. note::

   **Developer Contributors Wanted**
 
   Pyemaps is developed by EMLab Solutions, Champaign, IL for microscopy and crystallography research 
   and education. We welcome community input, contributions, and donations `PayPal <https://www.paypal.com/paypalme/pyemaps22>`_. 
   Your generous support will help the development of free software to the electron microscopy and research communities.