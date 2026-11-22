# This file is part of pyEMAPS.
# Copyright (C) 2021-2026 EMLab Solutions, Inc.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Additional permission under GPLv3 Section 7:
# See license-exception.txt for the exception permitting
# combination with the separately licensed backend, emaps.

'''
What the image readers share: the single-dataset readers (MRC, Merlin, image files, NumPy)
have one image dataset per file, read pattern by pattern; all readers describe what kind of
image a dataset is, and the files with several (DigitalMicrograph, EMD) choose one the same way.
:py:func:`~pyemaps.expimage.read_image` uses them.
'''
import numpy as np

# The kinds of image, in the order the default choice prefers them: pyEMAPS indexes diffraction
# patterns, so they come first; an image whose kind the file doesn't tell (no calibration)
# may be one.
DIFFRACTION, UNKNOWN, REAL_SPACE, SPECTRUM_MAP = 'diffraction', 'unknown', 'real-space', 'spectrum map'
KINDS = (DIFFRACTION, UNKNOWN, REAL_SPACE, SPECTRUM_MAP)

_LENGTHS = {'m', 'mm', 'um', 'nm', 'pm', 'a', 'ang', 'angstrom', 'angstroms'}
_ANGLES = {'rad', 'mrad', 'urad', 'deg', 'degree', 'degrees', '°'}


def unit_kind(units):
    '''
    The kind of image a pattern axis in *units* belongs to: ``'diffraction'`` for reciprocal
    lengths (``1/nm``, ``nm^-1``, ``1/m`` …) and scattering angles (``mrad`` …),
    ``'real-space'`` for lengths (``m``, ``nm``, ``Å`` …), ``'unknown'`` for anything else,
    including no units.
    '''
    if not isinstance(units, str):
        return UNKNOWN
    u = units.strip().lower().replace('µ', 'u').replace('μ', 'u').replace('å', 'a').replace(' ', '')
    if not u:
        return UNKNOWN
    if u.startswith('1/') or u.endswith('^-1') or u.endswith('-1') or u in _ANGLES:
        return DIFFRACTION
    if u in _LENGTHS:
        return REAL_SPACE
    return UNKNOWN


def calibration_kind(axes):
    '''The kind of image with pattern *axes* (rows, columns), when both axes' units agree.'''
    kinds = {unit_kind(a.get('units')) for a in axes or []}
    return kinds.pop() if len(kinds) == 1 else UNKNOWN


class Dataset:
    '''
    One image dataset: its patterns' layout, calibration and metadata. The formats these
    readers handle don't say reliably whether an image is a diffraction pattern, so its kind is
    ``'unknown'``.
    '''

    def __init__(self, name, nav_shape, pattern_shape, dtype, axes, metadata, read):
        self.name = name
        self.nav_shape = tuple(nav_shape)
        self.pattern_shape = tuple(pattern_shape)
        self.dtype = np.dtype(dtype)
        self.axes = axes
        self.metadata = metadata
        self._read = read
        self.kind = UNKNOWN

    @property
    def npatterns(self):
        return int(np.prod(self.nav_shape)) if self.nav_shape else 1

    def read(self, indices):
        '''Patterns *indices* (in scan order, ascending), as ``(n, rows, columns)``.'''
        return self._read(list(indices))

    def describe(self):
        scan = ' x '.join(str(n) for n in self.nav_shape) or 'one'
        return (f'{self.name}: {scan} pattern(s) of {self.pattern_shape[0]} x '
                f'{self.pattern_shape[1]} {self.dtype}')


class SingleDatasetFile:
    '''A file with one dataset. Subclasses set ``path``, ``datasets`` and ``close``.'''

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        f = getattr(self, '_f', None)
        if f is not None:
            f.close()

    def choose(self, dataset=None):
        if dataset is not None:
            raise ValueError(f'dataset is for files with several images; {self.path} has one')
        return self.datasets[0]


def default_dataset(datasets):
    '''
    The dataset to read from a file with several when none is named: diffraction patterns
    first, then images of unknown kind, then real-space images, then maps computed from a
    spectrum image (each dataset's ``kind``); within a kind, the one with the most patterns,
    the first of them on a tie. Single images that are all zero are passed over while another
    dataset is left. Only single images are checked for zeros, so choosing never reads a whole
    scan.
    '''
    rank = {k: i for i, k in enumerate(KINDS)}
    order = sorted(range(len(datasets)),
                   key=lambda i: (rank.get(getattr(datasets[i], 'kind', UNKNOWN), 1),
                                  -datasets[i].npatterns, i))
    for i in order:
        d = datasets[i]
        if d.npatterns == 1 and not np.any(d.read([0])):
            continue
        return d
    return datasets[order[0]]


def runs(idx):
    '''Consecutive runs in ascending indices *idx*, as (position in idx, first index, count).'''
    out, k = [], 0
    while k < len(idx):
        j = k
        while j + 1 < len(idx) and idx[j + 1] == idx[j] + 1:
            j += 1
        out.append((k, idx[k], j - k + 1))
        k = j + 1
    return out


def plain_axes():
    return [{'name': 'rows', 'scale': 1.0, 'offset': 0.0, 'units': ''},
            {'name': 'columns', 'scale': 1.0, 'offset': 0.0, 'units': ''}]
