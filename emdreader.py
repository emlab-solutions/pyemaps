# This file is part of pyEMAPS.
# Copyright (C) 2021-2026 EMLab Solutions, Inc.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Additional permission under GPLv3 Section 7:
# See license-exception.txt for the exception permitting
# combination with the separately licensed backend, emaps.

'''
A reader for EMD files (``.emd``): HDF5 files in either of two unrelated layouts that share the
extension.

- **Thermo Fisher Velox** files: the images and image series Velox saves, such as diffraction
  patterns, with the microscope settings it records for each frame (high voltage, camera
  length, detector, pixel size …). Spectra in the same file (EDS, EELS) aren't images, and are
  skipped.
- **Berkeley EMD** files (the open EMD format of the National Center for Electron Microscopy,
  versions 0.x and 1.0), including the 4D-STEM datacubes of py4DSTEM: arrays whose last two
  axes are the pattern, with the calibration of every axis.

It needs `h5py <https://www.h5py.org/>`_ (BSD license), an optional dependency: install it with
``pip install "pyemaps[emd]"``.

:py:func:`~pyemaps.expimage.read_image` uses this module; most code should call that instead.
'''
import json

import numpy as np

INSTALL_HINT = 'pip install "pyemaps[emd]"'

# Velox data kinds that hold spectra or text rather than images
VELOX_IMAGE = 'Image'


def h5py():
    '''The h5py module, or an ImportError that says how to install it.'''
    try:
        import h5py as module
    except ImportError as e:
        raise ImportError('Reading .emd files needs the h5py package, which isn\'t installed. '
                          f'Install it with: {INSTALL_HINT} (on Python 3.15, h5py has no '
                          'Windows release yet)') from e
    return module


def is_hdf5(path):
    '''Whether the file has an HDF5 signature (at offset 0 or a power-of-two offset).'''
    sig = b'\x89HDF\r\n\x1a\n'
    try:
        with open(path, 'rb') as f:
            off = 0
            while True:
                f.seek(off)
                head = f.read(8)
                if head == sig:
                    return True
                if len(head) < 8 or off > (1 << 20):
                    return False
                off = 512 if off == 0 else off * 2
    except OSError:
        return False


class EmdError(ValueError):
    '''An EMD file this reader can't read, with the reason.'''


class EmdDataset:
    '''
    One image dataset in an EMD file: its patterns' layout, calibration and metadata, read
    without reading the pixels.
    '''

    def __init__(self, name, nav_shape, pattern_shape, dtype, axes, metadata, read):
        self.name = name                       # the dataset's path in the file
        self.nav_shape = tuple(nav_shape)      # () for one pattern
        self.pattern_shape = tuple(pattern_shape)
        self.dtype = np.dtype(dtype)
        self.axes = axes                       # [rows, columns]: name, scale, offset, units
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


