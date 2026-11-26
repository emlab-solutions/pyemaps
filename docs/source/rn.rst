Release Notes
=============

Version 2.9.0 Stable
--------------------

11-26-2026
~~~~~~~~~~

New
~~~

- Thick crystals by the multislice method, a licensed feature computed in emaps 2.6.0:

  - :py:meth:`~pyemaps.probe.Probe.crystal_exit_wave`: a crystal's exit wave under plane-wave illumination, to pass to :py:meth:`~pyemaps.probe.Probe.hrem` for HREM images of thick crystals;
  - :py:meth:`~pyemaps.probe.Probe.crystal_ronchigram`: the probe through the crystal, giving its Ronchigram, or a CBED pattern with a small focused probe.

  A list of thicknesses gives every result from one pass. *slice_thickness* sets the slicing, and *bandlimit*, on by default, applies the 2/3 band limit. Without an active license, both raise :py:class:`~pyemaps.errors.LicenseError`. The sample *crystal_thickness.py* shows HREM and CBED thickness series of silicon [110], and the notebook :doc:`notebooks/si_multislice` checks the thickness fringes against Bloch waves. See "Thick crystals" in :doc:`user_guide/probe`.
- Maps without a seam: *fit=True* on :py:meth:`~pyemaps.probe.Probe.crystal_potential` and the multislice methods strains the crystal slightly in the plane of the map, so it repeats exactly at the map's edges. A strain above 1% gives a warning. :py:meth:`~pyemaps.probe.Probe.crystal_repeats` gives a crystal's repeats along and across a zone axis, and the map sizes that fit with little strain.
- Phase maps, experimental and licensed: :py:meth:`~pyemaps.stackimg.StackImage.mapPhases` finds which of several crystal phases each pattern of a 4D-STEM scan belongs to, with one diffraction pattern database per phase. It decides by the spacings of each pattern's peaks, which tells apart phases with the same structure that indexing alone can't, such as aluminium and copper. It returns a :py:class:`~pyemaps.phasemap.PhaseMap`: each pattern's phase, confidence and scores, each phase's orientation map, and the phase fractions, with plots, saving and loading. emaps 2.6.0 scores the phases and decides, in compiled code. The sample *al_cu_phasemap.py* and the notebook :doc:`notebooks/al_cu_phasemap` map a synthetic scan of aluminium and copper grains. See "Phase maps" in :doc:`user_guide/indexing`.
- 4D-STEM scan analysis, licensed and computed in emaps 2.6.0, on all the processor's cores:

  - :py:meth:`~pyemaps.stackimg.StackImage.averagePattern`: the mean of a scan's patterns;
  - :py:meth:`~pyemaps.stackimg.StackImage.averageByLabel`: one mean pattern per label, such as per grain;
  - :py:meth:`~pyemaps.stackimg.StackImage.correlationMap`: how closely each pattern matches a template, over a mask's pixels;
  - :py:meth:`~pyemaps.stackimg.StackImage.findSimilar`: groups similar patterns, such as a scan's grains, without a database;
  - :py:meth:`~pyemaps.stackimg.StackImage.classifyPatterns`: labels every pattern by the template it matches best;
  - :py:meth:`~pyemaps.stackimg.StackImage.polarTransform` and :py:func:`~pyemaps.stackimg.polar_transform`: patterns in polar coordinates about a centre.

  Steps 7 to 12 of the notebook :doc:`notebooks/adf` run them on the 4D-STEM test scan: they find its grains, average and label them, and measure each grain's rotation. See "Averages, similar patterns and polar transforms" in :doc:`user_guide/imaging`.
- :py:class:`~pyemaps.errors.LicenseError`, raised by the licensed features of the probe module and of database generation when no license is active.
- The samples' crystals for the multislice, the orientation map and the phase map are refined structures from the Crystallography Open Database, which is public domain, in CIF files that come with the samples: silicon (COD 2102763), aluminium (COD 4004108) and copper (COD 7101269).

Changes
~~~~~~~

- :py:meth:`~pyemaps.probe.Probe.crystal_potential` is computed in emaps, 3 to 4 times faster than in 2.8.0, with the same results.
- From emaps 2.6.0: :py:meth:`~pyemaps.crystals.Crystal.generateDPDB` checks the license before generating a database, and raises :py:class:`~pyemaps.errors.LicenseError` without an active one. Before, it ran without a license.
- The *al_orientmap.py* sample reads aluminium from its CIF file, and its ``map_scan`` function takes the crystal: ``map_scan(crystal=ALUMINIUM, seed=1)``. Its results are the same within the synthetic scan's noise.
- The probe notebook, :doc:`notebooks/probe`, no longer covers thick crystals, which moved to :doc:`notebooks/si_multislice`. It needs no license.

