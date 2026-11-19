# This file is part of pyEMAPS.
# Copyright (C) 2021-2026 EMLab Solutions, Inc.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Additional permission under GPLv3 Section 7:
# See license-exception.txt for the exception permitting
# combination with the separately licensed backend, emaps.

'''
Orientation maps from 4D-STEM scans: the result of
:py:meth:`StackImage.mapOrientation <pyemaps.stackimg.StackImage.mapOrientation>`.

.. note::

   **Experimental.** Orientation mapping hasn't yet been validated against an independent
   orientation map of real data. Its interface and results may change in later releases.

Frames. The *sample frame* is the image's: x along the image columns (to the right), y along
the image rows (down), and z = x × y, into the image. The *crystal frame* is Cartesian, with x
along the crystal's a axis and y in the plane of a and b. An orientation matrix U turns a
vector's crystal components into its sample components: ``v_sample = U @ v_crystal``.
'''

import numpy as np

#: The pattern was indexed.
OM_INDEXED = 0
#: Too few diffraction peaks were found to index the pattern.
OM_FEW_PEAKS = 1
#: The indexing failed.
OM_FAILED = 2
#: The pattern wasn't processed, because the run was interrupted.
OM_NOT_RUN = 3

_STATUS_NAMES = {OM_INDEXED: 'indexed', OM_FEW_PEAKS: 'too few peaks',
                 OM_FAILED: 'indexing failed', OM_NOT_RUN: 'not processed'}

# The fields saved by OrientationMap.save, besides the scan shape.
_FIELDS = ('status', 'dp', 'rotation', 'correlation', 'map_peak', 'rindex', 'npeaks',
           'nindexed', 'orientation')


def direct_basis(gmx):
    '''
    The crystal's direct lattice vectors a, b, c as the rows of a 3 x 3 matrix in the
    Cartesian crystal frame (a along x, b in the xy plane), from the metric tensor *gmx*.
    '''
    G = np.asarray(gmx, dtype=float).reshape(3, 3)
    a, b, c = np.sqrt(np.diag(G))
    cos_g = G[0, 1] / (a * b)
    cos_b = G[0, 2] / (a * c)
    cos_a = G[1, 2] / (b * c)
    sin_g = np.sqrt(1.0 - cos_g * cos_g)
    cx = c * cos_b
    cy = c * (cos_a - cos_b * cos_g) / sin_g
    return np.array([[a, 0.0, 0.0],
                     [b * cos_g, b * sin_g, 0.0],
                     [cx, cy, np.sqrt(max(c * c - cx * cx - cy * cy, 0.0))]])


def reciprocal_basis(A):
    '''The reciprocal lattice vectors a*, b*, c* as rows (without 2 pi), from *A*'s rows.'''
    return np.linalg.inv(np.asarray(A, dtype=float)).T


def fit_rotation(P, Q):
    '''The proper rotation R that best maps the rows of *P* onto the rows of *Q* (Kabsch).'''
    U, _, Vt = np.linalg.svd(np.asarray(P, float).T @ np.asarray(Q, float))
    d = np.sign(np.linalg.det(Vt.T @ U.T)) or 1.0
    return Vt.T @ np.diag([1.0, 1.0, d]) @ U.T


def image_rotation(alpha):
    '''
    The in-plane rotation stem4d applies to a database pattern rotated by *alpha* degrees:
    image column = x cos a + y sin a, image row = -x sin a + y cos a.
    '''
    a = np.radians(alpha)
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, s, 0.0], [-s, c, 0.0], [0.0, 0.0, 1.0]])


def euler_from_matrix(U):
    '''
    Bunge Euler angles (phi1, Phi, phi2), in degrees, of orientation matrices *U* (crystal to
    sample, shape (..., 3, 3)). Bunge's g turns sample components into crystal components,
    so g is U transposed.
    '''
    g = np.swapaxes(np.asarray(U, float), -1, -2)
    Phi = np.arccos(np.clip(g[..., 2, 2], -1.0, 1.0))
    phi1 = np.arctan2(g[..., 2, 0], -g[..., 2, 1])
    phi2 = np.arctan2(g[..., 0, 2], g[..., 1, 2])
    flat = np.abs(np.sin(Phi)) < 1e-6
    # Phi = 0 or 180 degrees: only phi1 + phi2 (or phi1 - phi2) is defined; put it in phi1
    phi1 = np.where(flat, np.arctan2(g[..., 0, 1], g[..., 0, 0]), phi1)
    phi2 = np.where(flat, 0.0, phi2)
    e = np.degrees(np.stack([phi1, Phi, phi2], axis=-1))
    e[..., 0] %= 360.0
    e[..., 2] %= 360.0
    return e


