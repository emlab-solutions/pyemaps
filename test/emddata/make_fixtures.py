'''
Write the EMD test files in this folder, with h5py, for run_expimage.py.

    pip install h5py
    python make_fixtures.py [STEM_EELS_1.emd]

Velox files (Thermo Fisher):
- velox_series.emd follows the layout of Velox files: Data/Image/<id>/Data holds
  (rows, columns, frames), and each frame's metadata is a JSON text in a column of
  Data/Image/<id>/Metadata. It also holds an overview image, an EDS spectrum stream and a text
  item, which aren't the patterns.
- velox_maps.emd follows the layout of a Velox spectrum-image file: elemental maps Velox
  computed from an EELS spectrum image (the first all zero), an all-zero image, the DF-S image
  and a reference DF-S image, with the displays (Displays/ImageDisplay and
  SharedProperties/ImageSeriesDataReference) that give each its title, and a spectrum image.
- velox_iliad_dfs.emd is cut from a real Velox file: the DF-S STEM image, its metadata and
  Velox's thumbnail, from "DSO: STEM EELS EMD" by Daen Jannis, Zenodo record 18267156
  (https://zenodo.org/records/18267156), CC BY 4.0
  (https://creativecommons.org/licenses/by/4.0/), acquired on a Thermo Fisher Iliad. Changes:
  only that image is kept. The thumbnail shows that Velox stores rows first. Give the path of
  STEM_EELS_1.emd to rewrite it; without it, the existing file is kept.

Berkeley EMD files (https://emdatasets.com/format/), written from the specification:
- emd1_datacube.emd: EMD 1.0, a 3 x 4 scan of 37 x 41 patterns with dim vectors (two-value
  linear calibration for the pattern axes);
- emd1_stack.emd: EMD 1.0, a stack of 5 images labelled by a "_labels_" dim vector;
- emd02_image.emd: EMD 0.2, one image, emd_group_type 1, units written as "[n_m^-1]";
- py4dstem_datacube.emd: the layout of py4DSTEM 0.x files: a "datacube" dataset in a group
  whose emd_group_type is the string "1".

Files to refuse: an HDF5 file that isn't EMD, a Velox file with only spectra, and an EMD
array that is a spectrum.

It writes expected.npz (the patterns each file must read as, (patterns, rows, columns)) and
manifest.json (scan shape, dtype and calibration, or error words).
'''
import json
import os
import sys

import h5py
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS, COLS = 37, 41
EXPECT, MANIFEST = {}, {}


def rand(dtype, shape, seed):
    rng = np.random.default_rng(seed)
    dt = np.dtype(dtype)
    if dt.kind == 'f':
        return (rng.standard_normal(shape) * 500).astype(dt)
    info = np.iinfo(dt)
    return rng.integers(info.min, info.max, size=shape, endpoint=True, dtype=dt)


def velox_json(frame, kv=200000, cl=0.38, detector='BM-Ceta', pixel=2.5e7, unit='1/m'):
    '''pixel=None: no pixel size, as Velox writes for the elemental maps of a spectrum image.'''
    result = {'AcquisitionUnit': 'CameraImage', 'Detector': detector}
    if pixel is not None:
        result.update({'PixelSize': {'width': str(pixel), 'height': str(pixel)},
                       'PixelUnitX': unit, 'PixelUnitY': unit, 'Offset': {'x': '0', 'y': '0'}})
    result['Encoding'] = 'Signed'
    return json.dumps({
        'Core': {'MetadataDefinitionVersion': '7.9'},
        'Instrument': {'Manufacturer': 'FEI Company', 'InstrumentModel': 'Talos'},
        'Optics': {'AccelerationVoltage': str(kv), 'CameraLength': str(cl), 'ProjectorMode': '2'},
        'Scan': {'ScanSize': {'width': '0', 'height': '0'}},
        'BinaryResult': result,
        'CustomProperties': {'Frame': {'value': str(frame)}},
    }, indent=4)


def velox_display(f, did, rid, uid, display_id, title):
    '''
    A display as Velox records it: Displays/ImageDisplay/<did> refers to
    SharedProperties/ImageSeriesDataReference/<rid>, which gives the image's path. Velox writes
    each as a JSON text in a one-element variable-length string dataset. rid=None: a display
    without data (such as Velox's ColorMix); uid=None: a reference that is missing.
    '''
    text = h5py.string_dtype()
    disp = {'id': display_id, 'title': title, 'settings': '/SharedProperties/ImageDisplaySettings/0'}
    if rid is not None:
        disp['data'] = f'/SharedProperties/ImageSeriesDataReference/{rid}'
        if uid is not None:
            f.require_group('SharedProperties/ImageSeriesDataReference').create_dataset(
                rid, data=[json.dumps({'dataPath': f'/Data/Image/{uid}', 'frameIndex': 0}).encode()],
                dtype=text)
    f.require_group('Displays/ImageDisplay').create_dataset(did, data=[json.dumps(disp).encode()],
                                                            dtype=text)


