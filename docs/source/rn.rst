Release Notes
=============

Version 1.1.6 Stable
--------------------

09-18-2026
~~~~~~~~~~

Improvements
~~~~~~~~~~~~

- Fixed a bug in dynamic diffraction (Bloch) simulations where, for larger unit cells or zone axes with a large number of beams, an uninitialized internal value could silently corrupt the computed scattering matrix and produce a visibly incorrect image without any error or crash. Simulations in this regime are also noticeably faster now that the underlying computation is correct.
- Fixed structure factor calculations for atoms specified with an ionic charge or site-index suffix in their element label (e.g. ``K1+``, ``Zr4+``, ``F1-``), which were previously being silently matched to the wrong element's scattering data.
- Improved the performance of powder diffraction pattern generation for large reflection counts.
- Requires ``emaps >= 1.1.0``.

Version 1.1.5 Stable
--------------------

09-12-2026
~~~~~~~~~~

New
~~~

- `generateCSF <pyemaps.crystals.html#pyemaps.crystals.Crystal.generateCSF>`_ now raises a catchable `CSFError <pyemaps.errors.html#pyemaps.errors.CSFError>`_ when structure factor generation fails, an invalid *sftype* is given, or the number of reflections within *smax* exceeds the backend beam limit -- instead of silently returning a partial result.

Improvements
~~~~~~~~~~~~

- Fixed an out-of-bounds memory write in dynamic diffraction (Bloch) image generation that could occasionally cause instability on repeated runs.
- Significant performance improvement to dynamic diffraction (Bloch) simulations from a corrected OpenMP parallelization fix in the eigensolver -- benchmarks show consistent speedups across all built-in crystals, with the largest gains on bigger structures.
- Raised the structure factor calculation's reflection limit and improved the reflection-selection algorithm to scale linearly with reflection count, allowing larger *smax* values that previously failed.
- Packaging fix ensuring the scattering and space-group backend modules link correctly during installation.

Version 1.1.4 Stable
-------------------- 

03-19-2025 
~~~~~~~~~~

Improvements
~~~~~~~~~~~~

- Bug fixes and performance imporvements in dynamic diffraction or Bloch simulations. 
- Added python package short description in python package repository pypi.org. 


Version 1.1.3 Stable
-------------------- 

03-01-2025 
~~~~~~~~~~

New
~~~

- Added new crystal structure data module :py:mod:`xtal` with :py:class:`Xtal` class for better handling of crystal structure data. The return from `generateMxtal <pyemaps.crystals.html#pyemaps.crystals.Crystal.generateMxtal>`_ now also return an :py:class:`Xtal` class object. 

Improvements
~~~~~~~~~~~~

- Bug fixes.
- Dynamic diffraction image list class :py:class:`BlochImgs` in :py:mod:`ddiffs` now has better data comparison function with overloading == operator.
- Microscopy and simulation controls module :py:mod:`emcontrols` also has imporoved data comparison functions for all of its classes.
- Added automated testing for quality control. Before this version, the tests are run by developers' on his/her local systems prior to every release. Now it is done with github's workflow automatically triggered by code changes on release branch. More tests are to be added.
- Adjusting sample code based on the new feature and improvements in this latest version. 

Version 1.1.2 Stable
-------------------- 

12-03-2024 
~~~~~~~~~~

Improvements
~~~~~~~~~~~~

- Bug fixes.
- User based license storage. All authenticated users on the system should be able to use pyEMAPS 4D STEM features. 
  See the section on license activation :ref:`License Activation` for how to activate icense for each user.

Version 1.1.1 Stable
-------------------- 

11-02-2024 
~~~~~~~~~~

What's New?
~~~~~~~~~~~~

**License activation** of 4DSTEM features added. While many features remained free without license.
See the section on license activation :ref:`License Activation` for more details. 

New **4DSTEM** module and its sub-modules. Importing the new 4DSTEM module as follows:
   
.. code-block:: console

  from pyemaps import stem4d

where stem4d functions are organized into two submodules called *ediom* and *send*:

* *ediom*: electron diffraction indexing and oriention mapping. currently,
  this module contains the diffraction indexing. 
  
  * `Experimental diffraction pattern indexing <modules.html#pyemaps.stackimg.StackImage.indexImage>`_

  Orientan mapping will be added to ediom later.
  
* *send*: scanning electronic nano-diffraction. This module now has the following functions:

  * `Annular bright or darkfield <modules.html#pyemaps.stackimg.StackImage.generateBDF>`_.
  * `Masked images <modules.html#pyemaps.stackimg.StackImage.generateMaskedImage>`_.

To import these two modules, use the follwoing code:

.. code-block:: console

  from pyemaps import ediom
  from pyemaps import send

Both modules will share some common values in its parent module *stem4d*.

Improvements
~~~~~~~~~~~~

* Simplified pyEMAPS command line from:

.. code-block:: console

  pyemaps -m pyemaps [options]

to:

.. code-block:: console

  pyemaps [options]

Version 1.0.9 Stable
-------------------- 

05-29-2024 
~~~~~~~~~~

Improvements
~~~~~~~~~~~~

* Bug fixes for image display. Now all displays are utilizing Matplotlib's Tkinter backend.
* Expanded pyemaps build guide.

Version 1.0.8 Stable
-------------------- 

11-07-2023 
~~~~~~~~~~

New
~~~

- Separated pyemaps simulations backend into standalone python package.
- pyemaps package installation automatically installs backend python package. 
  as one of its depedencies. 
- Made pyemaps source code ready for open source and community contribution. 
  We invite you to become pyemaps contributor, contact support@emlabsoftware.com
  for further information.

Improvements
~~~~~~~~~~~~

- Bug fixes related to DigitalMicrograph (DM) integration and added DM python 
  script sample code, as shown in :ref:`Rendering by Third Party Tools <thirdparty>`




    