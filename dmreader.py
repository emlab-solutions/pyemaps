# This file is part of pyEMAPS.
# Copyright (C) 2021-2026 EMLab Solutions, Inc.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Additional permission under GPLv3 Section 7:
# See license-exception.txt for the exception permitting
# combination with the separately licensed backend, emaps.

'''
A reader for Gatan DigitalMicrograph files (``.dm3``, ``.dm4``), in Python and numpy only.

Gatan doesn't publish these formats. This reader follows Chris Boothroyd's public description of
them (https://personal.ntu.edu.sg/cbb/info/dmformat/), and the layout of real files: a tree of
tag groups and tags, in big-endian byte order, whose values are in the byte order the header
gives. The images are in the ``ImageList`` group; each has ``ImageData`` with its
``Dimensions``, ``DataType``, ``Data`` and ``Calibrations``.

It reads grayscale images of 8 to 64-bit integers and 32 or 64-bit floats: single images,
stacks, and 4D-STEM datacubes. Thumbnails, colour (RGB) and complex images are skipped.

:py:func:`~pyemaps.expimage.read_image` uses this module; most code should call that instead.
'''
import os
import struct

import numpy as np


class DMError(ValueError):
    '''A file that isn't a DigitalMicrograph file this reader can read, with the reason.'''


# tag value types: struct code and size
SHORT, LONG, USHORT, ULONG, FLOAT, DOUBLE, BOOL, CHAR, OCTET, LONGLONG, ULONGLONG = \
    2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
STRUCT, STRING, ARRAY = 15, 18, 20
SIMPLE = {SHORT: ('h', 2), LONG: ('i', 4), USHORT: ('H', 2), ULONG: ('I', 4),
          FLOAT: ('f', 4), DOUBLE: ('d', 8), BOOL: ('?', 1), CHAR: ('b', 1),
          OCTET: ('B', 1), LONGLONG: ('q', 8), ULONGLONG: ('Q', 8)}
NUMPY = {SHORT: 'i2', LONG: 'i4', USHORT: 'u2', ULONG: 'u4', FLOAT: 'f4', DOUBLE: 'f8',
         BOOL: 'u1', CHAR: 'i1', OCTET: 'u1', LONGLONG: 'i8', ULONGLONG: 'u8'}

# ImageData DataType: pixel type, or a reason it isn't a grayscale image
PIXEL_TYPES = {1: 'i2', 2: 'f4', 6: 'u1', 7: 'i4', 9: 'i1', 10: 'u2', 11: 'u4', 12: 'f8',
               14: 'u1'}
NOT_GRAYSCALE = {3: 'complex', 5: 'packed complex', 8: 'RGB', 13: 'complex', 23: 'RGBA'}

MAX_DEPTH = 64


def is_dm(path):
    '''Whether the file starts with a DM3 or DM4 header.'''
    try:
        with open(os.fspath(path), 'rb') as f:
            head = f.read(4)
    except OSError:
        return False
    return head in (b'\0\0\0\3', b'\0\0\0\4')


class _Array:
    '''A numeric array tag's place in the file, read only when needed.'''
    __slots__ = ('offset', 'count', 'type')

    def __init__(self, offset, count, typ):
        self.offset, self.count, self.type = offset, count, typ

    def __repr__(self):
        return f'<array of {self.count} {NUMPY.get(self.type, self.type)} at {self.offset}>'


