'''
.. This file is part of pyEMAPS

.. ----

.. pyEMAPS is free software. You can redistribute it and/or modify
.. it under the terms of the GNU General Public License as published
.. by the Free Software Foundation, either version 3 of the License,
.. or (at your option) any later version..

.. pyEMAPS is distributed in the hope that it will be useful,
.. but WITHOUT ANY WARRANTY; without even the implied warranty of
.. MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
.. GNU General Public License for more details.

.. You should have received a copy of the GNU General Public License
.. along with pyEMAPS.  If not, see `<https://www.gnu.org/licenses/>`_.

.. Contact supprort@emlabsoftware.com for any questions and comments.

.. ----

Read experimental diffraction images from microscope and detector files.

:py:func:`read_image` reads the file formats that `RosettaSciIO
<https://hyperspy.org/rosettasciio/>`_ supports, such as Gatan DigitalMicrograph (``.dm3``,
``.dm4``), Quantum Detectors Merlin (``.mib``), TIFF, Velox and NCEM EMD, TIA (``.ser``,
``.emi``), MRC, TopSpin (``.app5``), Dectris Arina (``.h5``) and HyperSpy (``.hspy``,
``.zspy``), as well as pyEMAPS' own small-header files (``.im3``). It returns the patterns as
numpy arrays, with the scan shape and calibration from the file. Reading files needs no
license; analysing them with the 4D-STEM features does (see
:py:meth:`StackImage.from_file <pyemaps.stackimg.StackImage.from_file>`).

RosettaSciIO is an optional dependency. Install it with ``pip install "pyemaps[io]"``.
'''
import importlib
import os

import numpy as np

INSTALL_HINT = 'pip install "pyemaps[io]"'

# pyEMAPS small-header files: an 8-byte header of four little-endian shorts (width, height,
# number of patterns, data type), then the patterns, row by row. Data types above 10 are
# stacks; for single images the third short isn't used.
SH_TYPES = {1: np.int16, 2: np.float32, 4: np.float64}
SH_STACK = 10

# Readers to try first, for extensions that several RosettaSciIO readers share.
_PREFERRED = {'h5': ['Arina', 'USID', 'Delmic', 'Tofwerk'],
              'hdf5': ['HSPY', 'USID', 'Delmic'],
              'xml': ['EMPAD', 'JobinYvon'],
              'img': ['Hamamatsu', 'JEOL'],
              'mrc': ['MRC', 'MRCZ'],
              'csv': ['Impulse', 'Protochips']}

# pip package names for modules that RosettaSciIO readers import
_PIP_NAMES = {'skimage': 'scikit-image', 'h5py': 'h5py', 'tifffile': 'tifffile',
              'imageio': 'imageio', 'mrcz': 'mrcz', 'zarr': 'zarr', 'hdf5plugin': 'hdf5plugin',
              'pyUSID': 'pyUSID', 'sparse': 'sparse'}


class ExperimentalImage:
    '''
    Experimental diffraction patterns read from a file by :py:func:`read_image`: one pattern,
    or a stack of them, one per scan position.
    '''
    def __init__(self, data, scan_shape, reader, axes, metadata, source):
        self._data = data
        self._scan_shape = tuple(scan_shape)
        self._reader = reader
        self._axes = axes
        self._metadata = metadata
        self._source = source

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
        '''The reader that read the file: a RosettaSciIO reader's name, or ``pyEMAPS``.'''
        return self._reader

    @property
    def axes(self):
        '''
        The calibration of the pattern axes, rows then columns, from the file: dictionaries
        with the ``name``, ``size``, ``scale`` (per pixel, after binning), ``offset`` and
        ``units``. Files differ in what they record; the units can be missing.
        '''
        return self._axes

    @property
    def metadata(self):
        '''The file's metadata, as RosettaSciIO reports it, or an empty dictionary.'''
        return self._metadata

    @property
    def source(self):
        '''The path of the file.'''
        return self._source

    def __repr__(self):
        return (f'ExperimentalImage({os.path.basename(self._source)!r}: {self.npatterns} '
                f'pattern(s) of {self.pattern_shape[0]} x {self.pattern_shape[1]}, '
                f'scan {self._scan_shape}, {self._data.dtype}, read by {self._reader})')


