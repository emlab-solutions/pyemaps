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

"""Ronchigrams of a corrected and an uncorrected probe.

A Ronchigram is the shadow image of a convergent probe through a thin amorphous sample. Where
the probe's aberrations are small, the shadow is a smooth, magnified image of the sample; where
they're large, it's distorted into rings and streaks. Corrector alignment is done on it.

This sample uses pyEMAPS' Probe class to show the Ronchigrams of 100 A of amorphous aluminium:

1. a 200 kV probe with a corrector: a 25 mrad aperture, a small negative Cs balancing C5, and
   the residual aberrations a corrector measured on a real microscope;
2. the same probe with 20 nm of two-fold astigmatism added;
3. an uncorrected probe, Cs 1.2 mm, at its Scherzer defocus, with the aperture opened to
   25 mrad, which shows the rings of spherical aberration.

Run it with:

    python ronchigram.py
"""
import matplotlib.pyplot as plt

from pyemaps import Probe

# Residual aberrations, (amplitude, angle in degrees): a1, a2, b2 in nm; a3, a4, b4, d4, s3 in
# um; a5 in mm.
CORRECTOR = {'a1': (1.349, 146.2), 'a2': (58.94, -131.9), 'b2': (22.89, 141.4),
             'a3': (0.3054, -7.5), 's3': (0.1977, -161.2), 'a4': (35.96, 68.9),
             'd4': (20.8, -47.0), 'b4': (8.769, 2.8), 'a5': (0.7825, -114.8)}


def corrected_probe():
    """A corrected 200 kV probe. The map is 100 A across with 256 x 256 pixels, so the
    Ronchigram reaches 32 mrad from its center, beyond the aperture."""
    return Probe(kv=200, aperture=25, defocus=-5.14, cs=-0.00355, c5=3.829,
                 aberrations=CORRECTOR, size=100, sampling=256)


def main():
    probes = {}
    probes['Corrected'] = corrected_probe()

    astigmatic = corrected_probe()
    astigmatic.set_aberration('a1', 20.0, 30.0)
    probes['With 20 nm of a1'] = astigmatic

    uncorrected = Probe(kv=200, cs=1.2, size=100, sampling=256)
    uncorrected.scherzer()
    uncorrected.aperture = 25.0       # open the aperture to see the aberrations
    probes['Uncorrected, Cs 1.2 mm'] = uncorrected

    # The same sample for all three: 100 A of amorphous aluminium (the default potential).
    sample = corrected_probe().random_potential(density=0.05, z=13, thickness=100, seed=1211)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, (name, probe) in zip(axes, probes.items()):
        probe.show(probe.ronchigram(sample), 'ronchigram', ax=ax,
                   title=f'{name}\ndefocus {probe.defocus:.1f} nm')
        print(f'{name}: {probe}')
    fig.suptitle('Ronchigrams, 200 kV, 25 mrad aperture (yellow)')
    fig.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()