class DMFile:
    '''
    An open DigitalMicrograph file: its tag tree, with large arrays (the image data) located
    but not read. Use it as a context manager, or call :py:meth:`close`.

    :raise DMError: if the file isn't a DM3 or DM4 file.
    '''

    def __init__(self, path):
        self.path = os.fspath(path)
        self._f = open(self.path, 'rb')
        try:
            self._size = os.fstat(self._f.fileno()).st_size
            self._parse()
            self._images()
        except DMError:
            self._f.close()
            raise
        except (struct.error, EOFError, IndexError, ValueError) as e:
            self._f.close()
            raise DMError(f'{self.path} is damaged or truncated: {e}') from None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        '''Close the file.'''
        self._f.close()

    # ------------------------------------------------------------------ tag tree

    def _read(self, n):
        b = self._f.read(n)
        if len(b) < n:
            raise EOFError('the file ends early')
        return b

    def _parse(self):
        head = self._f.read(4)
        if head not in (b'\0\0\0\3', b'\0\0\0\4'):
            raise DMError(f'{self.path} is not a DigitalMicrograph (DM3 or DM4) file')
        self.version = head[3]
        if self.version == 3:
            _rootlen, order = struct.unpack('>II', self._read(8))
            self._isz, self._ifmt = 4, '>I'
        else:
            _rootlen, order = struct.unpack('>QI', self._read(12))
            self._isz, self._ifmt = 8, '>Q'
        self._bo = '<' if order == 1 else '>'
        self.tags = self._group(0)

    def _int(self):
        return struct.unpack(self._ifmt, self._read(self._isz))[0]

    def _group(self, depth):
        if depth > MAX_DEPTH:
            raise DMError(f'{self.path}: tag groups nested too deeply')
        self._read(2)                                    # sorted, open flags
        n = self._int()
        out, unnamed = {}, []
        for _ in range(n):
            kind = self._read(1)[0]
            if kind == 0:
                break
            nlen = struct.unpack('>H', self._read(2))[0]
            name = self._read(nlen).decode('latin-1') if nlen else None
            if self.version == 4:
                self._int()                              # the entry's size in bytes
            if kind == 20:
                value = self._group(depth + 1)
            elif kind == 21:
                value = self._tag(name)
            else:
                raise DMError(f'{self.path}: unknown tag entry type {kind}')
            if name is None:
                unnamed.append(value)
            else:
                out[name] = value
        if unnamed and not out:
            return unnamed                               # a list: unnamed entries
        if unnamed:
            out['_unnamed'] = unnamed
        return out

    def _tag(self, name=None):
        if self._read(4) != b'%%%%':
            raise DMError(f'{self.path}: a tag lacks its "%%%%" marker')
        ninfo = self._int()
        info = [self._int() for _ in range(ninfo)]
        return self._value(info, pixels=(name == 'Data'))

    def _value(self, info, pixels=False):
        t = info[0]
        if t in SIMPLE:
            fmt, size = SIMPLE[t]
            return struct.unpack(self._bo + fmt, self._read(size))[0]
        if t == STRING:
            n = info[1] if len(info) > 1 else 0
            return self._read(n).decode('latin-1')
        if t == STRUCT:
            nfields = info[2]
            types = [info[4 + 2 * k] for k in range(nfields)]
            return tuple(self._simple(tt) for tt in types)
        if t == ARRAY:
            elem = info[1]
            if elem == STRUCT:
                nfields = info[3]
                types = [info[5 + 2 * k] for k in range(nfields)]
                count = info[-1]
                return [tuple(self._simple(tt) for tt in types) for _ in range(count)]
            if elem not in SIMPLE:
                raise DMError(f'{self.path}: unknown array element type {elem}')
            count = info[2]
            size = SIMPLE[elem][1]
            if elem == USHORT and count < 4096 and not pixels:   # text (UTF-16): units, names
                raw = self._read(count * size)
                return _Text(raw, self._bo)
            offset = self._f.tell()
            if offset + count * size > self._size:
                raise EOFError('an array runs past the end of the file')
            self._f.seek(count * size, 1)
            return _Array(offset, count, elem)
        raise DMError(f'{self.path}: unknown tag type {t}')

    def _simple(self, t):
        if t not in SIMPLE:
            raise DMError(f'{self.path}: unknown structure field type {t}')
        fmt, size = SIMPLE[t]
        return struct.unpack(self._bo + fmt, self._read(size))[0]

    # ------------------------------------------------------------------ images

    def choose(self, dataset=None):
        '''
        The image to read: *dataset* (its number in :py:attr:`datasets`, or its name), or by
        default the one with the most patterns, the first of them on a tie.
        '''
        if dataset is None:
            return max(self.datasets, key=lambda d: d.npatterns)
        if isinstance(dataset, (int, np.integer)) and not isinstance(dataset, bool):
            if not 0 <= dataset < len(self.datasets):
                raise DMError(f'dataset must be 0 to {len(self.datasets) - 1} for {self.path}, '
                              f'not {dataset}')
            return self.datasets[dataset]
        for d in self.datasets:
            if d.name == dataset:
                return d
        raise DMError(f'No image {dataset!r} in {self.path}; it has: '
                      + '; '.join(d.describe() for d in self.datasets))

    def _images(self):
        self.datasets, self.skipped = [], []
        images = self.tags.get('ImageList') if isinstance(self.tags, dict) else None
        if not isinstance(images, list):
            raise DMError(f'{self.path} holds no image list')
        thumbs = {t.get('ImageIndex') for t in self.tags.get('Thumbnails', [])
                  if isinstance(t, dict)}
        for i, img in enumerate(images):
            if not isinstance(img, dict):
                continue
            name = str(img.get('Name') or f'image {i}')
            d = img.get('ImageData', {})
            dtype, data = d.get('DataType'), d.get('Data')
            dims = [int(v) for v in (d.get('Dimensions') or [])]
            cal = d.get('Calibrations', {}).get('Dimension', []) if isinstance(
                d.get('Calibrations'), dict) else []
            cal = [c if isinstance(c, dict) else {} for c in cal] + [{}] * (len(dims) - len(cal))
            units = [str(c.get('Units', '')) for c in cal[:len(dims)]]
            if i in thumbs:
                self.skipped.append(f'{name}: thumbnail')
                continue
            if dtype in NOT_GRAYSCALE:
                self.skipped.append(f'{name}: {NOT_GRAYSCALE[dtype]} image')
                continue
            if dtype not in PIXEL_TYPES or not isinstance(data, _Array):
                self.skipped.append(f'{name}: data type {dtype}')
                continue
            if len(dims) < 2:
                self.skipped.append(f'{name}: a spectrum or profile of {dims} points')
                continue
            if any(u.strip().lower() in ('ev', 'kev') for u in units):
                self.skipped.append(f'{name}: a spectrum image (energy axis, {dims})')
                continue
            if len(dims) > 4:
                self.skipped.append(f'{name}: {len(dims)}-D data {dims}')
                continue
            pixel = PIXEL_TYPES[dtype]
            dt, offset, count = self.raw_view(data, pixel)
            if count < int(np.prod(dims)):
                raise DMError(f'{self.path}: {name} has {count} pixels, expected '
                              f'{int(np.prod(dims))}')
            self.datasets.append(self._dataset(name, img, dims, cal, units, dt, offset))
        if not self.datasets:
            raise DMError(f'{self.path} holds no 2-D image: '
                          + ('; '.join(self.skipped) or 'nothing'))

    def _dataset(self, name, img, dims, cal, units, dt, offset):
        '''
        The data is stored row by row, x fastest: Dimensions list x (width) first. A 3-D image
        is a stack of 2-D patterns (x, y, pattern). A 4-D image is a datacube; its pattern axes
        are the two whose units are reciprocal (1/nm …), the first two otherwise.
        '''
        tags = img.get('ImageTags', {}) if isinstance(img.get('ImageTags'), dict) else {}
        recip = [u.strip().startswith('1/') for u in units]
        transpose = len(dims) == 4 and recip[2] and recip[3] and not (recip[0] and recip[1])
        if transpose:
            pat, nav_dims = (2, 3), (0, 1)          # pattern axes stored slowest
        else:
            pat, nav_dims = (0, 1), tuple(range(2, len(dims)))
        cols, rows = dims[pat[0]], dims[pat[1]]
        nav = tuple(dims[k] for k in reversed(nav_dims))        # slowest first
        if len(nav) == 1:
            nav = _scan_from_tags(tags, nav[0]) or nav
        if nav == (1,):
            nav = ()
        axes = [_axis(cal[pat[1]], 'rows'), _axis(cal[pat[0]], 'columns')]
        scan_axes = [_axis(cal[k], f'scan {n}') for n, k in enumerate(reversed(nav_dims))]
        meta = _summary(name, tags)
        meta['scan_axes'] = scan_axes
        npat = int(np.prod(nav)) if nav else 1
        f, isz = self._f, dt.itemsize
        pattern_bytes = rows * cols * isz

        def read(idx):
            out = np.empty((len(idx), rows, cols), dtype=dt.newbyteorder('='))
            if transpose:                           # read it all, then reorder the axes
                f.seek(offset)
                full = np.frombuffer(self._read(int(np.prod(dims)) * isz), dtype=dt)
                cube = full.reshape(dims[::-1])     # (qy, qx, ry, rx)
                cube = cube.reshape(rows, cols, -1)
                for k, i in enumerate(idx):
                    out[k] = cube[:, :, i]
                return out
            k = 0
            while k < len(idx):                     # consecutive patterns in one read
                j = k
                while j + 1 < len(idx) and idx[j + 1] == idx[j] + 1:
                    j += 1
                f.seek(offset + idx[k] * pattern_bytes)
                raw = self._read((j - k + 1) * pattern_bytes)
                out[k:j + 1] = np.frombuffer(raw, dtype=dt).reshape(j - k + 1, rows, cols)
                k = j + 1
            return out

        return _Dataset(name, nav, (rows, cols), dt.newbyteorder('='), axes, meta, read, npat)

    # ------------------------------------------------------------------ arrays

    def array(self, a, start=0, count=None):
        '''The values of array tag *a* (elements *start* to *start* + *count*), native order.'''
        count = a.count - start if count is None else count
        dt = np.dtype(self._bo + NUMPY[a.type])
        self._f.seek(a.offset + start * dt.itemsize)
        raw = self._f.read(count * dt.itemsize)
        if len(raw) < count * dt.itemsize:
            raise DMError(f'{self.path} is truncated: image data is missing')
        return np.frombuffer(raw, dtype=dt).astype(dt.newbyteorder('='))

    def raw_view(self, a, pixel):
        '''Read image data *a* as pixels of type *pixel* (numpy code), native order.'''
        dt = np.dtype(self._bo + pixel)
        nbytes = a.count * np.dtype(NUMPY[a.type]).itemsize
        return dt, a.offset, nbytes // dt.itemsize


