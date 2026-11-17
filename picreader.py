# This file is part of pyEMAPS.
# Copyright (C) 2021-2026 EMLab Solutions, Inc.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Additional permission under GPLv3 Section 7:
# See license-exception.txt for the exception permitting
# combination with the separately licensed backend, emaps.

'''
Readers for common picture files (PNG, BMP, JPEG), through Pillow, which matplotlib installs,
and for NumPy arrays saved with ``numpy.save`` (``.npy``).

Pictures: 8 and 16-bit grayscale, 32-bit integer and float images are read as they are. RGB
pictures whose three channels are equal, as grayscale exports often are, are read as grayscale;
colour pictures, palette pictures with colours and black-and-white pictures are refused. JPEG
is lossy: fine for a quick look, not for measurements.

NumPy arrays: a 2-D array is one pattern; a 3-D array a series of patterns; a 4-D array a scan,
(scan rows, scan columns, rows, columns).

:py:func:`~pyemaps.expimage.read_image` uses this module; most code should call that instead.
'''
import os

import numpy as np

from .readerbase import Dataset, SingleDatasetFile, plain_axes

SIGNATURES = ((b'\x89PNG\r\n\x1a\n', 'PNG'), (b'BM', 'BMP'), (b'\xff\xd8\xff', 'JPEG'))


class PictureError(ValueError):
    '''A picture or NumPy file this reader can't read, with the reason.'''


def picture_kind(path):
    ''''PNG', 'BMP' or 'JPEG' from the file's first bytes, or None.'''
    try:
        with open(os.fspath(path), 'rb') as f:
            head = f.read(8)
    except OSError:
        return None
    for sig, kind in SIGNATURES:
        if head.startswith(sig):
            return kind
    return None


def is_npy(path):
    try:
        with open(os.fspath(path), 'rb') as f:
            return f.read(6) == b'\x93NUMPY'
    except OSError:
        return False


class PictureFile(SingleDatasetFile):
    '''A PNG, BMP or JPEG picture, read with Pillow.'''

    def __init__(self, path):
        self.path = os.fspath(path)
        try:
            from PIL import Image
        except ImportError as e:                     # matplotlib installs Pillow
            raise ImportError('Reading PNG, BMP and JPEG files needs Pillow: pip install pillow') from e
        try:
            with Image.open(self.path) as im:
                kind, mode, info = im.format, im.mode, dict(im.info)
                frames = getattr(im, 'n_frames', 1)
                data = _pixels(im, self.path)
        except PictureError:
            raise
        except Exception as e:
            raise PictureError(f'{self.path} can\'t be read as a picture: {e}') from None
        if frames > 1:
            raise PictureError(f'{self.path} is an animated picture with {frames} frames; save '
                               'a stack as a multi-page TIFF instead')
        meta = {'format': kind, 'mode': mode, 'lossy': kind == 'JPEG',
                'info': {k: v for k, v in info.items() if isinstance(v, (str, int, float, tuple))}}
        rows, cols = data.shape
        self.datasets = [Dataset(os.path.basename(self.path), (), (rows, cols), data.dtype,
                                 plain_axes(), meta, lambda idx: data[np.newaxis][idx])]


def _pixels(im, path):
    mode = im.mode
    if mode == '1':
        raise PictureError(f'{path} is a black-and-white (1-bit) picture, not diffraction data')
    if mode in ('L', 'I;16', 'I;16B', 'I;16L', 'I', 'F'):
        return np.array(im)
    if mode == 'LA':
        return np.array(im)[..., 0]
    if mode == 'P':
        rgb = np.array(im.convert('RGB'))
        return _gray(rgb, path, 'palette')
    if mode in ('RGB', 'RGBA', 'RGBX'):
        return _gray(np.array(im)[..., :3], path, 'colour')
    raise PictureError(f'{path} is a {mode} picture; diffraction patterns must be grayscale')


def _gray(rgb, path, what):
    if np.array_equal(rgb[..., 0], rgb[..., 1]) and np.array_equal(rgb[..., 0], rgb[..., 2]):
        return rgb[..., 0].copy()
    raise PictureError(f'{path} is a {what} picture with different red, green and blue values; '
                       'diffraction patterns must be grayscale')


class NpyFile(SingleDatasetFile):
    '''A NumPy array file (.npy): 2-D, 3-D (a series) or 4-D (a scan).'''

    def __init__(self, path):
        self.path = os.fspath(path)
        try:
            arr = np.load(self.path, mmap_mode='r', allow_pickle=False)
        except ValueError as e:
            raise PictureError(f'{self.path} can\'t be read as a NumPy array: {e}') from None
        if arr.dtype.kind not in 'uif' or arr.dtype.names is not None:
            raise PictureError(f'{self.path} holds {arr.dtype} values, not a numeric image')
        if not 2 <= arr.ndim <= 4:
            raise PictureError(f'{self.path} holds a {arr.ndim}-D array; pyEMAPS reads 2-D '
                               'patterns, 3-D series and 4-D scans')
        rows, cols = arr.shape[-2:]
        nav = tuple(int(n) for n in arr.shape[:-2])
        flat = arr.reshape((-1, rows, cols))

        def read(idx):
            return np.array(flat[idx])            # a copy, so the memory-mapped file is released

        self._arr = arr
        self.datasets = [Dataset(os.path.basename(self.path), nav, (rows, cols),
                                 arr.dtype.newbyteorder('='), plain_axes(),
                                 {'format': 'NumPy'}, read)]

    def close(self):
        mm = getattr(self._arr, '_mmap', None)
        self._arr = None
        if mm is not None:
            try:
                mm.close()
            except (BufferError, ValueError):
                pass
