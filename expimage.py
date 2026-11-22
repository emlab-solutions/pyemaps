# This file is part of pyEMAPS.
# Copyright (C) 2021-2026 EMLab Solutions, Inc.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Additional permission under GPLv3 Section 7:
# See license-exception.txt for the exception permitting
# combination with the separately licensed backend, emaps.

'''
Read experimental diffraction patterns from image files.

:py:func:`read_image` reads:

- TIFF files (``.tif``, ``.tiff``): single images and multi-page stacks such as 4D-STEM scans;
- Gatan DigitalMicrograph files (``.dm3``, ``.dm4``): single images, stacks and 4D-STEM
  datacubes, with their calibration and the microscope settings DigitalMicrograph recorded;
- MRC files (``.mrc``, ``.mrcs``, ``.st``): images and stacks, such as 3D electron diffraction
  tilt series;
- Quantum Detectors Merlin files (``.mib``): 4D-STEM frames from Medipix3 detectors;
- PNG, BMP and JPEG pictures (8 or 16-bit grayscale), and NumPy arrays (``.npy``);
- EMD files (``.emd``): Thermo Fisher Velox images and image series, with the microscope
  settings Velox records, and Berkeley EMD files, including py4DSTEM's 4D-STEM datacubes,
  with their calibration. EMD files need the h5py package: ``pip install "pyemaps[emd]"``;
- pyEMAPS' own small-header files (``.im3``, ``.img``).

It returns the patterns as numpy arrays, with the scan shape. :py:func:`image_datasets` lists
the images in a file without reading them, with the kind of each: diffraction patterns, which
pyEMAPS indexes, real-space images such as STEM images, or maps computed from a spectrum image.
pyEMAPS reads all of these itself, except EMD, with no other package. Reading files needs no license; analysing
them with the 4D-STEM features does (see
:py:meth:`StackImage.from_file <pyemaps.stackimg.StackImage.from_file>`).

TIFF files can be 8 to 64-bit integers or 16 to 64-bit floats, uncompressed or compressed with
LZW, Deflate (zip) or PackBits, including BigTIFF and ImageJ stacks. Large stacks read fastest
uncompressed or with Deflate; LZW is decoded in Python, at a few MB per second.
'''
import os

import numpy as np

from . import dmreader, emdreader, mibreader, mrcreader, picreader, tiffreader
from .readerbase import UNKNOWN

# pyEMAPS small-header files: an 8-byte header of four little-endian shorts (width, height,
# number of patterns, data type), then the patterns, row by row. Data types above 10 are
# stacks; for single images the third short isn't used.
SH_TYPES = {1: np.int16, 2: np.float32, 4: np.float64}
SH_STACK = 10

READERS = (('TIFF', ['tif', 'tiff']), ('DM', ['dm3', 'dm4']), ('EMD', ['emd']),
           ('MRC', ['mrc', 'mrcs', 'st']), ('MIB', ['mib']), ('PICTURE', ['png', 'bmp', 'jpg', 'jpeg']),
           ('NPY', ['npy']), ('pyEMAPS', ['im3', 'img']))
OPENERS = {'DM': dmreader.DMFile, 'EMD': emdreader.EmdFile, 'MRC': mrcreader.MRCFile,
           'MIB': mibreader.MIBFile, 'PICTURE': picreader.PictureFile, 'NPY': picreader.NpyFile}


