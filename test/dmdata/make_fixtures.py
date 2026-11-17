'''
Write the DigitalMicrograph test files in this folder for run_expimage.py.

    python make_fixtures.py [Al_irradiated.dm4]

No open software writes DM3/DM4 files, so this script has its own small writer, separate from
pyEMAPS' reader, following Chris Boothroyd's description of the formats
(https://personal.ntu.edu.sg/cbb/info/dmformat/) and the layout of real files: a big-endian tag
tree, values in the byte order the header gives, images in ImageList (image 0 a thumbnail),
each with ImageData (Calibrations, Data, DataType, Dimensions, PixelDepth) and ImageTags.

dm4_al_crop.dm4 keeps real data: a 2 x 2 part of the scan, cropped to the central 128 x 128
pixels, with the original ImageTags, from "Al_irradiated.dm4" in "Nanoscale mapping of point
defect concentrations with 4D-STEM", Zenodo record 7041997
(https://zenodo.org/records/7041997), CC BY 4.0
(https://creativecommons.org/licenses/by/4.0/). Changes: cropped as described. Give the path of
Al_irradiated.dm4 to rewrite it; without it, the existing file is kept.

It writes expected.npz (the patterns each file must read as, (patterns, rows, columns)) and
manifest.json (scan shape, calibration and settings, or error words).
'''
import json
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS, COLS = 37, 41
EXPECT, MANIFEST = {}, {}

# DM tag value types
T_SHORT, T_LONG, T_USHORT, T_ULONG, T_FLOAT, T_DOUBLE, T_BOOL = 2, 3, 4, 5, 6, 7, 8
T_OCTET, T_ARRAY = 10, 20
NUMPY_TYPE = {'int16': T_SHORT, 'int32': T_LONG, 'uint16': T_USHORT, 'uint32': T_ULONG,
              'float32': T_FLOAT, 'float64': T_DOUBLE, 'uint8': T_OCTET, 'int8': 9}
DATA_TYPE = {'int16': 1, 'float32': 2, 'uint8': 6, 'int32': 7, 'int8': 9, 'uint16': 10,
             'uint32': 11, 'float64': 12}


class Text(str):
    '''A string, written as DM writes text: an array of UTF-16 ushorts.'''


class Writer:
    def __init__(self, version, bo='<'):
        self.v, self.bo = version, bo
        self.n = '>Q' if version == 4 else '>I'

    def num(self, v):
        return struct.pack(self.n, v)

    def value(self, v):
        '''(info list, data bytes) for a tag value.'''
        if isinstance(v, bool):
            return [T_BOOL], struct.pack(self.bo + '?', v)
        if isinstance(v, int):
            return [T_LONG], struct.pack(self.bo + 'i', v)
        if isinstance(v, float):
            return [T_DOUBLE], struct.pack(self.bo + 'd', v)
        if isinstance(v, str):
            data = v.encode('utf-16-le' if self.bo == '<' else 'utf-16-be')
            return [T_ARRAY, T_USHORT, len(v)], data
        if isinstance(v, np.ndarray):
            t = NUMPY_TYPE[v.dtype.name]
            return [T_ARRAY, t, v.size], np.ascontiguousarray(v, v.dtype.newbyteorder(self.bo)).tobytes()
        raise TypeError(type(v))

    def tag(self, name, v):
        nm = (name or '').encode('latin-1')
        if isinstance(v, (dict, list)):
            body = self.group(v)
            head = bytes([20]) + struct.pack('>H', len(nm)) + nm
            return head + (self.num(len(body)) if self.v == 4 else b'') + body
        info, data = self.value(v)
        body = b'%%%%' + self.num(len(info)) + b''.join(self.num(i) for i in info) + data
        head = bytes([21]) + struct.pack('>H', len(nm)) + nm
        return head + (self.num(len(body)) if self.v == 4 else b'') + body

    def group(self, g):
        items = g.items() if isinstance(g, dict) else [(None, x) for x in g]
        items = list(items)
        return b'\0\1' + self.num(len(items)) + b''.join(self.tag(k, x) for k, x in items)

    def file(self, root):
        body = self.group(root) + b'\0' * 8
        if self.v == 4:
            head = struct.pack('>IQI', 4, len(body), 1 if self.bo == '<' else 0)
        else:
            head = struct.pack('>III', 3, len(body), 1 if self.bo == '<' else 0)
        return head + body


