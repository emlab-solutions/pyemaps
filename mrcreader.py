# This file is part of pyEMAPS.
# Copyright (C) 2021-2026 EMLab Solutions, Inc.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Additional permission under GPLv3 Section 7:
# See license-exception.txt for the exception permitting
# combination with the separately licensed backend, emaps.

'''
A reader for MRC files (``.mrc``, ``.mrcs``, ``.st``), following the open MRC2014 standard
(https://www.ccpem.ac.uk/mrc_format/mrc2014.php), in Python and numpy only.

MRC files hold images and image stacks from 3D electron diffraction (MicroED), SerialEM,
Direct Electron cameras and Thermo Fisher software: a 1024-byte header, an optional extended
header, then the sections, each NY rows of NX columns. Sections are read as patterns, in the
file's row order. 8 and 16-bit integers and 16 and 32-bit floats are read; complex and 4-bit
data are refused.

:py:func:`~pyemaps.expimage.read_image` uses this module; most code should call that instead.
'''
import os
import struct

import numpy as np

from .readerbase import Dataset, SingleDatasetFile, runs

MODES = {0: 'i1', 1: 'i2', 2: 'f4', 6: 'u2', 12: 'f2'}
OTHER_MODES = {3: 'complex 16-bit integers (a transform)', 4: 'complex 32-bit floats (a transform)',
               101: '4-bit packed integers'}


class MRCError(ValueError):
    '''A file that isn't an MRC file this reader can read, with the reason.'''


def is_mrc(path):
    '''Whether the file has an MRC header: "MAP" at byte 208 and plausible sizes and mode.'''
    try:
        with open(os.fspath(path), 'rb') as f:
            head = f.read(1024)
    except OSError:
        return False
    return len(head) == 1024 and _byte_order(head) is not None and head[208:211] == b'MAP'


def _byte_order(head):
    '''The header's byte order: from the machine stamp, else whichever gives sane sizes.'''
    stamp = head[212:214]
    if stamp in (b'\x44\x44', b'\x44\x41'):
        return '<'
    if stamp == b'\x11\x11':
        return '>'
    for bo in ('<', '>'):
        nx, ny, nz, mode = struct.unpack(bo + '4i', head[:16])
        if 0 < nx < 1 << 20 and 0 < ny < 1 << 20 and 0 < nz < 1 << 24 and \
                (mode in MODES or mode in OTHER_MODES):
            return bo
    return None


class MRCFile(SingleDatasetFile):
    '''
    An open MRC file. Use it as a context manager, or call :py:meth:`close`.

    :raise MRCError: if the file isn't an MRC file, or holds data this reader can't read.
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
        head = f.read(1024)
        if len(head) < 1024:
            raise MRCError(f'{path} is not an MRC file: it is shorter than the 1024-byte header')
        bo = _byte_order(head)
        if bo is None:
            raise MRCError(f'{path} is not an MRC file: its header makes no sense')
        nx, ny, nz, mode = struct.unpack(bo + '4i', head[:16])
        mx, my, mz = struct.unpack(bo + '3i', head[28:40])
        cella = struct.unpack(bo + '3f', head[40:52])
        mapc = struct.unpack(bo + '3i', head[64:76])
        ispg, nsymbt = struct.unpack(bo + '2i', head[88:96])
        exttyp = head[104:108].decode('latin-1').strip('\0 ')
        nversion = struct.unpack(bo + 'i', head[108:112])[0]
        nlabl = struct.unpack(bo + 'i', head[220:224])[0]
        labels = [head[224 + 80 * k:224 + 80 * (k + 1)].decode('latin-1').rstrip('\0 ')
                  for k in range(max(0, min(nlabl, 10)))]
        if mode in OTHER_MODES:
            raise MRCError(f'{path} holds {OTHER_MODES[mode]} (MRC mode {mode}), not '
                           'diffraction patterns pyEMAPS can read')
        if mode not in MODES:
            raise MRCError(f'{path}: unknown MRC mode {mode}')
        if tuple(mapc) not in ((1, 2, 3), (0, 0, 0)):
            raise MRCError(f'{path}: its axes are reordered (MAPC, MAPR, MAPS = {mapc}); only '
                           'the standard order 1, 2, 3 is supported')
        if nsymbt < 0:
            raise MRCError(f'{path}: negative extended header size {nsymbt}')
        dt = np.dtype(bo + MODES[mode])
        offset = 1024 + nsymbt
        pattern_bytes = nx * ny * dt.itemsize
        if offset + nz * pattern_bytes > size:
            raise MRCError(f'{path} is truncated: its header promises {nz} section(s) of '
                           f'{nx} x {ny}, but the file is too short')

        axes = []
        for k, (name, n, m) in enumerate((('rows', ny, my), ('columns', nx, mx))):
            length = cella[1 - k]
            scale = length / m if m > 0 and length > 0 else 0.0
            axes.append({'name': name, 'scale': scale or 1.0, 'offset': 0.0,
                         'units': 'Å' if scale else ''})
        metadata = {'format': 'MRC', 'mode': mode, 'ispg': ispg, 'nversion': nversion,
                    'extended_header_type': exttyp, 'extended_header_bytes': nsymbt,
                    'labels': labels, 'volume': ispg not in (0,)}

        def read(idx):
            out = np.empty((len(idx), ny, nx), dtype=dt.newbyteorder('='))
            for pos, first, count in runs(idx):
                f.seek(offset + first * pattern_bytes)
                raw = f.read(count * pattern_bytes)
                out[pos:pos + count] = np.frombuffer(raw, dtype=dt).reshape(count, ny, nx)
            return out

        nav = (nz,) if nz > 1 else ()
        self.datasets = [Dataset(os.path.basename(path), nav, (ny, nx), dt.newbyteorder('='),
                                 axes, metadata, read)]
