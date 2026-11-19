# This file is part of pyEMAPS.
# Copyright (C) 2021-2026 EMLab Solutions, Inc.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Additional permission under GPLv3 Section 7:
# See license-exception.txt for the exception permitting
# combination with the separately licensed backend, emaps.
#
# Author: EMLab Solutions, Inc. Questions and comments: support@emlabsoftware.com

"""Orientation map of a synthetic Aluminium 4D-STEM scan.

This sample uses pyEMAPS' dpgen and stem4d modules. It makes a small scan of four Aluminium
grains whose orientations are known, maps the crystal orientation at every scan point with
StackImage.mapOrientation, and compares the map with the truth:

1. the true orientations and the mapped ones, coloured by the beam direction in the crystal
   (inverse pole figure colours) with the same colour key;
2. the angle between the true and the mapped orientation at each point;
3. the reliability index of each pattern.

The patterns are kinematic spot patterns with counting noise and a small orientation spread
inside each grain. Real patterns are harder: dynamical intensities, background, overlapping
grains. The four grain orientations are ones that index well; try your own in GRAINS.

It needs an activated pyEMAPS license; see the License page of the pyEMAPS documentation.
Contact support@emlabsoftware.com for license information.

Run it with:

    python al_orientmap.py
"""
import itertools
import os
import tempfile

import numpy as np

from pyemaps import (EMC, Crystal, StackImage, XDPImageError, write_im3,
                     OrientationMap, OM_INDEXED)

A = 4.0493                  # Aluminium lattice parameter, Å (cubic: a along x, b along y)
SIZE = 200                  # pattern size, pixels
CENTER = (99.5, 99.5)       # pattern center (column, row), pixels
CC = 29.0                   # camera constant, pixels per 1/Å
SIGMA = 3.0                 # spot width, pixels: the spots' standard deviation, about
                            # half their full width at half maximum, as sigma wants
SCAN = (12, 12)             # scan rows and columns

# Each grain: its zone axis [u v w] along the beam, its in-plane rotation in degrees, and the
# scan point (row, column) its region grows from.
GRAINS = [((1, 1, 1), 17.0, (2, 3)),
          ((1, 1, 2), 141.0, (3, 10)),
          ((1, 1, 4), 233.0, (9, 2)),
          ((0, 1, 2), 302.0, (9, 9))]


def zone_orientation(zone, angle):
    """The orientation with the beam along *zone*, turned *angle* degrees about it.

    An orientation matrix U takes a vector in the crystal frame to the image frame: x along
    the pattern's columns, y along its rows and z along the beam, as in pyEMAPS' maps.
    """
    b = np.asarray(zone, float)
    b /= np.linalg.norm(b)
    x = np.cross(b, [0.3, 0.5, 0.8])
    x /= np.linalg.norm(x)
    y = np.cross(b, x)
    c, s = np.cos(np.radians(angle)), np.sin(np.radians(angle))
    return np.array([c * x + s * y, -s * x + c * y, b])


def small_rotation(rng, degrees):
    """A random rotation by up to about *degrees*, for the spread inside a grain."""
    axis = rng.normal(size=3)
    axis /= np.linalg.norm(axis)
    t = np.radians(rng.normal(0.0, degrees))
    K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    return np.eye(3) + np.sin(t) * K + (1 - np.cos(t)) * K @ K


def spot_pattern(U, rng):
    """A kinematic Aluminium spot pattern at 200 kV for orientation *U*, with counting noise."""
    h = np.arange(-8, 9)
    H = np.array(np.meshgrid(h, h, h, indexing='ij')).reshape(3, -1).T
    odd = (H % 2).sum(1)
    H = H[((odd == 0) | (odd == 3)) & np.any(H != 0, axis=1)]      # FCC reflections
    g = (H / A) @ U.T                                               # in the image frame
    gl = np.linalg.norm(g, axis=1)
    k, sg_tol = 1 / 0.0251, 0.02                                    # 1/wavelength at 200 kV
    s = -(2 * k * g[:, 2] + gl ** 2) / (2 * k)                      # excitation error
    keep = (gl < 1.6) & (np.abs(s) < sg_tol)
    yy, xx = np.mgrid[0:SIZE, 0:SIZE].astype(float)
    img = 3.0 * np.exp(-((xx - CENTER[0]) ** 2 + (yy - CENTER[1]) ** 2) / (2 * (2 * SIGMA) ** 2))
    for (gx, gy, _), gg, ss in zip(g[keep], gl[keep], s[keep]):
        amp = np.exp(-0.6 * gg ** 2) * np.exp(-(ss / (sg_tol / 2)) ** 2)
        img += amp * np.exp(-((xx - CENTER[0] - CC * gx) ** 2 + (yy - CENTER[1] - CC * gy) ** 2)
                            / (2 * SIGMA ** 2))
    return rng.poisson(img * 400 + 5).astype(np.float32)