Improvements
~~~~~~~~~~~~

- Requires ``emaps >= 2.6.0``.

Version 2.8.0 Stable
--------------------

11-25-2026
~~~~~~~~~~

New
~~~

- :py:class:`~pyemaps.probe.Probe`: electron probes, Ronchigrams, contrast transfer functions and HREM images of a lens with aberrations, from J. M. Zuo's probe program, now part of emaps 2.5.0. Free, with no license needed. A probe holds the microscope settings: the high voltage, the aperture, the defocus, Cs, C5 and Cc, and the residual aberrations a corrector measures (a1 to a5, b2, b4, d4, s3). Its methods return NumPy arrays:

  - :py:meth:`~pyemaps.probe.Probe.ronchigram`: the shadow image of the probe through a thin sample, which corrector alignment is done on;
  - :py:meth:`~pyemaps.probe.Probe.probe` and :py:meth:`~pyemaps.probe.Probe.diameter`: the probe's intensity and the diameter holding a given share of it;
  - :py:meth:`~pyemaps.probe.Probe.ctf`: the contrast transfer function, with its temporal and spatial coherence envelopes;
  - :py:meth:`~pyemaps.probe.Probe.hrem` and :py:meth:`~pyemaps.probe.Probe.exit_wave`: the HREM image of a thin sample's exit wave, coherent or added up over the energy spread;
  - :py:meth:`~pyemaps.probe.Probe.phase_map`: the aberration function χ(k);
  - :py:meth:`~pyemaps.probe.Probe.stem_image` and :py:meth:`~pyemaps.probe.Probe.mtf`: the incoherent STEM image of a sample, and the probe's transfer function;
  - :py:meth:`~pyemaps.probe.Probe.apply_psf`: a camera's point spread function;
  - :py:meth:`~pyemaps.probe.Probe.focal_series`: any of these over a range of defocus;
  - :py:meth:`~pyemaps.probe.Probe.scherzer` and :py:meth:`~pyemaps.probe.Probe.haider`: the optimum defocus and aperture of an uncorrected and a corrected lens, and :py:meth:`~pyemaps.probe.Probe.optimize`: the defocus and residual aberrations that make the probe smallest;
  - :py:meth:`~pyemaps.probe.Probe.random_potential`: an amorphous sample, and :py:meth:`~pyemaps.probe.Probe.crystal_potential`: a pyEMAPS crystal along a zone axis, from its atoms;
  - :py:meth:`~pyemaps.probe.Probe.from_file`: the probe program's parameter files;
  - :py:meth:`~pyemaps.probe.Probe.show`: any result with its axes.

  Every setting has a default, the probe program's. The samples *ronchigram.py*, *stem_probe.py*, *ctf.py*, *hrem.py* and *crystal_imaging.py* show each mode, and the User Guide page :doc:`user_guide/probe` and the notebook :doc:`notebooks/probe` explain them. Needs emaps 2.5.0 or later.
- :doc:`user_guide/imaging`, a User Guide page on 4D-STEM imaging with virtual detectors: bright field, annular dark field and dark field images with :py:meth:`~pyemaps.stackimg.StackImage.generateBDF`, and detector masks with :py:meth:`~pyemaps.stackimg.StackImage.generateMaskedImage`. The documentation now shows the *adf* notebook, :doc:`notebooks/adf`, with its results.
- :py:meth:`~pyemaps.stackimg.StackImage.generateBDF` and :py:meth:`~pyemaps.stackimg.StackImage.generateMaskedImage` take an optional *title* for the image they display.

Changes
~~~~~~~

- :py:meth:`~pyemaps.stackimg.StackImage.generateBDF` and :py:meth:`~pyemaps.stackimg.StackImage.generateMaskedImage` title their images by the detector, such as "Ring Detector, Radii 50-200 px, Center (263, 263)" or "Masked Image, Mask mask.im3". Before, every image was titled "Dark or Bright Field Image", "Annular Dark or Bright Field Image" or "Experimental Diffraction Image - Masked".
- The *adf.py* sample centres its annular detector on the direct beam, at (263, 263), instead of the middle of the pattern, 7 pixels away, and titles its images "Annular Dark Field", "Dark Field" and "Masked Image".

