Probes, Ronchigrams, CTF and HREM
=================================

A lens adds a phase error χ(k) to the part of the electron wave travelling at each spatial
frequency k: from the defocus, the spherical aberration Cs (C3) and C5, and in a real lens the
residual aberrations a corrector measures. :py:class:`~pyemaps.probe.Probe` holds such a lens
and computes what it does, in four modes:

- **Ronchigram**: the shadow image of a convergent probe through a thin amorphous sample, the
  pattern correctors are aligned on;
- **Probe**: the STEM probe's intensity in the sample plane, and its diameter;
- **CTF**: the contrast transfer function of an objective lens, with its coherence envelopes;
- **HREM**: the high-resolution TEM image of a thin sample.

This feature needs no license.

.. seealso::

   The notebook :doc:`../notebooks/probe` explains the physics and runs all four modes step by
   step, shown here with its plots and output.

.. toctree::
   :hidden:

   ../notebooks/probe

The lens
--------

.. code-block:: python

   from pyemaps import Probe

   corrector = {'a1': (1.349, 146.2), 'a2': (58.94, -131.9), 'b2': (22.89, 141.4)}
   lens = Probe(kv=200, aperture=25, defocus=-5.14, cs=-0.00355, c5=3.829,
                aberrations=corrector, size=100, sampling=256)
   print(lens)

A :py:class:`~pyemaps.probe.Probe` takes its settings as keyword arguments, all optional, and
keeps them as attributes you can change between calculations:

- *kv*: the high voltage, in kV;
- *aperture*: the aperture semi-angle, in mrad: the probe's convergence angle, or the objective
  aperture for HREM. :py:attr:`~pyemaps.probe.Probe.kmax` gives it in 1/Å;
- *defocus*, in nm, negative for underfocus; *cs* and *c5*, in mm;
- *cc*, in mm, and *energy_spread*, in eV, for the chromatic aberration;
- *semi_angle*: the illumination semi-angle, in mrad, for the spatial coherence of the CTF and
  HREM images;
- *tilt*: the beam tilt, amplitude in mrad and direction in degrees; *rotation*: the
  rotation of the residual aberrations, in degrees;
- *aberrations*: the residual aberrations, ``{name: (amplitude, angle)}``, or one at a time
  with :py:meth:`~pyemaps.probe.Probe.set_aberration`. Two-fold astigmatism a1, three-fold
  a2 and coma b2 are in nm; a3, a4, s3, b4 and d4 in µm; a5 in mm.

:py:meth:`Probe.from_file <pyemaps.probe.Probe.from_file>` reads the settings from a probe
program parameter file, with lines such as ``kv 200``, ``df -5.14`` or ``a1 1.349 146.2``.

**The map.** Results are computed on a square map *size* Å across, with *sampling* x
*sampling* pixels. The probe, the sample and HREM images are in real space, with pixels of
``size / sampling`` Å. The Ronchigram and the CTF are in reciprocal space, with pixels of
``1 / size`` 1/Å; a Ronchigram reaches ``1000 * wavelength * sampling / (2 * size)`` mrad from
its center. :py:meth:`~pyemaps.probe.Probe.show` displays any result with its axes, and
:py:meth:`~pyemaps.probe.Probe.extent` gives those axes for your own plots. The sampling can be
up to 32768 pixels, as memory allows.

**The aberration function.** :py:meth:`~pyemaps.probe.Probe.phase_map` returns χ(k) itself, in
radians, the phase the lens adds at each spatial frequency. Where it stays within about π/4 of
its value at the center, the lens is free of aberrations; that region sets how large an aperture
can be used. ``lens.show(lens.phase_map(), 'phase')`` draws it with the aperture.

Ronchigram
----------

:py:meth:`~pyemaps.probe.Probe.ronchigram` takes the sample's projected potential, a
*sampling* x *sampling* array. By default, it's
:py:meth:`~pyemaps.probe.Probe.random_potential`: 100 Å of amorphous aluminium, 0.05 atoms
per Å³, with a fixed random number seed. Change the density, atomic number, thickness or seed
there, or pass a potential of your own.