class ExperimentalImage:
    '''
    Experimental diffraction patterns read from a file by :py:func:`read_image`: one pattern,
    or a stack of them, one per scan position.
    '''
    def __init__(self, data, scan_shape, reader, axes, metadata, source, kind=UNKNOWN):
        self._data = data
        self._scan_shape = tuple(scan_shape)
        self._reader = reader
        self._axes = axes
        self._metadata = metadata
        self._source = source
        self._kind = kind

    @property
    def kind(self):
        '''
        What the file says these images are: ``'diffraction'`` for diffraction patterns, which
        the 4D-STEM features index (calibrated in reciprocal lengths or angles, such as 1/nm or
        mrad); ``'real-space'`` for images of the sample, such as STEM images (calibrated in
        lengths, such as nm); ``'spectrum map'`` for a map Velox computed from a spectrum image,
        such as an elemental map; ``'unknown'`` when the file doesn't tell, as for TIFF, MRC,
        Merlin, picture, NumPy and pyEMAPS files, and for DigitalMicrograph and EMD images
        without a calibration.
        '''
        return self._kind

    @property
    def data(self):
        '''
        The patterns, as a numpy array of shape ``(patterns, rows, columns)``, in scan order:
        along a scan row first. 16-bit integer data, and integer data that fits in 16 bits,
        is ``int16``; everything else is ``float32``.
        '''
        return self._data

    @property
    def scan_shape(self):
        '''
        The scan shape: ``()`` for a single pattern, ``(n,)`` for a series, ``(rows, columns)``
        for a 2-D scan.
        '''
        return self._scan_shape

    @property
    def npatterns(self):
        '''The number of patterns.'''
        return int(self._data.shape[0])

    @property
    def pattern_shape(self):
        '''The size of each pattern, ``(rows, columns)``, in pixels.'''
        return tuple(int(n) for n in self._data.shape[1:])

    @property
    def reader(self):
        '''
        The reader that read the file: ``TIFF``, ``DM``, ``EMD``, ``MRC``, ``MIB``,
        ``PICTURE``, ``NPY`` or ``pyEMAPS``.
        '''
        return self._reader

    @property
    def axes(self):
        '''
        The pattern axes, rows then columns: dictionaries with the ``name``, ``size``,
        ``scale`` (per pixel, after binning), ``offset`` and ``units``. DigitalMicrograph and
        EMD files record the calibration, and MRC files a pixel size in Å; for the other
        formats, the scale is the binning and the units are empty.
        '''
        return self._axes

    @property
    def metadata(self):
        '''
        The file's descriptive metadata. For TIFF files: the first image's descriptive tags
        by name (``ImageDescription``, ``Software``, ``DateTime`` …), the ``compression``,
        and ``imagej`` or ``shaped`` with the settings ImageJ or tifffile recorded. For Velox
        files: ``high_voltage_kV``, ``camera_length_m``, ``detector`` and ``instrument``,
        the ``title`` Velox shows the image under, ``spectrum_map`` (``'EELS'`` or ``'EDS'``
        for an elemental map computed from a spectrum image, else None), and the full metadata
        of the first frame under ``velox``. For Berkeley EMD files:
        the ``format``, the ``dataset`` and its ``attributes``, and the ``scan_axes``. For
        DigitalMicrograph files: ``high_voltage_kV`` and ``camera_length_mm`` when recorded,
        ``scan_axes``, the image's ``name``, and its tags under ``tags``. For MRC files: the
        ``mode``, ``labels`` and extended header type. For Merlin files: the ``pixel_type``,
        ``exposure_s``, the first frame's ``header`` fields, and the settings of the ``.hdr``
        file next to it under ``hdr``. For pictures: the ``format``, ``mode`` and whether it
        is ``lossy`` (JPEG).
        '''
        return self._metadata

    @property
    def source(self):
        '''The path of the file.'''
        return self._source

    def __repr__(self):
        kind = f', {self._kind}' if self._kind != UNKNOWN else ''
        return (f'ExperimentalImage({os.path.basename(self._source)!r}: {self.npatterns} '
                f'pattern(s) of {self.pattern_shape[0]} x {self.pattern_shape[1]}, '
                f'scan {self._scan_shape}, {self._data.dtype}, read by {self._reader}{kind})')


def image_readers():
    '''
    The readers :py:func:`read_image` uses, with their file extensions.

    :return: ``(name, extensions)`` pairs.
    :rtype: list of tuple
    '''
    return [(name, list(exts)) for name, exts in READERS]