class EmdFile:
    '''
    An open EMD file and its image datasets. Use it as a context manager, or call
    :py:meth:`close`.

    :raise ImportError: if h5py isn't installed.
    :raise EmdError: if the file isn't an EMD file, or holds no image.
    '''

    def __init__(self, path):
        self.path = str(path)
        h5 = h5py()
        try:
            self._f = h5.File(self.path, 'r')
        except OSError as e:
            raise EmdError(f'{self.path} is not an HDF5 file, so not an EMD file: {e}') from None
        try:
            self.datasets, self.skipped = [], []
            if self._is_velox():
                self.format = 'Velox'
                self._velox()
            elif self._is_berkeley():
                self._berkeley()
            else:
                raise EmdError(f'{self.path} is an HDF5 file, but neither a Velox nor a Berkeley '
                               'EMD file')
            if not self.datasets:
                what = '; '.join(self.skipped) or 'nothing'
                raise EmdError(f'{self.path} holds no 2-D image: {what}')
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

    def choose(self, dataset=None):
        '''
        The dataset to read: *dataset* (its number in :py:attr:`datasets`, or its name), or
        by default the one with the most patterns, the first of them on a tie.
        '''
        if dataset is None:
            return max(self.datasets, key=lambda d: d.npatterns)
        if isinstance(dataset, (int, np.integer)) and not isinstance(dataset, bool):
            if not 0 <= dataset < len(self.datasets):
                raise EmdError(f'dataset must be 0 to {len(self.datasets) - 1} for {self.path}, '
                               f'not {dataset}')
            return self.datasets[dataset]
        for d in self.datasets:
            if d.name == dataset or d.name.split('/')[-1] == dataset:
                return d
        raise EmdError(f'No image dataset {dataset!r} in {self.path}; it has: '
                       + '; '.join(d.describe() for d in self.datasets))

    # ------------------------------------------------------------------ Velox

    def _is_velox(self):
        if 'Version' in self._f:
            try:
                v = json.loads(_text(self._f['Version'][0]))
                return str(v.get('format', '')).lower() == 'velox'
            except (ValueError, TypeError, AttributeError, IndexError):
                pass
        return 'Data' in self._f and VELOX_IMAGE in self._f['Data']

    def _velox(self):
        data = self._f['Data']
        for kind in data:
            if kind != VELOX_IMAGE:
                self.skipped.append(f'Velox {kind} (not images)')
                continue
            for uid in data[kind]:
                g = data[kind][uid]
                if 'Data' not in g:
                    continue
                ds = g['Data']
                if ds.ndim != 3 or not _numeric(ds.dtype):
                    self.skipped.append(f'Velox image {uid} of shape {ds.shape} {ds.dtype}')
                    continue
                rows, cols, frames = (int(n) for n in ds.shape)
                md = _velox_metadata(g)
                self.datasets.append(EmdDataset(
                    name=f'Data/{kind}/{uid}', nav_shape=(frames,) if frames > 1 else (),
                    pattern_shape=(rows, cols), dtype=ds.dtype, axes=_velox_axes(md),
                    metadata=_velox_summary(md, uid),
                    read=lambda idx, ds=ds: np.moveaxis(ds[:, :, _index(idx)], 2, 0)))

    # ------------------------------------------------------------------ Berkeley EMD

    def _is_berkeley(self):
        a = self._f.attrs
        return ('version_major' in a or _attr(a.get('emd_group_type')) == 'file' or
                any(_is_array_group(g) for g in self._groups()))

    def _groups(self):
        out = []
        self._f.visititems(lambda name, obj: out.append(obj) if hasattr(obj, 'keys') else None)
        return out

    def _berkeley(self):
        a = self._f.attrs
        major, minor = _attr(a.get('version_major')), _attr(a.get('version_minor'))
        self.format = f'EMD {major}.{minor}' if major is not None else 'EMD'
        h5 = h5py()
        for g in self._groups():
            if not _is_array_group(g):
                continue
            ds = g['data'] if 'data' in g else _data_like(g, h5)
            if ds is None:
                continue
            dims = [g[f'dim{k}'] if f'dim{k}' in g else None for k in range(1, ds.ndim + 1)]
            stack = (ds.ndim == 3 and dims[2] is not None and
                     _attr(dims[2].attrs.get('name')) == '_labels_')
            if ds.ndim < 2 or not _numeric(ds.dtype):
                self.skipped.append(f'{g.name}: {_kind(ds.ndim)} of shape {ds.shape} {ds.dtype}')
                continue
            if stack:
                rows, cols, n = (int(v) for v in ds.shape)
                nav = (n,) if n > 1 else ()
                pattern_dims = dims[:2]
                read = (lambda idx, ds=ds: np.moveaxis(ds[:, :, _index(idx)], 2, 0))
            else:
                nav = tuple(int(v) for v in ds.shape[:-2])
                rows, cols = (int(v) for v in ds.shape[-2:])
                pattern_dims = dims[-2:]
                read = (lambda idx, ds=ds: _read_flat(ds, idx))
            if len(nav) > 2:
                self.skipped.append(f'{g.name}: {len(nav)}-D scan of shape {ds.shape}')
                continue
            axes = [_dim_axis(d, ('rows', 'columns')[k]) for k, d in enumerate(pattern_dims)]
            scan_axes = [_dim_axis(d, f'scan {k}') for k, d in enumerate(dims[:len(nav)])] \
                if not stack else []
            meta = {'format': self.format, 'dataset': g.name,
                    'attributes': {k: _attr(v) for k, v in g.attrs.items()},
                    'scan_axes': scan_axes}
            self.datasets.append(EmdDataset(g.name.lstrip('/'), nav, (rows, cols), ds.dtype,
                                            axes, meta, read))


# ------------------------------------------------------------------ helpers

def _text(v):
    if isinstance(v, bytes):
        return v.decode('utf-8', 'replace')
    if isinstance(v, np.ndarray):
        return v.tobytes().split(b'\0', 1)[0].decode('utf-8', 'replace')
    return str(v)


def _attr(v):
    if isinstance(v, bytes):
        return v.decode('utf-8', 'replace')
    if isinstance(v, np.ndarray):
        return v.tolist() if v.ndim else v.item()
    if isinstance(v, np.generic):
        return v.item()
    return v


