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

"""The contrast transfer function of an objective lens.

The contrast transfer function (CTF), sin(chi), tells how strongly, and with which sign, each
spatial frequency of a thin sample shows in a high-resolution TEM image. Coherence envelopes
damp it at high frequencies: the temporal one from the chromatic aberration and the energy
spread, the spatial one from the illumination's convergence.

This sample uses pyEMAPS' Probe class for an uncorrected 200 kV lens, Cs 1.2 mm:

1. the CTF at the Scherzer defocus, in 2-D, with and without the envelopes;
2. profiles of the CTF along a line, at the Scherzer defocus and 30 nm either side of it;
3. the CTF of a corrected lens with a small negative Cs, -13 um, and 7 nm of overfocus, which
   transfers frequencies with one sign until the envelopes stop them, near 1.1 1/A.

Run it with:

    python ctf.py
"""
import matplotlib.pyplot as plt
import numpy as np

from pyemaps import Probe

# A 200 A map of 1024 x 1024 pixels: the CTF reaches 2.56 1/A from its center in steps of
# 0.005 1/A, fine enough for the uncorrected lens's fast oscillations at high frequencies.
MAP = {'size': 200, 'sampling': 1024}

# Envelopes: Cc 1.5 mm with a 0.7 eV energy spread, and a 0.2 mrad illumination semi-angle.
ENVELOPES = {'cc': 1.5, 'energy_spread': 0.7, 'semi_angle': 0.2}


def profile(probe, ctf):
    """The CTF along the row through the center, from zero frequency outwards."""
    n = probe.sampling
    k = np.arange(n // 2) / probe.size
    return k, ctf[n // 2, n // 2:]


def main():
    coherent = Probe(kv=200, cs=1.2, semi_angle=0.0, **MAP)
    settings = coherent.scherzer(mode=2)
    damped = Probe(kv=200, cs=1.2, **ENVELOPES, **MAP)
    damped.scherzer(mode=2)
    print(f'Scherzer defocus {settings["defocus"]:.1f} nm; the point resolution is about '
          f'{1 / settings["kmax"]:.2f} A')

    fig, axes = plt.subplots(2, 2, figsize=(11, 10))
    k_max = 1.0
    for ax, (name, probe) in zip(axes[0], (('Coherent', coherent), ('With envelopes', damped))):
        probe.show(probe.ctf(), 'ctf', ax=ax, aperture=False,
                   title=f'{name}, defocus {probe.defocus:.1f} nm')
        # further out, the oscillations are finer than the screen's pixels
        ax.set_xlim(-0.6, 0.6)
        ax.set_ylim(0.6, -0.6)

    # Profiles: Scherzer and either side of it, with the envelopes.
    ax = axes[1, 0]
    scherzer = damped.defocus
    for df in (scherzer - 30, scherzer, scherzer + 30):
        damped.defocus = df
        k, line = profile(damped, damped.ctf())
        ax.plot(k, line, label=f'{df:.1f} nm')
    damped.defocus = scherzer
    ax.axhline(0, color='gray', linewidth=0.5)
    ax.set_xlim(0, k_max)
    ax.set_xlabel('spatial frequency (1/Å)')
    ax.set_ylabel('CTF')
    ax.set_title('Profiles, with envelopes')
    ax.legend(fontsize=8)

    # A corrected lens: Cs small and negative, and the Scherzer-like overfocus that balances it,
    # sqrt(1.5 |Cs| wavelength).
    corrected = Probe(kv=200, cs=-0.013, defocus=7.0, **ENVELOPES, **MAP)
    ax = axes[1, 1]
    for name, probe in (('Uncorrected, Scherzer', damped), ('Corrected', corrected)):
        k, line = profile(probe, probe.ctf())
        ax.plot(k, line, label=name)
    ax.axhline(0, color='gray', linewidth=0.5)
    ax.set_xlim(0, 2 * k_max)
    ax.set_xlabel('spatial frequency (1/Å)')
    ax.set_title('Uncorrected and corrected')
    ax.legend(fontsize=8)

    fig.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()
