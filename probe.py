# This file is part of pyEMAPS.
# Copyright (C) 2021-2026 EMLab Solutions, Inc.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Additional permission under GPLv3 Section 7:
# See license-exception.txt for the exception permitting
# combination with the separately licensed backend, emaps.

'''
Electron probes, Ronchigrams and contrast transfer functions of a probe-forming lens with
aberrations, from emaps' probe module.

A :py:class:`Probe` holds the microscope settings: the high voltage, the aperture, the defocus,
the spherical, fifth-order and chromatic aberrations, the residual aberrations a corrector
measures (a1 to a5, b2, b4, d4, s3), and the map the results are computed on. Its methods return
the results as NumPy arrays:

- :py:meth:`~Probe.ronchigram`: the Ronchigram, the shadow image of the probe through a thin
  sample, of a random amorphous potential or one you give;
- :py:meth:`~Probe.probe`: the probe's intensity, and :py:meth:`~Probe.diameter` its size;
- :py:meth:`~Probe.ctf`: the contrast transfer function, with its coherence envelopes.

:py:meth:`~Probe.scherzer` and :py:meth:`~Probe.haider` set the defocus and aperture to the
optimum for an uncorrected or a corrected lens, and :py:meth:`~Probe.show` displays the results
with their axes.
'''

import math
import os

import numpy as np

try:
    from emaps.probe import probesim
except ImportError:  # an emaps without the probe module
    probesim = None

#: The residual aberrations, in the order the backend takes them, with their units:
#: two-fold astigmatism a1, three-fold astigmatism a2, four-fold a3, five-fold a4, six-fold
#: a5, axial coma b2, axial star aberration s3, fourth-order coma b4 and three-lobe
#: aberration d4.
ABERRATIONS = {'a1': 'nm', 'a2': 'nm', 'a3': 'um', 'a4': 'um', 'a5': 'mm',
               'b2': 'nm', 'b4': 'um', 'd4': 'um', 's3': 'um'}

_ERRORS = {1: 'the map is invalid: sampling must be an even number of at least 8 pixels, '
              'and size positive',
           2: 'the microscope settings are invalid: high voltage and aperture must be '
              'positive, cc and energy_spread not negative, and energy_spread positive with cc'}


def _backend():
    if probesim is None:
        raise ImportError('The probe simulations need an emaps with the probe module: '
                          'pip install --upgrade emaps')
    return probesim


