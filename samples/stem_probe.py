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

"""The STEM probe of a corrected and an uncorrected lens, and its size.

This sample uses pyEMAPS' Probe class to compute the probe's intensity in the sample plane, and
the diameters that hold 50% and 80% of it, for:

1. an uncorrected 200 kV lens, Cs 1.2 mm, at its Scherzer defocus and aperture;
2. a corrected 200 kV lens with a 25 mrad aperture, with the Cs and defocus that balance its
   C5 (Haider et al.): the probe is close to the diffraction limit of the aperture;
3. the same corrected lens with the residual aberrations a corrector measured on a real
   microscope.

It shows the probes and their profiles through the center, and the 50% diameter of the
uncorrected probe over a range of defocus.

Run it with:

    python stem_probe.py
"""
import matplotlib.pyplot as plt
import numpy as np

from pyemaps import Probe

# Residual aberrations, (amplitude, angle in degrees): a1, a2, b2 in nm; a3, a4, b4, d4, s3 in
# um; a5 in mm.
CORRECTOR = {'a1': (1.349, 146.2), 'a2': (58.94, -131.9), 'b2': (22.89, 141.4),
             'a3': (0.3054, -7.5), 's3': (0.1977, -161.2), 'a4': (35.96, 68.9),
             'd4': (20.8, -47.0), 'b4': (8.769, 2.8), 'a5': (0.7825, -114.8)}

# A 25.6 A map of 512 x 512 pixels: 0.05 A pixels. The diameter counts whole pixels, so the
# pixels must be much smaller than the probe.
MAP = {'size': 25.6, 'sampling': 512}


def probes():
    """The three lenses."""
    uncorrected = Probe(kv=200, cs=1.2, **MAP)
    uncorrected.scherzer()
    corrected = Probe(kv=200, aperture=25, c5=3.829, **MAP)
    corrected.haider(optimum_aperture=False)      # Cs and defocus for C5, at 25 mrad
    residual = Probe(kv=200, aperture=25, c5=3.829, aberrations=CORRECTOR, **MAP)
    residual.haider(optimum_aperture=False)
    return {'Uncorrected (Scherzer)': uncorrected, 'Corrected (Haider)': corrected,
            'Corrected, measured residuals': residual}


def main():
    lenses = probes()
    fig = plt.figure(figsize=(15, 9))
    grid = fig.add_gridspec(2, 6)
    top = [fig.add_subplot(grid[0, 2 * k:2 * k + 2]) for k in range(3)]
    profiles, series = fig.add_subplot(grid[1, 0:3]), fig.add_subplot(grid[1, 3:6])
    for k, (name, probe) in enumerate(lenses.items()):
        intensity = probe.probe()
        d50, d80 = probe.diameter(50, intensity), probe.diameter(80, intensity)
        print(f'{name}: 50% within {d50:.3f} A, 80% within {d80:.3f} A; {probe}')

        ax = top[k]
        probe.show(intensity, 'probe', ax=ax, title=f'{name}\n50%: {d50:.2f} A, 80%: {d80:.2f} A')
        ax.set_xlim(-4, 4)
        ax.set_ylim(4, -4)

        # the profile through the center, along the rows
        n = probe.sampling
        x = (np.arange(n) - n // 2) * probe.size / n
        profiles.plot(x, intensity[n // 2] / intensity.max(), label=name)
    profiles.set_xlim(-4, 4)
    profiles.set_xlabel('Å')
    profiles.set_title('Profiles through the center (normalized)')
    profiles.legend(fontsize=8)

    # The uncorrected probe's size over a range of defocus: smallest near Scherzer.
    uncorrected = lenses['Uncorrected (Scherzer)']
    scherzer = uncorrected.defocus
    defocus = np.linspace(scherzer - 40, scherzer + 40, 17)
    sizes = []
    for df in defocus:
        uncorrected.defocus = df
        sizes.append(uncorrected.diameter(50))
    uncorrected.defocus = scherzer
    series.plot(defocus, sizes, 'o-')
    series.axvline(scherzer, color='gray', linestyle=':', label='Scherzer defocus')
    series.set_xlabel('defocus (nm)')
    series.set_ylabel('50% diameter (Å)')
    series.set_title('Uncorrected probe size over defocus')
    series.legend(fontsize=8)

    fig.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()