Improvements
~~~~~~~~~~~~

- Requires ``emaps >= 2.5.0``.

Version 2.7.0 Stable
--------------------

11-25-2026
~~~~~~~~~~

New
~~~

- *rmax* in :py:meth:`~pyemaps.stackimg.StackImage.indexImage` and :py:meth:`~pyemaps.stackimg.StackImage.mapOrientation`: the outer radius, in pixels, of the peaks matched against the database. The default, None, keeps the automatic radius, two thirds of the distance from the pattern centre to the nearest edge, so results don't change unless you set it. Raise it when useful peaks lie further out. Needs emaps 2.4.0 or later.
- :py:meth:`~pyemaps.stackimg.StackImage.indexImage` and :py:meth:`~pyemaps.stackimg.StackImage.mapOrientation` warn when the diffraction pattern database doesn't reach as far out as the peaks they match: when its longest reflection is shorter than the outer radius divided by the camera constant. The warning gives the *gmax* to generate the database with. A database that is too short leaves out the outer reflections, and patterns index on fewer peaks with lower reliability. See :doc:`user_guide/indexing`.
- The image readers tell diffraction patterns from other images, such as STEM images and maps computed from spectra:

  - :py:attr:`ExperimentalImage.kind <pyemaps.expimage.ExperimentalImage.kind>` gives what the file says an image is: ``'diffraction'``, ``'real-space'``, ``'spectrum map'`` or ``'unknown'``. Only DigitalMicrograph and EMD files record enough to tell.
  - DigitalMicrograph and EMD files are read from their diffraction patterns by default, then from images of unknown kind, real-space images and spectrum maps. Images that are all zero are passed over.
  - :py:func:`pyemaps.image_datasets <pyemaps.expimage.image_datasets>` lists a file's images without reading them, with each one's title, kind, scan shape, pattern count and size, and whether :py:func:`~pyemaps.expimage.read_image` reads it by default.
  - :py:meth:`StackImage.from_file <pyemaps.stackimg.StackImage.from_file>` warns when the image it reads is a real-space image or a spectrum map, and says which dataset holds the file's diffraction patterns, or that it has none.
  - Thermo Fisher Velox images get the titles Velox shows them under, such as ``DF-S`` or ``Ta``, and ``dataset=`` accepts a title. Velox EELS and EDS maps are marked as spectrum maps.

  See "Does a file hold diffraction patterns?" in :doc:`user_guide/indexing`.

Changes
~~~~~~~

From emaps 2.4.0:

- 16-bit image stacks index correctly. Before, the peak search read their data as floating-point numbers, so indexing and orientation maps of 16-bit stacks, which most 4D-STEM detectors record, found no peaks or meaningless ones. Single patterns given as numpy arrays weren't affected.
- 4D-STEM indexing draws the database patterns faster, so its correlations and reliability indexes can differ from earlier versions in the last digits. On the patterns tested, no indexing result changed.
- Loading a diffraction pattern database frees the one loaded before. Before, each :py:meth:`~pyemaps.stackimg.StackImage.indexImage` and :py:meth:`~pyemaps.stackimg.StackImage.mapOrientation` call after the first kept the previous database in memory until Python exited. A database file that fails to load is now closed; before, it stayed open, and locked on Windows.
- The indexing details :py:meth:`~pyemaps.stackimg.StackImage.indexImage` prints:

  - show the peaks at their real positions. Before, each position was up to a pixel short, by the fraction of the pattern centre. Indexing itself always used the real centre.
  - are printed when the best match is the database's first pattern, number 0. Before, they said "Indexing details are not available".
  - The best-match line says the number is the pattern's number in the database, counting from 0.

Improvements
~~~~~~~~~~~~

From emaps 2.4.0:

- 4D-STEM indexing is about 3.5 to 4 times faster than with emaps 2.3.0. On a 6-core laptop, the orientation map of the *al_orientmap.py* sample takes about 23 milliseconds per pattern instead of 92, and a 64 x 64 scan of 256 x 256 pixel patterns about 2 minutes. The peak search is 2 to 3 times faster.

Other improvements:

