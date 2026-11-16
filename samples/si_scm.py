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

"""Scattering matrices of a dynamic diffraction (Bloch) session for Silicon.

A Bloch session calculates the scattering matrix, its eigenvalues and the diffracted beams at
each sampling point of the incident beam. This sample starts a session and prints them at the
central sampling point and at a randomly chosen one, then the beams calculated in the session.

Run it with:

    python si_scm.py
"""
import random

from pyemaps import EMC, SIMC, BlochError, Crystal

NAME = 'Silicon'

# Microscope and simulation controls, and the diffracted beam (disk) size, for the session.
CONTROLS = EMC(cl=200, tilt=(0.0, 0.0), simc=SIMC(gmax=2.0, excitation=(1.0, 2.0)))
DISK_SIZE = 0.25


def print_scattering_matrix(crystal, point):
    """Print the scattering matrix, eigenvalues and diffracted beams at a sampling point."""
    try:
        ndim, matrix, eigenvalues, beams = crystal.getSCMatrix(ib_coords=point)
    except BlochError as e:
        print(f'Failed to get the scattering matrix at {point}: {e.message}')
        return

    print(f'\n---- Scattering matrix at sampling point {point}, size {ndim}x{ndim} ----')
    print(matrix)
    print(f'\n---- Eigenvalues at {point} ----')
    print(eigenvalues)
    print(f'\n---- Diffracted beams at {point} ----')
    print(beams)


def print_scattering_matrices():
    """Run a Bloch session and print its results at two sampling points."""
    crystal = Crystal.from_builtin(NAME)
    print(crystal)

    try:
        npoints, points = crystal.beginBloch(em_controls=CONTROLS, dbsize=DISK_SIZE)
    except Exception as e:
        print(f'Failed to start the Bloch session: {e}')
        return

    try:
        print(f'\n---- {npoints} sampling points in this session ----')
        print(points)

        print_scattering_matrix(crystal, (0, 0))

        print('\n---- More details of the scattering matrix calculation ----')
        crystal.getIBDetails()

        print_scattering_matrix(crystal, random.choice(points))

        print('\n---- Beams calculated in this session ----')
        crystal.getCalculatedBeams(bPrint=True)
    finally:
        crystal.endBloch()


def all_scattering_matrices():
    """Run a Bloch session and return its results at every sampling point.

    :return: three dictionaries:

        1. the beams calculated in the session: ``ncb``, their number, and ``cbs``, the beams.
        2. the scattering matrices: ``nscm``, the number of sampling points, and ``lscm``, a
           list with one dictionary per sampling point: ``ib``, the point; ``ndim``, the
           matrix size; ``scm``, the matrix; ``ev``, its eigenvalues; ``beams``, the
           diffracted beams.
        3. the incident beam details: ``nib``, their number, and ``libt``, the details.
    """
    crystal = Crystal.from_builtin(NAME)

    npoints, points = crystal.beginBloch(em_controls=CONTROLS, dbsize=DISK_SIZE)
    try:
        nib, ib_details = crystal.getIBDetails(bPrint=False)

        matrices = []
        for point in points:
            ndim, matrix, eigenvalues, beams = crystal.getSCMatrix(ib_coords=point)
            matrices.append(dict(ib=point, ndim=ndim, scm=matrix, ev=eigenvalues, beams=beams))

        ncb, calculated_beams = crystal.getCalculatedBeams(bPrint=False)
    finally:
        crystal.endBloch()

    return (dict(ncb=ncb, cbs=calculated_beams),
            dict(nscm=npoints, lscm=matrices),
            dict(nib=nib, libt=ib_details))


def main():
    print_scattering_matrices()


if __name__ == '__main__':
    main()
