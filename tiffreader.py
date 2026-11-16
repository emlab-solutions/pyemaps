# This file is part of pyEMAPS.
# Copyright (C) 2021-2026 EMLab Solutions, Inc.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Additional permission under GPLv3 Section 7:
# See license-exception.txt for the exception permitting
# combination with the separately licensed backend, emaps.

'''
A TIFF reader for experimental diffraction patterns, in Python and numpy only.

It reads grayscale TIFF and BigTIFF files: single images and multi-page stacks, in strips or
tiles, 8 to 64-bit integers and 16 to 64-bit floats, in either byte order, uncompressed or
compressed with PackBits, LZW or Deflate, with or without a predictor. ImageJ stacks larger
than 4 GB, which ImageJ writes with a single image directory, are read too. The scan shape of
a 4D-STEM stack comes from the metadata that tifffile writes, when it's there.

Colour, palette and black-and-white images, and other compressions such as JPEG, raise
:py:class:`TiffError`, a :py:class:`ValueError`, that says what the file holds.

:py:func:`~pyemaps.expimage.read_image` uses this module; most code should call that instead.
'''
import json
import os
import struct
import zlib

import numpy as np


class TiffError(ValueError):
    '''A file that isn't a TIFF file this reader can read, with the reason.'''


# Tag numbers used here (TIFF 6.0, and the TIFF Technical Notes for SampleFormat and tiles)
NEW_SUBFILE_TYPE = 254
IMAGE_WIDTH = 256
IMAGE_LENGTH = 257
BITS_PER_SAMPLE = 258
COMPRESSION = 259
PHOTOMETRIC = 262
IMAGE_DESCRIPTION = 270
MAKE = 271
MODEL = 272
STRIP_OFFSETS = 273
SAMPLES_PER_PIXEL = 277
ROWS_PER_STRIP = 278
STRIP_BYTE_COUNTS = 279
X_RESOLUTION = 282
Y_RESOLUTION = 283
PLANAR_CONFIG = 284
RESOLUTION_UNIT = 296
SOFTWARE = 305
DATE_TIME = 306
PREDICTOR = 317
TILE_WIDTH = 322
TILE_LENGTH = 323
TILE_OFFSETS = 324
TILE_BYTE_COUNTS = 325
SAMPLE_FORMAT = 339

# Tags whose values go into the metadata, by name
METADATA_TAGS = {IMAGE_DESCRIPTION: 'ImageDescription', MAKE: 'Make', MODEL: 'Model',
                 SOFTWARE: 'Software', DATE_TIME: 'DateTime', X_RESOLUTION: 'XResolution',
                 Y_RESOLUTION: 'YResolution', RESOLUTION_UNIT: 'ResolutionUnit'}

# Field types: numpy type code and size in bytes
FIELD_TYPES = {1: ('u1', 1), 2: ('u1', 1), 3: ('u2', 2), 4: ('u4', 4), 5: ('u4', 8),
               6: ('i1', 1), 7: ('u1', 1), 8: ('i2', 2), 9: ('i4', 4), 10: ('i4', 8),
               11: ('f4', 4), 12: ('f8', 8), 13: ('u4', 4), 16: ('u8', 8), 17: ('i8', 8),
               18: ('u8', 8)}
ASCII, RATIONAL, SRATIONAL = 2, 5, 10

NONE, LZW, DEFLATE, OLD_DEFLATE, PACKBITS = 1, 5, 8, 32946, 32773
COMPRESSIONS = {NONE: 'none', LZW: 'LZW', DEFLATE: 'Deflate', OLD_DEFLATE: 'Deflate',
                PACKBITS: 'PackBits'}
OTHER_COMPRESSIONS = {2: 'CCITT Group 3 (1-D)', 3: 'CCITT Group 3 fax', 4: 'CCITT Group 4 fax',
                      6: 'old-style JPEG', 7: 'JPEG', 9: 'JBIG', 10: 'JBIG', 32771: 'NeXT',
                      32809: 'ThunderScan', 34661: 'JBIG', 34676: 'SGI LogLuv',
                      34677: 'SGI LogLuv', 34712: 'JPEG 2000', 34887: 'LERC', 34925: 'LZMA',
                      34926: 'Zstandard', 34927: 'WebP', 50000: 'Zstandard', 50001: 'WebP',
                      50002: 'JPEG XL', 52546: 'JPEG XL'}
