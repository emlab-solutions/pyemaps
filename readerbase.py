# This file is part of pyEMAPS.
# Copyright (C) 2021-2026 EMLab Solutions, Inc.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Additional permission under GPLv3 Section 7:
# See license-exception.txt for the exception permitting
# combination with the separately licensed backend, emaps.

'''
What the single-dataset image readers (MRC, Merlin, image files, NumPy) share: one image
dataset per file, read pattern by pattern. :py:func:`~pyemaps.expimage.read_image` uses them.
'''
import numpy as np


class Dataset:
    '''One image dataset: its patterns' layout, calibration and metadata.'''

    def __init__(self, name, nav_shape, pattern_shape, dtype, axes, metadata, read):
        self.name = name
        self.nav_shape = tuple(nav_shape)
        self.pattern_shape = tuple(pattern_shape)
        self.dtype = np.dtype(dtype)
        self.axes = axes
        self.metadata = metadata
        self._read = read

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


def default_dataset(datasets, skip=None):
    '''
    The dataset to read from a file with several when none is named: the one with the most
    patterns, the first of them on a tie, passing over the datasets *skip* marks (a function
    of a dataset, such as Velox's elemental maps) and single images that are all zero, as long
    as another dataset is left; otherwise the first with the most patterns. Only single images
    are checked for zeros, so choosing never reads a whole scan.
    '''
    order = sorted(range(len(datasets)), key=lambda i: (-datasets[i].npatterns, i))
    for i in order:
        d = datasets[i]
        if skip is not None and skip(d):
            continue
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