def velox_image(data_group, uid, stack, **meta):
    '''stack: (frames, rows, columns); stored as Velox does, (rows, columns, frames).'''
    g = data_group.create_group(uid)
    g.create_dataset('Data', data=np.moveaxis(stack, 0, 2), chunks=True)
    md = np.zeros((60000, stack.shape[0]), dtype=np.uint8)
    for k in range(stack.shape[0]):
        b = velox_json(k, **meta).encode()
        md[:len(b), k] = np.frombuffer(b, dtype=np.uint8)
    g.create_dataset('Metadata', data=md, chunks=(60000, 1))
    g.create_dataset('FrameLookupTable', data=np.arange(stack.shape[0], dtype=np.uint32))


def velox_file(fn):
    f = h5py.File(fn, 'w')
    f.create_dataset('Version', data=[json.dumps({'version': '11', 'format': 'Velox'}).encode()],
                     dtype=h5py.string_dtype())
    return f, f.create_group('Data')


def ok(name, stack, scan, axes=None, meta=None):
    EXPECT[name] = stack
    MANIFEST[name] = {'scan_shape': list(scan), 'dtype': stack.dtype.str,
                      'axes': axes or [], 'meta': meta or {}}


def bad(name, words):
    MANIFEST[name] = {'error': words}


def emd1_root(f):
    f.attrs['emd_group_type'] = 'file'
    f.attrs['version_major'] = 1
    f.attrs['version_minor'] = 0
    f.attrs['authoring_program'] = 'pyEMAPS test fixtures'
    root = f.create_group('experiment')
    root.attrs['emd_group_type'] = 'root'
    return root


def dim(g, k, values, name, units=None):
    d = g.create_dataset(f'dim{k}', data=values)
    d.attrs['name'] = name
    if units is not None:
        d.attrs['units'] = units


