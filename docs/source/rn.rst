Release Notes
=============

Unreleased
----------

Changes
~~~~~~~

- :py:meth:`~pyemaps.crystals.Crystal.generateBloch` and :py:meth:`~pyemaps.crystals.Crystal.beginBloch` called without *em_controls* now start from the default controls every time. Before, every such call shared one controls object, so the crystal x-axis chosen for the first call was reused for every later call in the session, for any crystal. Results for those later calls change: each crystal now gets the x-axis chosen for it. :py:meth:`~pyemaps.crystals.Crystal.generateDPDB` called without *emc* is fixed the same way.
- Non-default ``gctl`` and ``zctl`` simulation controls now reach the simulation. Before, they were silently ignored. A value too small for the pattern, such as ``gctl=1``, now makes :py:meth:`~pyemaps.crystals.Crystal.generateDP` fail.
- :py:meth:`~pyemaps.stackimg.StackImage.convertImage` now converts numpy images: pass the 2-D array as *imgfn* with ``nformat=E_NPY``. It returns the converted file's path, and raises :py:class:`~pyemaps.errors.XDPImageError` when the conversion fails instead of only printing a message.
- :py:func:`~pyemaps.display.plot2Powder` has new *titles* and *ylabels* parameters. By default the plots have no titles; before, they were always titled "Silicon" and "Diamond".
- :py:func:`~pyemaps.display.showDif` raises :py:class:`~pyemaps.errors.DPListError` when it isn't given a :py:class:`DPList <pyemaps.kdiffs.Diffraction>`, and plots nothing for an empty one.
- Comparing a pyEMAPS point, index, disk, diffraction pattern or controls object with ``==`` to an object of another type returns ``False`` instead of raising an error.
- An invalid camera length in :py:class:`~pyemaps.emcontrols.EMControl` raises :py:class:`~pyemaps.errors.EMCError`, like the other controls, instead of ``ValueError``.

Improvements
~~~~~~~~~~~~

- Fixed :py:class:`~pyemaps.crystals.Crystal`, :py:class:`~pyemaps.crystals.Atom` and :py:class:`~pyemaps.crystals.Cell`:

  - A crystal created without data can be checked with :py:meth:`~pyemaps.crystals.Crystal.loaded`, and no longer prints an error when it's freed.
  - :py:attr:`Atom.atype <pyemaps.crystals.Atom.atype>` returns the thermal factor type instead of the element symbol, so identical atoms and crystals now compare equal.
  - An atom created without a position has 5 values (10 for anisotropic atoms), not 6.
  - Creating a crystal from a dictionary no longer deletes ``symb`` from the dictionary's atoms, so the same data can be used again.
  - Cell errors name the right cell constant.
  - :py:attr:`Cell.session_controls <pyemaps.crystals.Cell.session_controls>` is ``None`` until set, instead of raising an error.
  - :py:meth:`~pyemaps.crystals.Crystal.from_xtl` and :py:meth:`~pyemaps.crystals.Crystal.from_cif` report a file that can't be read as :py:class:`~pyemaps.errors.CrystalClassError`.

- Fixed the microscope and simulation controls:

  - Each :py:class:`~pyemaps.emcontrols.EMControl` created without simulation controls gets its own :py:class:`~pyemaps.emcontrols.SIMControl`. Before, they all shared one, so changing one changed them all.
  - :py:meth:`EMControl.from_dict <pyemaps.emcontrols.EMControl.from_dict>` uses the defaults for missing keys, and the simulation controls given in the dictionary.
  - Plot captions show a non-default diffracted beam size and ``bmin``.
  - Unknown keys passed to a :py:class:`~pyemaps.emcontrols.SIMControl` are ignored, as its message says.
  - Error messages name the right control.

- Fixed kinematic and dynamic diffraction results:

  - Printing a diffraction pattern shows the number of diffracted beams, not the number of Kikuchi lines.
  - Kikuchi and HOLZ lines sort by their end points and intensity.
  - Points, lines and disks that compare equal also hash equally, so sets and dictionaries treat them as the same.
  - ``(emc, image) in bloch_images`` works on :py:class:`BImgList <pyemaps.ddiffs.BlochImgs>`.

- Fixed 4D-STEM (stem4d) images:

  - :py:meth:`~pyemaps.stackimg.StackImage.viewExpImage` displays images that aren't square correctly, and its stack check no longer accepts one stack past the last.
  - :py:meth:`~pyemaps.stackimg.StackImage.generateMaskedImage` rejects a missing or blank mask file name, and prints the error when the image can't be loaded.
  - :py:meth:`~pyemaps.stackimg.StackImage.showMatchedDBDP` returns -1 on failure instead of ending the Python session.
  - Invalid image dimensions report the valid ranges.
  - The database pattern shown by :py:meth:`~pyemaps.stackimg.StackImage.showMatchedDBDP` is now normalized as intended.
  - A script no longer prints an ``Exception ignored in: StackImage.__del__`` error when it ends while a :py:class:`~pyemaps.stackimg.StackImage` is still alive.

