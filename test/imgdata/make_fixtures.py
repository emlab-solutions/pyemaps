'''
Write the MRC, Merlin, picture and NumPy test files in this folder, for run_expimage.py.

    pip install mrcfile pillow        # in a development environment
    python make_fixtures.py [quad4.mib]

- MRC files are written by mrcfile (BSD), the CCP-EM reference library for the MRC2014 format.
  pyEMAPS doesn't use it; its reader (pyemaps/mrcreader.py) is checked against these files.
- Merlin files: no open software writes .mib files, so this script writes them following the
  frame header described in Diamond Light Source's mib_props (MIT,
  https://github.com/ePSIC-DLS/mib_props), with big-endian pixels as real files have.
  mib_quad_real.mib keeps real data: the first 4 frames of "MerlinEM quad 4D-STEM dataset" by
  Mohsen Danaie, Zenodo record 10813049 (https://zenodo.org/records/10813049), CC BY 4.0
  (https://creativecommons.org/licenses/by/4.0/), cropped to the central 128 x 128 pixels
  (header sizes changed to match). Give the path of a file with those 4 frames to rewrite it.
- Pictures are written by Pillow; NumPy files by numpy.

It writes expected.npz (the patterns each file must read as, (patterns, rows, columns)) and
manifest.json (scan shape, calibration and metadata, or error words).
'''
import json
import os
import struct
import sys

import mrcfile
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS, COLS = 37, 41
EXPECT, MANIFEST = {}, {}


def rand(dtype, shape, seed, top=None):
    rng = np.random.default_rng(seed)
    dt = np.dtype(dtype)
    if dt.kind == 'f':
        return (rng.standard_normal(shape) * 500).astype(dt)
    info = np.iinfo(dt)
    return rng.integers(info.min, top or info.max, size=shape, endpoint=True, dtype=dt)


def ok(name, stack, scan, axes=None, meta=None):
    EXPECT[name] = stack
    MANIFEST[name] = {'scan_shape': list(scan), 'axes': axes or [], 'meta': meta or {}}


def bad(name, words):
    MANIFEST[name] = {'error': words}


def path(name):
    return os.path.join(HERE, name)


# ------------------------------------------------------------------ MRC

def mrc(name, data, voxel=None, byteorder=None, ispg=None, ext=None):
    with mrcfile.new(path(name), overwrite=True) as m:
        m.set_data(data)
        if voxel:
            m.voxel_size = voxel
        if ispg is not None:
            m.header.ispg = ispg
        if ext is not None:
            m.set_extended_header(ext)
            m.header.exttyp = b'SERI'
    if byteorder == '>':                     # rewrite in big-endian, as mrcfile does on request
        with mrcfile.open(path(name), mode='r+') as m:
            pass
        with mrcfile.mmap(path(name), mode='r') as m:
            hdr, arr = m.header.copy(), np.array(m.data)
        with mrcfile.new(path(name), overwrite=True) as m:
            m.set_data(arr.astype(arr.dtype.newbyteorder('>')))
            if voxel:
                m.voxel_size = voxel


def make_mrc():
    for k, dt in enumerate(('int8', 'int16', 'float32', 'uint16', 'float16')):
        stack = rand(dt, (3, ROWS, COLS), k + 1)
        mrc(f'mrc_{dt}.mrc', stack, voxel=(1.5, 1.5, 1.5))
        ok(f'mrc_{dt}.mrc', stack, [3],
           axes=[{'name': 'rows', 'scale': 1.5, 'units': 'Å'},
                 {'name': 'columns', 'scale': 1.5, 'units': 'Å'}],
           meta={'mode': {'int8': 0, 'int16': 1, 'float32': 2, 'uint16': 6, 'float16': 12}[dt]})
    single = rand('float32', (ROWS, COLS), 6)
    mrc('mrc_single.mrc', single)
    ok('mrc_single.mrc', single[np.newaxis], [])
    big = rand('int16', (2, ROWS, COLS), 7)
    mrc('mrc_bigendian.mrc', big, byteorder='>')
    ok('mrc_bigendian.mrc', big, [2])
    ext = np.frombuffer(b'serialem tilt angles' + b'\0' * 1004, dtype='V1024')
    tilt = rand('int16', (4, ROWS, COLS), 8)
    mrc('mrc_extheader.mrcs', tilt, ext=ext)
    ok('mrc_extheader.mrcs', tilt, [4], meta={'extended_header_bytes': 1024})
    vol = rand('float32', (2, ROWS, COLS), 9)
    mrc('mrc_volume.mrc', vol, ispg=1)
    ok('mrc_volume.mrc', vol, [2], meta={'volume': True})
    mrc('bad_mrc_complex.mrc', (rand('float32', (ROWS, COLS), 10) + 1j).astype(np.complex64))
    bad('bad_mrc_complex.mrc', ['complex'])


# ------------------------------------------------------------------ Merlin

def mib_header(n, cols, rows, kind, chips=1, layout='   1x1', length=384):
    fields = ['MQ1', f'{n:06d}', f'{length:05d}', f'{chips:02d}', f'{cols:04d}', f'{rows:04d}',
              kind, layout, '01', '2026-11-18 10:00:00.000000', '0.001000', '0', '0', '0',
              '4.000000E+1', '5.110000E+2'] + ['0.000000E+0'] * 6
    text = ','.join(fields).encode('ascii')
    return text + b'\0' * (length - len(text))


def mib(name, frames, kind, **kw):
    dt = {'U08': '>u1', 'U16': '>u2', 'U32': '>u4', 'R64': '>u8'}[kind]
    n, rows, cols = frames.shape
    with open(path(name), 'wb') as f:
        for k in range(n):
            f.write(mib_header(k + 1, cols, rows, kind, **kw))
            f.write(frames[k].astype(dt).tobytes())