def image_readers():
    '''
    The readers :py:func:`read_image` can use, with their file extensions.

    :return: ``(name, extensions)`` pairs: pyEMAPS' own reader, then RosettaSciIO's, if it's
        installed.
    :rtype: list of tuple
    '''
    out = [('pyEMAPS', ['im3', 'img'])]
    try:
        from rsciio import IO_PLUGINS
    except ImportError:
        return out
    for p in IO_PLUGINS:
        exts = sorted({e.lower() for e in p['file_extensions']})
        out.append((p['name'], exts))
    return out


def read_image(path, reader=None, signal=None, binning=1, scan_roi=None):
    '''
    Read experimental diffraction patterns from a file.

    :param path: the file. Its extension selects the reader.
    :type path: str or os.PathLike
    :param reader: the name of the reader to use, such as ``'TIFF'``, ``'HSPY'`` or ``'pyEMAPS'``,
        for an extension that several readers share (``.h5``, ``.img``, ``.xml``). See
        :py:func:`image_readers`.
    :type reader: str, optional
    :param signal: which dataset in the file to read, counting from 0, when a file has several.
        By default, the image dataset with the most patterns: the 4D-STEM scan rather than its
        navigation image.
    :type signal: int, optional
    :param binning: average square blocks of *binning* x *binning* pixels into one. Pixels left
        over at the right and bottom edges are dropped. Binning also scales the calibration in
        :py:attr:`ExperimentalImage.axes`, and the camera constant and pattern center you give
        :py:meth:`~pyemaps.stackimg.StackImage.indexImage` must be scaled the same way.
    :type binning: int, optional
    :param scan_roi: the part of the scan to read: ``(row, column, rows, columns)`` for a 2-D
        scan, ``(first, count)`` for a series of patterns, counting from 0.
    :type scan_roi: tuple of int, optional
    :return: the patterns.
    :rtype: ExperimentalImage
    :raise FileNotFoundError: if the file doesn't exist.
    :raise ImportError: if the file needs RosettaSciIO, or a package one of its readers needs,
        and it isn't installed. The message says what to install.
    :raise ValueError: if no reader can read the file, the file holds no 2-D image (a spectrum,
        for example), or an option is invalid.
    '''
    path = os.fspath(path)
    if not os.path.exists(path):          # a file, or a folder for ZSPY (zarr) stores
        raise FileNotFoundError(f'Image file not found: {path}')
    if not isinstance(binning, (int, np.integer)) or isinstance(binning, bool) or binning < 1:
        raise ValueError(f'binning must be a positive integer, not {binning!r}')

    ext = os.path.splitext(path)[1][1:].lower()
    own = (reader or '').lower() in ('pyemaps', 'im3')
    if own or (reader is None and (ext == 'im3' or (ext == 'img' and _is_small_header(path)))):
        data, axes_info, metadata, name = _read_small_header(path), None, {}, 'pyEMAPS'
        nav_shape = data.shape[:-2]
    else:
        # Read lazily only for a scan_roi, which then reads just that part: a lazy read can
        # keep the file open (h5py), so close it once the data is read.
        lazy = scan_roi is not None
        name, sigs = _read_signals(path, ext, reader, lazy)
        data, nav_shape, axes_info, metadata = _pick_image(sigs, signal, path)
        del sigs

    lazy = hasattr(data, 'dask')
    stack, nav_shape = _materialize(data, nav_shape, scan_roi)
    del data
    if lazy:
        import gc
        gc.collect()               # a lazy TIFF keeps its file until the dask graph is freed
    if not stack.flags.owndata:
        stack = stack.copy()       # a view of a memory-mapped file (.im3, Ripple) keeps it open
    stack = _convert(stack)
    rows, cols = (int(n) for n in stack.shape[1:])
    if binning > 1:
        rows, cols = rows // binning, cols // binning
        if rows < 1 or cols < 1:
            raise ValueError(f'binning={binning} is larger than the patterns')
        stack = stack[:, :rows * binning, :cols * binning].reshape(
            -1, rows, binning, cols, binning).mean(axis=(2, 4), dtype=np.float64).astype(np.float32)

    axes = []
    for k, size in enumerate((rows, cols)):
        a = dict(axes_info[k]) if axes_info else {'name': ('rows', 'columns')[k]}
        a['size'] = size
        a['scale'] = float(a.get('scale', 1.0)) * binning
        a['offset'] = float(a.get('offset', 0.0))
        units = a.get('units')
        a['units'] = units if isinstance(units, str) else ''
        axes.append({key: a[key] for key in ('name', 'size', 'scale', 'offset', 'units') if key in a})
    return ExperimentalImage(np.ascontiguousarray(stack), nav_shape, name, axes, metadata, path)


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


