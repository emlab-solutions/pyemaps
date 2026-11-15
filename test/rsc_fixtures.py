'''
Write test files in RosettaSciIO's formats, for run_expimage.py and run_stem4d.py.

RosettaSciIO's writers take a signal dictionary like HyperSpy's: the data, an axes list in
array order with a 'navigate' flag (scan axes first), and the HyperSpy metadata and
attributes some writers read.
'''
import importlib
import os

# extension: (RosettaSciIO module, smallest number of dimensions the writer takes)
WRITERS = {
    'tif': ('rsciio.tiff', 2),
    'hspy': ('rsciio.hspy', 2),
    'zspy': ('rsciio.zspy', 2),
    'mrcz': ('rsciio.mrcz', 3),
    'npy': ('rsciio.numpy', 1),
    'emd': ('rsciio.emd', 2),
    'rpl': ('rsciio.ripple', 1),
    'unf': ('rsciio.semper', 1),
    'msa': ('rsciio.msa', 1),
}


class WriterUnavailable(Exception):
    '''The writer, or a package it needs, isn't installed (e.g. h5py on Python 3.15).'''


def write(path, data, nav=0, scale=1.0, units=''):
    '''
    Write *data* to *path*, in the format its extension names. The first *nav* dimensions are
    scan axes, the rest the pattern (or a spectrum, for 1-D data). The pattern axes get
    *scale* and *units*.
    '''
    import numpy as np
    ext = os.path.splitext(path)[1][1:].lower()
    module, min_dims = WRITERS[ext]
    try:
        writer = importlib.import_module(module).file_writer
    except ImportError as e:
        raise WriterUnavailable(f'{module}: {e}') from e

    data = np.asarray(data)
    if data.ndim < min_dims:                 # MRCZ writes 3-D data: add scan axes of size 1
        added = min_dims - data.ndim
        data = data.reshape((1,) * added + data.shape)
        nav += added
    axes = []
    for i, size in enumerate(data.shape):
        is_nav = i < nav
        axes.append(dict(name=f'axis{i}', size=int(size), offset=0.0, navigate=is_nav,
                         scale=1.0 if is_nav else float(scale), units='' if is_nav else units))
    signal = dict(data=data, axes=axes,
                  metadata={'General': {'title': 'pyemaps test'}, 'Signal': {'signal_type': ''}},
                  original_metadata={}, tmp_parameters={}, attributes={'_lazy': False},
                  learning_results={}, models={},
                  package_info={'name': 'pyemaps', 'version': 'test'})
    try:
        writer(os.fspath(path), signal)
    except ModuleNotFoundError as e:
        raise WriterUnavailable(f'{module}: {e}') from e