- Fixed file and structure utilities:

  - :py:func:`~pyemaps.fileutils.compose_ofn` accepts an empty file name.
  - :py:meth:`~pyemaps.crystals.Crystal.from_cif` reports a missing CIF file, and a space group setting or number out of range, with the right error.
  - Each :py:class:`~pyemaps.xtal.ACoord` created without coordinates gets its own coordinate list.

Version 2.0.0 Stable
--------------------

11-10-2026
~~~~~~~~~~

New
~~~

- pyEMAPS now runs on Python 3.12, 3.13, 3.14 and 3.15 on Windows, with NumPy 2. The emaps backend ships one wheel for each of these Python versions.
- pyEMAPS is now a pure-Python package: a single wheel installs on every supported Python version, with no compiler needed.

Changes
~~~~~~~

- Python 3.7 is no longer supported. On Python 3.7, ``pip install pyemaps`` keeps installing pyEMAPS 1.1.x with emaps 1.1.x.
- Requires ``numpy >= 2.0`` and ``matplotlib >= 3.8.4``.
- The emaps backend no longer exposes the undocumented ``emaps.diffract.emaps_sims.metric`` attribute (the crystal metric tensors). Nothing in pyEMAPS used it, and simulation results are unchanged.
- emaps no longer depends on the ``msvc-runtime`` package. The C++ runtime that the 4D-STEM (stem4d) module needs now ships inside emaps.

Improvements
~~~~~~~~~~~~

- Fixed plot windows on matplotlib 3.6 and newer, which removed the window-title call pyEMAPS used.
- Simulation results are identical to pyEMAPS 1.1.8 on every supported Python version.
- Plot windows shown with ``bClose=True`` now stay up 3 seconds after the last image before closing, instead of about 1 second.
- New 4D-STEM (stem4d) checks in the test suite cover image loading, diffraction pattern database generation and indexing.
- Requires ``emaps >= 2.0.0``.

Version 1.1.8 Stable
--------------------

11-09-2026
~~~~~~~~~~

Improvements
~~~~~~~~~~~~

- Fixed a threading bug in dynamic diffraction (Bloch) and LACBED simulations with more than 512 beams, where parallel threads shared internal work arrays. Results in this regime could be wrong and could differ from one run to the next, without any error.
- Fixed loading 4D-STEM (stem4d) images from numpy arrays. ``StackImage`` with ``nformat=E_NPY`` failed with ``TypeError`` whenever its ``data`` was set, and now works. Any 2-D boolean, integer or floating-point array, including ``float64`` and ``int32``, is accepted and converted to ``float32``. Invalid input raises ``XDPImageError`` with a clear message. In the emaps backend, images with more rows than columns, or transposed arrays, could crash Python, and ``uint8``/``uint16`` arrays and wide or non-C-ordered arrays loaded wrong pixel values without any error.
- Fixed a memory leak when loading multiple images into the 4D-STEM (stem4d) feature in one session, and possible memory corruption or wrong fit maps when switching diffraction pattern databases without reloading the image.
- The Bloch stress test now compares its result exactly against a stored baseline (``-bc``), instead of relying only on a visual check.
- Requires ``emaps >= 1.1.2``.

Version 1.1.7 Stable
--------------------

09-21-2026
~~~~~~~~~~

Improvements
~~~~~~~~~~~~

- Tuned the dynamic diffraction (Bloch) stress test with a wider thickness range and longer camera length, and updated it to save its rendered image and leave the plot window open for visual inspection.
- Regenerated the stored Bloch feature test baselines against emaps 1.1.0.
- Reduced memory usage when generating large diffraction pattern databases (``dpgen``) by streaming database records to disk as they are computed instead of accumulating them all in memory first.
- Fixed memory leaks and improved out-of-memory robustness in the peak-search code used by the 4D-STEM (stem4d) feature.
- Requires ``emaps >= 1.1.1``.

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

- :py:meth:`~pyemaps.crystals.Crystal.generateCSF` now raises a catchable :py:class:`~pyemaps.errors.CSFError` when structure factor generation fails, an invalid *sftype* is given, or the number of reflections within *smax* exceeds the backend beam limit -- instead of silently returning a partial result.

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

- Added new crystal structure data module :py:mod:`~pyemaps.xtal` with :py:class:`~pyemaps.xtal.Xtal` class for better handling of crystal structure data. The return from :py:meth:`~pyemaps.crystals.Crystal.generateMxtal` now also return an :py:class:`~pyemaps.xtal.Xtal` class object. 

Improvements
~~~~~~~~~~~~

- Bug fixes.
- Dynamic diffraction image list class :py:class:`~pyemaps.ddiffs.BlochImgs` in :py:mod:`~pyemaps.ddiffs` now has better data comparison function with overloading == operator.
- Microscopy and simulation controls module :py:mod:`~pyemaps.emcontrols` also has improved data comparison functions for all of its classes.
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
  
  * :py:meth:`Experimental diffraction pattern indexing <pyemaps.stackimg.StackImage.indexImage>`

  Orientan mapping will be added to ediom later.
  
* *send*: scanning electronic nano-diffraction. This module now has the following functions:

  * :py:meth:`Annular bright or darkfield <pyemaps.stackimg.StackImage.generateBDF>`.
  * :py:meth:`Masked images <pyemaps.stackimg.StackImage.generateMaskedImage>`.

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




    