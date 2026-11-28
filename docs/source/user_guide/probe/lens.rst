The lens and its aberrations
============================

:py:class:`~pyemaps.probe.Probe` holds a lens: its settings, the map its results are computed
on, and the phase error χ(k) it adds at each spatial frequency. Every page in this section
starts from one.

.. seealso::

   Step 2 of the step-by-step guide, the notebook :doc:`probe.ipynb <../../notebooks/probe>`, sets
   up a lens and draws its aberration function, shown here with its plots and output.

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