def _is_small_header(path):
    return _sh_layout(path) is not None


def _read_small_header(path):
    layout = _sh_layout(path)
    if layout is None:
        raise ValueError(f'{path} is not a pyEMAPS small-header file: its header and size '
                         'don\'t match')
    w, h, n, dtype = layout
    data = np.memmap(path, dtype=np.dtype(dtype).newbyteorder('<'), mode='r', offset=8,
                     shape=(n, h, w))
    return data if n > 1 else data[0]


def _rsciio(ext):
    try:
        import rsciio
    except ImportError as e:
        raise ImportError(f'Reading .{ext} files needs RosettaSciIO, which isn\'t installed. '
                          f'Install it with: {INSTALL_HINT}') from e
    # Import dask.array (a RosettaSciIO dependency) before any reader runs. When a reader
    # imports it for the first time, the import keeps that reader's frames alive, and with
    # them its memory-mapped file: a Merlin .mib or Ripple file stayed open, and couldn't be
    # moved or deleted on Windows, until Python exited (RosettaSciIO 0.15, without numba).
    try:
        import dask.array  # noqa: F401
    except ImportError:
        pass
    return rsciio


def _candidates(plugins, ext, reader):
    if reader:
        r = reader.lower()
        found = [p for p in plugins
                 if r == p['name'].lower() or r in [a.lower() for a in p.get('name_aliases', [])]]
        if not found:
            raise ValueError(f'Unknown reader {reader!r}; see pyemaps.image_readers()')
        return found
    found = [p for p in plugins if ext in [e.lower() for e in p['file_extensions']]]
    if not found:
        raise ValueError(f'No reader for .{ext} files; see pyemaps.image_readers()')
    order = _PREFERRED.get(ext, [])
    return sorted(found, key=lambda p: order.index(p['name']) if p['name'] in order else len(order))


def _materialize(data, nav_shape, roi):
    '''
    The patterns as an in-memory (patterns, rows, columns) array, reading only the scan_roi
    part of a lazy dataset, then closing the files the lazy dataset held open.
    '''
    lazy = hasattr(data, 'dask')
    try:
        part, nav_shape = _apply_roi(data, nav_shape, roi)
        rows, cols = (int(n) for n in part.shape[-2:])
        stack = np.asarray(part).reshape(-1, rows, cols)
    finally:
        if lazy:
            _release(data)
    return stack, nav_shape


def _release(data):
    '''Close the files a lazy (dask) array reads from, such as h5py's, once it's computed.'''
    graph = getattr(data, 'dask', None)
    if graph is None:
        return
    try:
        values = list(dict(graph).values())
    except Exception:
        return
    for v in values:
        obj = getattr(v, 'value', v)                    # dask's task spec wraps data nodes
        f = getattr(obj, 'file', None)
        if f is not None and callable(getattr(f, 'close', None)) and hasattr(obj, 'shape'):
            try:
                f.close()
            except Exception:
                pass


def _read_signals(path, ext, reader, lazy=False):
    rsciio = _rsciio(ext)
    missing, errors = [], []
    for p in _candidates(rsciio.IO_PLUGINS, ext, reader):
        try:
            mod = importlib.import_module(p['api'])
            if lazy:
                try:
                    sigs = mod.file_reader(path, lazy=True)
                except (TypeError, NotImplementedError):     # no lazy reading for this reader
                    sigs = mod.file_reader(path)
            else:
                sigs = mod.file_reader(path)
        except ModuleNotFoundError as e:
            missing.append((p['name'], e.name))
            continue
        except Exception as e:                           # not this reader's file, or a bad file
            errors.append(f'{p["name"]}: {type(e).__name__}: {e}')
            continue
        if sigs:
            return p['name'], sigs
        errors.append(f'{p["name"]}: no data')
    if missing and not errors:
        name, module = missing[0]
        package = _PIP_NAMES.get(module, module)
        raise ImportError(f'The {name} reader needs the {package!r} package, which isn\'t '
                          f'installed. Install it with: pip install {package}')
    raise ValueError(f'Can\'t read {path}: ' + '; '.join(errors + [
        f'{n}: needs {_PIP_NAMES.get(m, m)!r}' for n, m in missing]))