- The documentation explains how far the database must reach (*gmax*) for the patterns being indexed, with a worked example, in :py:meth:`~pyemaps.stackimg.StackImage.indexImage`, :py:meth:`~pyemaps.stackimg.StackImage.mapOrientation`, :py:meth:`~pyemaps.crystals.Crystal.generateDPDB` and :doc:`user_guide/indexing`.
- Requires ``emaps >= 2.4.0``.

Version 2.6.0 Stable
--------------------

11-20-2026
~~~~~~~~~~

Changes
~~~~~~~

From emaps 2.3.0:

- emaps is built with the Intel Fortran Compiler ``ifx`` 2026.2 and Intel oneMKL 2026.2, instead of the classic Intel Fortran Compiler and oneMKL 2022.1. Some simulation results can differ from earlier versions in the last few digits.
- When 4D-STEM indexing finds no peak in a pattern, the pattern's correlation is reported as 0. Before, it was a leftover value from an earlier step.

Improvements
~~~~~~~~~~~~

From emaps 2.3.0:

- Bloch simulations with many beams are 6 to 10 times faster. A large Bloch run of SiAlON, for example, takes about 8 seconds instead of 52 on a 6-core laptop.
- 4D-STEM indexing, :py:meth:`~pyemaps.stackimg.StackImage.indexImage` and :py:meth:`~pyemaps.stackimg.StackImage.mapOrientation`, is 4 to 10 times faster, and uses all the computer's cores. On a 6-core laptop, an orientation map takes about a sixth of a second per pattern instead of 0.7 to 1.6 seconds. The results are the same, with the rotation changing by at most 0.002 degrees.
- The first licensed 4D-STEM call in each Python session takes about 0.1 seconds instead of 1 to 2: the license check no longer contacts the license server.
- emaps sets the OpenMP environment variable ``KMP_BLOCKTIME`` to 0, unless you have set it, so its worker threads stop as soon as each parallel step ends. This speeds up 4D-STEM indexing and Bloch runs.
- emaps' *COPYING* file lists Intel oneMKL 2026.2, the OpenMP runtime from the Intel Fortran Compiler 2026.2 and the C++ runtime from Visual Studio 2026, with their license terms.

Other improvements:

- The 4D-STEM notebooks, *al_ediom.ipynb* and *al_orientmap.ipynb*, are shown with their results in the documentation: see :doc:`user_guide/indexing`.
- Requires ``emaps >= 2.3.0``.

Version 2.5.0 Stable
--------------------

11-19-2026
~~~~~~~~~~

New
~~~

- Orientation maps of 4D-STEM scans (experimental): :py:meth:`StackImage.mapOrientation <pyemaps.stackimg.StackImage.mapOrientation>` indexes every pattern of a scan against a diffraction pattern database, as :py:meth:`~pyemaps.stackimg.StackImage.indexImage` indexes one, and returns an :py:class:`~pyemaps.orientmap.OrientationMap`. The map holds each pattern's status, reliability index and orientation, gives the beam direction as a zone axis and the orientation as Bunge Euler angles, colours the map by beam direction (inverse pole figure colours, with their key), and saves and loads it. This is a licensed feature. It finds the right orientations on simulated scans, but it hasn't yet been validated against an independent orientation map of real data, and its parameters, defaults and results may change in later releases. See :doc:`user_guide/indexing`, the *al_orientmap.py* sample and the *al_orientmap.ipynb* notebook.
- *min_snr* in :py:meth:`~pyemaps.stackimg.StackImage.indexImage` and :py:meth:`~pyemaps.stackimg.StackImage.mapOrientation`: the peak search keeps only peaks at least *min_snr* times the noise above the background around them. The default, 0, keeps every peak, as before. 3 suits noisy patterns such as 4D-STEM scans.

Changes
~~~~~~~

From emaps 2.2.0:

- Diffraction patterns that aren't square index correctly. Before, indexing one could crash Python or give a wrong result.
- Masked images (:py:meth:`~pyemaps.stackimg.StackImage.generateMaskedImage`) with a 16-bit integer mask give the right image. Before, the mask was read as floating-point numbers, and the image was wrong.
- The detector centre and radii of bright and dark field images (:py:meth:`~pyemaps.stackimg.StackImage.generateBDF`) are used to a fraction of a pixel. Before, they were cut to whole pixels. Images with whole-pixel values are unchanged.
- When the peak search's first pass, which finds the spot the search kernel is refined from, finds none, it is retried with a looser threshold instead of failing. Some noisy patterns that failed with "No diffraction peaks found" now index; patterns that indexed before give the same result. A peak near the image edge no longer takes the previous peak's position.