PHOTOMETRICS = {2: 'an RGB colour image', 3: 'a palette (colour-mapped) image',
                4: 'a transparency mask', 5: 'a CMYK image', 6: 'a YCbCr colour image',
                8: 'a CIE L*a*b* colour image', 9: 'an ICC L*a*b* colour image',
                10: 'an ITU L*a*b* colour image', 32844: 'a LogL image',
                32845: 'a LogLuv image', 34892: 'a linear raw camera image'}
SAMPLE_KINDS = {1: 'u', 2: 'i', 3: 'f', 4: 'u'}     # 4: undefined, read as unsigned

MAX_TAGS = 100000          # per image directory; real files have a few dozen
MAX_PAGES = 10000000


def is_tiff(path):
    '''Whether the file starts with a TIFF or BigTIFF header.'''
    try:
        with open(os.fspath(path), 'rb') as f:
            head = f.read(4)
    except OSError:
        return False
    return head in (b'II*\0', b'MM\0*', b'II+\0', b'MM\0+')


class _Page:
    '''One image directory: the layout of one image.'''
    __slots__ = ('index', 'width', 'height', 'dtype', 'compression', 'predictor', 'tiled',
                 'block_rows', 'block_cols', 'offsets', 'counts', 'subfile', 'description')


class TiffFile:
    '''
    An open TIFF file: its images' layout and metadata, read without reading the pixels.
    Use it as a context manager, or call :py:meth:`close`.

    :param path: the file.
    :type path: str or os.PathLike
    :raise TiffError: if the file isn't a TIFF file, or holds no image this reader can read.
    '''

    def __init__(self, path):
        self.path = os.fspath(path)
        self._f = open(self.path, 'rb')
        try:
            self._size = os.fstat(self._f.fileno()).st_size
            self._parse()
        except Exception:
            self._f.close()
            raise

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        '''Close the file.'''
        self._f.close()

    # ------------------------------------------------------------------ public

    @property
    def npages(self):
        '''The number of images (patterns) in the file, without thumbnails.'''
        return len(self._pages)

    @property
    def shape(self):
        '''The size of each image, ``(rows, columns)``.'''
        p = self._pages[0]
        return p.height, p.width

    @property
    def dtype(self):
        '''The images' data type, in this computer's byte order.'''
        return self._pages[0].dtype.newbyteorder('=')

    @property
    def scan_shape(self):
        '''
        The scan shape the metadata records (tifffile's ``shape``), or ``(npages,)`` for a
        series, ``()`` for one image.
        '''
        return self._scan_shape

    @property
    def metadata(self):
        '''
        The first image's descriptive tags by name (ImageDescription, Software, DateTime …),
        with ``imagej`` (ImageJ's settings) or ``shaped`` (tifffile's) parsed from its
        description when present, and the ``compression``.
        '''
        return self._metadata

    def read(self, pages=None):
        '''
        Read images.

        :param pages: the images to read, counting from 0; all of them by default.
        :type pages: sequence of int, optional
        :return: the images, shape ``(images, rows, columns)``, in this computer's byte order.
        :rtype: numpy.ndarray
        :raise TiffError: if image data is missing or can't be decoded.
        '''
        idx = range(self.npages) if pages is None else [int(i) for i in pages]
        rows, cols = self.shape
        out = np.empty((len(idx), rows, cols), dtype=self.dtype)
        for k, i in enumerate(idx):
            if not 0 <= i < self.npages:
                raise IndexError(f'image {i} is outside the {self.npages} images in {self.path}')
            self._read_page(self._pages[i], out[k])
        return out

    # ------------------------------------------------------------------ structure

    def _parse(self):
        f = self._f
        head = f.read(16)
        if head[:2] == b'II':
            self._bo = '<'
        elif head[:2] == b'MM':
            self._bo = '>'
        else:
            raise TiffError(f'{self.path} is not a TIFF file')
        magic = struct.unpack(self._bo + 'H', head[2:4])[0]
        if magic == 42:
            self._big = False
            first = struct.unpack(self._bo + 'I', head[4:8])[0]
        elif magic == 43:
            self._big = True
            size, zero = struct.unpack(self._bo + 'HH', head[4:8])
            if size != 8 or zero != 0:
                raise TiffError(f'{self.path}: unsupported BigTIFF offset size {size}')
            first = struct.unpack(self._bo + 'Q', head[8:16])[0]
        else:
            raise TiffError(f'{self.path} is not a TIFF file')

        dirs = self._read_dirs(first)
        if not dirs:
            raise TiffError(f'{self.path} holds no image')
        pages = []
        for i, d in enumerate(dirs):
            subfile = self._value(d, NEW_SUBFILE_TYPE, 0)
            if i > 0 and subfile & 0b101:       # reduced resolution (thumbnail) or mask
                continue
            pages.append(self._page(d, i))
        first_page = pages[0]
        for p in pages[1:]:
            if (p.height, p.width) != (first_page.height, first_page.width) or \
                    p.dtype.newbyteorder('=') != first_page.dtype.newbyteorder('='):
                raise TiffError(
                    f'{self.path}: image {p.index} is {p.width} x {p.height} '
                    f'{p.dtype.newbyteorder("=")}, but image 0 is {first_page.width} x '
                    f'{first_page.height} {first_page.dtype.newbyteorder("=")}; the images in '
                    'a file must all be the same size and type')
        self._pages = pages

        meta = {}
        d0 = dirs[0]
        for tag, name in METADATA_TAGS.items():
            if tag in d0:
                meta[name] = self._value(d0, tag)
        meta['compression'] = COMPRESSIONS[first_page.compression]
        desc = first_page.description or ''
        imagej = _parse_imagej(desc)
        shaped = _parse_shaped(desc)
        if imagej:
            meta['imagej'] = imagej
            self._expand_imagej(imagej)
        if shaped:
            meta['shaped'] = shaped
        self._metadata = meta
        self._scan_shape = self._scan_from(shaped)

    def _read_dirs(self, offset):
        f, bo = self._f, self._bo
        count_fmt, entry, next_fmt = (('Q', 20, 'Q') if self._big else ('H', 12, 'I'))
        count_size = struct.calcsize(count_fmt)
        dirs, seen = [], set()
        while offset:
            if offset in seen:
                raise TiffError(f'{self.path}: its image directories form a loop')
            if offset + count_size > self._size:
                raise TiffError(f'{self.path} is truncated: image directory {len(dirs)} is '
                                'missing')
            seen.add(offset)
            f.seek(offset)
            n = struct.unpack(bo + count_fmt, f.read(count_size))[0]
            if not 0 < n <= MAX_TAGS:
                raise TiffError(f'{self.path}: image directory {len(dirs)} has {n} tags')
            raw = f.read(n * entry + struct.calcsize(next_fmt))
            if len(raw) < n * entry:
                raise TiffError(f'{self.path} is truncated in image directory {len(dirs)}')
            d = {}
            for k in range(n):
                e = raw[k * entry:(k + 1) * entry]
                if self._big:
                    tag, typ, cnt = struct.unpack(bo + 'HHQ', e[:12])
                    field = e[12:20]
                else:
                    tag, typ, cnt = struct.unpack(bo + 'HHI', e[:8])
                    field = e[8:12]
                if typ in FIELD_TYPES:
                    d[tag] = (typ, cnt, field)
            dirs.append(d)
            if len(dirs) > MAX_PAGES:
                raise TiffError(f'{self.path} has more than {MAX_PAGES} images')
            tail = raw[n * entry:]
            if len(tail) < struct.calcsize(next_fmt):
                raise TiffError(f'{self.path} is truncated in image directory {len(dirs) - 1}')
            offset = struct.unpack(bo + next_fmt, tail)[0]
        return dirs

    def _value(self, d, tag, default=None):
        '''A tag's value: a number, a string, or a numpy array for several numbers.'''
        if tag not in d:
            return default
        typ, cnt, field = d[tag]
        code, size = FIELD_TYPES[typ]
        nbytes = cnt * size
        if nbytes <= len(field):
            raw = field[:nbytes]
        else:
            off = struct.unpack(self._bo + ('Q' if self._big else 'I'), field)[0]
            if off + nbytes > self._size:
                raise TiffError(f'{self.path} is truncated: tag {tag}\'s values are missing')
            self._f.seek(off)
            raw = self._f.read(nbytes)
        if typ == ASCII:
            return raw.split(b'\0', 1)[0].decode('latin-1').strip()
        a = np.frombuffer(raw, dtype=self._bo + code, count=cnt * (2 if typ in (RATIONAL, SRATIONAL) else 1))
        if typ in (RATIONAL, SRATIONAL):
            a = a.reshape(-1, 2)
            with np.errstate(divide='ignore', invalid='ignore'):
                a = a[:, 0] / a[:, 1].astype(np.float64)
        if cnt == 1:
            v = a[0]
            return float(v) if a.dtype.kind == 'f' else int(v)
        return a

    def _page(self, d, index):
        where = f'{self.path}, image {index}'
        need = [t for t in (IMAGE_WIDTH, IMAGE_LENGTH) if t not in d]
        if need:
            raise TiffError(f'{where}: the image size is missing')
        p = _Page()
        p.index = index
        p.width = self._value(d, IMAGE_WIDTH)
        p.height = self._value(d, IMAGE_LENGTH)
        if p.width < 1 or p.height < 1:
            raise TiffError(f'{where}: the image is {p.width} x {p.height}')
        p.subfile = self._value(d, NEW_SUBFILE_TYPE, 0)
        p.description = self._value(d, IMAGE_DESCRIPTION)

        spp = self._value(d, SAMPLES_PER_PIXEL, 1)
        photometric = self._value(d, PHOTOMETRIC, 1)
        if photometric in PHOTOMETRICS or spp != 1:
            what = PHOTOMETRICS.get(photometric, f'an image with {spp} samples per pixel')
            raise TiffError(f'{where} is {what}. Diffraction patterns must be grayscale: one '
                            'value per pixel')
        bits = _first(self._value(d, BITS_PER_SAMPLE, 1))
        fmt = _first(self._value(d, SAMPLE_FORMAT, 1))
        kind = SAMPLE_KINDS.get(fmt)
        if bits == 1:
            raise TiffError(f'{where} is a black-and-white (1-bit) image, not diffraction data')
        if kind is None:
            raise TiffError(f'{where}: unsupported sample format {fmt} (complex numbers?)')
        if bits not in (8, 16, 32, 64) or (kind == 'f' and bits == 8):
            raise TiffError(f'{where}: {bits}-bit {"floating-point" if kind == "f" else "integer"} '
                            'pixels aren\'t supported')
        p.dtype = np.dtype(f'{self._bo}{kind}{bits // 8}')

        p.compression = self._value(d, COMPRESSION, NONE)
        if p.compression not in COMPRESSIONS:
            name = OTHER_COMPRESSIONS.get(p.compression, f'number {p.compression}')
            raise TiffError(f'{where} uses {name} compression, which pyEMAPS can\'t read. '
                            'Save it uncompressed, or with LZW, Deflate (zip) or PackBits '
                            'compression')
        p.predictor = self._value(d, PREDICTOR, 1)
        if p.predictor not in (1, 2, 3):
            raise TiffError(f'{where}: unknown predictor {p.predictor}')
        if p.predictor == 2 and kind == 'f':
            raise TiffError(f'{where}: the horizontal predictor on floating-point pixels isn\'t '
                            'supported')
        if p.predictor == 3 and kind != 'f':
            raise TiffError(f'{where}: the floating-point predictor on integer pixels')
        if self._value(d, PLANAR_CONFIG, 1) not in (1, 2):
            raise TiffError(f'{where}: unknown planar configuration')

        isz = p.dtype.itemsize
        if TILE_OFFSETS in d:
            p.tiled = True
            p.block_cols = self._value(d, TILE_WIDTH)
            p.block_rows = self._value(d, TILE_LENGTH)
            if not p.block_cols or not p.block_rows:
                raise TiffError(f'{where}: the tile size is missing')
            offsets = self._value(d, TILE_OFFSETS)
            counts = self._value(d, TILE_BYTE_COUNTS)
            nblocks = (-(-p.height // p.block_rows)) * (-(-p.width // p.block_cols))
            full = p.block_rows * p.block_cols * isz
        elif STRIP_OFFSETS in d:
            p.tiled = False
            p.block_cols = p.width
            p.block_rows = min(self._value(d, ROWS_PER_STRIP, p.height) or p.height, p.height)
            offsets = self._value(d, STRIP_OFFSETS)
            counts = self._value(d, STRIP_BYTE_COUNTS)
            nblocks = -(-p.height // p.block_rows)
            full = None
        else:
            raise TiffError(f'{where}: the image data\'s location is missing')
        offsets = np.atleast_1d(np.asarray(offsets, dtype=np.int64))
        if counts is None:
            if p.compression != NONE:
                raise TiffError(f'{where}: the compressed data sizes are missing')
            if p.tiled:
                counts = np.full(len(offsets), full)
            else:
                counts = np.array([min(p.block_rows, p.height - k * p.block_rows) * p.width * isz
                                   for k in range(len(offsets))])
        counts = np.atleast_1d(np.asarray(counts, dtype=np.int64))
        if len(offsets) < nblocks or len(counts) < nblocks:
            raise TiffError(f'{where}: {len(offsets)} data blocks for an image that needs '
                            f'{nblocks}')
        p.offsets, p.counts = offsets[:nblocks], counts[:nblocks]
        return p

    def _expand_imagej(self, imagej):
        '''
        ImageJ writes stacks over 4 GB with one image directory, followed by all the images,
        uncompressed and back to back. Add the images the directories don't list.
        '''
        n = imagej.get('images')
        if not isinstance(n, int) or n <= len(self._pages):
            return
        p = self._pages[0]
        if len(self._pages) != 1 or p.compression != NONE or p.tiled:
            return
        page_bytes = p.width * p.height * p.dtype.itemsize
        ends = p.offsets + p.counts
        if np.any(p.offsets[1:] != ends[:-1]) or p.counts.sum() != page_bytes:
            return
        start = int(p.offsets[0])
        if start + n * page_bytes > self._size:
            raise TiffError(f'{self.path} is truncated: ImageJ recorded {n} images, but the file '
                            f'only has room for {(self._size - start) // page_bytes}')
        for k in range(1, n):
            q = _Page()
            for s in _Page.__slots__:
                setattr(q, s, getattr(p, s))
            q.index = k
            q.offsets = p.offsets + k * page_bytes
            self._pages.append(q)

    def _scan_from(self, shaped):
        n = len(self._pages)
        shape = shaped.get('shape') if shaped else None
        if isinstance(shape, list) and len(shape) >= 2 and all(isinstance(v, int) for v in shape):
            if tuple(shape[-2:]) == self.shape:
                nav = tuple(v for v in shape[:-2] if v != 1)
                if int(np.prod(nav or (1,))) == n and len(nav) <= 2:
                    return nav
        return (n,) if n > 1 else ()

    # ------------------------------------------------------------------ pixels

    def _read_page(self, p, out):
        f, isz = self._f, p.dtype.itemsize
        rows_total, cols_total = p.height, p.width
        if p.compression == NONE and not p.tiled and p.predictor == 1:
            ends = p.offsets + p.counts
            need = rows_total * cols_total * isz
            if np.all(p.offsets[1:] == ends[:-1]) and p.counts.sum() >= need:
                out[...] = np.frombuffer(self._read_at(p, int(p.offsets[0]), need),
                                         dtype=p.dtype).reshape(out.shape)
                return
        tiles_across = -(-cols_total // p.block_cols)
        for b, (off, cnt) in enumerate(zip(p.offsets, p.counts)):
            r0 = (b // tiles_across) * p.block_rows
            c0 = (b % tiles_across) * p.block_cols
            nrows = p.block_rows if p.tiled else min(p.block_rows, rows_total - r0)
            raw = self._read_at(p, int(off), int(cnt))
            data = self._decode(p, raw, b)
            need = nrows * p.block_cols * isz
            if len(data) < need:
                if p.tiled or p.compression == NONE:
                    raise TiffError(f'{self.path}, image {p.index}: data block {b} has '
                                    f'{len(data)} bytes, expected {need}')
                raise TiffError(f'{self.path}, image {p.index}: data block {b} decodes to '
                                f'{len(data)} bytes, expected {need}')
            block = self._unpredict(p, data[:need], nrows)
            r1 = min(r0 + nrows, rows_total)
            c1 = min(c0 + p.block_cols, cols_total)
            out[r0:r1, c0:c1] = block[:r1 - r0, :c1 - c0]

    def _read_at(self, p, off, count):
        if off < 0 or off + count > self._size:
            raise TiffError(f'{self.path} is truncated: image {p.index}\'s data is missing')
        self._f.seek(off)
        return self._f.read(count)

    def _decode(self, p, raw, b):
        c = p.compression
        try:
            if c == NONE:
                return raw
            if c in (DEFLATE, OLD_DEFLATE):
                return zlib.decompressobj().decompress(raw)
            if c == LZW:
                return lzw_decode(raw)
            return packbits_decode(raw)
        except (zlib.error, TiffError) as e:
            raise TiffError(f'{self.path}, image {p.index}: data block {b} can\'t be decoded '
                            f'({COMPRESSIONS[c]}): {e}') from None

    def _unpredict(self, p, data, nrows):
        cols = p.block_cols
        if p.predictor == 3:
            # Floating-point predictor (Adobe TIFF Technical Note 3): each row holds the bytes
            # of its values as planes, most significant first, differenced byte by byte.
            isz = p.dtype.itemsize
            b = np.frombuffer(data, dtype=np.uint8).reshape(nrows, isz * cols)
            b = np.cumsum(b, axis=1, dtype=np.uint8).reshape(nrows, isz, cols)
            b = np.ascontiguousarray(b.transpose(0, 2, 1))
            return b.view(f'>f{isz}').reshape(nrows, cols)
        a = np.frombuffer(data, dtype=p.dtype).reshape(nrows, cols)
        if p.predictor == 2:
            native = a.astype(p.dtype.newbyteorder('='))
            return np.cumsum(native, axis=1, dtype=native.dtype)
        return a


# ------------------------------------------------------------------ codecs

def packbits_decode(data):
    '''Decode PackBits (Apple Macintosh run-length) data.'''
    out = bytearray()
    i, n = 0, len(data)
    while i < n:
        h = data[i]
        i += 1
        if h < 128:
            out += data[i:i + h + 1]
            i += h + 1
        elif h > 128:
            if i >= n:
                break
            out += bytes((data[i],)) * (257 - h)
            i += 1
    return bytes(out)


def lzw_decode(data):
    '''
    Decode TIFF LZW data: codes of 9 to 12 bits, most significant bit first, with the code
    width growing one code early, as TIFF 6.0 specifies.
    '''
    if len(data) >= 2 and data[0] == 0 and (data[1] & 1):
        raise TiffError('old-style (pre-TIFF 6.0) LZW isn\'t supported')
    clear, eoi = 256, 257
    base = [bytes((i,)) for i in range(256)] + [b'', b'']
    table = list(base)
    out = bytearray()
    nbits, mask = 9, 511
    bitbuf = bitcnt = 0
    prev = None
    for byte in data:
        bitbuf = ((bitbuf << 8) | byte) & 0xFFFFFF
        bitcnt += 8
        while bitcnt >= nbits:
            bitcnt -= nbits
            code = (bitbuf >> bitcnt) & mask
            if code == clear:
                table = list(base)
                nbits, mask = 9, 511
                prev = None
                continue
            if code == eoi:
                return bytes(out)
            if prev is None:
                if code >= 256:
                    raise TiffError('corrupt LZW data')
                entry = table[code]
            elif code < len(table):
                entry = table[code]
                if len(table) < 4096:
                    table.append(prev + entry[:1])
            elif code == len(table):
                entry = prev + prev[:1]
                table.append(entry)
            else:
                raise TiffError('corrupt LZW data')
            out += entry
            prev = entry
            if len(table) >= mask and nbits < 12:
                nbits += 1
                mask = (1 << nbits) - 1
    return bytes(out)


# ------------------------------------------------------------------ metadata

def _first(v):
    return int(v[0]) if isinstance(v, np.ndarray) else int(v)


def _parse_imagej(desc):
    '''ImageJ's settings from its ImageDescription (``ImageJ=…`` then ``key=value`` lines).'''
    if not desc.startswith('ImageJ='):
        return {}
    out = {}
    for line in desc.splitlines():
        if '=' not in line:
            continue
        key, value = line.split('=', 1)
        value = value.strip()
        for conv in (int, float):
            try:
                value = conv(value)
                break
            except ValueError:
                pass
        if value in ('true', 'false'):
            value = value == 'true'
        out[key.strip()] = value
    return out


def _parse_shaped(desc):
    '''tifffile's JSON ImageDescription, such as ``{"shape": [30, 30, 256, 256]}``.'''
    if not desc.startswith('{'):
        return {}
    try:
        v = json.loads(desc)
    except ValueError:
        return {}
    return v if isinstance(v, dict) and 'shape' in v else {}
