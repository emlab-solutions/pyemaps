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

"""HREM images and CBED patterns of silicon [110] at several thicknesses, by the multislice method.

A thin crystal's image follows its projected potential, but as the crystal gets thicker the
electron wave is scattered again and again on its way through it, and the image and the
diffraction pattern change with the thickness. The multislice method follows the wave through
the crystal slice by slice.

This sample uses pyEMAPS' Probe class (a licensed feature: it needs an active pyEMAPS license)
for silicon along [110]. The silicon is a refined crystal structure from the Crystallography
Open Database (COD entry 2102763; Wu et al., Acta Cryst. B 63, 2007), with its thermal factor,
read from the CIF file next to this sample:

1. the HREM images of its exit waves at 20, 100 and 300 A, with a corrected 200 kV objective
   lens (Cs -13 um, defocus +7 nm), from one pass through the crystal (crystal_exit_wave);
2. its convergent-beam diffraction (CBED) patterns at 100, 300 and 600 A, with a 3 mrad probe
   focused on it (crystal_ronchigram): the intensity inside the disks changes with thickness.

The maps hold a whole number of the crystal's repeats, which crystal_repeats lists, and
fit=True removes the last 0.17% so the crystal has no seam at their edges.

Run it with:

    python crystal_thickness.py
"""
import os

import matplotlib.pyplot as plt
import numpy as np

from pyemaps import Crystal, Probe

# silicon from the Crystallography Open Database (https://www.crystallography.net, public
# domain): COD 2102763, a = 5.42712 A, Uiso = 0.0072 A^2
SILICON = Crystal.from_cif(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        'Si_COD_2102763.cif'))
SILICON.name = 'Silicon'            # a CIF names it after its COD entry
ZONE = (1, 1, 0)


def main():
    a = float(SILICON.cell.a)
    repeats = Probe().crystal_repeats(SILICON, zone=ZONE, max_size=70)
    print(f'Silicon [110]: repeats {np.hypot(*repeats["repeats"][0]):.4f} and '
          f'{np.hypot(*repeats["repeats"][1]):.4f} A across, {repeats["period"]:.4f} A along '
          f'the beam; seam-free sizes up to 70 A: {[round(s, 2) for s, _ in repeats["sizes"]]}')

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))

    # HREM: 12 a = 65.2 A, 512 pixels of 0.13 A
    lens = Probe(kv=200, cs=-0.013, defocus=7.0, aperture=40.0, cc=1.5, energy_spread=0.7,
                 semi_angle=0.2, size=12 * a, sampling=512)
    thicknesses = [20, 100, 300]
    waves = lens.crystal_exit_wave(SILICON, zone=ZONE, thickness=thicknesses, fit=True)
    for ax, t, wave in zip(axes[0], thicknesses, waves):
        image = lens.hrem(wave)
        print(f'HREM at {t} A: contrast (std / mean) {image.std() / image.mean():.3f}')
        lens.show(image, 'hrem', ax=ax, title=f'HREM image, {t} Å')
        ax.set_xlim(-6, 6)
        ax.set_ylim(6, -6)

    # CBED: a larger map, 24 a = 130 A with 1024 pixels, for finer angles (0.19 mrad per pixel)
    probe = Probe(kv=200, aperture=3.0, cs=1.2, defocus=0.0, size=24 * a, sampling=1024)
    thicknesses = [100, 300, 600]
    patterns = probe.crystal_ronchigram(SILICON, zone=ZONE, thickness=thicknesses, fit=True)
    for ax, t, pattern in zip(axes[1], thicknesses, patterns):
        probe.show(np.sqrt(pattern), 'ronchigram', ax=ax, aperture=False,
                   title=f'CBED pattern, {t} Å (square root)')
        ax.set_xlim(-25, 25)
        ax.set_ylim(25, -25)

    fig.suptitle('Silicon [110] at 200 kV, by the multislice method')
    fig.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()
