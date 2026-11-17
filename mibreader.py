# This file is part of pyEMAPS.
# Copyright (C) 2021-2026 EMLab Solutions, Inc.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Additional permission under GPLv3 Section 7:
# See license-exception.txt for the exception permitting
# combination with the separately licensed backend, emaps.

'''
A reader for Quantum Detectors Merlin files (``.mib``), the 4D-STEM data of Medipix3 detectors,
in Python and numpy only.

Each frame is an ASCII header of comma-separated fields, then the pixels. The header fields
follow the description in Diamond Light Source's mib_props (MIT license,
https://github.com/ePSIC-DLS/mib_props): "MQ1", the frame number, the header length in bytes
(384 for one chip, 768 for a quad), the number of chips, the detector columns and rows, the
pixel type (U01, U08, U16, U32, U64, or R64 for raw), the sensor layout, and the acquisition
settings. The pixels are big-endian unsigned integers, rows of columns.

Frames in counting mode (U08, U16, U32, U64) are read. Raw mode (R64), which stores the chips'
counters unassembled, and 1-bit frames (U01) are refused with a message saying so. Merlin
files don't record the scan shape: give it to :py:func:`~pyemaps.expimage.read_image` with
*scan_shape*. The acquisition settings in the ``.hdr`` file next to the ``.mib``, if there is
one, go into the metadata.

:py:func:`~pyemaps.expimage.read_image` uses this module; most code should call that instead.
'''
import os

import numpy as np

from .readerbase import Dataset, SingleDatasetFile, plain_axes, runs

PIXELS = {'U08': '>u1', 'U16': '>u2', 'U32': '>u4', 'U64': '>u8'}


class MIBError(ValueError):
    '''A file that isn't a Merlin file this reader can read, with the reason.'''


def is_mib(path):
    '''Whether the file starts with a Merlin frame header ("MQ1,").'''
    try:
        with open(os.fspath(path), 'rb') as f:
            return f.read(4) == b'MQ1,'
    except OSError:
        return False


def _fields(raw):
    return [v.strip() for v in raw.decode('latin-1').rstrip('\0 ').split(',')]


def read_hdr(path):
    '''The acquisition settings in a Merlin .hdr file, as {name: value}, or {}.'''
    try:
        text = open(path, 'rb').read().decode('latin-1')
    except OSError:
        return {}
    out = {}
    for line in text.replace('\r', '\n').split('\n'):
        if ':' in line and not line.startswith('HDR'):
            key, value = line.split(':', 1)
            out[key.strip()] = value.strip().rstrip('\0 ')
    return out


class MIBFile(SingleDatasetFile):
    '''
    An open Merlin .mib file. Use it as a context manager, or call :py:meth:`close`.

    :raise MIBError: if the file isn't a Merlin file, or holds frames this reader can't read.
    '''

    def __init__(self, path):
        self.path = os.fspath(path)
        self._f = open(self.path, 'rb')
        try:
            self._parse()
        except Exception:
            self._f.close()
            raise

    def _parse(self):
        f, path = self._f, self.path
        size = os.fstat(f.fileno()).st_size
        head = f.read(64)
        if not head.startswith(b'MQ1,'):
            raise MIBError(f'{path} is not a Merlin file: it doesn\'t start with "MQ1,"')
        first = _fields(head)
        try:
            header_bytes = int(first[2])
            f.seek(0)
            fields = _fields(f.read(header_bytes))
            chips, cols, rows = int(fields[3]), int(fields[4]), int(fields[5])
        except (IndexError, ValueError):
            raise MIBError(f'{path}: its first frame header can\'t be read') from None
        kind = fields[6]
        if kind == 'R64':
            raise MIBError(f'{path} holds raw (R64) frames, whose chips are stored unassembled; '
                           'pyEMAPS reads frames saved in counting mode (U08, U16, U32)')
        if kind not in PIXELS:
            raise MIBError(f'{path}: unsupported Merlin pixel type {kind!r}')
        dt = np.dtype(PIXELS[kind])
        frame_bytes = header_bytes + rows * cols * dt.itemsize
        nframes, rest = divmod(size, frame_bytes)
        if nframes < 1 or rest:
            raise MIBError(f'{path} is truncated: {size} bytes isn\'t a whole number of '
                           f'{frame_bytes}-byte frames ({nframes} complete)')
        f.seek((nframes - 1) * frame_bytes)
        if f.read(4) != b'MQ1,':
            raise MIBError(f'{path}: its frames aren\'t all the same size; frame {nframes} '
                           'doesn\'t start with a header')

        hdr_path = os.path.splitext(path)[0] + '.hdr'
        metadata = {'format': 'Merlin', 'pixel_type': kind, 'chips': chips,
                    'layout': fields[7] if len(fields) > 7 else '',
                    'exposure_s': _number(fields[10]) if len(fields) > 10 else None,
                    'timestamp': fields[9] if len(fields) > 9 else '',
                    'header': fields, 'hdr': read_hdr(hdr_path) if os.path.isfile(hdr_path) else {}}

        def read(idx):
            out = np.empty((len(idx), rows, cols), dtype=dt.newbyteorder('='))
            for pos, start, count in runs(idx):
                f.seek(start * frame_bytes)
                raw = np.frombuffer(f.read(count * frame_bytes), dtype=np.uint8)
                frames = raw.reshape(count, frame_bytes)[:, header_bytes:]
                out[pos:pos + count] = frames.copy().view(dt).reshape(count, rows, cols)
            return out

        nav = (nframes,) if nframes > 1 else ()
        self.datasets = [Dataset(os.path.basename(path), nav, (rows, cols),
                                 dt.newbyteorder('='), plain_axes(), metadata, read)]


def _number(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None