def _numeric(dtype):
    dtype = np.dtype(dtype)
    return dtype.names is None and dtype.kind in 'uif'


def _kind(ndim):
    return {0: 'a single value', 1: 'a spectrum or profile'}.get(ndim, f'{ndim}-D data')


def _is_array_group(g):
    t = _attr(g.attrs.get('emd_group_type'))
    return t in (1, '1', 'array')


def _data_like(g, h5):
    '''py4DSTEM 0.x names its data "datacube" (or similar): the dataset with dim vectors.'''
    candidates = [g[k] for k in g if isinstance(g[k], h5.Dataset) and not k.startswith('dim')
                  and g[k].ndim >= 2]
    for ds in candidates:
        if all(f'dim{k}' in g for k in range(1, ds.ndim + 1)):
            return ds
    return candidates[0] if len(candidates) == 1 else None


def _index(idx):
    '''A slice for consecutive indices (much faster in h5py than a list), else the list.'''
    if idx and idx == list(range(idx[0], idx[-1] + 1)):
        return slice(idx[0], idx[-1] + 1)
    return idx


def _read_flat(ds, idx):
    '''Patterns *idx* (flat scan positions) of an array whose last two axes are the pattern.'''
    nav = ds.shape[:-2]
    if not nav:
        return np.asarray(ds[()])[np.newaxis]
    if len(nav) == 1:
        return np.asarray(ds[_index(idx)])
    if idx == list(range(int(np.prod(nav)))):
        return np.asarray(ds[()]).reshape((-1,) + tuple(ds.shape[-2:]))
    out = np.empty((len(idx),) + tuple(ds.shape[-2:]), dtype=ds.dtype)
    for k, i in enumerate(idx):
        out[k] = ds[np.unravel_index(i, nav)]
    return out


def _units(u):
    '''EMD 0.x writes units like "[n_m^-1]"; give "nm^-1".'''
    u = _attr(u)
    if not isinstance(u, str):
        return ''
    return u.strip().strip('[]').replace('_', '')


def _dim_axis(d, default):
    axis = {'name': default, 'scale': 1.0, 'offset': 0.0, 'units': ''}
    if d is None:
        return axis
    name = _attr(d.attrs.get('name'))
    if isinstance(name, str) and name and name != '_labels_':
        axis['name'] = name
    axis['units'] = _units(d.attrs.get('units'))
    try:
        v = np.asarray(d[:2], dtype=np.float64)
        if v.size >= 1:
            axis['offset'] = float(v[0])
        if v.size >= 2:
            axis['scale'] = float(v[1] - v[0])
    except (TypeError, ValueError):
        pass
    return axis


def _velox_metadata(g):
    '''The first frame's metadata, a JSON text stored as bytes in column 0 of "Metadata".'''
    if 'Metadata' not in g:
        return {}
    try:
        return json.loads(_text(g['Metadata'][:, 0]))
    except (ValueError, TypeError, IndexError):
        return {}


def _float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _velox_axes(md):
    br = md.get('BinaryResult', {}) if isinstance(md, dict) else {}
    size = br.get('PixelSize', {}) if isinstance(br.get('PixelSize'), dict) else {}
    offset = br.get('Offset', {}) if isinstance(br.get('Offset'), dict) else {}
    out = []
    for name, key, okey, ukey in (('rows', 'height', 'y', 'PixelUnitY'),
                                  ('columns', 'width', 'x', 'PixelUnitX')):
        scale = _float(size.get(key))
        out.append({'name': name, 'scale': scale if scale else 1.0,
                    'offset': _float(offset.get(okey)) or 0.0,
                    'units': br.get(ukey, '') if scale else ''})
    return out


def _velox_summary(md, uid):
    '''The settings that matter for diffraction, plus the full metadata under "velox".'''
    optics = md.get('Optics', {}) if isinstance(md, dict) else {}
    br = md.get('BinaryResult', {}) if isinstance(md, dict) else {}
    inst = md.get('Instrument', {}) if isinstance(md, dict) else {}
    kv = _float(optics.get('AccelerationVoltage'))
    cl = _float(optics.get('CameraLength'))
    return {'format': 'Velox', 'dataset': uid,
            'high_voltage_kV': kv / 1000 if kv else None,
            'camera_length_m': cl,
            'detector': br.get('Detector'),
            'instrument': ' '.join(str(inst[k]) for k in ('Manufacturer', 'InstrumentModel')
                                   if inst.get(k)) or None,
            'velox': md}
