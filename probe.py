# This file is part of pyEMAPS.
# Copyright (C) 2021-2026 EMLab Solutions, Inc.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Additional permission under GPLv3 Section 7:
# See license-exception.txt for the exception permitting
# combination with the separately licensed backend, emaps.

'''
Electron probes, Ronchigrams, contrast transfer functions and HREM images of a lens with
aberrations, from emaps' probe module.

A :py:class:`Probe` holds the microscope settings: the high voltage, the aperture, the defocus,
the spherical, fifth-order and chromatic aberrations, the residual aberrations a corrector
measures (a1 to a5, b2, b4, d4, s3), and the map the results are computed on. Its methods return
the results as NumPy arrays, in four modes:

- :py:meth:`~Probe.ronchigram`: the Ronchigram, the shadow image of the probe through a thin
  sample: a random amorphous potential (:py:meth:`~Probe.random_potential`), a crystal along a
  zone axis (:py:meth:`~Probe.crystal_potential`) or one you give;
- :py:meth:`~Probe.probe`: the probe's intensity, and :py:meth:`~Probe.diameter` its size;
- :py:meth:`~Probe.ctf`: the contrast transfer function, with its coherence envelopes;
- :py:meth:`~Probe.hrem`: the high-resolution TEM image of a thin sample's exit wave
  (:py:meth:`~Probe.exit_wave`), with the lens as the objective lens.

And around them:

- :py:meth:`~Probe.phase_map`: the aberration function χ(k) itself;
- :py:meth:`~Probe.stem_image` and :py:meth:`~Probe.mtf`: the incoherent STEM image of a sample,
  and the probe's transfer function;
- :py:meth:`~Probe.apply_psf`: a camera's point spread function, for HREM images;
- :py:meth:`~Probe.focal_series`: any of these over a range of defocus;
- :py:meth:`~Probe.scherzer` and :py:meth:`~Probe.haider`: the optimum defocus and aperture for
  an uncorrected or a corrected lens, and :py:meth:`~Probe.optimize`: the defocus and residual
  aberrations that make the probe smallest;
- :py:meth:`~Probe.show`: the results with their axes.
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

_KINDS = ("kind must be 'ronchigram', 'probe', 'ctf', 'hrem', 'stem', 'phase', 'mtf' or "
          "'potential'")

#: The largest sampling: larger maps' pixel counts overflow the backend's 32-bit integers.
MAX_SAMPLING = 32768

_ERRORS = {1: 'the map is invalid: sampling must be an even number of pixels from 8 to '
              f'{MAX_SAMPLING}, and size positive',
           2: 'the microscope settings are invalid: high voltage and aperture must be '
              'positive, cc and energy_spread not negative, and energy_spread positive with cc',
           3: 'not enough memory for the map: use a smaller sampling',
           4: 'the random potential would have more than 1e8 atoms: use a smaller map, '
              'density or thickness'}

#: The largest random number seed: the Park-Miller generator's modulus, 2**31 - 1, is excluded,
#: since the generator never leaves it.
MAX_SEED = 2**31 - 2

#: The most atoms :py:meth:`Probe.crystal_potential` places, as for the random potential.
MAX_ATOMS = 10**8

# m0 e^2 / (8 pi^2 eps0 h^2) in A, of the Mott-Bethe formula, as emaps' structure factors use it
_MOTT = 0.023933754
# 2 pi a0 e, in V A^2: the projected potential of an atom from its electron scattering factor,
# as the probe module's random potential uses it
_TWO_PI_A0_E = 47.878


def _lattice(cell):
    # the direct lattice vectors as rows, in A: a along x, b in the xy plane
    a, b, c = float(cell.a), float(cell.b), float(cell.c)
    al, be, ga = (math.radians(float(x)) for x in (cell.alpha, cell.beta, cell.gamma))
    cx = c * math.cos(be)
    cy = c * (math.cos(al) - math.cos(be) * math.cos(ga)) / math.sin(ga)
    cz2 = c * c - cx * cx - cy * cy
    if not (a > 0 and b > 0 and c > 0 and cz2 > 0):
        raise ValueError('the crystal\'s cell is invalid')
    return np.array([[a, 0.0, 0.0], [b * math.cos(ga), b * math.sin(ga), 0.0],
                     [cx, cy, math.sqrt(cz2)]])


def _scattering(symbol):
    # emaps' X-ray scattering factor of an element: Z and the 9 Cromer-Mann coefficients
    from .scattering.sct_dec import sct, sct_symbtable, sct_cifsymbtable
    name = symbol.strip().upper()
    for table in (sct_symbtable, sct_cifsymbtable):
        if name in table:
            k = table.index(name)
            return float(sct.zt0[k]), np.array(sct.abx0[k], dtype=np.float64)
    raise ValueError(f'no scattering factor for the element {symbol!r}')


def _electron_factor(symbol, s2):
    # the electron scattering factor in A at s^2 = (sin(theta) / lambda)^2, by the Mott-Bethe
    # formula as emaps' sfsub has it; its limit at s = 0 leaves out any ionic charge, which a
    # neutral crystal cancels
    z, abx = _scattering(symbol)
    a, b, c = abx[0:8:2], abx[1:8:2], abx[8]
    fe = np.empty_like(s2)
    zero = s2 <= 0.0
    s = s2[~zero]
    fx = c + sum(ai * np.exp(-bi * s) for ai, bi in zip(a, b))
    fe[~zero] = _MOTT * (z - fx) / s
    fe[zero] = _MOTT * float(np.dot(a, b))
    return fe


def _isotropic_b(atom, lattice):
    # the atom's Debye-Waller factor B, in A^2; anisotropic factors are averaged to the
    # equivalent isotropic one, B = 8 pi^2 U_eq
    loc = [float(v) for v in atom.loc]
    if atom.atype == 1:
        return loc[3]
    # U_eq = (1/3) sum_ij U_ij a*_i a*_j (a_i . a_j)
    rec = np.linalg.norm(np.linalg.inv(lattice).T, axis=1)     # a*, b*, c*
    g = lattice @ lattice.T
    t = loc[3:9]
    m = np.array([[t[0], t[3], t[4]], [t[3], t[1], t[5]], [t[4], t[5], t[2]]])
    if atom.atype == 2:
        # beta_ij = 2 pi^2 a*_i a*_j U_ij
        m = m / (2.0 * math.pi ** 2 * np.outer(rec, rec))
    ueq = float(np.sum(m * np.outer(rec, rec) * g)) / 3.0
    return 8.0 * math.pi ** 2 * ueq


def _site_orbit(crystal, atom, lattice):
    # all the positions of one site in the unit cell, fractional, from emaps' mxtal: it applies
    # the space group with its lattice centering
    import copy
    one = copy.deepcopy(crystal)
    one.atoms = [atom]
    cstar = np.linalg.solve(lattice @ lattice.T, [0.0, 0.0, 1.0])
    # x along a and z along c*: the same Cartesian frame as _lattice
    mx = one.generateMxtal(cellbox=[[0, 0, 0], [1, 1, 1]], xz=[[1.0, 0.0, 0.0], list(cstar)])
    xyz = np.array([a.coord for a in mx.acoordList], dtype=np.float64).reshape(-1, 3)
    frac = np.mod(np.linalg.solve(lattice.T, xyz.T).T + 1e-6, 1.0) - 1e-6
    sites = []
    for f in frac:
        if not any(np.allclose(np.mod(f - g + 0.5, 1.0) - 0.5, 0.0, atol=1e-4) for g in sites):
            sites.append(f)
    return np.array(sites)


def _perpendicular(zone, lattice):
    # the shortest lattice direction [uvw], indices up to 6, perpendicular to the zone axis; in
    # an oblique cell there may be none, and then the shortest one not parallel to it
    t = np.asarray(zone, dtype=np.float64) @ lattice
    r = np.arange(-6, 7)
    n = np.stack(np.meshgrid(r, r, r, indexing='ij'), axis=-1).reshape(-1, 3)
    n = n[np.any(n != 0, axis=1)]
    v = n @ lattice
    length, tn = np.linalg.norm(v, axis=1), np.linalg.norm(t)
    ok = np.abs(v @ t) <= 1e-6 * length * tn
    if not ok.any():
        ok = np.linalg.norm(np.cross(v, t), axis=1) > 1e-6 * length * tn
    n, v = n[ok], v[ok]
    # shortest, then the first in a fixed order with a positive first nonzero index
    first = np.array([row[np.flatnonzero(row)[0]] for row in n])
    n, v = n[first > 0], v[first > 0]
    k = np.lexsort((-n[:, 2], -n[:, 1], -n[:, 0], np.round(np.linalg.norm(v, axis=1), 6)))
    return n[k[0]]


def _backend():
    if probesim is None:
        raise ImportError('The probe simulations need an emaps with the probe module: '
                          'pip install --upgrade emaps')
    return probesim


def _nelder_mead(f, x0, step, max_evaluations, tolerance=1e-4):
    '''
    Minimize *f* from *x0* with the Nelder-Mead simplex method: the first simplex has *x0* and,
    for each coordinate, *x0* moved by its *step*. It stops when the simplex's values agree to
    *tolerance* (relative), or after *max_evaluations* evaluations of *f*.
    Returns ``(best point, its value, evaluations)``.
    '''
    n = len(x0)
    points = [np.array(x0, dtype=float)]
    for i in range(n):
        p = np.array(x0, dtype=float)
        p[i] += step[i]
        points.append(p)
    values = [f(p) for p in points]
    evaluations = n + 1
    while evaluations < max_evaluations:
        order = np.argsort(values)
        points = [points[i] for i in order]
        values = [values[i] for i in order]
        best, worst = values[0], values[-1]
        if math.isfinite(worst) and abs(worst - best) <= tolerance * max(abs(best), 1e-12):
            break
        centroid = np.mean(points[:-1], axis=0)
        # reflect the worst point through the others' centroid
        reflected = centroid + (centroid - points[-1])
        fr = f(reflected)
        evaluations += 1
        if fr < best:
            # going further that way
            expanded = centroid + 2.0 * (centroid - points[-1])
            fe = f(expanded)
            evaluations += 1
            points[-1], values[-1] = (expanded, fe) if fe < fr else (reflected, fr)
        elif fr < values[-2]:
            points[-1], values[-1] = reflected, fr
        else:
            # contract toward the centroid, on the better side of the worst point
            if fr < worst:
                contracted = centroid + 0.5 * (reflected - centroid)
            else:
                contracted = centroid + 0.5 * (points[-1] - centroid)
            fc = f(contracted)
            evaluations += 1
            if fc < min(fr, worst):
                points[-1], values[-1] = contracted, fc
            else:
                # shrink every point toward the best
                for i in range(1, n + 1):
                    points[i] = points[0] + 0.5 * (points[i] - points[0])
                    values[i] = f(points[i])
                evaluations += n
    i = int(np.argmin(values))
    return points[i], values[i], evaluations


def _slab_atoms(crystal, zone, x_axis, size, depth):
    # the crystal's atoms in the slab x, y in [0, size), z in [0, depth), in the map's frame
    # (x along the columns, y along the rows, z along the zone axis), in A, grouped by element
    # and Debye-Waller factor: {(symbol, B): (positions (m, 3), occupancies (m,))}
    lattice = _lattice(crystal.cell)
    zone = np.asarray(zone, dtype=np.float64)
    t = zone @ lattice
    if zone.shape != (3,) or not np.linalg.norm(t) > 0:
        raise ValueError('zone must be three numbers, not all 0')
    ez = t / np.linalg.norm(t)
    if x_axis is None:
        x_axis = _perpendicular(zone, lattice)
    x = np.asarray(x_axis, dtype=np.float64)
    if x.shape != (3,):
        raise ValueError('x_axis must be three numbers')
    full = x @ lattice
    x = full - (full @ ez) * ez
    if not np.linalg.norm(x) > 1e-6 * np.linalg.norm(full):
        raise ValueError('x_axis must not be parallel to the zone axis')
    ex = x / np.linalg.norm(x)
    rot = np.array([ex, np.cross(ez, ex), ez])
    cell = lattice @ rot.T          # the lattice vectors as rows, in the map's frame

    # each site's positions in the cell, its scattering factor group and its weight
    groups = {}
    for atom in crystal.atoms:
        loc = [float(v) for v in atom.loc]
        occ = loc[-1]
        if occ <= 0:
            continue
        key = (atom.symb.strip().upper(), round(_isotropic_b(atom, lattice), 6))
        _scattering(key[0])                  # every element has one
        groups.setdefault(key, []).append((_site_orbit(crystal, atom, lattice), occ))

    # the lattice translations that reach the slab
    corners = np.array([[i * size, j * size, k * depth]
                        for i in (0, 1) for j in (0, 1) for k in (0, 1)])
    frac = corners @ np.linalg.inv(cell)
    lo = np.floor(frac.min(axis=0)).astype(int) - 1
    hi = np.ceil(frac.max(axis=0)).astype(int) + 1
    volume = abs(np.linalg.det(cell))
    per_cell = sum(len(p) for sites in groups.values() for p, _ in sites)
    if size * size * depth / volume * per_cell > MAX_ATOMS:
        raise ValueError(f'the slab would have more than {MAX_ATOMS:.0e} atoms: use a '
                         'smaller map or thickness')
    r = [np.arange(lo[i], hi[i] + 1) for i in range(3)]
    trans = np.stack(np.meshgrid(*r, indexing='ij'), axis=-1).reshape(-1, 3) @ cell

    # an atom on a face counts once: rounding puts it just inside or just outside, and its
    # image on the opposite face is then outside
    tol = 1e-6
    out = {}
    for key, sites in groups.items():
        xyz, occ = [], []
        for positions, weight in sites:
            for p in positions @ cell:
                q = trans + p
                q = q[(q[:, 0] >= -tol) & (q[:, 0] < size - tol) & (q[:, 1] >= -tol)
                      & (q[:, 1] < size - tol) & (q[:, 2] >= -tol) & (q[:, 2] < depth - tol)]
                xyz.append(q)
                occ.append(np.full(len(q), weight))
        out[key] = (np.concatenate(xyz), np.concatenate(occ))
    return out


class Probe:
    '''
    A lens with aberrations, and the map its probe, Ronchigram, CTF and HREM images are
    computed on. For the probe and the Ronchigram it's the probe-forming lens; for the CTF and
    HREM images, the objective lens.

    :param kv: high voltage, in kV.
    :type kv: float, optional
    :param aperture: aperture semi-angle, in mrad: the probe's convergence angle, or for HREM
        images the objective aperture. The CTF isn't cut off at it; :py:meth:`show` draws it.
    :type aperture: float, optional
    :param defocus: defocus, in nm. Negative values are underfocus.
    :type defocus: float, optional
    :param cs: spherical aberration C3, in mm.
    :type cs: float, optional
    :param c5: fifth-order spherical aberration C5, in mm.
    :type c5: float, optional
    :param cc: chromatic aberration, in mm. With 0.01 mm or more, :py:meth:`probe` adds up the
        probes over the energy spread, and :py:meth:`ctf` includes the temporal coherence
        envelope, as do HREM images. The Ronchigram doesn't include it.
    :type cc: float, optional
    :param energy_spread: energy spread of the beam, full width at half maximum, in eV.
    :type energy_spread: float, optional
    :param semi_angle: illumination semi-angle, in mrad, for the spatial coherence envelope of
        :py:meth:`ctf` and :py:meth:`hrem`.
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
        # a new dictionary, not a change to the old one, so a copy.copy of the probe keeps its own
        self._aberrations = {**self._aberrations, key: (float(amplitude), float(angle))}

    def zero_aberrations(self):
        '''Set all residual aberrations to 0.'''
        self._aberrations = {name: (0.0, 0.0) for name in ABERRATIONS}

    def __repr__(self):
        res = [n for n, (a, _) in self._aberrations.items() if a != 0.0]
        return (f'Probe({self.kv:g} kV, aperture {self.aperture:g} mrad, defocus '
                f'{self.defocus:g} nm, Cs {self.cs:g} mm, C5 {self.c5:g} mm, Cc {self.cc:g} mm; '
                f'residual aberrations: {", ".join(res) if res else "none"}; '
                f'{self.size:g} A map of {self.sampling} x {self.sampling})')

    def _check_map(self):
        # before f2py sizes its arrays from sampling**2, which overflows a 32-bit integer from
        # 46341 pixels
        n = self.sampling
        if not (isinstance(n, (int, np.integer)) and 8 <= n <= MAX_SAMPLING and n % 2 == 0
                and self.size > 0):
            raise ValueError(f'Probe simulation failed: {_ERRORS[1]}')

    def _mic(self):
        self._check_map()
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
        :param seed: the random number seed, from 1 to 2147483646 (:py:data:`MAX_SEED`). The
            same seed gives the same potential.
        :type seed: int, optional
        :return: the projected potential, ``(sampling, sampling)``, rows then columns.
        :rtype: numpy.ndarray
        :raise ValueError: if a setting is invalid, or the sample would have more than 10⁸
            atoms (size² × thickness × density).

        The defaults are those of the probe program: 100 Å of amorphous aluminium.
        '''
        if not 1 <= int(seed) <= MAX_SEED:
            raise ValueError(f'seed must be an integer from 1 to {MAX_SEED}')
        self._check_map()
        v, ierr = _backend().potential(self.size, self.sampling, density, z, thickness,
                                       int(seed))
        if ierr == 2:
            raise ValueError('density and thickness must not be negative')
        return self._image(v, ierr)

    def crystal_potential(self, crystal, zone=(0, 0, 1), thickness=50.0, x_axis=None,
                          shift=(0.0, 0.0)):
        '''
        The projected potential of a crystal along a zone axis: the atoms of the crystal in a
        slab of the given thickness, each with its projected atomic potential, added up.

        :param crystal: the crystal, such as ``Crystal.from_builtin('Silicon')``.
        :type crystal: :py:class:`~pyemaps.crystals.Crystal`
        :param zone: the zone axis [uvw], a direction in the crystal's direct lattice, along
            the beam.
        :type zone: tuple of int, optional
        :param thickness: the slab's thickness along the zone axis, in Å.
        :type thickness: float, optional
        :param x_axis: the direction [uvw] along the map's x axis (its columns). It must not be
            parallel to the zone axis; its part along the zone axis is ignored. By default, the
            shortest direction with indices up to 6 perpendicular to the zone axis.
        :type x_axis: tuple of int, optional
        :param shift: where the crystal's origin is on the map, (x, y) in Å from the map's top
            left corner.
        :type shift: tuple of float, optional
        :return: the projected potential in V·Å, ``(sampling, sampling)``, rows then columns,
            as :py:meth:`random_potential` gives it.
        :rtype: numpy.ndarray
        :raise ValueError: if a setting is invalid, an element has no scattering factor, or
            the slab would have more than 10⁸ atoms (:py:data:`MAX_ATOMS`).

        Each atom's potential comes from its electron scattering factor, by the Mott–Bethe
        formula from emaps' X-ray scattering factors, as emaps' structure factors have it. It
        includes the atom's Debye–Waller factor, an anisotropic one averaged to the equivalent
        isotropic factor, and its occupancy. The unit cell is filled with the space group by
        :py:meth:`~pyemaps.crystals.Crystal.generateMxtal`.

        The potential is that of the whole slab projected onto one plane, as the probe
        program's random potential is, so it suits thin crystals: there's no propagation
        through the thickness.

        The map repeats itself at its edges. Unless *size* is a whole number of the crystal's
        repeats along x and y, the crystal has a seam there; it's away from the map's center,
        where the probe is.
        '''
        self._check_map()
        if not float(thickness) > 0:
            raise ValueError('thickness must be positive')
        size, depth = self.size, float(thickness)
        groups = _slab_atoms(crystal, zone, x_axis, size, depth)

        n = self.sampling
        k = np.fft.fftfreq(n, d=size / n)                    # 1/A
        s2 = (k[:, None] ** 2 + k[None, :] ** 2) / 4.0       # (sin(theta) / lambda)^2
        total = np.zeros((n, n), dtype=np.complex128)
        for (symbol, b), (xyz, occ) in groups.items():
            # the columns: atoms at the same projected position add up
            xy = np.column_stack([np.mod(xyz[:, 0] + shift[0], size),
                                  np.mod(xyz[:, 1] + shift[1], size)])
            xy, inverse = np.unique(np.round(xy, 6), axis=0, return_inverse=True)
            w = np.bincount(inverse.ravel(), weights=occ, minlength=len(xy))
            # the structure factor of the columns, sum_j w_j exp(-2 pi i k . r_j), by blocks
            sf = np.zeros((n, n), dtype=np.complex128)
            for i in range(0, len(xy), 2048):
                ex = np.exp(-2j * math.pi * np.outer(xy[i:i + 2048, 0], k))
                ey = np.exp(-2j * math.pi * np.outer(xy[i:i + 2048, 1], k))
                sf += (ey * w[i:i + 2048, None]).T @ ex      # rows ky, columns kx
            total += sf * _electron_factor(symbol, s2) * np.exp(-b * s2)
        v = np.fft.ifft2(total).real * (_TWO_PI_A0_E * n * n / (size * size))
        return v.astype(np.float32)

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
        v = self._potential(potential)
        amp, ang = self._abr()
        img, ierr = _backend().ronchigram(self._mic(), amp, ang, self.size, self.sampling,
                                          v.ravel())
        return self._image(img, ierr)

    def _potential(self, potential):
        if potential is None:
            potential = self.random_potential()
        v = np.asarray(potential, dtype=np.float32)
        if v.shape != (self.sampling, self.sampling):
            raise ValueError(f'potential must be {self.sampling} x {self.sampling}, the sampling, '
                             f'not {" x ".join(str(s) for s in v.shape)}')
        return v

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

    def diameter(self, percent=50.0, probe=None, interpolate=False):
        '''
        The probe's diameter: that of the circle around the map's center that holds *percent*
        percent of its intensity.

        :param percent: the share of the intensity, in percent.
        :type percent: float, optional
        :param probe: the probe intensity from :py:meth:`probe`. By default, computed.
        :type probe: numpy.ndarray, optional
        :param interpolate: False: count whole pixels, as the probe program does. True:
            interpolate the intensity within the circle between the pixels' distances from the
            center, so the diameter changes smoothly with the probe; :py:meth:`optimize` uses
            it.
        :type interpolate: bool, optional
        :return: the diameter, in Å.
        :rtype: float
        :raise ValueError: if *percent* isn't between 0 and 100, the probe has no intensity
            near the center of the map, the map is too small to hold *percent* percent of it, or
            its pixels are too large to measure it (it fits within one pixel of the center).

        Counting whole pixels, the diameter changes in steps of about a pixel, and probes of
        slightly different sizes can give the same value. Use a map whose pixels
        (*size* / *sampling*) are much smaller than the probe, such as 0.1 Å, or *interpolate*.
        '''
        if not 0.0 < percent < 100.0:
            raise ValueError('percent must be between 0 and 100')
        self._check_map()
        img = self.probe() if probe is None else np.asarray(probe, dtype=np.float32)
        if img.shape != (self.sampling, self.sampling):
            raise ValueError(f'probe must be {self.sampling} x {self.sampling}, the sampling')
        if interpolate:
            return self._interpolated_diameter(img, percent)
        d = _backend().probediameter(self.size, self.sampling, img.ravel(), percent)
        if d == -2:
            raise ValueError(f'The map, {self.size:g} Å across, holds less than {percent:g}% of '
                             f'the probe: use a larger size')
        if d == -3:
            raise ValueError(f'{percent:g}% of the probe lies within one pixel of the center: '
                             f'use smaller pixels (size / sampling, now '
                             f'{self.size / self.sampling:.3g} Å)')
        if d < 0:
            raise ValueError('The probe has no intensity near the center of the map')
        return float(d)

    def _interpolated_diameter(self, img, percent):
        # the pixels by their distance from the center pixel, and the intensity within each
        n, step = self.sampling, self.size / self.sampling
        yy, xx = np.indices(img.shape)
        r = (np.hypot(xx - n // 2, yy - n // 2) * step).ravel()
        order = np.argsort(r, kind='stable')
        r = r[order]
        total = float(img.sum())
        if total <= 0.0:
            raise ValueError('The probe has no intensity')
        within = np.cumsum(img.ravel()[order], dtype=np.float64) / total
        # Many pixels lie at the same distance: take the intensity within each distinct radius,
        # so the result moves smoothly as the probe changes, instead of stepping from ring to
        # ring.
        radii, counts = np.unique(r, return_counts=True)
        within = within[np.cumsum(counts) - 1]
        share = percent / 100.0
        inscribed = radii <= self.size / 2
        if within[inscribed][-1] < share:
            raise ValueError(f'The map, {self.size:g} Å across, holds less than {percent:g}% of '
                             f'the probe: use a larger size')
        if within[0] >= share:
            raise ValueError(f'{percent:g}% of the probe is in the center pixel: use smaller '
                             f'pixels (size / sampling, now {step:.3g} Å)')
        # the radius at which the intensity within reaches the share, between the two radii
        # that bracket it
        k = int(np.searchsorted(within, share))
        r0, r1, w0, w1 = radii[k - 1], radii[k], within[k - 1], within[k]
        radius = r0 + (r1 - r0) * (share - w0) / (w1 - w0) if w1 > w0 else r1
        return float(2 * radius)

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

    def exit_wave(self, potential=None):
        '''
        The exit wave of a thin sample under plane-wave illumination: its transmission
        function, exp(iσV), for the projected potential V at this high voltage.

        :param potential: the projected potential, ``(sampling, sampling)``. By default,
            :py:meth:`random_potential` with its defaults.
        :type potential: numpy.ndarray, optional
        :return: the exit wave, complex, ``(sampling, sampling)``.
        :rtype: numpy.ndarray
        :raise ValueError: if a setting is invalid or *potential* has the wrong shape.
        '''
        v = self._potential(potential)
        self._check_map()
        wave, ierr = _backend().exitwave(self.kv, self.size, self.sampling, v.ravel())
        return self._image(wave, ierr)

    def hrem(self, wave=None, integrate=False):
        '''
        The high-resolution TEM (HREM) image of an exit wave, with this lens as the objective
        lens: the image intensity of the wave through the aperture, with the aberrations and
        the coherence envelopes. The direct beam passes unchanged.

        :param wave: the sample's exit wave, complex, ``(sampling, sampling)``, such as
            :py:meth:`exit_wave` gives or a multislice program computes. By default,
            :py:meth:`exit_wave` of the default random potential: 100 Å of amorphous aluminium.
        :type wave: numpy.ndarray, optional
        :param integrate: how to include the chromatic aberration. False: the coherent image,
            damped by the temporal coherence envelope (*cc*, *energy_spread*) and the spatial
            one (*semi_angle*). True: the images at each energy across the energy spread, added
            up with the spatial envelope only; this needs *energy_spread*.
        :type integrate: bool, optional
        :return: the image intensity, ``(sampling, sampling)``, with pixels of
            ``size / sampling`` Å. A plane wave's image is 1 everywhere.
        :rtype: numpy.ndarray
        :raise ValueError: if a setting is invalid or *wave* has the wrong shape.
        '''
        if wave is None:
            wave = self.exit_wave()
        w = np.asarray(wave, dtype=np.complex64)
        if w.shape != (self.sampling, self.sampling):
            raise ValueError(f'wave must be {self.sampling} x {self.sampling}, the sampling, '
                             f'not {" x ".join(str(s) for s in w.shape)}')
        amp, ang = self._abr()
        img, ierr = _backend().hremimage(self._mic(), amp, ang, self.size, self.sampling,
                                         w.ravel(), 1 if integrate else 0)
        if ierr == 2 and integrate and self.energy_spread <= 0:
            raise ValueError('integrate needs a positive energy_spread')
        return self._image(img, ierr)

    def phase_map(self):
        '''
        The aberration function χ(k): the phase, in radians, that the lens adds to the wave at
        each spatial frequency, from the defocus, Cs, C5 and the residual aberrations, with the
        beam tilt and rotation. The CTF without its envelopes is sin(χ). It's computed within
        80% of the map's radius, as the CTF, and is 0 outside.

        :return: χ, ``(sampling, sampling)``, with zero frequency at the center. Each pixel is
            ``1 / size`` 1/Å.
        :rtype: numpy.ndarray
        :raise ValueError: if a setting is invalid.

        Where χ is nearly flat, within about π/4 of its value at the center, the lens is free of
        aberrations: that region sets how large an aperture can be used.
        '''
        amp, ang = self._abr()
        img, ierr = _backend().phasemap(self._mic(), amp, ang, self.size, self.sampling)
        return self._image(img, ierr)

    def stem_image(self, potential=None):
        '''
        The incoherent (annular dark field) STEM image of a thin sample: the probe's intensity,
        as :py:meth:`probe` computes it, convolved with the sample's projected potential.

        :param potential: the projected potential, ``(sampling, sampling)``. By default,
            :py:meth:`random_potential` with its defaults.
        :type potential: numpy.ndarray, optional
        :return: the image, ``(sampling, sampling)``, with pixels of ``size / sampling`` Å.
        :rtype: numpy.ndarray
        :raise ValueError: if a setting is invalid or *potential* has the wrong shape.
        '''
        v = self._potential(potential)
        amp, ang = self._abr()
        img, ierr = _backend().stemimage(self._mic(), amp, ang, self.size, self.sampling,
                                         v.ravel())
        return self._image(img, ierr)

    def mtf(self):
        '''
        The probe's modulation transfer function: the amplitude of the Fourier transform of its
        intensity, which tells how strongly each spatial frequency of the sample shows in an
        incoherent STEM image. It's 1 at zero frequency.

        :return: the MTF, ``(sampling, sampling)``, with zero frequency at the center. Each
            pixel is ``1 / size`` 1/Å.
        :rtype: numpy.ndarray
        :raise ValueError: if a setting is invalid.
        '''
        amp, ang = self._abr()
        img, ierr = _backend().probemtf(self._mic(), amp, ang, self.size, self.sampling)
        return self._image(img, ierr)

    def apply_psf(self, image, a, b):
        '''
        Blur an image with a detector's point spread function, as recorded by a camera: its
        transfer function is ``a / (1 + b w²) + 1 - a`` at the spatial frequency w, in cycles per
        pixel (0 to 0.5).

        :param image: the image, square, with an even number of pixels along each side, such as
            :py:meth:`hrem` gives.
        :type image: numpy.ndarray
        :param a: the share of the transfer that falls off with frequency, 0 to 1.
        :type a: float
        :param b: how fast it falls off; 0 leaves the image as it is.
        :type b: float
        :return: the blurred image, the same shape.
        :rtype: numpy.ndarray
        :raise ValueError: if *image* isn't square with an even size of at least 8 pixels, or
            *b* is negative.
        '''
        img = np.asarray(image, dtype=np.float32)
        n = img.shape[0] if img.ndim == 2 else 0
        if img.ndim != 2 or img.shape[1] != n or n < 8 or n % 2 or n > MAX_SAMPLING:
            raise ValueError(f'image must be square, with an even number of pixels from 8 to '
                             f'{MAX_SAMPLING} along each side')
        if b < 0:
            raise ValueError('b must not be negative')
        out, ierr = _backend().applypsf(n, a, b, img.ravel())
        if ierr != 0:
            raise ValueError(f'Probe simulation failed: {_ERRORS.get(ierr, f"error {ierr}")}')
        return np.asarray(out).reshape(n, n)

    def focal_series(self, defocus, kind='probe', sample=None, integrate=False):
        '''
        A result at each of a series of defocus values, the probe program's focus command.

        :param defocus: the defocus values, in nm.
        :type defocus: sequence of float
        :param kind: ``'probe'``, ``'ronchigram'``, ``'ctf'``, ``'hrem'``, ``'stem'`` or
            ``'phase'``.
        :type kind: str, optional
        :param sample: the projected potential for ``'ronchigram'`` and ``'stem'``, or the exit
            wave for ``'hrem'``. By default, as those methods take it, computed once.
        :type sample: numpy.ndarray, optional
        :param integrate: for ``'hrem'``, as :py:meth:`hrem` takes it.
        :type integrate: bool, optional
        :return: the results, ``(len(defocus), sampling, sampling)``.
        :rtype: numpy.ndarray
        :raise ValueError: if *kind* or a setting is invalid.

        The probe's defocus is left as it was.
        '''
        methods = {'probe': self.probe, 'ctf': self.ctf, 'phase': self.phase_map}
        if kind in ('ronchigram', 'stem'):
            sample = self._potential(sample)
            method = self.ronchigram if kind == 'ronchigram' else self.stem_image
            methods[kind] = lambda: method(sample)
        elif kind == 'hrem':
            sample = self.exit_wave() if sample is None else sample
            methods[kind] = lambda: self.hrem(sample, integrate=integrate)
        if kind not in methods:
            raise ValueError("kind must be 'probe', 'ronchigram', 'ctf', 'hrem', 'stem' or "
                             "'phase'")
        saved = self.defocus
        try:
            results = []
            for df in defocus:
                self.defocus = float(df)
                results.append(methods[kind]())
        finally:
            self.defocus = saved
        return np.stack(results)

    # ------------------------------------------------------------------ optimization
    def optimize(self, percent=50.0, vary=('defocus', 'a1'), steps=None, max_evaluations=400):
        '''
        Find the settings that make the probe smallest: the diameter holding *percent* percent of
        its intensity, as :py:meth:`diameter` measures it with ``interpolate=True``, the
        probe program's optimize command. It searches with the Nelder-Mead simplex method and
        sets the probe to the best settings it found.

        :param percent: the share of the intensity whose diameter is minimized, in percent.
        :type percent: float, optional
        :param vary: what to adjust: ``'defocus'``, and the residual aberrations, such as
            ``'a1'``, ``'a2'`` and ``'b2'``, each by its two components (amplitude times the
            cosine and sine of its angle). The probe program's options were ('defocus', 'a1'),
            ('defocus', 'a1', 'a2', 'b2'), ('a1', 'a2', 'b2') and ('defocus',).
        :type vary: sequence of str, optional
        :param steps: the size of the first steps, ``{name: step}``, in the setting's units.
            By default, as the probe program: 10 nm for the defocus, and 25 in each aberration's
            units.
        :type steps: dict, optional
        :param max_evaluations: the most probes to compute.
        :type max_evaluations: int, optional
        :return: the result: ``diameter`` (Å), the settings found (``defocus`` in nm, and each
            aberration as ``(amplitude, angle)``), and ``evaluations``.
        :rtype: dict
        :raise ValueError: if *vary* names an unknown setting, or the probe can't be measured at
            the starting settings (see :py:meth:`diameter`).

        The probe's map must hold the probe with room to spare, with pixels much smaller than
        it. The search finds a local minimum, near the starting settings.
        '''
        vary = list(vary)
        for name in vary:
            if name != 'defocus' and name not in ABERRATIONS:
                raise ValueError(f'Unknown setting {name!r}: use defocus or one of '
                                 f'{", ".join(ABERRATIONS)}')
        steps = dict(steps or {})

        def unpack(x):
            values, k = {}, 0
            for name in vary:
                if name == 'defocus':
                    values[name] = x[k]
                    k += 1
                else:
                    values[name] = (x[k], x[k + 1])
                    k += 2
            return values

        def apply(x):
            for name, value in unpack(x).items():
                if name == 'defocus':
                    self.defocus = float(value)
                else:
                    cx, cy = value
                    self.set_aberration(name, math.hypot(cx, cy),
                                        math.degrees(math.atan2(cy, cx)))

        x0, step = [], []
        for name in vary:
            if name == 'defocus':
                x0.append(self.defocus)
                step.append(steps.get(name, 10.0))
            else:
                amplitude, angle = self._aberrations[name]
                x0 += [amplitude * math.cos(math.radians(angle)),
                       amplitude * math.sin(math.radians(angle))]
                step += [steps.get(name, 25.0)] * 2
        start = self.diameter(percent, interpolate=True)    # raises if it can't be measured

        def objective(x):
            apply(x)
            try:
                return self.diameter(percent, interpolate=True)
            except ValueError:
                return math.inf

        best, value, evaluations = _nelder_mead(objective, x0, step, max_evaluations)
        if value > start:   # no better than where it started: keep the starting settings
            best, value = x0, start
        apply(best)
        result = {'diameter': value, 'evaluations': evaluations}
        for name in vary:
            result[name] = self.defocus if name == 'defocus' else self._aberrations[name]
        return result

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

        :param kind: ``'probe'``, ``'potential'``, ``'hrem'`` or ``'stem'`` (Å),
            ``'ronchigram'`` (mrad), or ``'ctf'``, ``'phase'`` or ``'mtf'`` (1/Å).
        :type kind: str
        :return: ``(left, right, bottom, top)``.
        :rtype: tuple
        '''
        n, half = self.sampling, 0.5
        if kind in ('probe', 'potential', 'hrem', 'stem'):
            step = self.size / n
        elif kind == 'ronchigram':
            step = 1000.0 * self.wavelength / self.size
        elif kind in ('ctf', 'phase', 'mtf'):
            step = 1.0 / self.size
        else:
            raise ValueError(_KINDS)
        # pixel n/2 (from 0) is the center
        lo, hi = (-n / 2 - half) * step, (n / 2 - 1 + half) * step
        return (lo, hi, hi, lo)

    def show(self, image, kind, ax=None, title=None, aperture=True):
        '''
        Display a result with its axes.

        :param image: the result, from :py:meth:`ronchigram`, :py:meth:`probe`, :py:meth:`ctf`,
            :py:meth:`hrem`, :py:meth:`stem_image`, :py:meth:`phase_map`, :py:meth:`mtf`,
            :py:meth:`random_potential` or :py:meth:`crystal_potential`.
        :type image: numpy.ndarray
        :param kind: ``'ronchigram'``, ``'probe'``, ``'ctf'``, ``'hrem'``, ``'stem'``,
            ``'phase'``, ``'mtf'`` or ``'potential'``.
        :type kind: str
        :param ax: the axes to draw in. By default, a new figure, shown.
        :type ax: matplotlib.axes.Axes, optional
        :param title: the title. By default, the kind and the main settings.
        :type title: str, optional
        :param aperture: on a Ronchigram, CTF, phase map or MTF, draw the aperture's edge.
            A phase map is shown modulo 2π, with a cyclic colour map.
        :type aperture: bool, optional
        :return: the axes.
        :rtype: matplotlib.axes.Axes
        '''
        import matplotlib.pyplot as plt

        labels = {'ronchigram': ('Ronchigram', 'mrad'), 'probe': ('Probe', 'Å'),
                  'ctf': ('CTF', '1/Å'), 'potential': ('Potential', 'Å'),
                  'hrem': ('HREM image', 'Å'), 'stem': ('STEM image', 'Å'),
                  'phase': ('Aberration phase (rad)', '1/Å'), 'mtf': ('Probe MTF', '1/Å')}
        if kind not in labels:
            raise ValueError(_KINDS)
        name, unit = labels[kind]
        new = ax is None
        if new:
            _, ax = plt.subplots(figsize=(6, 6))
        cmap = {'ctf': 'RdBu_r', 'phase': 'twilight_shifted'}.get(kind, 'gray')
        opts = {'vmin': -1, 'vmax': 1} if kind == 'ctf' else {}
        if kind == 'phase':
            # modulo 2 pi, with a cyclic colour map, as corrector software shows phase plates
            image = np.angle(np.exp(1j * np.asarray(image, dtype=np.float64)))
            opts = {'vmin': -math.pi, 'vmax': math.pi}
        shown = ax.imshow(image, cmap=cmap, extent=self.extent(kind), **opts)
        if kind == 'phase':
            ax.figure.colorbar(shown, ax=ax, fraction=0.046, pad=0.04)
        ax.set_xlabel(unit)
        ax.set_ylabel(unit)
        if aperture and kind in ('ronchigram', 'ctf', 'phase', 'mtf'):
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
        The program's other settings are read too: ``kmax`` (1/Å, instead of the aperture),
        ``semi``, ``cc``, ``de``, ``fhi``, ``tilt`` (amplitude and angle), ``dim`` (the map's
        size) and ``sam`` (its sampling). Lines starting with ``#``, and ``end``, are skipped.

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
                 'c5_mm': 'c5', 'cc': 'cc', 'de': 'energy_spread', 'fhi': 'rotation',
                 'sem': 'semi_angle', 'semi': 'semi_angle', 'km': 'kmax', 'kmax': 'kmax',
                 'dim': 'size', 'dimension': 'size', 'sam': 'sampling', 'sample': 'sampling',
                 'sampling': 'sampling'}
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
                elif key in ('tilt', 'til') and len(values) == 2:
                    settings['tilt'] = tuple(values)
                elif key in names and len(values) == 1:
                    settings[names[key]] = values[0]
                else:
                    raise ValueError(f'{path}, line {number}: not a probe setting: '
                                     f'{line.strip()}')
        # a written aperture of 0 means the file didn't set it
        if settings.get('aperture') == 0.0:
            settings.pop('aperture')
        if 'sampling' in settings:
            settings['sampling'] = int(settings['sampling'])
        # kmax, in 1/A, as the aperture: wavelength * kmax in mrad, at the file's high voltage
        kmax = settings.pop('kmax', None)
        if kmax is not None:
            settings['aperture'] = kmax * cls(kv=settings.get('kv', 200.0)).wavelength * 1000.0
        merged = dict(kwargs.get('aberrations') or {})
        merged.update(aberrations)
        settings['aberrations'] = merged
        return cls(**settings)