def matrix_from_euler(e):
    '''Orientation matrices U (crystal to sample) from Bunge Euler angles in degrees.'''
    p1, P, p2 = np.radians(np.moveaxis(np.asarray(e, float), -1, 0))
    c1, s1, c, s, c2, s2 = np.cos(p1), np.sin(p1), np.cos(P), np.sin(P), np.cos(p2), np.sin(p2)
    g = np.stack([np.stack([c1 * c2 - s1 * s2 * c, s1 * c2 + c1 * s2 * c, s2 * s], -1),
                  np.stack([-c1 * s2 - s1 * c2 * c, -s1 * s2 + c1 * c2 * c, c2 * s], -1),
                  np.stack([s1 * s, -c1 * s, c], -1)], -2)
    return np.swapaxes(g, -1, -2)


def _corner_order(corners):
    '''Corner order for the colours: simplest zone axis first ([001] red, [011] green, [111] blue).'''
    c = np.asarray(corners, float)
    m = np.max(np.abs(c), axis=1)
    m[m == 0] = 1.0
    complexity = np.sum(np.abs(c), axis=1) / m
    return np.argsort(complexity, kind='stable')


_CORNER_COLOURS = np.array([[1.0, 0.0, 0.0], [0.0, 0.8, 0.0], [0.0, 0.0, 1.0], [1.0, 0.85, 0.0]])


def _region_weights(dirs, corner_dirs):
    '''
    Weights of the unit vectors *dirs* (..., 3) with respect to the region's corner unit
    vectors (n, 3): barycentric for a triangle, mean value coordinates for a quadrilateral,
    on the gnomonic projection about the region's centre. Clipped to >= 0; rows sum to 1.
    '''
    m = corner_dirs.mean(axis=0)
    m /= np.linalg.norm(m)
    e1 = corner_dirs[0] - (corner_dirs[0] @ m) * m
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(m, e1)

    def project(v):
        v = np.asarray(v, float)
        t = v @ m
        t = np.where(np.abs(t) < 1e-9, 1e-9, t)
        p = v / t[..., None]
        return np.stack([p @ e1, p @ e2], axis=-1)

    P = project(dirs)
    C = project(corner_dirs)
    n = len(C)
    if n == 3:
        T = np.array([C[0] - C[2], C[1] - C[2]]).T
        ab = np.linalg.solve(T, (P - C[2]).reshape(-1, 2).T).T.reshape(P.shape)
        w = np.concatenate([ab, 1.0 - ab.sum(-1, keepdims=True)], axis=-1)
    else:
        d = C[None, :, :] - P.reshape(-1, 1, 2)                     # (k, n, 2)
        r = np.linalg.norm(d, axis=-1)
        r = np.maximum(r, 1e-12)
        nxt = np.roll(d, -1, axis=1)
        cross = d[..., 0] * nxt[..., 1] - d[..., 1] * nxt[..., 0]
        dot = (d * nxt).sum(-1)
        ang = np.arctan2(cross, dot)                                 # angle at P, corner i to i+1
        tanh = np.tan(ang / 2.0)
        w = (np.roll(tanh, 1, axis=1) + tanh) / r
        # at a corner itself the formula is 0/0: that corner gets all the weight
        at = r < 1e-9
        hit = at.any(axis=1)
        w[hit] = at[hit].astype(float)
        w = w.reshape(P.shape[:-1] + (n,))
    w = np.clip(w, 0.0, None)
    s = w.sum(-1, keepdims=True)
    s[s == 0] = 1.0
    return w / s


