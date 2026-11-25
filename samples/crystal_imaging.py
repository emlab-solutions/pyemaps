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

"""HREM and STEM images, and the Ronchigram, of a silicon crystal along [110].

Along [110], silicon's atoms line up in pairs of columns 1.36 Å apart: the "dumbbells". Whether
an image shows them as two spots or as one blob is a classic test of a microscope's resolution.

This sample uses pyEMAPS' Probe class to compute the projected potential of a thin silicon
crystal from its atoms, with Probe.crystal_potential, and then:

1. its HREM images with an uncorrected 200 kV objective lens (Cs 1.2 mm) at the Scherzer
   defocus, and with a corrected one (Cs -13 um, defocus +7 nm);
2. its STEM images with an uncorrected probe at the Scherzer defocus, and with a corrected
   probe (25 mrad aperture, Cs and defocus balancing C5);
3. the Ronchigram of the corrected probe on it, where the crystal's diffracted disks overlap.

Run it with:

    python crystal_imaging.py
"""
import math

import matplotlib.pyplot as plt

from pyemaps import Crystal, Probe

SILICON = Crystal.from_builtin('Silicon')
A = float(SILICON.cell.a)

# The map repeats itself, so it should hold a whole number of the crystal's repeats: along
# [110], with [001] along x, those are a = 5.43 A along x and a / sqrt(2) = 3.84 A along y.
# 12 a = 65.17 A is 17 repeats along y within 0.2%. 1024 pixels of 0.064 A.
MAP = {'size': 12 * A, 'sampling': 1024}
# 8 repeats of the crystal along [110], 30.7 A
THICKNESS = 8 * A / math.sqrt(2)
# the HREM lenses' coherence: a 1.5 mm Cc, 0.7 eV energy spread, 0.2 mrad illumination
ENVELOPES = {'cc': 1.5, 'energy_spread': 0.7, 'semi_angle': 0.2}


def zoom(ax, half=6.0):
    ax.set_xlim(-half, half)
    ax.set_ylim(half, -half)


def main():
    lens = Probe(kv=200, **MAP)
    potential = lens.crystal_potential(SILICON, zone=(1, 1, 0), thickness=THICKNESS)
    print(f'Projected potential of {THICKNESS:.1f} A of silicon along [110]: '
          f'mean {potential.mean() / THICKNESS:.2f} V (the mean inner potential)')

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    ax = axes[0, 0]
    lens.show(potential, 'potential', ax=ax,
              title=f'Projected potential, [110], {THICKNESS:.1f} Å\n[001] across')
    zoom(ax)

    # HREM: the exit wave through two objective lenses
    uncorrected = Probe(kv=200, cs=1.2, **ENVELOPES, **MAP)
    uncorrected.scherzer(mode=2)
    uncorrected.aperture = 20.0
    corrected = Probe(kv=200, cs=-0.013, defocus=7.0, aperture=40.0, **ENVELOPES, **MAP)
    wave = lens.exit_wave(potential)
    for k, (name, objective) in enumerate((('uncorrected, Scherzer', uncorrected),
                                           ('corrected', corrected))):
        ax = axes[0, k + 1]
        objective.show(objective.hrem(wave), 'hrem', ax=ax,
                       title=f'HREM image, {name}\ndefocus {objective.defocus:.1f} nm')
        zoom(ax)

    # STEM: the probe of an uncorrected and a corrected lens over the crystal
    probe_uncorrected = Probe(kv=200, cs=1.2, **MAP)
    probe_uncorrected.scherzer()
    probe_corrected = Probe(kv=200, aperture=25, c5=3.829, **MAP)
    probe_corrected.haider(optimum_aperture=False)
    for k, (name, probe) in enumerate((('uncorrected, Scherzer', probe_uncorrected),
                                       ('corrected (Haider)', probe_corrected))):
        ax = axes[1, k]
        d50 = probe.diameter(50)
        probe.show(probe.stem_image(potential), 'stem', ax=ax,
                   title=f'STEM image, {name}\nprobe 50% diameter {d50:.2f} Å')
        zoom(ax)
        print(f'STEM probe, {name}: 50% within {d50:.2f} A')

    # The Ronchigram of the corrected probe: the direct and diffracted disks overlap
    ax = axes[1, 2]
    probe_corrected.show(probe_corrected.ronchigram(potential), 'ronchigram', ax=ax,
                         title='Ronchigram, corrected probe')
    ax.set_xlim(-50, 50)
    ax.set_ylim(50, -50)

    fig.suptitle('Silicon [110]: the dumbbells, 1.36 Å apart, 200 kV')
    fig.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()