def make_scan(rng):
    """Scan patterns and the true orientation at each point."""
    rows, cols = np.mgrid[0:SCAN[0], 0:SCAN[1]]
    seeds = np.array([g[2] for g in GRAINS])
    dist = np.hypot(rows[..., None] - seeds[:, 0], cols[..., None] - seeds[:, 1])
    grain = np.argmin(dist, axis=-1)
    base = [zone_orientation(z, a) for z, a, _ in GRAINS]
    truth = np.zeros(SCAN + (3, 3))
    patterns = []
    for r in range(SCAN[0]):
        for c in range(SCAN[1]):
            truth[r, c] = small_rotation(rng, 0.3) @ base[grain[r, c]]
            patterns.append(spot_pattern(truth[r, c], rng))
    return np.array(patterns), truth, grain


def misorientation(U1, U2):
    """Smallest angle, in degrees, between two Aluminium orientations, over the cubic
    symmetry and a 180 degree turn about the beam (which a spot pattern can't tell apart)."""
    best = 180.0
    for p in itertools.permutations(range(3)):
        for sign in itertools.product([1, -1], repeat=3):
            S = np.zeros((3, 3))
            S[range(3), p] = sign
            if np.linalg.det(S) < 0:
                continue
            for E in (np.eye(3), np.diag([-1.0, -1.0, 1.0])):
                M = E @ U1 @ S @ U2.T
                best = min(best, np.degrees(np.arccos(np.clip((np.trace(M) - 1) / 2, -1, 1))))
    return best


def truth_map(m, truth):
    """An OrientationMap holding the true orientations, to colour them like the result."""
    n = m.status.size
    return OrientationMap(m.scan_shape, np.full(n, OM_INDEXED), m.dp, m.rotation,
                          m.correlation, m.map_peak, np.full(n, 100.0), m.npeaks,
                          np.full(n, 10), truth, m.basis, m.corners)


def show(m, truth):
    import matplotlib.pyplot as plt

    err = np.full(m.scan_shape, np.nan)
    for r, c in np.ndindex(m.scan_shape):
        if m.status[r, c] == OM_INDEXED:
            err[r, c] = misorientation(m.orientation[r, c], truth[r, c])

    fig, ax = plt.subplots(1, 5, figsize=(17, 3.8),
                           gridspec_kw={'width_ratios': [3, 3, 1.6, 3.6, 3.6]})
    ax[0].imshow(truth_map(m, truth).ipf_colors(), interpolation='nearest')
    ax[0].set_title('True orientations')
    ax[1].imshow(m.ipf_colors(), interpolation='nearest')
    ax[1].set_title('Mapped (black: not reliable)')
    xy, rgb, labels = m.color_key()
    ax[2].scatter(xy[:, 0], xy[:, 1], c=rgb, s=5, marker='s', linewidths=0)
    for (x, y), text in labels:
        ax[2].annotate(text, (x, y), textcoords='offset points', xytext=(0, 5),
                       ha='center', fontsize=8)
    ax[2].set_aspect('equal')
    ax[2].set_title('Beam direction')
    im = ax[3].imshow(err, interpolation='nearest', cmap='magma', vmin=0, vmax=2)
    fig.colorbar(im, ax=ax[3], label='degrees')
    ax[3].set_title('Mapped vs true')
    im = ax[4].imshow(m.rindex, interpolation='nearest', cmap='viridis')
    fig.colorbar(im, ax=ax[4])
    ax[4].set_title('Reliability index')
    for a in ax:
        if a is not ax[2]:
            a.set_xticks([])
            a.set_yticks([])
        else:
            a.axis('off')
    fig.tight_layout()
    plt.show()

    ok = ~np.isnan(err)
    print(f'{ok.sum()} of {err.size} patterns indexed; mapped orientation within 1 degree of '
          f'the truth for {np.sum(err[ok] < 1)}, median error {np.median(err[ok]):.2f} degrees')
    return fig


def map_scan(name='Aluminium', seed=1):
    """Make the synthetic scan, map its orientations and compare them with the truth.

    :return: the orientation map, or None on failure.
    """
    crystal = Crystal.from_builtin(name)
    ret, db_file = crystal.generateDPDB(emc=EMC(zone=(0, 0, 1)), xa=(2, 0, 0), res=200)
    if ret != 0:
        print('Failed to generate the diffraction pattern database')
        return None

    rng = np.random.default_rng(seed)
    patterns, truth, _ = make_scan(rng)
    with tempfile.TemporaryDirectory() as tmp:
        scan_file = os.path.join(tmp, 'al_scan.im3')
        write_im3(scan_file, patterns)          # the scan, one pattern per stack
        try:
            m = StackImage(scan_file).mapOrientation(
                db_file,
                cc=CC,                          # camera constant, pixels per 1/Å
                sigma=SIGMA,                    # half the peaks' full width at half maximum
                img_center=CENTER,              # pattern center (column, row), in pixels
                rmin=10,                        # radius excluded around the center
                search_box=10.0,                # peak search box size, in pixels
                # Noisy patterns need a looser peak shape test than the default (0.825), and
                # min_snr to keep the background out of the peaks. With the default, the [012]
                # grain here finds no peaks at all.
                peak_threshold=0.6,
                min_snr=3.0,
                scan_shape=SCAN)                # rows and columns of the scan
        except XDPImageError as e:
            print(f'Failed to map the orientations: {e.message}')
            return None

    print(m)
    show(m, truth)
    return m


def main():
    map_scan()


if __name__ == '__main__':
    main()