def main():
    # Velox: a 3-frame diffraction series (non-square, so rows and columns can't be swapped
    # unnoticed), an overview image, an EDS stream and a text item
    series = rand('<i2', (3, ROWS, COLS), 1)
    overview = rand('<u2', (1, 64, 48), 2)
    with velox_file(os.path.join(HERE, 'velox_series.emd'))[0] as f:
        data = f['Data']
        velox_image(data.create_group('Image'), 'a1b2c3d4e5f60718293a4b5c6d7e8f90', series,
                    kv=200000, cl=0.38, pixel=2.5e7, unit='1/m')
        velox_image(data['Image'], 'ffeeddccbbaa99887766554433221100', overview,
                    kv=200000, cl=0.38, detector='HAADF', pixel=1.2e-10, unit='m')
        s = data.create_group('SpectrumStream').create_group('0123456789abcdef0123456789abcdef')
        s.create_dataset('Data', data=rand('<u2', (5000,), 3))
        data.create_group('Text').create_dataset('00000000000000000000000000000001',
                                                 data=[b'{"text": "acquired"}'],
                                                 dtype=h5py.string_dtype())
    ok('velox_series', series, [3],
       axes=[{'name': 'rows', 'scale': 2.5e7, 'units': '1/m'},
             {'name': 'columns', 'scale': 2.5e7, 'units': '1/m'}],
       meta={'high_voltage_kV': 200.0, 'camera_length_m': 0.38, 'detector': 'BM-Ceta',
             'instrument': 'FEI Company Talos', 'format': 'Velox'})
    EXPECT['velox_series_overview'] = overview

    # Velox: the layout of a spectrum-image file, as Velox saves an EELS map: elemental maps it
    # computed from the spectrum image (an empty Ta map first, then Eu), an image that is all
    # zero, the DF-S image acquired with the spectrum image and a larger reference DF-S image,
    # with the displays that title them. The default must be the DF-S image.
    ta = np.zeros((1, 20, 30), dtype='<f4')
    eu = np.abs(rand('<f4', (1, 20, 30), 11))
    blank = np.zeros((1, 20, 30), dtype='<u2')
    dfs_si = rand('<u2', (1, 20, 30), 12)
    ref = rand('<u2', (1, 32, 32), 13)
    uids = {name: f'{k}' * 32 for k, name in enumerate(('ta', 'eu', 'blank', 'dfs', 'ref'))}
    with velox_file(os.path.join(HERE, 'velox_maps.emd'))[0] as f:
        images = f['Data'].create_group('Image')
        for name, stack, det in (('ta', ta, 'Zebra'), ('eu', eu, 'Zebra')):
            velox_image(images, uids[name], stack, kv=300000, cl=0.035, detector=det, pixel=None)
        velox_image(images, uids['blank'], blank, kv=300000, cl=0.035, detector='HAADF',
                    pixel=6.5e-11, unit='m')
        for name, stack in (('dfs', dfs_si), ('ref', ref)):
            velox_image(images, uids[name], stack, kv=300000, cl=0.035, detector='DF-S',
                        pixel=6.5e-11, unit='m')
        si = f['Data'].create_group('EelsSpectrumImage').create_group('9' * 32)
        si.create_dataset('Data', data=rand('<u2', (20, 30, 64), 14))
        velox_display(f, 'a' * 32, 'f' * 32, uids['ta'], 'Ta-EELS', 'Ta')
        velox_display(f, 'b' * 32, 'e' * 32, uids['eu'], 'Eu-EELS', 'Eu')
        velox_display(f, 'c' * 32, 'd' * 32, uids['dfs'], 'DF-S', 'DF-S')
        velox_display(f, 'd' * 32, 'c' * 32, uids['ref'], 'a', 'Ref DF-S')
        velox_display(f, 'e' * 32, None, None, 'CM', 'ColorMix')            # no data
        velox_display(f, 'f' * 32, 'b' * 32, None, 'Fe-EELS', 'Fe')          # reference missing
    ok('velox_maps', dfs_si, [],
       axes=[{'name': 'rows', 'scale': 6.5e-11, 'units': 'm'},
             {'name': 'columns', 'scale': 6.5e-11, 'units': 'm'}],
       meta={'title': 'DF-S', 'spectrum_map': None, 'detector': 'DF-S', 'format': 'Velox'})
    EXPECT['velox_maps_eu'] = eu
    EXPECT['velox_maps_ref'] = ref

    with velox_file(os.path.join(HERE, 'velox_spectra_only.emd'))[0] as f:
        s = f['Data'].create_group('SpectrumImage').create_group('1' * 32)
        s.create_dataset('Data', data=rand('<u2', (4, 4, 256), 4))
    bad('velox_spectra_only', ['no 2-D image', 'SpectrumImage'])

    # Velox, real data (CC BY 4.0), when the source file is given
    real = os.path.join(HERE, 'velox_iliad_dfs.emd')
    if len(sys.argv) > 1:
        with h5py.File(sys.argv[1], 'r') as src, velox_file(real)[0] as f:
            def detector(u):
                text = src['Data/Image'][u]['Metadata'][:, 0].tobytes().split(b'\0', 1)[0]
                return json.loads(text)['BinaryResult'].get('Detector')
            uid = next(u for u in src['Data/Image'] if detector(u) == 'DF-S')
            g = src['Data/Image'][uid]
            dst = f['Data'].create_group('Image').create_group(uid)
            for k in ('Data', 'Metadata', 'FrameLookupTable'):
                dst.create_dataset(k, data=g[k][()])
            f.create_dataset('Thumbnail.jpg', data=src['Thumbnail.jpg'][()])
            f['Version'][0] = src['Version'][0]
    with h5py.File(real, 'r') as f:
        uid = list(f['Data/Image'])[0]
        dfs = np.moveaxis(f['Data/Image'][uid]['Data'][()], 2, 0)
    ok('velox_iliad_dfs', dfs, [],
       meta={'high_voltage_kV': 300.0, 'detector': 'DF-S', 'format': 'Velox'})

    # Berkeley EMD 1.0: a 4D-STEM datacube
    cube = rand('<f4', (3, 4, ROWS, COLS), 5)
    with h5py.File(os.path.join(HERE, 'emd1_datacube.emd'), 'w') as f:
        g = emd1_root(f).create_group('datacube')
        g.attrs['emd_group_type'] = 'array'
        d = g.create_dataset('data', data=cube)
        d.attrs['units'] = 'counts'
        dim(g, 1, np.arange(3) * 2.0, 'R_x', 'nm')
        dim(g, 2, np.arange(4) * 2.0, 'R_y', 'nm')
        dim(g, 3, np.array([-1.5, -1.5 + 0.0731]), 'Q_x', 'nm^-1')
        dim(g, 4, np.array([-2.0, -2.0 + 0.0731]), 'Q_y', 'nm^-1')
    ok('emd1_datacube', cube.reshape(-1, ROWS, COLS), [3, 4],
       axes=[{'name': 'Q_x', 'scale': 0.0731, 'offset': -1.5, 'units': 'nm^-1'},
             {'name': 'Q_y', 'scale': 0.0731, 'offset': -2.0, 'units': 'nm^-1'}],
       meta={'format': 'EMD 1.0'})

    # Berkeley EMD 1.0: a labelled stack of images, (rows, columns, images)
    stack = rand('<u2', (5, ROWS, COLS), 6)
    with h5py.File(os.path.join(HERE, 'emd1_stack.emd'), 'w') as f:
        g = emd1_root(f).create_group('stack')
        g.attrs['emd_group_type'] = 'array'
        g.create_dataset('data', data=np.moveaxis(stack, 0, 2))
        dim(g, 1, np.array([0.0, 0.5]), 'y', 'nm^-1')
        dim(g, 2, np.array([0.0, 0.5]), 'x', 'nm^-1')
        labels = g.create_dataset('dim3', data=[f'image {k}'.encode() for k in range(5)],
                                  dtype=h5py.string_dtype())
        labels.attrs['name'] = '_labels_'
    ok('emd1_stack', stack, [5],
       axes=[{'name': 'y', 'scale': 0.5, 'units': 'nm^-1'},
             {'name': 'x', 'scale': 0.5, 'units': 'nm^-1'}], meta={'format': 'EMD 1.0'})

    # Berkeley EMD 0.2: one image
    image = rand('<u2', (ROWS, COLS), 7)
    with h5py.File(os.path.join(HERE, 'emd02_image.emd'), 'w') as f:
        f.attrs['version_major'] = 0
        f.attrs['version_minor'] = 2
        g = f.create_group('data').create_group('pattern')
        g.attrs['emd_group_type'] = 1
        g.create_dataset('data', data=image)
        dim(g, 1, np.arange(ROWS) * 0.02, 'k_y', '[n_m^-1]')
        dim(g, 2, np.arange(COLS) * 0.02, 'k_x', '[n_m^-1]')
    ok('emd02_image', image[np.newaxis], [],
       axes=[{'name': 'k_y', 'scale': 0.02, 'units': 'nm^-1'},
             {'name': 'k_x', 'scale': 0.02, 'units': 'nm^-1'}], meta={'format': 'EMD 0.2'})

    # py4DSTEM 0.x layout: "datacube", emd_group_type "1"
    cube2 = rand('<f4', (2, 2, ROWS, COLS), 8)
    with h5py.File(os.path.join(HERE, 'py4dstem_datacube.emd'), 'w') as f:
        top = f.create_group('4DSTEM_experiment')
        top.attrs['emd_group_type'] = 2
        top.attrs['version_major'] = 0
        top.attrs['version_minor'] = 12
        g = top.create_group('data').create_group('datacubes').create_group('datacube_0')
        g.attrs['emd_group_type'] = '1'
        g.create_dataset('datacube', data=cube2)
        for k, (n, u) in enumerate((('R_x', '[n_m]'), ('R_y', '[n_m]'),
                                    ('Q_x', '[n_m^-1]'), ('Q_y', '[n_m^-1]')), start=1):
            dim(g, k, np.arange(cube2.shape[k - 1]) * 0.1, n, u)
    ok('py4dstem_datacube', cube2.reshape(-1, ROWS, COLS), [2, 2],
       axes=[{'name': 'Q_x', 'scale': 0.1, 'units': 'nm^-1'},
             {'name': 'Q_y', 'scale': 0.1, 'units': 'nm^-1'}])

    # refused
    with h5py.File(os.path.join(HERE, 'plain_hdf5.h5'), 'w') as f:
        f.create_dataset('values', data=np.arange(10))
    bad('plain_hdf5', ['neither a Velox nor a Berkeley EMD'])
    with h5py.File(os.path.join(HERE, 'emd1_spectrum.emd'), 'w') as f:
        g = emd1_root(f).create_group('spectrum')
        g.attrs['emd_group_type'] = 'array'
        g.create_dataset('data', data=rand('<f4', (2048,), 9))
        dim(g, 1, np.array([0.0, 0.01]), 'energy', 'keV')
    bad('emd1_spectrum', ['no 2-D image', 'spectrum'])

    np.savez_compressed(os.path.join(HERE, 'expected.npz'), **EXPECT)
    with open(os.path.join(HERE, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump({'h5py': h5py.__version__, 'files': MANIFEST}, f, indent=1, sort_keys=True)
    print(f'{len(MANIFEST)} files, h5py {h5py.__version__}')


if __name__ == '__main__':
    sys.exit(main())