.. code-block:: python

   lens.show(lens.ronchigram(), 'ronchigram')

The map has to be large for the Ronchigram to reach beyond the aperture: 100 Å with 256 pixels
reaches 32 mrad at 200 kV. The sample *ronchigram.py* compares a corrected probe, the same with
two-fold astigmatism, and an uncorrected one, with the phase map behind each:

.. image:: ../_static/images/probe_ronchigram.png
   :width: 100%

The Ronchigram doesn't include the chromatic aberration.

Probe
-----

:py:meth:`~pyemaps.probe.Probe.probe` returns the probe's intensity, normalized to a sum of 1.
With *cc* of 0.01 mm or more, it's the sum of the probes over the energy spread.
:py:meth:`~pyemaps.probe.Probe.diameter` gives the diameter of the circle holding a share of
the intensity. It counts whole pixels, so compute the probe on a map with pixels much smaller
than the probe, such as 0.05 Å:

.. code-block:: python

   fine = Probe(kv=200, aperture=25, c5=3.829, size=25.6, sampling=512)
   fine.haider(optimum_aperture=False)     # the Cs and defocus that balance C5 at 25 mrad
   print(f'{fine.diameter(50):.2f} Å')     # 0.54 Å

Two methods set the optimum settings:

- :py:meth:`~pyemaps.probe.Probe.scherzer` sets the Scherzer defocus and aperture of an
  uncorrected lens, from Cs;
- :py:meth:`~pyemaps.probe.Probe.haider` sets the Cs and defocus that balance C5 in a corrected
  lens, and the aperture too unless you keep yours, after Haider et al., *Ultramicroscopy*
  (2000).

:py:meth:`~pyemaps.probe.Probe.optimize` searches for the defocus and residual aberrations
that make the probe smallest, as the probe program's optimize command did, with the
Nelder-Mead simplex method. It minimizes the diameter as ``diameter(interpolate=True)``
measures it, interpolating between pixels so that it changes smoothly:

.. code-block:: python

   fine.set_aberration('a1', 15.0, 40.0)                   # 15 nm of two-fold astigmatism
   result = fine.optimize(percent=50, vary=('defocus', 'a1'))
   print(result['diameter'], result['a1'])                 # a1 tuned back to about 0

**STEM images.** :py:meth:`~pyemaps.probe.Probe.stem_image` gives the incoherent (annular dark
field) STEM image of a sample: the probe's intensity convolved with its projected potential.
:py:meth:`~pyemaps.probe.Probe.mtf` gives the probe's modulation transfer function, the
amplitude of the Fourier transform of its intensity, which says how strongly each spatial
frequency of the sample shows in such an image.

:py:meth:`~pyemaps.probe.Probe.focal_series` computes a probe, Ronchigram, CTF, HREM or STEM
image, or phase map at each of a list of defocus values, as a stack.

The sample *stem_probe.py* compares an uncorrected probe at its Scherzer settings with a
corrected one at the Haider settings, with and without a corrector's measured residual
aberrations. It shows the uncorrected probe's size across defocus, the STEM images of a thin
amorphous sample and the probes' MTFs, then tunes out the measured astigmatism with
:py:meth:`~pyemaps.probe.Probe.optimize`:

.. image:: ../_static/images/probe_stem_probe.png
   :width: 100%

CTF
---

:py:meth:`~pyemaps.probe.Probe.ctf` returns sin χ, damped by the temporal coherence envelope
(from *cc* and *energy_spread*) and the spatial one (from *semi_angle*), within 80% of the map's
radius. It isn't cut off at the aperture. ``scherzer(mode=2)`` sets the Scherzer defocus for
phase contrast, where the CTF keeps one sign out to the point resolution.

.. code-block:: python

   tem = Probe(kv=200, cs=1.2, cc=1.5, energy_spread=0.7, semi_angle=0.2,
               size=200, sampling=1024)
   tem.scherzer(mode=2)
   ctf = tem.ctf()