def image(data, dims_xfirst, name, units=None, scales=None, tags=None, data_type=None):
    n = len(dims_xfirst)
    units = units or [''] * n
    scales = scales or [1.0] * n
    return {
        'ImageData': {
            'Calibrations': {
                'Brightness': {'Origin': 0.0, 'Scale': 1.0, 'Units': Text('')},
                'Dimension': [{'Origin': 0.0, 'Scale': float(s), 'Units': Text(u)}
                              for s, u in zip(scales, units)],
                'DisplayCalibratedUnits': True},
            'Data': np.ascontiguousarray(data).ravel(),
            'DataType': data_type if data_type is not None else DATA_TYPE[data.dtype.name],
            'Dimensions': [int(d) for d in dims_xfirst],
            'PixelDepth': int(data.dtype.itemsize)},
        'ImageTags': tags or {},
        'Name': Text(name),
        'UniqueID': {'0': 1, '1': 2, '2': 3, '3': 4},
    }


def thumbnail():
    rgba = np.full((32, 32), 0x7F7F7FFF, dtype=np.uint32).view(np.int32)
    return image(rgba, (32, 32), 'thumbnail', data_type=23)


def write(name, version, images, bo='<'):
    root = {'ImageList': images,
            'Thumbnails': [{'ImageIndex': 0, 'SourceSize_Pixels': (512, 512)}]}
    root['Thumbnails'] = [{'ImageIndex': 0}]
    with open(os.path.join(HERE, name), 'wb') as f:
        f.write(Writer(version, bo).file(root))


def rand(dtype, shape, seed):
    rng = np.random.default_rng(seed)
    dt = np.dtype(dtype)
    if dt.kind == 'f':
        return (rng.standard_normal(shape) * 500).astype(dt)
    info = np.iinfo(dt)
    return rng.integers(info.min, info.max, size=shape, endpoint=True, dtype=dt)


def ok(name, stack, scan, axes=None, meta=None):
    EXPECT[name] = stack
    MANIFEST[name] = {'scan_shape': list(scan), 'axes': axes or [], 'meta': meta or {}}


def bad(name, words):
    MANIFEST[name] = {'error': words}


MICROSCOPE = {'Microscope Info': {'Voltage': 200000.0, 'STEM Camera Length': 160.0,
                                  'Microscope': Text('JEM-ARM200F'),
                                  'Imaging Mode': Text('DIFFRACTION')}}