Improvements
~~~~~~~~~~~~

- The documentation of the indexing parameters is corrected. *peak_threshold* tests how closely a peak's shape matches the search kernel, not its brightness; for scans, 0.6 to 0.7 with *min_snr* 3 is recommended. *sigma* works best at about half the peaks' measured full width at half maximum: 3.0 for *al.img*.
- Requires ``emaps >= 2.2.0``.

Version 2.4.0 Stable
--------------------

11-18-2026
~~~~~~~~~~

New
~~~

- pyEMAPS reads experimental diffraction patterns from microscope and detector files itself, for 4D-STEM indexing and imaging. :py:meth:`StackImage.from_file <pyemaps.stackimg.StackImage.from_file>` creates an image from a file, and :py:func:`pyemaps.read_image <pyemaps.expimage.read_image>` returns the patterns as numpy arrays, with the scan shape, calibration and the file's metadata. Reading needs no license. The formats:

  - TIFF (``.tif``, ``.tiff``), including BigTIFF and ImageJ stacks over 4 GB.
  - Gatan DigitalMicrograph (``.dm3``, ``.dm4``), with the scan shape, calibration, high voltage and camera length DigitalMicrograph recorded.
  - EMD (``.emd``): Thermo Fisher Velox, and Berkeley EMD including py4DSTEM datacubes. These need the h5py package: ``pip install "pyemaps[emd]"``. On Python 3.15, h5py has no Windows release yet.
  - MRC (``.mrc``, ``.mrcs``, ``.st``), Quantum Detectors Merlin (``.mib``), PNG, BMP and JPEG pictures, and NumPy ``.npy`` arrays.

  *binning* and *scan_roi* read large patterns and scans within the 4D-STEM limits, and :py:meth:`convertImage <pyemaps.stackimg.StackImage.convertImage>` with ``nformat=E_FILE`` saves a converted copy in pyEMAPS' ``.im3`` format. See :doc:`user_guide/indexing`. We'd like to hear how these work with your files: contact us at support@emlabsoftware.com.
- CIF files in the CIF 2.0 format can be loaded with :py:meth:`~pyemaps.crystals.Crystal.from_cif`, as well as CIF 1.1.

Changes
~~~~~~~

- Anisotropic displacement parameters in a CIF file go to the atoms they're listed for, by the atom labels in ``_atom_site_aniso_label``. Before, they were assigned row by row, so when the anisotropic table listed only some atoms, or listed them in a different order (as most published structures with hydrogen atoms do), atoms got other atoms' values. Atoms the table doesn't list keep their isotropic value. Results change for such CIF files.
- CIF files that give ``_atom_site_Uiso_or_equiv`` instead of ``_atom_site_U_iso_or_equiv``, or a single atom written without a ``loop_``, now load. Before, they failed with an error.

Improvements
~~~~~~~~~~~~

- pyEMAPS reads CIF files with its own reader, following the IUCr CIF 1.1 and 2.0 standards, instead of the bundled PyCifRW package. Other CIF files give the same results as before, and the pyEMAPS package is smaller.
- Requires ``emaps >= 2.1.0``.

Version 2.3.0 Stable
--------------------

11-16-2026
~~~~~~~~~~

Changes
~~~~~~~

- Bloch and LACBED images are centred: the pattern's centre is at the image's centre. Before, every image from :py:meth:`~pyemaps.crystals.Crystal.generateBloch`, in both modes, and from :py:meth:`~pyemaps.crystals.Crystal.getBlochImages` was 2 rows too high, so images saved with earlier versions are offset by 2 rows from new ones. This comes from emaps 2.1.0.
- emaps 2.1.0 states its own license terms, in the *license.txt* file installed with it. emaps is free to use with pyEMAPS, including versions of pyEMAPS you have modified, and may be redistributed unmodified together with pyEMAPS. Its *COPYING* file lists the third-party software it includes, with their notices and license terms.

Improvements
~~~~~~~~~~~~

- From emaps 2.1.0:

  - The license checks of the 4D-STEM features use LicenseSpring C++ SDK 7.51.3, which comes with OpenSSL 3.5.7 and curl 8.21.0.
  - Third-party numerical routines in the 4D-STEM indexing are replaced by EMLab's own implementations. Results are unchanged.