An uncorrected lens's CTF oscillates fast at high frequencies, so it needs fine reciprocal
pixels, that is, a large map: 200 Å gives 0.005 1/Å. The sample *ctf.py* shows the CTF with
and without the envelopes, at and around the Scherzer defocus, and for a corrected lens:

.. image:: ../_static/images/probe_ctf.png
   :width: 100%

HREM
----

:py:meth:`~pyemaps.probe.Probe.hrem` images a sample's exit wave through the lens, used as the
objective lens: the aperture, the aberrations and the coherence envelopes. The direct beam
passes unchanged. :py:meth:`~pyemaps.probe.Probe.exit_wave` gives the exit wave of a thin sample
from its projected potential, and an exit wave from a multislice program works too. With
``integrate=True``, the images are added up over the energy spread instead of damped by the
temporal envelope.

.. code-block:: python

   tem = Probe(kv=200, cs=1.2, cc=1.5, energy_spread=0.7, semi_angle=0.2,
               size=100, sampling=512)
   tem.scherzer(mode=2)
   tem.aperture = 20.0                     # the objective aperture
   carbon = tem.random_potential(density=0.1, z=6, thickness=50, seed=7)
   image = tem.hrem(tem.exit_wave(carbon))
   tem.show(image, 'hrem')

A camera blurs the image it records. :py:meth:`~pyemaps.probe.Probe.apply_psf` applies a
detector's point spread function, through its transfer function ``a / (1 + b w²) + 1 - a`` at
w cycles per pixel, as the probe program's psf command did. The defaults, *a* = 0.6 and
*b* = 400, are typical of a camera: they transfer about 0.4 at the Nyquist frequency.

.. code-block:: python

   recorded = tem.apply_psf(image)                     # a=0.6, b=400.0
   sharper = tem.apply_psf(image, a=0.3, b=400.0)      # a better camera

The image of an amorphous sample shows the CTF in its Fourier transform, as Thon rings. The
sample *hrem.py* shows images at the Scherzer defocus, further underfocus, with two-fold
astigmatism, which makes the rings elliptical, and as a camera records them:

.. image:: ../_static/images/probe_hrem.png
   :width: 100%

Crystals
--------

Any of the samples above can be a crystal instead of an amorphous film.
:py:meth:`~pyemaps.probe.Probe.crystal_potential` builds the projected potential of a pyEMAPS
crystal along a zone axis: the atoms of a slab of the given thickness, each with its projected
atomic potential, added up. Pass it wherever a potential goes: to
:py:meth:`~pyemaps.probe.Probe.ronchigram`, :py:meth:`~pyemaps.probe.Probe.stem_image` or
:py:meth:`~pyemaps.probe.Probe.exit_wave`.

.. code-block:: python

   from pyemaps import Crystal, Probe

   si = Crystal.from_builtin('Silicon')
   a = float(si.cell.a)
   lens = Probe(kv=200, size=12 * a, sampling=1024)
   potential = lens.crystal_potential(si, zone=(1, 1, 0), thickness=30)
   lens.show(potential, 'potential')

The unit cell is filled from the space group by
:py:meth:`~pyemaps.crystals.Crystal.generateMxtal`, and emaps computes the potential. Each
atom's potential comes from its electron scattering factor, as emaps' structure factors have
it, with its Debye–Waller factor and occupancy. The beam is along the zone axis. *x_axis* sets
the direction along the map's columns; by default, it's the shortest lattice direction
perpendicular to the zone axis. *shift* moves the crystal on the map.

Like the random potential, it's the whole slab projected onto one plane, so it suits thin
crystals: the electrons don't propagate through the thickness. For thicker crystals, see
`Thick crystals`_ below.

**Maps without a seam.** The map repeats itself at its edges. Unless its *size* is a whole
number of the crystal's repeats across and down, the crystal has a seam there, away from the
probe at the map's center. :py:meth:`~pyemaps.probe.Probe.crystal_repeats` gives those
repeats, centering included, and the map sizes that hold whole numbers of them.
``fit=True`` then strains the crystal very slightly in the plane of the map, so that it
repeats exactly at the map's edges:

.. code-block:: python

   lens.crystal_repeats(si, zone=(1, 1, 0), max_size=70)
   # {'x_axis': (0, 0, 1), 'repeats': ((0.0, 3.8401), (-5.4307, 0.0)),
   #  'period': 3.8401, 'sizes': [(65.168, 0.00173), (65.281, 0.00173)]}
   potential = lens.crystal_potential(si, zone=(1, 1, 0), thickness=30, fit=True)

Along [110] in silicon, with [001] across, the repeats are *a* = 5.43 Å and *a*/√2 = 3.84 Å;
12 *a* = 65.17 Å is 17 of the second within 0.17%, which ``fit=True`` removes. A strain above
1% gives a warning: choose a size from the list instead.

The sample *crystal_imaging.py* shows silicon's [110] dumbbells, two columns 1.36 Å apart, in
HREM and STEM images with an uncorrected and a corrected lens, and the corrected probe's
Ronchigram, where the crystal's diffracted disks overlap. Only the corrected lenses resolve the
dumbbells. At the Scherzer defocus the columns are dark. With the corrected lens's negative Cs,
they're bright:

.. image:: ../_static/images/probe_crystal.png
   :width: 100%

Thick crystals
--------------

As a crystal gets thicker, the electron wave is scattered again and again on its way through
it, and the projected potential no longer tells the whole story. The multislice method follows
the wave through the crystal slice by slice (J. M. Cowley and A. F. Moodie; E. J. Kirkland,
*Advanced Computing in Electron Microscopy*). It's a licensed feature: it needs an active
pyEMAPS license, and raises :py:class:`~pyemaps.errors.LicenseError` without one. Run
``pyemaps -l trial`` for a 7-day trial license.

- :py:meth:`~pyemaps.probe.Probe.crystal_exit_wave`: the exit wave under plane-wave
  illumination; pass it to :py:meth:`~pyemaps.probe.Probe.hrem` for the HREM image.
- :py:meth:`~pyemaps.probe.Probe.crystal_ronchigram`: the probe's Ronchigram through the
  crystal; with a small aperture and the probe focused, a convergent-beam diffraction (CBED)
  pattern.

.. code-block:: python

   tem = Probe(kv=200, cs=-0.013, defocus=7.0, aperture=40.0, cc=1.5, energy_spread=0.7,
               semi_angle=0.2, size=12 * a, sampling=512)
   waves = tem.crystal_exit_wave(si, zone=(1, 1, 0), thickness=[20, 100, 300], fit=True)
   images = [tem.hrem(wave) for wave in waves]

A list of thicknesses gives the waves at each from one pass through the crystal. The crystal
repeats along the zone axis (``crystal_repeats()['period']``), so the slices of one repeat,
about *slice_thickness* = 2 Å each, serve for every repeat, and each thickness is rounded to a
whole number of slices. emaps computes everything: each slice's potential, from its atoms,
its transmission function, and the propagation between slices.

**Sampling.** The slices are band-limited to 2/3 of the map's largest spatial frequency,
``sampling / (2 * size)``, so their products don't alias. What the crystal scatters beyond
that is lost, and the wave's total intensity drops a little. Thick crystals need fine
pixels: with 0.13 Å pixels (512 over 65 Å), 200 Å of silicon keeps 99% of the intensity;
with 0.25 Å, 93%. A larger map makes finer angles in a CBED pattern or Ronchigram, since each
pixel there is ``1 / size``.

The beam is along the zone axis, and there is no absorption or thermal diffuse scattering. For
silicon [001], the beam intensities agree with emaps' Bloch-wave calculation, which includes
absorption, within 5% up to 200 Å.

The sample *crystal_thickness.py* shows silicon [110] at three thicknesses: the HREM images,
where the dumbbells turn into bars and then into a different pattern, and the CBED patterns,
where fringes appear inside the disks:

.. image:: ../_static/images/probe_multislice.png
   :width: 100%

The calculations come from the probe program by J. M. Zuo, now part of emaps.