def main():
    # single patterns: data types, DM3 and DM4, a big-endian DM3
    for k, (dt, ver) in enumerate((('int16', 3), ('float32', 4), ('uint8', 3), ('uint16', 4),
                                   ('int32', 4), ('float64', 3), ('int8', 4), ('uint32', 3))):
        name = f'single_{dt}.dm{ver}'
        p = rand(dt, (ROWS, COLS), k + 1)
        write(name, ver, [thumbnail(), image(p, (COLS, ROWS), 'pattern',
                                             units=['1/nm', '1/nm'], scales=[0.02, 0.02],
                                             tags=MICROSCOPE)])
        ok(name, p[np.newaxis], [],
           axes=[{'name': 'rows', 'scale': 0.02, 'units': '1/nm'},
                 {'name': 'columns', 'scale': 0.02, 'units': '1/nm'}],
           meta={'high_voltage_kV': 200.0, 'camera_length_mm': 160.0,
                 'microscope': 'JEM-ARM200F'})
    p = rand('float32', (ROWS, COLS), 20)
    write('single_bigendian.dm3', 3, [thumbnail(), image(p, (COLS, ROWS), 'pattern')], bo='>')
    ok('single_bigendian.dm3', p[np.newaxis], [])

    # a stack recorded as a 4D-STEM scan of 3 x 4 positions (Gatan's 4D STEM Tags)
    stack = rand('uint16', (12, ROWS, COLS), 21)
    tags = dict(MICROSCOPE, **{'4D STEM Tags': {'Scan shape X': 4.0, 'Scan shape Y': 3.0}})
    write('stack_4dstem.dm4', 4, [thumbnail(), image(stack, (COLS, ROWS, 12), 'scan',
                                                     units=['1/nm', '1/nm', ''], tags=tags)])
    ok('stack_4dstem.dm4', stack, [3, 4])

    # a plain stack (no scan tags), and an overview image next to it
    series = rand('int16', (5, ROWS, COLS), 22)
    overview = rand('float32', (64, 48), 23)
    write('stack_series.dm3', 3, [thumbnail(), image(overview, (48, 64), 'overview',
                                                     units=['nm', 'nm'], scales=[0.5, 0.5]),
                                  image(series, (COLS, ROWS, 5), 'series')])
    ok('stack_series.dm3', series, [5])
    EXPECT['stack_series.dm3:overview'] = overview[np.newaxis]

    # 4-D datacubes: pattern axes first (stored fastest), and pattern axes last
    cube = rand('float32', (3, 2, ROWS, COLS), 24)                 # (ry, rx, qy, qx)
    write('cube_qfirst.dm4', 4, [thumbnail(), image(cube, (COLS, ROWS, 2, 3), 'cube',
                                                    units=['1/nm', '1/nm', 'nm', 'nm'],
                                                    scales=[0.03, 0.03, 2.0, 2.0])])
    ok('cube_qfirst.dm4', cube.reshape(-1, ROWS, COLS), [3, 2],
       axes=[{'name': 'rows', 'scale': 0.03, 'units': '1/nm'},
             {'name': 'columns', 'scale': 0.03, 'units': '1/nm'}])
    cube2 = rand('int16', (3, 2, ROWS, COLS), 25)                  # patterns (ry, rx, qy, qx)
    stored = np.ascontiguousarray(cube2.transpose(2, 3, 0, 1))     # (qy, qx, ry, rx)
    write('cube_qlast.dm4', 4, [thumbnail(), image(stored, (2, 3, COLS, ROWS), 'cube',
                                                   units=['nm', 'nm', '1/nm', '1/nm'])])
    ok('cube_qlast.dm4', cube2.reshape(-1, ROWS, COLS), [3, 2])

    # files to refuse
    spec = rand('float32', (4, 3, 256), 26)
    write('bad_spectrum_image.dm4', 4, [thumbnail(), image(spec, (256, 3, 4), 'SI',
                                                           units=['eV', 'nm', 'nm'])])
    bad('bad_spectrum_image.dm4', ['no 2-D image', 'spectrum image'])
    rgb = rand('int32', (ROWS, COLS), 27)
    write('bad_rgb.dm3', 3, [thumbnail(), image(rgb, (COLS, ROWS), 'colour', data_type=8)])
    bad('bad_rgb.dm3', ['no 2-D image', 'RGB'])

    # real data (CC BY 4.0), when the source file is given
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'dmreader', os.path.join(HERE, '..', '..', 'dmreader.py'))
    dmreader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dmreader)
    real = os.path.join(HERE, 'dm4_al_crop.dm4')
    if len(sys.argv) > 1:
        with dmreader.DMFile(sys.argv[1]) as f:
            d = f.tags['ImageList'][1]
            w, h, n = d['ImageData']['Dimensions']
            idx = [r * 40 + c for r in (20, 21) for c in (20, 21)]
            pats = np.stack([f.array(d['ImageData']['Data'], i * w * h, w * h).reshape(h, w)
                             for i in idx])[:, 192:320, 192:320].astype(np.uint16)
            tags = d['ImageTags']
            keep = {k: tags[k] for k in ('Microscope Info',) if k in tags}
            keep['4D STEM Tags'] = {'Scan shape X': 2.0, 'Scan shape Y': 2.0}

            def clean(v):
                if isinstance(v, dict):
                    return {k: clean(x) for k, x in v.items()
                            if not type(x).__name__ == '_Array'}
                if isinstance(v, list):
                    return [clean(x) for x in v]
                if type(v).__name__ == '_Text':
                    return Text(str(v))
                if isinstance(v, tuple):
                    return [clean(x) for x in v]
                return v
            cal = d['ImageData']['Calibrations']['Dimension']
            img = image(pats, (128, 128, 4), str(d.get('Name')),
                        units=[str(c['Units']) for c in cal],
                        scales=[float(c['Scale']) for c in cal], tags=clean(keep))
        write('dm4_al_crop.dm4', 4, [thumbnail(), img])
    with dmreader.DMFile(real) as f:
        ds = f.choose()
        pats = ds.read(range(ds.npatterns))
    ok('dm4_al_crop.dm4', pats, [2, 2],
       axes=[{'name': 'rows', 'scale': 0.05839194729924202, 'units': '1/nm'}],
       meta={'high_voltage_kV': 300.0, 'camera_length_mm': 195.0, 'microscope': 'TitanX'})

    np.savez_compressed(os.path.join(HERE, 'expected.npz'), **EXPECT)
    with open(os.path.join(HERE, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump({'files': MANIFEST}, f, indent=1, sort_keys=True)
    print(f'{len(MANIFEST)} files')


if __name__ == '__main__':
    sys.exit(main())
