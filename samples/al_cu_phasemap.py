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

"""Phase map of a synthetic 4D-STEM scan of aluminium and copper grains.

This sample uses pyEMAPS' dpgen and stem4d modules. Aluminium and copper are both FCC, with
lattice constants 4.05 and 3.61 A, so their spot patterns look alike: the same angles, 12%
apart in scale. The sample makes a scan of grains of both, at known orientations, maps which
phase each pattern belongs to with StackImage.mapPhases, and compares the map with the truth:

1. the true phases and the mapped ones (grey: ambiguous);
2. the confidence of each pattern's phase;
3. each pattern's orientation, from its phase's orientation map.

The patterns are kinematic spot patterns with counting noise. Real patterns are harder:
dynamical intensities, background, overlapping grains, and a camera constant known only so
well. Phase mapping is experimental.

It needs an activated pyEMAPS license; see the License page of the pyEMAPS documentation.
Contact support@emlabsoftware.com for license information.

Run it with:

    python al_cu_phasemap.py
"""
import os
import tempfile

import numpy as np

from pyemaps import EMC, Crystal, StackImage, XDPImageError, write_im3

PHASES = {'Aluminium': ('Aluminium', 4.0493), 'Copper': ('Copper_FCC', 3.6149)}
SIZE = 200                  # pattern size, pixels
CENTER = (99.5, 99.5)       # pattern center (column, row), pixels
CC = 29.0                   # camera constant, pixels per 1/A
SIGMA = 3.0                 # spot width, pixels
SCAN = (14, 14)             # scan rows and columns
# Each grain: its phase, its zone axis along the beam, its in-plane rotation in degrees, and the
# scan point (row, column) its region grows from.
GRAINS = [('Aluminium', (1, 1, 1), 17.0, (2, 3)), ('Copper', (1, 1, 2), 141.0, (3, 10)),
          ('Copper', (0, 1, 1), 233.0, (9, 2)), ('Aluminium', (1, 1, 4), 302.0, (10, 10)),
          ('Copper', (1, 1, 1), 64.0, (7, 7))]


def zone_orientation(zone, angle):
    """The orientation with the beam along *zone*, turned *angle* degrees about it (crystal
    frame to the image frame: x along the columns, y along the rows, z along the beam)."""
    b = np.asarray(zone, float)
    b /= np.linalg.norm(b)
    x = np.cross(b, [0.3, 0.5, 0.8])
    x /= np.linalg.norm(x)
    y = np.cross(b, x)
    c, s = np.cos(np.radians(angle)), np.sin(np.radians(angle))
    return np.array([c * x + s * y, -s * x + c * y, b])


def spot_pattern(U, a, rng):
    """A kinematic FCC spot pattern at 200 kV for orientation *U* and lattice constant *a*,
    with counting noise."""
    h = np.arange(-8, 9)
    H = np.array(np.meshgrid(h, h, h, indexing='ij')).reshape(3, -1).T
    odd = (H % 2).sum(1)
    H = H[((odd == 0) | (odd == 3)) & np.any(H != 0, axis=1)]      # FCC reflections
    g = (H / a) @ U.T
    gl = np.linalg.norm(g, axis=1)
    k, sg_tol = 1 / 0.0251, 0.02
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
    """The scan's patterns and the true phase of each, as an index into PHASES."""
    rows, cols = np.mgrid[0:SCAN[0], 0:SCAN[1]]
    seeds = np.array([g[3] for g in GRAINS])
    grain = np.argmin(np.hypot(rows[..., None] - seeds[:, 0], cols[..., None] - seeds[:, 1]),
                      axis=-1)
    names = list(PHASES)
    truth = np.array([[names.index(GRAINS[g][0]) for g in row] for row in grain])
    patterns = []
    for r in range(SCAN[0]):
        for c in range(SCAN[1]):
            name, zone, angle, _ = GRAINS[grain[r, c]]
            patterns.append(spot_pattern(zone_orientation(zone, angle), PHASES[name][1], rng))
    return np.array(patterns), truth


def show(pm, truth):
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    from pyemaps.phasemap import _PHASE_COLOURS

    fig, ax = plt.subplots(1, 4, figsize=(17, 4.2))
    ax[0].imshow(truth, cmap=ListedColormap(_PHASE_COLOURS[:len(PHASES)]),
                 interpolation='nearest')
    ax[0].set_title('True phases')
    ax[1].imshow(pm.phase_colors(), interpolation='nearest')
    f = pm.fractions()
    ax[1].set_title('Mapped: ' + ', '.join(f'{k} {100 * v:.0f}%' for k, v in f.items()))
    im = ax[2].imshow(pm.confidence, interpolation='nearest', cmap='viridis')
    fig.colorbar(im, ax=ax[2])
    ax[2].set_title('Confidence')
    ax[3].imshow(pm.ipf_colors(), interpolation='nearest')
    ax[3].set_title('Orientation (each phase its own key)')
    for a in ax:
        a.set_xticks([])
        a.set_yticks([])
    fig.tight_layout()
    plt.show()
    names = np.array(pm.names)
    decided = pm.decided()
    right = np.count_nonzero(pm.phase[decided] == truth[decided])
    print(f'{np.count_nonzero(decided)} of {truth.size} patterns decided, {right} of them '
          f'correctly; {np.count_nonzero(pm.ambiguous)} ambiguous')
    return fig


def map_scan(seed=1):
    """Make the synthetic scan, map its phases and compare them with the truth.

    :return: the phase map, or None on failure.
    """
    databases = {}
    for name, (builtin, _) in PHASES.items():
        ret, databases[name] = Crystal.from_builtin(builtin).generateDPDB(
            emc=EMC(zone=(0, 0, 1)), xa=(2, 0, 0), res=200)
        if ret != 0:
            print(f'Failed to generate the {name} diffraction pattern database')
            return None
    patterns, truth = make_scan(np.random.default_rng(seed))
    with tempfile.TemporaryDirectory() as tmp:
        scan_file = os.path.join(tmp, 'al_cu_scan.im3')
        write_im3(scan_file, patterns)          # the scan, one pattern per stack
        try:
            pm = StackImage(scan_file).mapPhases(databases, cc=CC, sigma=SIGMA,
                                                 img_center=CENTER, scan_shape=SCAN)
        except XDPImageError as e:
            print(f'Phase mapping failed: {e}')
            return None
    print(pm)
    show(pm, truth)
    return pm


if __name__ == '__main__':
    map_scan()