class OrientationMap:
    '''
    The crystal orientation at each pattern of a 4D-STEM scan, from
    :py:meth:`StackImage.mapOrientation <pyemaps.stackimg.StackImage.mapOrientation>`. Each
    array has the scan's shape, ``(rows, columns)``, with an extra axis or two for vectors
    and matrices. Orientation mapping is experimental; see *mapOrientation*.

    Every pattern is indexed against the database on its own, as by
    :py:meth:`~pyemaps.stackimg.StackImage.indexImage`. Each result is a database pattern
    (``dp``) and the in-plane rotation that best match the pattern. The orientation follows
    from them.

    A kinematic diffraction pattern from the zero-order Laue zone looks the same for an
    orientation and for the same orientation rotated 180 degrees about the beam, so an
    orientation is only known up to that rotation (and the crystal's symmetry). Use the
    reliability index (``rindex``), the number of peaks indexed and the correlation to judge
    each pattern; :py:meth:`reliable` selects the patterns that pass.
    '''

    def __init__(self, scan_shape, status, dp, rotation, correlation, map_peak, rindex,
                 npeaks, nindexed, orientation, basis, corners, database='', params=None):
        '''
        :param scan_shape: ``(rows, columns)``.
        :param status: per pattern, one of ``OM_INDEXED``, ``OM_FEW_PEAKS``, ``OM_FAILED``,
            ``OM_NOT_RUN``.
        :param dp: the best matching database pattern, -1 where not indexed.
        :param rotation: its in-plane rotation, in degrees.
        :param correlation: correlation of the experimental and the database pattern.
        :param map_peak: peak of the matching index map.
        :param rindex: reliability index; above 5 means the indexing succeeded.
        :param npeaks: peaks found in the pattern.
        :param nindexed: peaks indexed.
        :param orientation: orientation matrices, shape (rows, columns, 3, 3); NaN where not
            indexed.
        :param basis: the crystal's direct lattice vectors as rows, in the crystal frame.
        :param corners: the zone axes at the corners of the database's orientation region,
            as rows of [u, v, w].
        :param database: the database file.
        :param params: the indexing parameters used.
        '''
        self.scan_shape = tuple(int(n) for n in scan_shape)
        shape = self.scan_shape
        self.status = np.asarray(status, dtype=np.int8).reshape(shape)
        self.dp = np.asarray(dp, dtype=np.int32).reshape(shape)
        self.rotation = np.asarray(rotation, dtype=np.float32).reshape(shape)
        self.correlation = np.asarray(correlation, dtype=np.float32).reshape(shape)
        self.map_peak = np.asarray(map_peak, dtype=np.float32).reshape(shape)
        self.rindex = np.asarray(rindex, dtype=np.float32).reshape(shape)
        self.npeaks = np.asarray(npeaks, dtype=np.int32).reshape(shape)
        self.nindexed = np.asarray(nindexed, dtype=np.int32).reshape(shape)
        self.orientation = np.asarray(orientation, dtype=float).reshape(shape + (3, 3))
        self.basis = np.asarray(basis, dtype=float).reshape(3, 3)
        self.corners = np.asarray(corners, dtype=float).reshape(-1, 3)
        self.database = str(database)
        self.params = dict(params or {})

    def __repr__(self):
        n = self.status.size
        counts = ', '.join(f'{np.count_nonzero(self.status == k)} {name}'
                           for k, name in _STATUS_NAMES.items()
                           if np.count_nonzero(self.status == k))
        return (f'OrientationMap: {self.scan_shape[0]} x {self.scan_shape[1]} scan, {n} '
                f'patterns: {counts}; {np.count_nonzero(self.reliable())} reliable '
                f'(reliability index >= 5)')

    def reliable(self, min_rindex=5.0, min_indexed=3):
        '''
        The patterns indexed with a reliability index of at least *min_rindex* and at least
        *min_indexed* peaks indexed, as a boolean array of the scan's shape.
        '''
        return ((self.status == OM_INDEXED) & (self.rindex >= min_rindex)
                & (self.nindexed >= min_indexed))

    def beam_directions(self):
        '''
        The beam direction at each pattern as a unit vector in the crystal frame, shape
        (rows, columns, 3), taken in the database's orientation region; NaN where not indexed.
        '''
        d = self.orientation[..., 2, :]               # U^T z: the beam's crystal components
        corners = self._corner_dirs()
        m = corners.mean(axis=0)
        flip = (d @ m) < 0
        return np.where(flip[..., None], -d, d)

    def beam_indices(self):
        '''The beam directions as zone axis indices [u, v, w], scaled so the largest is 1.'''
        uvw = self.beam_directions() @ np.linalg.inv(self.basis)
        m = np.max(np.abs(uvw), axis=-1, keepdims=True)       # NaN where not indexed
        with np.errstate(invalid='ignore', divide='ignore'):
            return uvw / m

    def euler_angles(self):
        '''
        Bunge Euler angles (phi1, Phi, phi2) in degrees, shape (rows, columns, 3), for the
        sample and crystal frames described in :py:mod:`pyemaps.orientmap`; NaN where not
        indexed.
        '''
        return euler_from_matrix(self.orientation)

    def ipf_colors(self, min_rindex=5.0, background=(0.0, 0.0, 0.0)):
        '''
        Inverse pole figure colours of the beam direction, shape (rows, columns, 3), values
        0 to 1. The corners of the database's orientation region are red, green and blue (and
        yellow, for a fourth corner), simplest zone axis first: for a cubic crystal, [001] is
        red, [011] green and [111] blue. Patterns that aren't :py:meth:`reliable` get
        *background*.
        '''
        corners = self._corner_dirs()
        order = _corner_order(self.corners)
        w = _region_weights(np.nan_to_num(self.beam_directions()), corners[order])
        rgb = w @ _CORNER_COLOURS[:len(order)]
        peak = rgb.max(axis=-1, keepdims=True)
        peak[peak == 0] = 1.0
        rgb = rgb / peak
        ok = self.reliable(min_rindex)
        rgb[~ok] = background
        return rgb

    def color_key(self, n=120):
        '''
        The colour key of :py:meth:`ipf_colors`: ``(xy, rgb, labels)``, points across the
        orientation region in stereographic projection about its centre, their colours, and
        the corners' positions and [u v w] labels.
        '''
        corners_c = self._corner_dirs()
        order = _corner_order(self.corners)
        cs = corners_c[order]
        k = len(cs)
        # directions across the region: combinations of the corners
        t = np.linspace(0.0, 1.0, n)
        if k == 3:
            a, b = np.meshgrid(t, t)
            keep = a + b <= 1.0
            wts = np.stack([a[keep], b[keep], 1.0 - a[keep] - b[keep]], -1)
        else:
            a, b = np.meshgrid(t, t)
            wts = np.stack([(1 - a) * (1 - b), a * (1 - b), a * b, (1 - a) * b], -1).reshape(-1, 4)
        dirs = wts @ cs
        dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
        w = _region_weights(dirs, cs)
        rgb = w @ _CORNER_COLOURS[:k]
        rgb /= np.maximum(rgb.max(axis=1, keepdims=True), 1e-12)
        xy = self._stereo(dirs, cs)
        labels = [(self._stereo(cs[i:i + 1], cs)[0], self._corner_label(order[i]))
                  for i in range(k)]
        return xy, rgb, labels

    def _corner_dirs(self):
        '''The region's corners as unit vectors in the crystal frame. dpgen gives them, like
        the beam directions, in reciprocal lattice components.'''
        c = self.corners @ reciprocal_basis(self.basis)
        return c / np.linalg.norm(c, axis=1, keepdims=True)

    def _corner_label(self, i):
        '''[u v w] when the corner is a zone axis with small indices, else its plane normal (h k l).'''
        hkl = self.corners[i]
        uvw = self._corner_dirs()[i] @ np.linalg.inv(self.basis)
        uvw = uvw / np.max(np.abs(uvw))
        for n in range(1, 7):
            v = uvw * n
            if np.allclose(v, np.round(v), atol=0.02):
                return '[' + ' '.join(f'{int(x):d}' for x in np.round(v) + 0) + ']'
        return '(' + ' '.join(f'{x:g}' for x in hkl) + ') normal'

    @staticmethod
    def _stereo(dirs, corners):
        '''
        Stereographic projection about the region's centre, turned so the first corner is at
        the bottom left, the second at the bottom right and the third above them.
        '''
        m = corners.mean(axis=0)
        m /= np.linalg.norm(m)

        def tangent(v):
            return v - (v @ m) * m

        e1 = tangent(corners[1]) - tangent(corners[0])
        e1 /= np.linalg.norm(e1)
        e2 = np.cross(m, e1)
        if tangent(corners[2]) @ e2 < tangent(corners[0]) @ e2:
            e2 = -e2
        t = 1.0 + dirs @ m
        return np.stack([(dirs @ e1) / t, (dirs @ e2) / t], -1)

    def show(self, kind='ipf', min_rindex=5.0, title=None, show=True):
        '''
        Plot the map.

        :param kind: ``'ipf'`` for the inverse pole figure colours of the beam direction, with
            their colour key; or one of ``'rindex'``, ``'correlation'``, ``'nindexed'``,
            ``'npeaks'`` and ``'status'`` for that value at each pattern.
        :param min_rindex: for ``'ipf'``, the reliability index below which a pattern is
            black.
        :param title: the figure title.
        :param show: call ``matplotlib.pyplot.show``; with False, the figure is returned for
            you to save or change.
        :return: the matplotlib figure.
        '''
        import matplotlib.pyplot as plt

        if kind == 'ipf':
            fig, (ax, kax) = plt.subplots(1, 2, figsize=(10, 4.8),
                                          gridspec_kw={'width_ratios': [3, 1.4]})
            ax.imshow(self.ipf_colors(min_rindex), interpolation='nearest')
            ax.set_title(title or 'Orientation map (beam direction)')
            xy, rgb, labels = self.color_key()
            kax.scatter(xy[:, 0], xy[:, 1], c=rgb, s=6, marker='s', linewidths=0)
            for (x, y), text in labels:
                kax.annotate(text, (x, y), textcoords='offset points', xytext=(0, 6),
                             ha='center', fontsize=9)
            kax.set_aspect('equal')
            kax.axis('off')
            kax.set_title('Colour key')
        else:
            values = {'rindex': self.rindex, 'correlation': self.correlation,
                      'nindexed': self.nindexed, 'npeaks': self.npeaks, 'status': self.status}
            if kind not in values:
                raise ValueError(f"kind must be 'ipf' or one of {sorted(values)}, not {kind!r}")
            fig, ax = plt.subplots(figsize=(6, 5))
            im = ax.imshow(values[kind], interpolation='nearest', cmap='viridis')
            fig.colorbar(im, ax=ax)
            ax.set_title(title or kind)
        ax.set_xlabel('scan column')
        ax.set_ylabel('scan row')
        fig.tight_layout()
        if show:
            plt.show()
        return fig

    def save(self, path):
        '''Save the map to a NumPy ``.npz`` file, to load with :py:meth:`load`.'''
        np.savez_compressed(path, scan_shape=np.array(self.scan_shape),
                            basis=self.basis, corners=self.corners,
                            database=np.array(self.database),
                            params=np.array(repr(self.params)),
                            **{f: getattr(self, f) for f in _FIELDS})

    @classmethod
    def load(cls, path):
        '''Load a map saved by :py:meth:`save`.'''
        import ast
        with np.load(path, allow_pickle=False) as z:
            kw = {f: z[f] for f in _FIELDS}
            params = ast.literal_eval(str(z['params']))
            return cls(tuple(z['scan_shape']), basis=z['basis'], corners=z['corners'],
                       database=str(z['database']), params=params, **kw)


