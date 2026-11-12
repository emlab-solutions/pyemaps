About pyEMAPS
=============

**pyEMAPS** is a Python package for transmission electron diffraction simulations and
crystallographic computing, for all crystal systems. Its simulations are based on the theories of
kinematical and dynamical electron diffraction described by J. C. H. Spence and J. M. Zuo in
*Electron Microdiffraction* (Plenum Press, New York, 1992).

pyEMAPS is the backbone of
`cloudEMAPS on premise <https://www.emlabsolutions.com/software/#cloudemapsop>`_, and is also a
complete standalone Python package.

The base features are free software under the GNU General Public License v3.0, for personal and
commercial use. The extended 4D-STEM features need a license. See :doc:`license`.

Features
--------

The free base features:

* **Crystallography**

  * Crystal construction, from your own data or the built-in crystal library
  * CIF import
  * Crystallographic transformations
  * Real and reciprocal space vector calculations
  * Stereodiagrams
  * Crystal structure factors

* **Kinematical electron diffraction**

  * Selected area diffraction
  * Kikuchi and higher order Laue zone (HOLZ) line geometry
  * Convergent beam electron diffraction (CBED)
  * Electron powder diffraction

* **Dynamical electron diffraction** (Bloch wave)

  * Convergent beam electron diffraction, including large-angle CBED
  * The electron scattering matrix
  * Electron dispersion (the eigenvalues of the Bloch wave solution)

The extended 4D-STEM features, which need :ref:`License Activation`:

* Building and searching diffraction pattern databases
* Indexing experimental diffraction patterns
* Annular bright and dark field images
* Masked images

In development
--------------

* Coherent convergent beam electron diffraction
* Electron image simulation
* Pendellösung calculation
* Electron diffraction orientation mapping

Implementation
--------------

pyEMAPS is a set of object-oriented Python modules. The computations run in **emaps**, its
compiled backend of Fortran and C++ libraries, which pip installs with pyEMAPS.

To install pyEMAPS and run a first simulation, see :doc:`getting_started`.

.. note::

   **Contributors wanted**

   pyEMAPS is developed by EMLab Solutions, Champaign, IL, for microscopy and crystallography
   research and education. We welcome community input and contributions; see
   `DEVELOPMENT.md <https://github.com/emlab-solutions/pyemaps/blob/main/DEVELOPMENT.md>`_.
   Donations through `PayPal <https://www.paypal.com/paypalme/pyemaps22>`_ help us keep
   providing free software to the electron microscopy and research communities.