def read_image(path, reader=None, binning=1, scan_roi=None, scan_shape=None, dataset=None):
    '''
    Read experimental diffraction patterns from a file.

    :param path: the file. TIFF, DigitalMicrograph and EMD (HDF5) files are recognised by their
        content, whatever their extension; ``.im3`` and ``.img`` files by their header.
    :type path: str or os.PathLike
    :param reader: the reader to use whatever the file's extension, such as ``'TIFF'`` or
        ``'MRC'``. See :py:func:`image_readers`.
    :type reader: str, optional
    :param binning: average square blocks of *binning* x *binning* pixels into one. Pixels left
        over at the right and bottom edges are dropped. The camera constant and pattern center
        you give :py:meth:`~pyemaps.stackimg.StackImage.indexImage` must be scaled by
        ``1 / binning`` too.
    :type binning: int, optional
    :param scan_roi: the part of the scan to read: ``(row, column, rows, columns)`` for a 2-D
        scan, ``(first, count)`` for a series of patterns, counting from 0. Only those patterns
        are read from a TIFF file.
    :type scan_roi: tuple of int, optional
    :param scan_shape: the scan shape, ``(rows, columns)``, for a stack whose file doesn't
        record it, such as an ImageJ stack or a Merlin file. The patterns must fill it exactly. By default, the
        shape the file recorded, or else a series of patterns.
    :type scan_shape: tuple of int, optional
    :param dataset: for a DigitalMicrograph or EMD file with several images, the one to read:
        its number, counting from 0, its name in the file, or for a Velox file the title Velox
        shows it under, such as ``'DF-S'``. By default, diffraction patterns before images of
        unknown kind, real-space images and Velox's elemental maps (see
        :py:attr:`ExperimentalImage.kind`), and among those the one with the most patterns,
        such as the 4D-STEM scan rather than an overview image, passing over single images that
        are all zero unless nothing else is left. :py:func:`image_datasets` lists a file's
        images; so does the error for a dataset the file doesn't have.
    :type dataset: int or str, optional
    :return: the patterns.
    :rtype: ExperimentalImage
    :raise FileNotFoundError: if the file doesn't exist.
    :raise ImportError: for an EMD file, if h5py isn't installed. The message says how to
        install it.
    :raise ValueError: if the file isn't one these readers read, holds no grayscale image
        (an RGB image, for example), uses a compression they can't decode, or an option is
        invalid. The message says which.
    '''
    path = os.fspath(path)
    if not os.path.isfile(path):
        raise FileNotFoundError(f'Image file not found: {path}')
    if not isinstance(binning, (int, np.integer)) or isinstance(binning, bool) or binning < 1:
        raise ValueError(f'binning must be a positive integer, not {binning!r}')

    name = _choose_reader(path, reader)
    if dataset is not None and name not in ('EMD', 'DM'):
        raise ValueError(f'dataset is for files with several images, such as DigitalMicrograph '
                         f'and EMD files; {path} is read by the {name} reader')
    calibration = None
    kind = UNKNOWN
    if name == 'TIFF':
        with tiffreader.TiffFile(path) as tif:
            nav = _scan_shape(scan_shape, tif.npages, tif.scan_shape, path)
            pages, nav = _roi_pages(nav, scan_roi)
            stack = tif.read(pages)
            metadata = tif.metadata
    elif name in OPENERS:
        with OPENERS[name](path) as f:
            ds = f.choose(dataset)
            nav = _scan_shape(scan_shape, ds.npatterns, ds.nav_shape, path)
            pages, nav = _roi_pages(nav, scan_roi)
            stack = ds.read(pages)
            metadata, calibration, kind = ds.metadata, ds.axes, ds.kind
    else:
        data = _read_small_header(path)
        stack = data.reshape(-1, *data.shape[-2:])
        nav = _scan_shape(scan_shape, stack.shape[0], data.shape[:-2], path)
        pages, nav = _roi_pages(nav, scan_roi)
        stack = np.array(stack[pages])         # a copy, so the memory-mapped file is released
        del data
        metadata = {}

    stack = _convert(stack)
    rows, cols = (int(n) for n in stack.shape[1:])
    if binning > 1:
        rows, cols = rows // binning, cols // binning
        if rows < 1 or cols < 1:
            raise ValueError(f'binning={binning} is larger than the patterns')
        stack = stack[:, :rows * binning, :cols * binning].reshape(
            -1, rows, binning, cols, binning).mean(axis=(2, 4), dtype=np.float64).astype(np.float32)

    axes = []
    for k, (axis, size) in enumerate((('rows', rows), ('columns', cols))):
        c = calibration[k] if calibration else {}
        axes.append({'name': c.get('name', axis), 'size': size,
                     'scale': float(c.get('scale', 1.0)) * binning,
                     'offset': float(c.get('offset', 0.0)), 'units': c.get('units', '')})
    return ExperimentalImage(np.ascontiguousarray(stack), nav, name, axes, metadata, path, kind)


