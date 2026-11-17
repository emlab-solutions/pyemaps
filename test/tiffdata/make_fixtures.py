'''
Write the TIFF test files in this folder, with tifffile, for run_expimage.py.

    pip install tifffile imagecodecs        # in a development environment only
    python make_fixtures.py

pyEMAPS doesn't use tifffile: its own reader (pyemaps/tiffreader.py) is checked against
files written by this independent, widely used writer. tifffile and imagecodecs are
BSD-licensed. The files are committed, so the tests don't need either package.

It writes:
- <name>.tif for each case, and expected.npz with the pixels each one must read as;
- manifest.json: each file's expected scan shape and data type, or for a file that must be
  refused, words the error message must contain.

The random data is fixed by the seed, and expected.npz records it, so the checks don't
depend on numpy's random number streams.
'''
import json
import os
import struct
import sys

import numpy as np
import tifffile

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS, COLS = 37, 41            # not square, and not a multiple of the 16-pixel tiles
EXPECT = {}
MANIFEST = {}


def data(kind, shape=(ROWS, COLS), seed=0):
    rng = np.random.default_rng(seed)
    dt = np.dtype(kind)
    if dt.kind == 'f':
        return (rng.standard_normal(shape) * 1000).astype(dt)
    info = np.iinfo(dt)
    native = dt.newbyteorder('=')
    return rng.integers(info.min, info.max, size=shape, endpoint=True, dtype=native).astype(dt)


def ok(name, arr, scan=None, **kw):
    '''A file the reader must read: *arr* is what tifffile writes, (pages, rows, cols) or 2-D.'''
    fn = os.path.join(HERE, f'{name}.tif')
    kw.setdefault('photometric', 'minisblack')    # never colour planes, whatever the shape
    tifffile.imwrite(fn, arr, **kw)
    stack = arr.reshape(-1, *arr.shape[-2:])
    EXPECT[name] = stack.astype(stack.dtype.newbyteorder('='))
    n = stack.shape[0]
    MANIFEST[name] = {'scan_shape': list(scan if scan is not None else ((n,) if n > 1 else ())),
                      'dtype': stack.dtype.newbyteorder('=').str,
                      'writer': 'tifffile ' + json.dumps({k: str(v) for k, v in kw.items()})}


def bad(name, words, write):
    '''A file the reader must refuse, with an error containing *words*.'''
    fn = os.path.join(HERE, f'{name}.tif')
    write(fn)
    MANIFEST[name] = {'error': words}


