About pyEMAPS
=============

**pyEMAPS** is a Python package for transmission electron diffraction simulations and
crystallographic computing, for all crystal systems. Its simulations are based on the theories of
kinematical and dynamical electron diffraction described by J. C. H. Spence and J. M. Zuo in
*Electron Microdiffraction* (Plenum Press, New York, 1992).

pyEMAPS is free software under the GNU General Public License v3.0 or later, for personal and
commercial use, with a linking exception that permits its use with emaps, its separately licensed
simulation engine. The 4D-STEM features of emaps need a license. See :doc:`license`.

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

* **Electron lenses with aberrations**, corrected or not

  * Ronchigrams
  * STEM probes and their size
  * Contrast transfer functions, with their coherence envelopes
  * HREM images of thin samples

The extended 4D-STEM features, which need :ref:`License Activation`:

* Building and searching diffraction pattern databases
* Indexing experimental diffraction patterns
* Orientation and phase maps of 4D-STEM scans (experimental)
* Bright field, dark field and annular dark field images with virtual detectors, and masked images
* Grain maps from similar patterns, average patterns and polar transforms

See :doc:`user_guide/stem4d/index`.

Reading experimental patterns is free: TIFF, Gatan DigitalMicrograph (``.dm3``, ``.dm4``),
MRC, Quantum Detectors Merlin (``.mib``), PNG, BMP, JPEG and NumPy files, single images, stacks
and 4D-STEM scans, with no other package, and EMD files from
Thermo Fisher Velox or in the Berkeley EMD format, including py4DSTEM's 4D-STEM datacubes. See
:ref:`user_guide/stem4d/data:Images from TIFF files`,
:ref:`user_guide/stem4d/data:Images from DigitalMicrograph files`,
:ref:`user_guide/stem4d/data:Images from MRC, Merlin and other files` and
:ref:`user_guide/stem4d/data:Images from EMD files`.

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