def image_datasets(path, reader=None):
    '''
    The images in a file, without reading their pixels: to see whether it holds diffraction
    patterns, and which image :py:func:`read_image` reads by default.

    :param path: the file, in any format :py:func:`read_image` reads.
    :type path: str or os.PathLike
    :param reader: the reader to use whatever the file's extension; see :py:func:`image_readers`.
    :type reader: str, optional
    :return: one dictionary per image, in the file's order: its ``dataset`` number (for
        :py:func:`read_image`'s *dataset*), ``name``, ``title`` (the title Velox shows it
        under, else None), ``kind`` (see :py:attr:`ExperimentalImage.kind`), ``scan_shape``
        as the file records it, ``npatterns``, ``pattern_shape``, ``dtype``, and ``default``,
        True for the image :py:func:`read_image` reads when no *dataset* is given.
    :rtype: list of dict
    :raise FileNotFoundError: if the file doesn't exist.
    :raise ImportError: for an EMD file, if h5py isn't installed.
    :raise ValueError: if the file isn't one these readers read.

    For a DigitalMicrograph or EMD file with several images, telling the default reads the
    single images that are candidates for it, to pass over those that are all zero.
    '''
    path = os.fspath(path)
    if not os.path.isfile(path):
        raise FileNotFoundError(f'Image file not found: {path}')
    name = _choose_reader(path, reader)
    out = []
    if name == 'TIFF':
        with tiffreader.TiffFile(path) as tif:
            out.append(_describe(0, os.path.basename(path), None, UNKNOWN, tif.scan_shape,
                                 tif.npages, tif.shape, tif.dtype, True))
    elif name in OPENERS:
        with OPENERS[name](path) as f:
            chosen = f.choose(None)
            for k, d in enumerate(f.datasets):
                out.append(_describe(k, d.name, getattr(d, 'title', None),
                                     getattr(d, 'kind', UNKNOWN), d.nav_shape, d.npatterns,
                                     d.pattern_shape, d.dtype, d is chosen))
    else:
        data = _read_small_header(path)
        n = data.shape[0] if data.ndim == 3 else 1
        out.append(_describe(0, os.path.basename(path), None, UNKNOWN,
                             (n,) if data.ndim == 3 else (), n, data.shape[-2:], data.dtype, True))
        del data
    return out


def _describe(k, name, title, kind, scan_shape, npatterns, pattern_shape, dtype, default):
    return {'dataset': k, 'name': name, 'title': title, 'kind': kind,
            'scan_shape': tuple(int(n) for n in scan_shape), 'npatterns': int(npatterns),
            'pattern_shape': tuple(int(n) for n in pattern_shape), 'dtype': str(np.dtype(dtype)),
            'default': bool(default)}


def write_im3(path, data):
    '''
    Write patterns to a pyEMAPS small-header file (``.im3``), which the 4D-STEM features read.

    :param path: the file to write.
    :type path: str or os.PathLike
    :param data: one pattern ``(rows, columns)`` or a stack ``(patterns, rows, columns)``. 16-bit
        integers are written as such; everything else as 32-bit floats.
    :type data: numpy.ndarray
    '''
    a = np.asarray(data)
    if a.ndim == 2:
        a = a[np.newaxis]
    if a.ndim != 3 or a.shape[0] < 1:
        raise ValueError(f'expected one pattern or a stack of them, not an array of shape {a.shape}')
    n, rows, cols = a.shape
    if max(n, rows, cols) > 32767:
        raise ValueError(f'too large for a small-header file: {a.shape}')
    base = 1 if a.dtype == np.int16 else 2
    out = a if base == 1 else a.astype(np.float32)
    code = base + SH_STACK if n > 1 else base
    with open(os.fspath(path), 'wb') as f:
        f.write(np.array([cols, rows, n, code], dtype='<i2').tobytes())
        f.write(np.ascontiguousarray(out, dtype=out.dtype.newbyteorder('<')).tobytes())


# ------------------------------------------------------------------ helpers

def _choose_reader(path, reader):
    if reader is not None:
        for name, _ in READERS:
            if str(reader).lower() == name.lower():
                return name
        raise ValueError(f'Unknown reader {reader!r}; the readers are '
                         + ', '.join(n for n, _ in READERS))
    if tiffreader.is_tiff(path):
        return 'TIFF'
    if dmreader.is_dm(path):
        return 'DM'
    if mibreader.is_mib(path):
        return 'MIB'
    if emdreader.is_hdf5(path):
        return 'EMD'
    if picreader.picture_kind(path):
        return 'PICTURE'
    if picreader.is_npy(path):
        return 'NPY'
    ext = os.path.splitext(path)[1][1:].lower()
    if mrcreader.is_mrc(path) or (ext in ('mrc', 'mrcs', 'st') and
                                  mrcreader._byte_order(_head(path, 1024)) is not None):
        return 'MRC'
    if ext in ('dm3', 'dm4'):
        raise ValueError(f'{path} is not a DigitalMicrograph file: it doesn\'t start with a DM3 or '
                         'DM4 header (DM5 files, which are HDF5, aren\'t supported yet)')
    if ext == 'emd':
        raise ValueError(f'{path} is not an EMD file: it doesn\'t start with an HDF5 header')
    if ext in ('tif', 'tiff'):
        raise ValueError(f'{path} is not a TIFF file: it doesn\'t start with a TIFF header')
    if _sh_layout(path) is not None:
        return 'pyEMAPS'
    if ext in ('im3', 'img'):
        raise ValueError(f'{path} is not a pyEMAPS small-header file: its header and size '
                         'don\'t match')
    raise ValueError(f'Can\'t read {path}: pyEMAPS reads TIFF, DigitalMicrograph (.dm3, .dm4), '
                     'EMD, MRC, Merlin (.mib), PNG, BMP, JPEG and NumPy (.npy) files, and its own '
                     'small-header files (.im3, .img)')