def main():
    # data types and byte orders, uncompressed, one strip
    for kind in ('u1', 'i1', 'u2', 'i2', 'u4', 'i4', 'u8', 'i8', 'f2', 'f4', 'f8'):
        ok(f'dtype_{kind}_le', data('<' + kind, seed=1))
        ok(f'dtype_{kind}_be', data('>' + kind, seed=2), byteorder='>')

    # strips of 5 rows (the last one shorter)
    ok('strips_i2', data('<i2', seed=3), rowsperstrip=5)
    ok('strips_f4_be', data('>f4', seed=4), rowsperstrip=5, byteorder='>')

    # compressions, with and without predictors
    ok('packbits_u1', data('u1', seed=5), compression='packbits')
    ok('packbits_i2', data('<i2', seed=6), compression='packbits', rowsperstrip=8)
    ok('lzw_u2', data('<u2', seed=7), compression='lzw')
    ok('lzw_u2_pred', data('<u2', seed=8), compression='lzw', predictor=True)
    ok('lzw_i4_pred_be', data('>i4', seed=9), compression='lzw', predictor=True, byteorder='>')
    ok('lzw_f4_fpred', data('<f4', seed=10), compression='lzw', predictor=3)
    ok('lzw_f4_fpred_be', data('>f4', seed=11), compression='lzw', predictor=3, byteorder='>')
    ok('deflate_i2', data('<i2', seed=12), compression='zlib')
    ok('deflate_i2_pred', data('<i2', seed=13), compression='zlib', predictor=True,
       rowsperstrip=6)
    ok('deflate_f8_fpred', data('<f8', seed=14), compression='zlib', predictor=3)
    ok('deflate_u2_pred_be', data('>u2', seed=15), compression='zlib', predictor=True,
       byteorder='>')
    # LZW over a larger image, so the codes grow to 12 bits and the table is cleared
    big = (np.add.outer(np.arange(300), np.arange(280)) % 251).astype(np.uint8)
    big[::7] = data('u1', shape=big[::7].shape, seed=16)
    ok('lzw_u1_large', big, compression='lzw')

    # tiles of 16 x 16 (partly outside the image at the right and bottom)
    ok('tiles_u2', data('<u2', seed=17), tile=(16, 16))
    ok('tiles_i2_deflate_pred', data('<i2', seed=18), tile=(16, 16), compression='zlib',
       predictor=True)
    ok('tiles_f4_lzw_fpred_be', data('>f4', seed=19), tile=(16, 16), compression='lzw',
       predictor=3, byteorder='>')

    # stacks
    ok('stack_i2', data('<i2', shape=(6, ROWS, COLS), seed=20))
    ok('stack_scan_2x3', data('<u2', shape=(2, 3, ROWS, COLS), seed=21), scan=(2, 3))
    ok('stack_scan_2x3_lzw', data('<f4', shape=(2, 3, ROWS, COLS), seed=22), scan=(2, 3),
       compression='lzw', predictor=3)
    ok('stack_imagej', data('<u2', shape=(5, ROWS, COLS), seed=23), imagej=True)
    ok('bigtiff_stack', data('<f4', shape=(3, ROWS, COLS), seed=24), bigtiff=True,
       compression='zlib', predictor=3)
    ok('bigtiff_be', data('>i2', shape=(2, ROWS, COLS), seed=25), bigtiff=True, byteorder='>')

    # a stack with a thumbnail after it, which isn't one of the patterns
    name = 'stack_thumbnail'
    main_pages = data('<u2', shape=(4, ROWS, COLS), seed=26)
    fn = os.path.join(HERE, f'{name}.tif')
    with tifffile.TiffWriter(fn) as w:
        w.write(main_pages, photometric='minisblack')
        w.write(data('<u2', shape=(9, 10), seed=27), subfiletype=1, photometric='minisblack')
    EXPECT[name] = main_pages
    MANIFEST[name] = {'scan_shape': [4], 'dtype': '<u2', 'writer': 'tifffile, thumbnail page'}

    # ImageJ's layout for stacks over 4 GB: one image directory, then the images back to back
    name = 'imagej_contiguous'
    pages = data('<i2', shape=(4, ROWS, COLS), seed=28)
    write_imagej_contiguous(os.path.join(HERE, f'{name}.tif'), pages)
    EXPECT[name] = pages
    MANIFEST[name] = {'scan_shape': [4], 'dtype': '<i2',
                      'writer': 'hand-written: ImageJ layout for stacks over 4 GB'}

    # files that must be refused
    rgb = data('u1', shape=(ROWS, COLS, 3), seed=30)
    bad('bad_rgb', ['RGB'], lambda fn: tifffile.imwrite(fn, rgb, photometric='rgb'))
    cmap = np.zeros((3, 256), dtype=np.uint16)
    bad('bad_palette', ['palette'],
        lambda fn: tifffile.imwrite(fn, data('u1', seed=31), photometric='palette',
                                    colormap=cmap))
    bits = data('u1', seed=32) > 128
    bad('bad_bilevel', ['black-and-white'], lambda fn: tifffile.imwrite(fn, bits))
    bad('bad_jpeg', ['JPEG'],
        lambda fn: tifffile.imwrite(fn, data('u1', seed=33), compression='jpeg'))
    bad('bad_zstd', ['Zstandard'],
        lambda fn: tifffile.imwrite(fn, data('<u2', seed=34), compression='zstd'))
    bad('bad_complex', ['sample format'],
        lambda fn: tifffile.imwrite(fn, (data('<f4', seed=35) + 1j).astype(np.complex64)))

    def mixed(fn):
        with tifffile.TiffWriter(fn) as w:
            w.write(data('<u2', seed=36), photometric='minisblack')
            w.write(data('<u2', shape=(ROWS + 1, COLS), seed=37), photometric='minisblack')
    bad('bad_mixed_sizes', ['same size'], mixed)

    # al.img (samples) as TIFF, for the 4D-STEM indexing check in run_stem4d.py
    al = np.fromfile(os.path.join(HERE, '..', '..', 'samples', 'al.img'), dtype='<f4',
                     offset=8).reshape(200, 200)
    ok('al', al)

    # a small 4D-STEM scan (6 x 5 positions of 120 x 128, a bright disk on noise, one darker
    # position) and a disk mask, for the bright field and masked image checks in run_stem4d.py
    yy, xx = np.mgrid[:120, :128]
    disk = (yy - 60) ** 2 + (xx - 64) ** 2 < 15 ** 2
    rng = np.random.default_rng(11)
    scan = (rng.random((6, 5, 120, 128)) * 200 + disk * 3000).astype(np.int16)
    scan[2, 3] //= 4
    ok('stem4d_scan', scan, scan=(6, 5), compression='zlib', predictor=True)
    ok('stem4d_mask', disk.astype(np.float32), compression='zlib', predictor=3)

    np.savez_compressed(os.path.join(HERE, 'expected.npz'), **EXPECT)
    with open(os.path.join(HERE, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump({'tifffile': tifffile.__version__, 'files': MANIFEST}, f, indent=1,
                  sort_keys=True)
    print(f'{len(MANIFEST)} files, tifffile {tifffile.__version__}')


def write_imagej_contiguous(fn, pages):
    '''
    A little-endian TIFF with one image directory whose ImageDescription says
    ``images=<n>``, followed by all n images, uncompressed and contiguous, as ImageJ writes
    stacks over 4 GB.
    '''
    n, rows, cols = pages.shape
    desc = f'ImageJ=1.54f\nimages={n}\nslices={n}\nloop=false\n'.encode('ascii') + b'\0'
    tags = [(256, 3, 1, cols), (257, 3, 1, rows), (258, 3, 1, 16), (259, 3, 1, 1),
            (262, 3, 1, 1), (270, 2, len(desc), None), (273, 4, 1, None), (277, 3, 1, 1),
            (278, 3, 1, rows), (279, 4, 1, rows * cols * 2), (339, 3, 1, 2)]
    ifd_off = 8
    ifd_size = 2 + 12 * len(tags) + 4
    desc_off = ifd_off + ifd_size
    data_off = desc_off + len(desc)
    data_off += (-data_off) % 16
    out = bytearray(struct.pack('<2sHI', b'II', 42, ifd_off))
    out += struct.pack('<H', len(tags))
    for tag, typ, cnt, val in tags:
        if tag == 270:
            val = desc_off
        elif tag == 273:
            val = data_off
        if typ == 3:
            out += struct.pack('<HHIHH', tag, typ, cnt, val, 0)
        else:
            out += struct.pack('<HHII', tag, typ, cnt, val)
    out += struct.pack('<I', 0)
    out += desc
    out += b'\0' * (data_off - len(out))
    out += pages.astype('<i2').tobytes()
    with open(fn, 'wb') as f:
        f.write(out)


if __name__ == '__main__':
    sys.exit(main())