def make_mib(real_source):
    for k, (kind, top) in enumerate((('U08', 255), ('U16', 4095), ('U32', 100000))):
        dt = {'U08': 'uint8', 'U16': 'uint16', 'U32': 'uint32'}[kind]
        frames = rand(dt, (6, ROWS, COLS), 20 + k, top=top)
        mib(f'mib_{kind.lower()}.mib', frames, kind)
        ok(f'mib_{kind.lower()}.mib', frames, [6], meta={'pixel_type': kind})
    quad = rand('uint16', (2, 64, 64), 23, top=4095)
    mib('mib_quad.mib', quad, 'U16', chips=4, layout='   2x2', length=768)
    ok('mib_quad.mib', quad, [2], meta={'pixel_type': 'U16', 'chips': 4})
    with open(path('mib_quad.hdr'), 'w', newline='\r\n') as f:
        f.write('HDR,\t\nCounter Depth (number):\t12\nFrames in Acquisition (Number):\t2\nEnd\t\n')
    mib('bad_mib_raw.mib', rand('uint16', (2, 16, 16), 24).astype(np.uint64), 'R64')
    bad('bad_mib_raw.mib', ['raw (R64)'])

    real = path('mib_quad_real.mib')
    if real_source:
        raw = open(real_source, 'rb').read()
        fb = 768 + 512 * 512 * 2
        frames = np.stack([np.frombuffer(raw[k * fb + 768:(k + 1) * fb], '>u2').reshape(512, 512)
                           for k in range(4)])[:, 192:320, 192:320]
        with open(real, 'wb') as f:
            for k in range(4):
                head = raw[k * fb:k * fb + 768].decode('latin-1').split(',')
                head[4], head[5] = '0128', '0128'
                text = ','.join(head).encode('latin-1')[:768]
                f.write(text + b'\0' * (768 - len(text)))
                f.write(frames[k].astype('>u2').tobytes())
    fb = 768 + 128 * 128 * 2
    raw = open(real, 'rb').read()
    frames = np.stack([np.frombuffer(raw[k * fb + 768:(k + 1) * fb], '>u2').reshape(128, 128)
                       for k in range(4)])
    ok('mib_quad_real.mib', frames.astype(np.uint16), [4], meta={'pixel_type': 'U16'})


# ------------------------------------------------------------------ pictures and NumPy

def make_pictures():
    g8 = rand('uint8', (ROWS, COLS), 30)
    Image.fromarray(g8).save(path('pic_gray8.png'))
    ok('pic_gray8.png', g8[np.newaxis], [], meta={'format': 'PNG', 'lossy': False})
    g16 = rand('uint16', (ROWS, COLS), 31)
    Image.fromarray(g16).save(path('pic_gray16.png'))
    ok('pic_gray16.png', g16[np.newaxis], [], meta={'format': 'PNG'})
    Image.fromarray(g8).save(path('pic_gray8.bmp'))
    ok('pic_gray8.bmp', g8[np.newaxis], [], meta={'format': 'BMP'})
    Image.fromarray(g8).save(path('pic_gray8.jpg'), quality=95)
    with Image.open(path('pic_gray8.jpg')) as im:
        decoded = np.array(im)                     # JPEG is lossy: what Pillow decodes
    ok('pic_gray8.jpg', decoded[np.newaxis], [], meta={'format': 'JPEG', 'lossy': True})
    rgb = np.repeat(g8[..., np.newaxis], 3, axis=2)
    Image.fromarray(rgb).save(path('pic_gray_as_rgb.png'))
    ok('pic_gray_as_rgb.png', g8[np.newaxis], [])
    pal = Image.fromarray(g8 // 16 * 16).convert('P', palette=Image.Palette.ADAPTIVE, colors=16)
    pal.save(path('pic_gray_palette.png'))
    with Image.open(path('pic_gray_palette.png')) as im:
        pal_gray = np.array(im.convert('RGB'))[..., 0]
    ok('pic_gray_palette.png', pal_gray[np.newaxis], [])

    colour = rand('uint8', (ROWS, COLS, 3), 32)
    Image.fromarray(colour).save(path('bad_pic_colour.png'))
    bad('bad_pic_colour.png', ['colour picture'])
    Image.fromarray(g8 > 128).save(path('bad_pic_bilevel.png'))
    bad('bad_pic_bilevel.png', ['black-and-white'])

    for name, arr, scan in (('npy_single.npy', rand('float64', (ROWS, COLS), 33), []),
                            ('npy_series.npy', rand('int16', (5, ROWS, COLS), 34), [5]),
                            ('npy_scan.npy', rand('uint16', (2, 3, ROWS, COLS), 35), [2, 3])):
        np.save(path(name), arr)
        ok(name, arr.reshape(-1, ROWS, COLS), scan, meta={'format': 'NumPy'})
    np.save(path('bad_npy_1d.npy'), np.arange(10.0))
    bad('bad_npy_1d.npy', ['1-D array'])


def main():
    make_mrc()
    make_mib(sys.argv[1] if len(sys.argv) > 1 else None)
    make_pictures()
    np.savez_compressed(path('expected.npz'), **EXPECT)
    with open(path('manifest.json'), 'w', encoding='utf-8') as f:
        json.dump({'mrcfile': mrcfile.__version__, 'files': MANIFEST}, f, indent=1,
                  sort_keys=True, ensure_ascii=False)
    print(f'{len(MANIFEST)} files')


if __name__ == '__main__':
    sys.exit(main())