class _Text(str):
    '''A short UTF-16 array tag, read as text (units, names).'''

    def __new__(cls, raw, bo):
        try:
            s = raw.decode('utf-16-le' if bo == '<' else 'utf-16-be')
        except UnicodeDecodeError:
            s = ''
        obj = super().__new__(cls, s)
        obj.raw = raw
        return obj


class _Dataset:
    '''One image in a DigitalMicrograph file: its layout, calibration and metadata.'''

    def __init__(self, name, nav_shape, pattern_shape, dtype, axes, metadata, read, npatterns):
        self.name = name
        self.nav_shape = tuple(nav_shape)
        self.pattern_shape = tuple(pattern_shape)
        self.dtype = np.dtype(dtype)
        self.axes = axes
        self.metadata = metadata
        self._read = read
        self.npatterns = npatterns

    def read(self, indices):
        '''Patterns *indices* (in scan order, ascending), as ``(n, rows, columns)``.'''
        return self._read(list(indices))

    def describe(self):
        scan = ' x '.join(str(n) for n in self.nav_shape) or 'one'
        return (f'{self.name}: {scan} pattern(s) of {self.pattern_shape[0]} x '
                f'{self.pattern_shape[1]} {self.dtype}')


def _axis(c, default):
    '''A DM calibration (value = (pixel - Origin) * Scale) as name, scale, offset, units.'''
    scale = c.get('Scale', 1.0)
    origin = c.get('Origin', 0.0)
    try:
        scale, origin = float(scale), float(origin)
    except (TypeError, ValueError):
        scale, origin = 1.0, 0.0
    return {'name': default, 'scale': scale or 1.0, 'offset': -origin * scale,
            'units': str(c.get('Units', ''))}