- Requires ``emaps >= 2.1.0``.

Version 2.2.1 Stable
--------------------

11-16-2026
~~~~~~~~~~

Changes
~~~~~~~

- pyEMAPS stays under the GNU General Public License v3.0 or later, now with a linking exception that permits combining it with emaps, the separately licensed simulation engine it runs on. The exception is in the *license-exception.txt* file, installed with pyEMAPS, and on the :doc:`license` page. Each source file's license notice is now a short SPDX header that points to it.
- The commercial license covers the 4D-STEM features of emaps. pyEMAPS' own code is all under the GPL with the exception. How to buy and activate a license is unchanged.

Improvements
~~~~~~~~~~~~

- :py:func:`~pyemaps.display.showDif` and :py:func:`~pyemaps.display.showBloch` with ``layout='table'`` leave room for each pattern's caption, which no longer runs into the panel below it.
- :py:func:`~pyemaps.display.showBloch`'s "No intensity detected" message for a dark image fits its panel. Before, only fragments of it showed in a LACBED table.

Version 2.2.0 Stable
--------------------

11-14-2026
~~~~~~~~~~

New
~~~

- Jupyter notebooks, one for each sample, that walk through pyEMAPS step by step, with the physics behind each step: kinematic and dynamic diffraction, large-angle CBED, the scattering matrix, structure factors, stereographic projections, supercells, powder diffraction, and 4D-STEM indexing and virtual detectors. ``pyemaps -cp notebooks`` copies them into a *pyemaps_notebooks* folder. On GitHub, the `notebooks folder <https://github.com/emlab-solutions/pyemaps/tree/main/notebooks>`_ shows them with their results.
- In a Jupyter notebook, pyEMAPS draws its plots in the notebook, instead of in a separate window.
- ``pyemaps -cp`` takes ``samples`` or ``notebooks`` to copy only the sample scripts or only the notebooks; with neither, it copies both. It no longer overwrites files already there.
- Printing an :py:class:`~pyemaps.emcontrols.EMControl` or :py:class:`~pyemaps.emcontrols.SIMControl`, or showing one at the Python prompt, gives an aligned list of the controls, with the default value next to each control that was changed.

Changes
~~~~~~~

- Powder profiles from :py:meth:`~pyemaps.crystals.Crystal.generatePowder` put each peak at its scattering angle 2θ. Before, every peak was at θ, half its angle. This comes from emaps 2.0.1, so powder results change.
- A crystal simulated after another crystal now gives its own results. Before, a :py:class:`~pyemaps.crystals.Crystal` used after another one could reuse the other crystal's data, and deleting it could crash the current one.
- The built-in ``Germanium`` crystal declared the wrong origin for its space group, giving 16 atoms per cell instead of 8. Results for Germanium change.
- The sample scripts are rewritten for readability, and their functions have new names. Code that imports them from ``pyemaps.samples`` needs the new names.
- :py:meth:`~pyemaps.crystals.Crystal.printCSF` prints the right units: volts for electron structure factors, and 1/Angstrom^2 for the other electron types; the high voltage is in kV.

Improvements
~~~~~~~~~~~~

- From emaps 2.0.1:

  - :py:meth:`~pyemaps.stackimg.StackImage.loadImage` reads 16-bit 4D-STEM images correctly. Before, it returned wrong values for them, and loading a single pattern could crash Python.
  - A one-character mask file name in :py:meth:`~pyemaps.stackimg.StackImage.generateMaskedImage` no longer crashes Python.

- :py:func:`~pyemaps.display.showDif` with ``layout='table'`` frames each pattern, and hides indices cut off at its edge.
- Fixed samples: *si_constructor.py* always builds the supercell, *dm_diff.py* saves the images it reports, and *si_scm.py* always closes its session.
- :py:meth:`~pyemaps.crystals.Crystal.generatePowder` documents *gamma* as the peaks' full width at half maximum.
- The README, Get Started, User Guide and Help pages are corrected throughout, checked against the code.
- pyEMAPS files on PyPI now come with provenance attestations, which link each file to the GitHub workflow and commit that built it.
- Requires ``emaps >= 2.0.1``.

Version 2.1.0 Stable
--------------------

11-12-2026
~~~~~~~~~~

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

- Requires ``emaps >= 2.0.0``.

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




    