def _split_axes(sig):
    axes = sig['axes']
    if any(a.get('navigate') for a in axes):
        nav = [i for i, a in enumerate(axes) if a.get('navigate')]
        img = [i for i, a in enumerate(axes) if not a.get('navigate')]
    else:
        # No scan axis marked (Arina, NumPy arrays): the patterns are the last two axes.
        k = max(len(axes) - 2, 0)
        nav, img = list(range(k)), list(range(k, len(axes)))
    return nav, img


def _is_image(sig):
    _, img = _split_axes(sig)
    dtype = np.dtype(sig['data'].dtype)
    return (len(img) == 2 and dtype.names is None and
            (np.issubdtype(dtype, np.number) or dtype == np.bool_) and
            not np.issubdtype(dtype, np.complexfloating))


def _pick_image(sigs, signal, path):
    if signal is not None:
        if not isinstance(signal, (int, np.integer)) or not 0 <= signal < len(sigs):
            raise ValueError(f'signal must be 0 to {len(sigs) - 1} for this file, not {signal!r}')
        if not _is_image(sigs[signal]):
            raise ValueError(f'Dataset {signal} of {path} is not a 2-D image: '
                             f'{_describe(sigs[signal])}')
        k = signal
    else:
        images = [k for k, s in enumerate(sigs) if _is_image(s)]
        if not images:
            raise ValueError(f'{path} holds no 2-D image: '
                             + '; '.join(_describe(s) for s in sigs))
        k = max(images, key=lambda i: int(np.prod([sigs[i]['axes'][j]['size']
                                                   for j in _split_axes(sigs[i])[0]] or [1])))
    sig = sigs[k]
    nav, img = _split_axes(sig)
    data = sig['data']
    order = nav + img
    if order != list(range(len(order))):
        data = data.transpose(order)
    nav_shape = tuple(int(data.shape[i]) for i in range(len(nav)))
    axes_info = [sig['axes'][i] for i in img]
    return data, nav_shape, axes_info, dict(sig.get('metadata') or {})


def _describe(sig):
    _, img = _split_axes(sig)
    kind = {0: 'a single value', 1: 'a spectrum or profile', 2: 'an image'}.get(len(img),
                                                                                f'{len(img)}-D data')
    return f'{kind} of shape {tuple(sig["data"].shape)} ({sig["data"].dtype})'


def _apply_roi(data, nav_shape, roi):
    if roi is None:
        return data, nav_shape
    roi = tuple(roi)
    if not all(isinstance(v, (int, np.integer)) and not isinstance(v, bool) for v in roi):
        raise ValueError(f'scan_roi must be integers, not {roi!r}')
    if len(nav_shape) == 1 and len(roi) == 2:
        first, count = roi
        if first < 0 or count < 1 or first + count > nav_shape[0]:
            raise ValueError(f'scan_roi {roi} is outside the {nav_shape[0]} patterns')
        return data[first:first + count], (count,)
    if len(nav_shape) == 2 and len(roi) == 4:
        r0, c0, nr, nc = roi
        if r0 < 0 or c0 < 0 or nr < 1 or nc < 1 or r0 + nr > nav_shape[0] or c0 + nc > nav_shape[1]:
            raise ValueError(f'scan_roi {roi} is outside the {nav_shape[0]} x {nav_shape[1]} scan')
        return data[r0:r0 + nr, c0:c0 + nc], (nr, nc)
    want = {0: 'no scan_roi: the file holds a single pattern',
            1: 'scan_roi=(first, count) for a series of patterns',
            2: 'scan_roi=(row, column, rows, columns) for a 2-D scan'}.get(
                len(nav_shape), f'no scan_roi: a {len(nav_shape)}-D scan isn\'t supported')
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
    if dtype == np.bool_ or (stack.size and stack.min() >= -32768 and stack.max() <= 32767):
        return stack.astype(np.int16)
    return stack.astype(np.float32)