def _head(path, n):
    try:
        with open(path, 'rb') as f:
            head = f.read(n)
    except OSError:
        return b''
    return head if len(head) == n else b'\0' * n


def _sh_layout(path):
    '''(width, height, count, dtype) from a small-header file's header, or None.'''
    size = os.path.getsize(path)
    if size < 8:
        return None
    w, h, n, t = (int(v) for v in np.fromfile(path, dtype='<i2', count=4))
    stack = t > SH_STACK
    dtype = SH_TYPES.get(t - SH_STACK if stack else t)
    if dtype is None or w < 1 or h < 1 or (stack and n < 1):
        return None
    n = n if stack else 1
    if size != 8 + w * h * n * np.dtype(dtype).itemsize:
        return None
    return w, h, n, dtype


def _read_small_header(path):
    layout = _sh_layout(path)
    if layout is None:
        raise ValueError(f'{path} is not a pyEMAPS small-header file: its header and size '
                         'don\'t match')
    w, h, n, dtype = layout
    data = np.memmap(path, dtype=np.dtype(dtype).newbyteorder('<'), mode='r', offset=8,
                     shape=(n, h, w))
    return data if n > 1 else data[0]


def _scan_shape(given, n, recorded, path):
    '''The scan shape: *given* if set (it must hold exactly *n* patterns), else *recorded*.'''
    if given is None:
        return tuple(recorded)
    shape = tuple(given)
    if not shape or len(shape) > 2 or not all(
            isinstance(v, (int, np.integer)) and not isinstance(v, bool) and v > 0 for v in shape):
        raise ValueError(f'scan_shape must be (rows, columns) or (count,), not {given!r}')
    if int(np.prod(shape)) != n:
        raise ValueError(f'scan_shape {shape} needs {int(np.prod(shape))} patterns, but {path} '
                         f'has {n}')
    return tuple(int(v) for v in shape)


def _roi_pages(nav, roi):
    '''The pattern numbers in the scan region, and its shape.'''
    n = int(np.prod(nav)) if nav else 1
    if roi is None:
        return list(range(n)), tuple(nav)
    roi = tuple(roi)
    if not all(isinstance(v, (int, np.integer)) and not isinstance(v, bool) for v in roi):
        raise ValueError(f'scan_roi must be integers, not {roi!r}')
    if len(nav) == 1 and len(roi) == 2:
        first, count = roi
        if first < 0 or count < 1 or first + count > nav[0]:
            raise ValueError(f'scan_roi {roi} is outside the {nav[0]} patterns')
        return list(range(first, first + count)), (count,)
    if len(nav) == 2 and len(roi) == 4:
        r0, c0, nr, nc = roi
        if r0 < 0 or c0 < 0 or nr < 1 or nc < 1 or r0 + nr > nav[0] or c0 + nc > nav[1]:
            raise ValueError(f'scan_roi {roi} is outside the {nav[0]} x {nav[1]} scan')
        return [r * nav[1] + c for r in range(r0, r0 + nr) for c in range(c0, c0 + nc)], (nr, nc)
    want = {0: 'no scan_roi: the file holds a single pattern',
            1: 'scan_roi=(first, count) for a series of patterns',
            2: 'scan_roi=(row, column, rows, columns) for a 2-D scan'}[len(nav)]
    raise ValueError(f'Invalid scan_roi {roi}; this file needs {want}')


def _convert(stack):
    '''16-bit integers where the values fit, else float32; finite values only.'''
    dtype = stack.dtype
    if np.issubdtype(dtype, np.floating):
        out = stack.astype(np.float32, copy=False)
        if not np.isfinite(out).all():
            raise ValueError('The patterns contain NaN or infinite values')
        return out
    if dtype == np.int16:
        return stack
    if stack.size and stack.min() >= -32768 and stack.max() <= 32767:
        return stack.astype(np.int16)
    return stack.astype(np.float32)