class _DatabaseGeometry:
    '''The loaded stem4d database's crystal and each pattern's frame, for orientations.'''

    def __init__(self, stem4d):
        self._s = stem4d
        ret, gmx = stem4d.getDPDBMetric(9)
        if ret != 0:
            raise RuntimeError('the diffraction pattern database is not loaded')
        self.basis = direct_basis(gmx)
        self.recip = reciprocal_basis(self.basis)
        ret, uvw, n = stem4d.getDPDBCorners(12)
        self.corners = np.array(uvw, dtype=float).reshape(4, 3)[:n] if ret == 0 else np.eye(3)
        self._frames = {}

    def pattern(self, idp):
        ret, refl, ng = self._s.getDPDBPattern(int(idp), 6 * 256)
        if ret == 0 and ng > 256:
            ret, refl, ng = self._s.getDPDBPattern(int(idp), 6 * ng)
        if ret != 0:
            raise RuntimeError(f'database pattern {idp} is not available')
        return np.array(refl, dtype=float).reshape(-1, 6)[:ng]

    def beam(self, idp):
        '''
        Database pattern *idp*'s beam direction as a unit vector in the crystal frame. dpgen
        stores it in reciprocal lattice components (along a*, b*, c*).
        '''
        ret, bx, by, bz, _, _ = self._s.getDPDBBeam(int(idp))
        if ret != 0:
            raise RuntimeError(f'database pattern {idp} is not available')
        b = np.array([bx, by, bz]) @ self.recip
        return b / np.linalg.norm(b)

    def frame(self, idp):
        '''
        Rotation from the crystal frame to database pattern *idp*'s frame (x, y, beam): the
        pattern's reflections fitted to their positions, with its beam direction along z.
        '''
        if idp not in self._frames:
            r = self.pattern(idp)
            g = r[:, :3] @ self.recip
            q = np.c_[r[:, 3:5], np.zeros(len(r))]
            b = self.beam(idp)
            # the beam weighs as much as all the reflections together; it fixes the frame
            # even when the reflections are few or in a line
            w = np.sqrt(max(np.sum(g * g), 1e-6))
            best = None
            for sign in (1.0, -1.0):
                P = np.vstack([g, w * b])
                Q = np.vstack([q, [0.0, 0.0, sign * w]])
                R = fit_rotation(P, Q)
                res = np.sum((P @ R.T - Q) ** 2)
                if best is None or res < best[0]:
                    best = (res, R)
            self._frames[idp] = best[1]
        return self._frames[idp]

    def orientation(self, idp, rotation):
        return image_rotation(rotation) @ self.frame(idp)