class Probe:
    '''
    A probe-forming lens and the map its probe, Ronchigram and CTF are computed on.

    :param kv: high voltage, in kV.
    :type kv: float, optional
    :param aperture: aperture semi-angle (convergence angle), in mrad.
    :type aperture: float, optional
    :param defocus: defocus, in nm. Negative values are underfocus.
    :type defocus: float, optional
    :param cs: spherical aberration C3, in mm.
    :type cs: float, optional
    :param c5: fifth-order spherical aberration C5, in mm.
    :type c5: float, optional
    :param cc: chromatic aberration, in mm. With 0.01 mm or more, :py:meth:`probe` adds up the
        probes over the energy spread, and :py:meth:`ctf` includes the temporal coherence
        envelope. The Ronchigram doesn't include it.
    :type cc: float, optional
    :param energy_spread: energy spread of the beam, full width at half maximum, in eV.
    :type energy_spread: float, optional
    :param semi_angle: illumination semi-angle, in mrad, for the spatial coherence envelope of
        :py:meth:`ctf`.
    :type semi_angle: float, optional
    :param tilt: beam tilt: amplitude, in mrad, and direction, in degrees.
    :type tilt: tuple of float, optional
    :param rotation: rotation of the residual aberrations, in degrees.
    :type rotation: float, optional
    :param aberrations: residual aberrations, ``{name: (amplitude, angle)}``, with the angle in
        degrees and the amplitude in the units of :py:data:`ABERRATIONS`, for example
        ``{'a1': (1.35, 146.2), 'b2': (22.9, 141.4)}``. Those not given are 0.
    :type aberrations: dict, optional
    :param size: width and height of the map, in Å. The probe and the sample are in a square of
        this size; the Ronchigram and the CTF extend to ``sampling / (2 * size)`` 1/Å from their
        center.
    :type size: float, optional
    :param sampling: pixels along each side of the map, an even number.
    :type sampling: int, optional

    The defaults are those of the probe program: 200 kV, Cs 1 mm, a 20 Å map of 256 x 256
    pixels, with a 10 mrad aperture.
    '''

    def __init__(self, kv=200.0, aperture=10.0, defocus=0.0, cs=1.0, c5=0.0, cc=0.0,
                 energy_spread=0.7, semi_angle=0.1, tilt=(0.0, 0.0), rotation=0.0,
                 aberrations=None, size=20.0, sampling=256):
        self.kv = float(kv)
        self.aperture = float(aperture)
        self.defocus = float(defocus)
        self.cs = float(cs)
        self.c5 = float(c5)
        self.cc = float(cc)
        self.energy_spread = float(energy_spread)
        self.semi_angle = float(semi_angle)
        self.tilt = (float(tilt[0]), float(tilt[1]))
        self.rotation = float(rotation)
        self.size = float(size)
        self.sampling = int(sampling)
        self._aberrations = {name: (0.0, 0.0) for name in ABERRATIONS}
        for name, value in (aberrations or {}).items():
            self.set_aberration(name, *value)

    # ------------------------------------------------------------------ settings
    @property
    def wavelength(self):
        '''The electron wavelength, in Å, relativistically corrected.'''
        return 0.3878314 / math.sqrt(self.kv * (1.0 + 0.97846707e-3 * self.kv))

    @property
    def kmax(self):
        '''The aperture's radius in reciprocal space, in 1/Å.'''
        return self.aperture / 1000.0 / self.wavelength

    @property
    def aberrations(self):
        '''The residual aberrations, ``{name: (amplitude, angle)}``. A copy: change them with
        :py:meth:`set_aberration`.'''
        return dict(self._aberrations)

    def set_aberration(self, name, amplitude, angle=0.0):
        '''
        Set a residual aberration.

        :param name: its name: ``'a1'``, ``'a2'``, ``'a3'``, ``'a4'``, ``'a5'``, ``'b2'``,
            ``'b4'``, ``'d4'`` or ``'s3'``.
        :type name: str
        :param amplitude: its amplitude, in the units of :py:data:`ABERRATIONS`.
        :type amplitude: float
        :param angle: its angle, in degrees.
        :type angle: float, optional
        :raise ValueError: if *name* isn't one of them.
        '''
        key = str(name).lower()
        if key not in ABERRATIONS:
            raise ValueError(f'Unknown aberration {name!r}: use one of {", ".join(ABERRATIONS)}')
        self._aberrations[key] = (float(amplitude), float(angle))

    def zero_aberrations(self):
        '''Set all residual aberrations to 0.'''
        self._aberrations = {name: (0.0, 0.0) for name in ABERRATIONS}

    def __repr__(self):
        res = [n for n, (a, _) in self._aberrations.items() if a != 0.0]
        return (f'Probe({self.kv:g} kV, aperture {self.aperture:g} mrad, defocus '
                f'{self.defocus:g} nm, Cs {self.cs:g} mm, C5 {self.c5:g} mm, Cc {self.cc:g} mm; '
                f'residual aberrations: {", ".join(res) if res else "none"}; '
                f'{self.size:g} A map of {self.sampling} x {self.sampling})')

    def _mic(self):
        return np.array([self.kv, self.aperture, self.defocus, self.cs, self.c5, self.cc,
                         self.energy_spread, self.semi_angle, self.tilt[0], self.tilt[1],
                         self.rotation], dtype=np.float32)

    def _abr(self):
        amp = np.array([self._aberrations[n][0] for n in ABERRATIONS], dtype=np.float32)
        ang = np.array([self._aberrations[n][1] for n in ABERRATIONS], dtype=np.float32)
        return amp, ang

    def _image(self, data, ierr):
        if ierr != 0:
            raise ValueError(f'Probe simulation failed: {_ERRORS.get(ierr, f"error {ierr}")}')
        return np.asarray(data).reshape(self.sampling, self.sampling)

    # ------------------------------------------------------------------ results
    def random_potential(self, density=0.05, z=13.0, thickness=100.0, seed=1211):
        '''
        A random potential of an amorphous sample: atoms of one element at random positions,
        each a point-like potential, projected through the sample's thickness.

        :param density: number of atoms per Å³.
        :type density: float, optional
        :param z: their atomic number.
        :type z: float, optional
        :param thickness: the sample's thickness, in Å.
        :type thickness: float, optional
        :param seed: the random number seed, a positive integer. The same seed gives the same
            potential.
        :type seed: int, optional
        :return: the projected potential, ``(sampling, sampling)``, rows then columns.
        :rtype: numpy.ndarray
        :raise ValueError: if a setting is invalid.

        The defaults are those of the probe program: 100 Å of amorphous aluminium.
        '''
        if int(seed) <= 0:
            raise ValueError('seed must be a positive integer')
        v, ierr = _backend().potential(self.size, self.sampling, density, z, thickness,
                                       int(seed))
        if ierr == 2:
            raise ValueError('density and thickness must not be negative')
        return self._image(v, ierr)

    def ronchigram(self, potential=None):
        '''
        The Ronchigram: the intensity of the probe after a thin sample, in the far field.

        :param potential: the sample's projected potential, ``(sampling, sampling)``, covering
            the map. By default, :py:meth:`random_potential` with its defaults.
        :type potential: numpy.ndarray, optional
        :return: the Ronchigram, ``(sampling, sampling)``, with the beam at the center. Each pixel
            is ``1 / size`` 1/Å, or ``1000 * wavelength / size`` mrad.
        :rtype: numpy.ndarray
        :raise ValueError: if a setting is invalid or *potential* has the wrong shape.
        '''
        if potential is None:
            potential = self.random_potential()
        v = np.asarray(potential, dtype=np.float32)
        if v.shape != (self.sampling, self.sampling):
            raise ValueError(f'potential must be {self.sampling} x {self.sampling}, the sampling, '
                             f'not {" x ".join(str(s) for s in v.shape)}')
        amp, ang = self._abr()
        img, ierr = _backend().ronchigram(self._mic(), amp, ang, self.size, self.sampling,
                                          v.ravel())
        return self._image(img, ierr)

    def probe(self):
        '''
        The probe's intensity in the sample plane, normalized to a sum of 1.

        :return: the intensity, ``(sampling, sampling)``, with the probe at the center. Each
            pixel is ``size / sampling`` Å.
        :rtype: numpy.ndarray
        :raise ValueError: if a setting is invalid.
        '''
        amp, ang = self._abr()
        img, ierr = _backend().probeimage(self._mic(), amp, ang, self.size, self.sampling)
        return self._image(img, ierr)

    def diameter(self, percent=50.0, probe=None):
        '''
        The probe's diameter: that of the circle around the map's center that holds *percent*
        percent of its intensity.

        :param percent: the share of the intensity, in percent.
        :type percent: float, optional
        :param probe: the probe intensity from :py:meth:`probe`. By default, computed.
        :type probe: numpy.ndarray, optional
        :return: the diameter, in Å.
        :rtype: float
        :raise ValueError: if *percent* isn't between 0 and 100, or the probe has no intensity
            near the center of the map.

        The circle counts whole pixels, so the diameter changes in steps of about a pixel, and
        probes of slightly different sizes can give the same value. Use a map whose pixels
        (*size* / *sampling*) are much smaller than the probe, such as 0.1 Å.
        '''
        if not 0.0 < percent < 100.0:
            raise ValueError('percent must be between 0 and 100')
        img = self.probe() if probe is None else np.asarray(probe, dtype=np.float32)
        if img.shape != (self.sampling, self.sampling):
            raise ValueError(f'probe must be {self.sampling} x {self.sampling}, the sampling')
        d = _backend().probediameter(self.size, self.sampling, img.ravel(), percent)
        if d < 0:
            raise ValueError('The probe has no intensity near the center of the map')
        return float(d)

    def ctf(self):
        '''
        The contrast transfer function, sin(χ), damped by the temporal coherence envelope (from
        *cc* and *energy_spread*) and the spatial one (from *semi_angle*). It's computed within
        80% of the map's radius and is 0 outside.

        :return: the CTF, ``(sampling, sampling)``, with zero frequency at the center. Each
            pixel is ``1 / size`` 1/Å.
        :rtype: numpy.ndarray
        :raise ValueError: if a setting is invalid.
        '''
        amp, ang = self._abr()
        img, ierr = _backend().ctfimage(self._mic(), amp, ang, self.size, self.sampling)
        return self._image(img, ierr)

    # ------------------------------------------------------------------ optimum settings
    def scherzer(self, mode=1):
        '''
        Set the Scherzer defocus and aperture of an uncorrected lens, from Cs.

        :param mode: 1 for the optimum probe (defocus -sqrt(Cs λ), kmax (4 / (Cs λ³))^¼),
            2 for the optimum phase contrast (defocus -sqrt(1.5 Cs λ), kmax (6 / (Cs λ³))^¼).
        :type mode: int, optional
        :return: the settings: ``defocus`` (nm), ``aperture`` (mrad), ``kmax`` (1/Å), and with
            mode 1 the probe's ``fwhm`` (Å).
        :rtype: dict
        :raise ValueError: if Cs isn't positive or *mode* isn't 1 or 2.
        '''
        if self.cs <= 0.0:
            raise ValueError('The Scherzer settings need a positive Cs')
        cs, lam = self.cs * 1.0e7, self.wavelength
        if mode == 1:
            df, kmax = -math.sqrt(cs * lam) / 10, (4 / cs / lam ** 3) ** 0.25
        elif mode == 2:
            df, kmax = -math.sqrt(1.5 * cs * lam) / 10, (6 / cs / lam ** 3) ** 0.25
        else:
            raise ValueError('mode must be 1 or 2')
        self.defocus, self.aperture = df, kmax * lam * 1000.0
        result = {'defocus': df, 'aperture': self.aperture, 'kmax': kmax}
        if mode == 1:
            result['fwhm'] = 0.43 * cs ** 0.25 * lam ** 0.75
        return result

    def haider(self, optimum_aperture=True):
        '''
        Set the defocus and Cs that balance C5 in a corrected lens (Haider et al.,
        Ultramicroscopy, 2000).

        :param optimum_aperture: also set the aperture to its optimum for C5, and Cs and the
            defocus for it. With False, keep the aperture and set Cs and the defocus for it.
        :type optimum_aperture: bool, optional
        :return: the settings: ``defocus`` (nm), ``cs`` (mm) and ``aperture`` (mrad), and with
            *optimum_aperture* the expected ``resolution`` (Å).
        :rtype: dict
        :raise ValueError: if C5 isn't positive.
        '''
        if self.c5 <= 0.0:
            raise ValueError('The corrected-lens settings need a positive C5')
        c5, lam = self.c5 * 1.0e7, self.wavelength
        result = {}
        if optimum_aperture:
            self.defocus = 2.0 * (lam ** 2 * c5) ** (1 / 3) / 10
            self.cs = -3.2 * (lam * c5 ** 2) ** (1 / 3) / 1.0e7
            self.aperture = 7 * (lam / c5) ** (1 / 6) / 4 * 1000.0
            result['resolution'] = lam / (lam / c5) ** (1 / 6) / 3
        else:
            wa = self.aperture / 1000.0
            self.defocus = 0.144 * wa ** 4 * c5 / 10
            self.cs = -0.92 * wa ** 2 * c5 / 1.0e7
        result.update(defocus=self.defocus, cs=self.cs, aperture=self.aperture)
        return result

    # ------------------------------------------------------------------ display
    def extent(self, kind):
        '''
        The axis extent of a result for :py:func:`matplotlib.pyplot.imshow`.

        :param kind: ``'probe'`` or ``'potential'`` (Å), ``'ronchigram'`` (mrad) or ``'ctf'``
            (1/Å).
        :type kind: str
        :return: ``(left, right, bottom, top)``.
        :rtype: tuple
        '''
        n, half = self.sampling, 0.5
        if kind in ('probe', 'potential'):
            step = self.size / n
        elif kind == 'ronchigram':
            step = 1000.0 * self.wavelength / self.size
        elif kind == 'ctf':
            step = 1.0 / self.size
        else:
            raise ValueError("kind must be 'probe', 'potential', 'ronchigram' or 'ctf'")
        # pixel n/2 (from 0) is the center
        lo, hi = (-n / 2 - half) * step, (n / 2 - 1 + half) * step
        return (lo, hi, hi, lo)

    def show(self, image, kind, ax=None, title=None, aperture=True):
        '''
        Display a result with its axes.

        :param image: the result, from :py:meth:`ronchigram`, :py:meth:`probe`, :py:meth:`ctf`
            or :py:meth:`random_potential`.
        :type image: numpy.ndarray
        :param kind: ``'ronchigram'``, ``'probe'``, ``'ctf'`` or ``'potential'``.
        :type kind: str
        :param ax: the axes to draw in. By default, a new figure, shown.
        :type ax: matplotlib.axes.Axes, optional
        :param title: the title. By default, the kind and the main settings.
        :type title: str, optional
        :param aperture: on a Ronchigram or CTF, draw the aperture's edge.
        :type aperture: bool, optional
        :return: the axes.
        :rtype: matplotlib.axes.Axes
        '''
        import matplotlib.pyplot as plt

        labels = {'ronchigram': ('Ronchigram', 'mrad'), 'probe': ('Probe', 'Å'),
                  'ctf': ('CTF', '1/Å'), 'potential': ('Potential', 'Å')}
        if kind not in labels:
            raise ValueError("kind must be 'probe', 'potential', 'ronchigram' or 'ctf'")
        name, unit = labels[kind]
        new = ax is None
        if new:
            _, ax = plt.subplots(figsize=(6, 6))
        cmap = 'RdBu_r' if kind == 'ctf' else 'gray'
        opts = {'vmin': -1, 'vmax': 1} if kind == 'ctf' else {}
        ax.imshow(image, cmap=cmap, extent=self.extent(kind), **opts)
        ax.set_xlabel(unit)
        ax.set_ylabel(unit)
        if aperture and kind in ('ronchigram', 'ctf'):
            r = self.aperture if kind == 'ronchigram' else self.kmax
            ax.add_patch(plt.Circle((0, 0), r, fill=False, color='yellow', linewidth=1))
        if title is None:
            title = (f'{name}: {self.kv:g} kV, {self.aperture:g} mrad, '
                     f'defocus {self.defocus:g} nm')
        ax.set_title(title)
        if new:
            plt.show()
        return ax

    # ------------------------------------------------------------------ files
    @classmethod
    def from_file(cls, path, **kwargs):
        '''
        Create a probe from a probe program parameter file: lines of a name and values, such as
        ``kv 200``, ``aperture 25``, ``df -5.14``, ``cs -0.00355`` (or ``c3_mm``), ``c5 3.829``
        and ``a1 1.349 146.2``, as the program's ``write -m`` and its microscope files have them.
        Lines starting with ``#``, and ``end``, are skipped.

        :param path: the file.
        :type path: str or os.PathLike
        :param kwargs: other :py:class:`Probe` settings, such as *size* and *sampling*. Those in
            the file take precedence.
        :return: the probe.
        :rtype: Probe
        :raise ValueError: for a line it doesn't understand, with its number.
        '''
        names = {'kv': 'kv', 'aperture': 'aperture', 'ap': 'aperture', 'df': 'defocus',
                 'df_nm': 'defocus', 'cs': 'cs', 'c3': 'cs', 'c3_mm': 'cs', 'c5': 'c5',
                 'c5_mm': 'c5', 'cc': 'cc', 'de': 'energy_spread', 'fhi': 'rotation'}
        settings, aberrations = dict(kwargs), {}
        with open(os.fspath(path), encoding='utf-8', errors='replace') as f:
            for number, line in enumerate(f, 1):
                words = line.split()
                if not words or words[0].startswith('#') or words[0].lower() == 'end':
                    continue
                key = words[0].lower()
                try:
                    values = [float(w) for w in words[1:]]
                except ValueError:
                    raise ValueError(f'{path}, line {number}: numbers expected: {line.strip()}')
                base = key.split('_')[0]
                if base in ABERRATIONS and len(values) == 2:
                    aberrations[base] = tuple(values)
                elif key == 'tilt' and len(values) == 2:
                    settings['tilt'] = tuple(values)
                elif key in names and len(values) == 1:
                    settings[names[key]] = values[0]
                else:
                    raise ValueError(f'{path}, line {number}: not a probe setting: '
                                     f'{line.strip()}')
        # a written aperture of 0 means the file didn't set it
        if settings.get('aperture') == 0.0:
            settings.pop('aperture')
        merged = dict(kwargs.get('aberrations') or {})
        merged.update(aberrations)
        settings['aberrations'] = merged
        return cls(**settings)
