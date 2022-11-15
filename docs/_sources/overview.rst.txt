Overview
========

**pyemaps** package is a collection of python modules and libraries designed 
for transmission electron diffraction simulations and related crystallographic 
calculations for all crystal systems. The simulation is based on the theories 
of kinematical and dynamical electron diffraction, as described by Spence and Zuo 
in the book of Electron Microdiffraction (Plenum, New York, 1992).

Pyemaps serves as the backbone of `cloudEMAPS2.0 <https://emaps.emlabsolutions.com>`_
and can also be used as a fully functional Python package.

Current features include:

**Crystallography**
   
   * Crystal constructor
   * Loading from a built-in crystal library
   * CIF import

   * Crystallographic transformations
   * Real and reciprocal vector calculations
   * Stereodiagram plotting

   * Crystal Structure Factors Calculations

**Electron diffraction pattern, kinematical**

   * Selected area diffraction
   * Kikuchi and high order Laue zone line geometry
   * Convergent beam electron diffraction
   * Electron powder diffraction simulations

**Electron diffraction pattern, dynamical**

   * Convergent beam electron diffraction
   * Electron scattering Matrix
   * Electron dispersion

In development
--------------
   * Coherent convergent beam electron diffraction
   * Electron image simulation
   * Pendellösung calculation
   * Electron diffraction database builder and explorer

Implementation
--------------

*pyemaps* is implemented as the object-oriented python modules supported 
by compiled Fortran-95 libraries that handle the backend computations. 

Check out the :doc:`usage` section for further information, including how to
:ref:`install <installation>` pyemaps package.

.. note::

   *pyemaps* is currently under active Beta development phase. 

.. note::

   **Developer**
 
   Pyemaps is developed by EMLab Solutions, Champaign, IL for non-commercial
   microscopy and crystallography research and education. We welcome community input,
   contributions, and donations `PayPal <https://www.paypal.com/paypalme/pyemaps22>`_. 
   Your generous support will help the development of free software to the electron 
   microscopy and research communities.