def _number(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _scan_from_tags(tags, n):
    '''The 2-D scan shape (rows, columns) Gatan records for a stack of n patterns, if any.'''
    for group, kx, ky in (('4D STEM Tags', 'Scan shape X', 'Scan shape Y'),
                          ('Series', 'nimagesx', 'nimagesy')):
        g = tags.get(group)
        if isinstance(g, dict):
            x, y = _number(g.get(kx)), _number(g.get(ky))
            if x and y and int(x) * int(y) == n:
                return int(y), int(x)
    return None


def _plain(v, depth=0):
    '''Tags as plain Python values: groups as dicts, text as str, large arrays left out.'''
    if depth > 16:
        return None
    if isinstance(v, dict):
        return {k: _plain(x, depth + 1) for k, x in v.items() if not isinstance(x, _Array)}
    if isinstance(v, list):
        return [_plain(x, depth + 1) for x in v]
    if isinstance(v, _Text):
        return str(v)
    return v


def _summary(name, tags):
    info = tags.get('Microscope Info', {}) if isinstance(tags.get('Microscope Info'), dict) else {}
    kv = _number(info.get('Voltage'))
    cl = _number(info.get('STEM Camera Length'))
    if cl is None:
        cl = _number(info.get('Camera Length'))
    return {'format': 'DigitalMicrograph', 'name': name,
            'high_voltage_kV': kv / 1000 if kv else None,
            'camera_length_mm': cl,
            'microscope': str(info.get('Microscope') or info.get('Name') or '') or None,
            'tags': _plain(tags)}
