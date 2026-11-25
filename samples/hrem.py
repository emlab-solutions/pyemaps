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

"""High-resolution TEM images of a thin amorphous sample.

A thin sample changes the phase of the electron wave passing through it. The objective lens's
aberrations turn that phase into contrast, frequency by frequency, as the contrast transfer
function says. The image of an amorphous sample has the CTF's rings in its Fourier transform:
the Thon rings that microscopists use to measure defocus and astigmatism.

This sample uses pyEMAPS' Probe class, with the lens as an uncorrected 200 kV objective lens
(Cs 1.2 mm) and a 20 mrad objective aperture, on 50 A of amorphous carbon:

1. the HREM image at the Scherzer defocus and 40 nm further underfocus;
2. the Fourier transform of each, with its Thon rings;
3. the image at Scherzer with 30 nm of two-fold astigmatism, whose Thon rings become ellipses.

Run it with:

    python hrem.py
"""
import matplotlib.pyplot as plt
import numpy as np

from pyemaps import Probe


def spectrum(image):
    """The logarithm of the image's Fourier transform amplitude, zero frequency at the center."""
    return np.log1p(np.abs(np.fft.fftshift(np.fft.fft2(image - image.mean()))))


def main():
    lens = Probe(kv=200, cs=1.2, cc=1.5, energy_spread=0.7, semi_angle=0.2,
                 size=100, sampling=512)
    lens.scherzer(mode=2)
    lens.aperture = 20.0
    scherzer = lens.defocus

    # The sample: 50 A of amorphous carbon, 0.1 atoms per A^3, and its exit wave.
    carbon = lens.random_potential(density=0.1, z=6, thickness=50, seed=7)
    wave = lens.exit_wave(carbon)

    cases = [('Scherzer', scherzer, None), ('40 nm underfocus', scherzer - 40, None),
             ('Scherzer, 30 nm of a1', scherzer, (30.0, 45.0))]
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    for k, (name, df, a1) in enumerate(cases):
        lens.defocus = df
        lens.set_aberration('a1', *(a1 or (0.0, 0.0)))
        image = lens.hrem(wave)
        print(f'{name}: defocus {df:.1f} nm; image contrast (std / mean) '
              f'{image.std() / image.mean():.3f}')

        ax = axes[0, k]
        lens.show(image, 'hrem', ax=ax, title=f'{name}\ndefocus {df:.1f} nm')
        ax.set_xlim(-20, 20)
        ax.set_ylim(20, -20)

        ax = axes[1, k]
        ax.imshow(spectrum(image), cmap='gray', extent=lens.extent('ctf'))
        ax.set_xlim(-1, 1)
        ax.set_ylim(1, -1)
        ax.set_xlabel('1/Å')
        ax.set_title('Fourier transform: Thon rings')
    fig.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()
