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

"""Ronchigram, probe and contrast transfer function of an aberration-corrected probe.

This sample uses pyEMAPS' Probe class for a 200 kV probe-forming lens with a corrector: a 25 mrad
aperture, a small negative Cs balancing C5, and the residual aberrations a corrector measured
on a real microscope. It shows:

1. the Ronchigram of 100 A of amorphous aluminium;
2. the probe, with the diameter that holds half of its intensity;
3. the contrast transfer function;

then the same for an uncorrected lens (Cs 1.2 mm) at its Scherzer settings, for comparison.

Run it with:

    python ronchigram.py
"""
import copy

import matplotlib.pyplot as plt

from pyemaps import Probe

# Residual aberrations, (amplitude, angle in degrees): a1, a2, b2 in nm; a3, a4, b4, d4, s3 in
# um; a5 in mm.
CORRECTOR = {'a1': (1.349, 146.2), 'a2': (58.94, -131.9), 'b2': (22.89, 141.4),
             'a3': (0.3054, -7.5), 's3': (0.1977, -161.2), 'a4': (35.96, 68.9),
             'd4': (20.8, -47.0), 'b4': (8.769, 2.8), 'a5': (0.7825, -114.8)}


def show_probe(probe, title):
    """Show a probe's Ronchigram, intensity and CTF side by side."""
    ronchigram = probe.ronchigram()   # of the default random potential: 100 A of aluminium

    # The probe on a finer map, 0.1 A pixels: its diameter counts whole pixels.
    fine = copy.copy(probe)
    fine.size = 25.6
    intensity = fine.probe()
    d50 = fine.diameter(50, intensity)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    probe.show(ronchigram, 'ronchigram', ax=axes[0], title='Ronchigram')
    fine.show(intensity, 'probe', ax=axes[1], title=f'Probe: 50% within {d50:.2f} A')
    axes[1].set_xlim(-5, 5)
    axes[1].set_ylim(5, -5)
    probe.show(probe.ctf(), 'ctf', ax=axes[2], title='CTF')
    # Out to 1.5 times the aperture: further out, an uncorrected lens's CTF oscillates faster
    # than the map's pixels.
    k = 1.5 * probe.kmax
    axes[2].set_xlim(-k, k)
    axes[2].set_ylim(k, -k)
    fig.suptitle(f'{title}: {probe.kv:g} kV, {probe.aperture:.1f} mrad aperture, '
                 f'defocus {probe.defocus:.2f} nm, Cs {probe.cs:g} mm')
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    print(f'{title}: {probe}')
    print(f'  50% of the intensity within a diameter of {d50:.3f} A')


def main():
    # A corrected lens. The map is 100 A across with 256 x 256 pixels: the Ronchigram then
    # reaches 32 mrad from its center, beyond the aperture.
    corrected = Probe(kv=200, aperture=25, defocus=-5.14, cs=-0.00355, c5=3.829,
                      aberrations=CORRECTOR, size=100, sampling=256)
    show_probe(corrected, 'Corrected')

    # An uncorrected lens at its Scherzer defocus and aperture, on the same map.
    uncorrected = Probe(kv=200, cs=1.2, size=100, sampling=256)
    settings = uncorrected.scherzer()
    print(f'Scherzer settings for Cs 1.2 mm: defocus {settings["defocus"]:.1f} nm, '
          f'aperture {settings["aperture"]:.2f} mrad')
    show_probe(uncorrected, 'Uncorrected (Scherzer)')
    plt.show()


if __name__ == '__main__':
    main()
