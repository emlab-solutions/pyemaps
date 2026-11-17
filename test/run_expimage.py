'''
Checks for reading experimental images from files (pyemaps.expimage, pyemaps.tiffreader,
StackImage.from_file).

    python run_expimage.py        # any arguments (such as ci_sanity's "-bc all") are ignored

Needs no license, so it runs in CI. The EMD checks need h5py (pip install "pyemaps[emd]");
without it they're skipped and reported. Exits 1 if any check fails.

What it checks:
- Every TIFF in tiffdata/ that tifffile wrote (see tiffdata/make_fixtures.py) reads exactly
  as written, with the right scan shape: all data types and byte orders, strips and tiles,
  PackBits, LZW and Deflate with and without predictors, stacks, ImageJ and BigTIFF files,
  ImageJ's layout for stacks over 4 GB, and a stack with a thumbnail. Both the raw reader
  (pyemaps.tiffreader, in the file's data type) and read_image (int16 or float32).
- Files to refuse (RGB, palette, 1-bit, JPEG, Zstandard, complex, mixed sizes), a truncated
  file and a file that isn't a TIFF: each a ValueError that says what's wrong.
- pyEMAPS' small-header files (.im3, .img) and samples/al.img read back exactly.
- binning, scan_roi (only those pages are read), scan_shape, and the files are closed after
  reading.
- DigitalMicrograph files in dmdata/ (see dmdata/make_fixtures.py): DM3 and DM4, 8 data
  types, big-endian, stacks with Gatan's 4D-STEM scan tags, datacubes with the pattern axes
  first or last, a crop of a real 4D-STEM file (CC BY 4.0) with its microscope settings;
  thumbnails skipped; spectrum images, RGB, truncated and fake files refused; image choice,
  scan_roi and closed files.
- MRC, Merlin (.mib), picture (PNG, BMP, JPEG) and NumPy files in imgdata/ (see
  imgdata/make_fixtures.py): MRC written by mrcfile (5 modes, big-endian, extended header,
  volume), Merlin single and quad frames in 3 pixel types plus real frames (CC BY 4.0),
  grayscale pictures (8/16-bit, RGB with equal channels, gray palette), 2-D/3-D/4-D arrays;
  complex MRC, raw Merlin, colour and 1-bit pictures and 1-D arrays refused; truncated files;
  Merlin scan_shape, .hdr settings, scan_roi and closed files.
- EMD files in emddata/ (see emddata/make_fixtures.py): Velox series with their settings, a
  real Velox image (CC BY 4.0) whose orientation matches Velox's thumbnail, Berkeley EMD 1.0
  and 0.2, py4DSTEM datacubes with calibration; dataset choice, scan_roi, binning, refused
  files, closed files, and the message when h5py is missing.
- StackImage.from_file and convertImage(E_FILE), on full builds: single patterns, stacks
  through a temporary .im3 (byte-exact, removed afterwards), the scan width, and the size
  checks that ask for binning or scan_roi.
'''
import gc
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE / 'tiffdata'
MANIFEST = json.loads((DATA / 'manifest.json').read_text(encoding='utf-8'))['files']
EXPECTED = np.load(DATA / 'expected.npz')

RESULTS = []


def check(name):
    def wrap(fn):
        def run(*args):
            try:
                out = fn(*args)
                ok, msg = True, out or ''
            except AssertionError as e:
                ok, msg = False, str(e) or 'assertion failed'
            except Exception as e:
                ok, msg = False, f'{type(e).__name__}: {e}'
            RESULTS.append((name, ok, msg))
        return run
    return wrap


def raises(exc, fn, *words):
    try:
        fn()
    except exc as e:
        text = str(e)
        missing = [w for w in words if w not in text]
        assert not missing, f'{exc.__name__} raised, but the message lacks {missing}: {text}'
        return text
    raise AssertionError(f'{exc.__name__} not raised')


def as_read_image(a):
    '''What read_image returns for these pixels: int16 where they fit, else float32.'''
    if a.dtype.kind == 'f':
        return a.astype(np.float32)
    if a.dtype == np.int16 or (a.min() >= -32768 and a.max() <= 32767):
        return a.astype(np.int16)
    return a.astype(np.float32)


# ------------------------------------------------------------------ TIFF files

GOOD = sorted(n for n, m in MANIFEST.items() if 'error' not in m)
BAD = sorted(n for n, m in MANIFEST.items() if 'error' in m)


@check(f'{len(GOOD)} TIFF files written by tifffile read exactly (raw reader and read_image)')
def c_good():
    from pyemaps import read_image
    from pyemaps.tiffreader import TiffFile
    problems = []
    for name in GOOD:
        m, want = MANIFEST[name], EXPECTED[name]
        fn = DATA / f'{name}.tif'
        try:
            with TiffFile(fn) as t:
                raw, scan = t.read(), t.scan_shape
            if raw.dtype != want.dtype or raw.shape != want.shape or not np.array_equal(raw, want):
                problems.append(f'{name}: raw {raw.dtype}{raw.shape} differs')
            if list(scan) != m['scan_shape']:
                problems.append(f'{name}: scan {scan}, expected {m["scan_shape"]}')
            img = read_image(fn)
            conv = as_read_image(want)
            if img.data.dtype != conv.dtype or not np.array_equal(img.data, conv):
                problems.append(f'{name}: read_image {img.data.dtype} differs')
            if list(img.scan_shape) != m['scan_shape'] or img.reader != 'TIFF':
                problems.append(f'{name}: read_image scan {img.scan_shape}, reader {img.reader}')
        except Exception as e:
            problems.append(f'{name}: {type(e).__name__}: {e}')
    assert not problems, '; '.join(problems)
    kinds = sorted({str(EXPECTED[n].dtype) for n in GOOD})
    return f'dtypes {", ".join(kinds)}'


@check(f'{len(BAD)} TIFF files that must be refused raise ValueError saying why')
def c_bad():
    from pyemaps import read_image
    msgs, problems = [], []
    for name in BAD:
        words = MANIFEST[name]['error']
        try:
            read_image(DATA / f'{name}.tif')
            problems.append(f'{name}: not refused')
        except ValueError as e:
            if not all(w in str(e) for w in words):
                problems.append(f'{name}: message lacks {words}: {e}')
            msgs.append(f'{name}: {str(e).replace(str(DATA / name), "").lstrip(".:, ")[:60]}')
        except Exception as e:
            problems.append(f'{name}: {type(e).__name__}: {e}')
    assert not problems, '; '.join(problems)
    return ' | '.join(msgs)


@check('a truncated TIFF and a non-TIFF .tif raise ValueError')
def c_truncated(tmp):
    from pyemaps import read_image
    src = (DATA / 'stack_i2.tif').read_bytes()
    cut = os.path.join(tmp, 'cut.tif')
    Path(cut).write_bytes(src[:len(src) // 2])
    msg = raises(ValueError, lambda: read_image(cut), 'truncated')
    fake = os.path.join(tmp, 'fake.tif')
    Path(fake).write_bytes(b'this is not a TIFF file at all')
    raises(ValueError, lambda: read_image(fake), 'not a TIFF')
    return msg


@check('ImageJ and tifffile metadata are reported')
def c_metadata():
    from pyemaps import read_image
    ij = read_image(DATA / 'stack_imagej.tif').metadata
    assert ij.get('imagej', {}).get('images') == 5, ij
    sh = read_image(DATA / 'stack_scan_2x3.tif').metadata
    assert sh.get('shaped', {}).get('shape') == [2, 3, 37, 41], sh
    lzw = read_image(DATA / 'lzw_u2.tif').metadata
    assert lzw.get('compression') == 'LZW', lzw
    return f'imagej images=5, shaped {sh["shaped"]["shape"]}, {lzw["compression"]}'


# ------------------------------------------------------------------ options

@check('binning averages blocks, drops the remainder and scales the axes')
def c_binning():
    from pyemaps import read_image
    want = EXPECTED['stack_i2'].astype(np.float64)                 # 6 x 37 x 41
    img = read_image(DATA / 'stack_i2.tif', binning=4)
    ref = want[:, :36, :40].reshape(6, 9, 4, 10, 4).mean(axis=(2, 4)).astype(np.float32)
    assert img.data.shape == (6, 9, 10) and np.array_equal(img.data, ref), img.data.shape
    assert img.data.dtype == np.float32 and img.axes[0]['scale'] == 4.0, img.axes
    return f'{img.data.shape}, scale {img.axes[0]["scale"]}'


@check('scan_roi reads part of a 2-D scan and of a series; scan_shape sets the scan')
def c_roi():
    from pyemaps import read_image
    scan = EXPECTED['stack_scan_2x3']                           # 2 x 3 scan, row by row
    img = read_image(DATA / 'stack_scan_2x3.tif', scan_roi=(0, 1, 2, 2))
    assert img.scan_shape == (2, 2) and np.array_equal(img.data, scan[[1, 2, 4, 5]]), img
    series = EXPECTED['stack_i2']
    img = read_image(DATA / 'stack_i2.tif', scan_roi=(2, 3))
    assert img.scan_shape == (3,) and np.array_equal(img.data, series[2:5])
    img = read_image(DATA / 'stack_i2.tif', scan_shape=(2, 3), scan_roi=(1, 0, 1, 3))
    assert img.scan_shape == (1, 3) and np.array_equal(img.data, series[3:6])
    raises(ValueError, lambda: read_image(DATA / 'stack_i2.tif', scan_shape=(4, 4)), '16 patterns')
    raises(ValueError, lambda: read_image(DATA / 'stack_i2.tif', scan_roi=(0, 0, 1, 1)),
           'scan_roi=(first, count)')
    raises(ValueError, lambda: read_image(DATA / 'dtype_u2_le.tif', scan_roi=(0, 1)),
           'single pattern')
    return 'scan (2, 2) from (2, 3); series (3,); scan_shape (2, 3)'


@check('errors: missing file, unknown format or reader, bad binning')
def c_errors(tmp):
    from pyemaps import read_image
    raises(FileNotFoundError, lambda: read_image(os.path.join(tmp, 'nothere.tif')), 'not found')
    txt = os.path.join(tmp, 'notes.txt')
    Path(txt).write_text('hello')
    raises(ValueError, lambda: read_image(txt), 'TIFF')
    raises(ValueError, lambda: read_image(DATA / 'al.tif', reader='DM4'), 'Unknown reader')
    raises(ValueError, lambda: read_image(DATA / 'al.tif', binning=0), 'binning')
    raises(ValueError, lambda: read_image(DATA / 'al.tif', binning=1.5), 'binning')
    renamed = os.path.join(tmp, 'al_tiff.dat')
    shutil.copy(DATA / 'al.tif', renamed)
    assert read_image(renamed).reader == 'TIFF', 'a TIFF with another extension'
    assert read_image(renamed, reader='tiff').pattern_shape == (200, 200)


@check('files are closed after reading (can be deleted on Windows)')
def c_closed(tmp):
    from pyemaps import read_image, write_im3
    for name in ('stack_scan_2x3_lzw', 'imagej_contiguous', 'bigtiff_stack'):
        fn = os.path.join(tmp, f'{name}.tif')
        shutil.copy(DATA / f'{name}.tif', fn)
        img = read_image(fn, scan_roi=(0, 1) if name != 'stack_scan_2x3_lzw' else None)
        os.remove(fn)
    im3 = os.path.join(tmp, 'closed.im3')
    write_im3(im3, EXPECTED['stack_i2'])
    img = read_image(im3, scan_roi=(1, 2))
    os.remove(im3)
    assert img.npatterns == 2


# ------------------------------------------------------------------ small-header files

@check('small-header stack (.im3) and single image (.img) read back exactly')
def c_im3(tmp):
    from pyemaps import read_image, write_im3
    src = EXPECTED['stack_i2']
    fn = os.path.join(tmp, 'stack.im3')
    write_im3(fn, src)
    img = read_image(fn)
    assert img.reader == 'pyEMAPS' and img.scan_shape == (6,), (img.reader, img.scan_shape)
    assert img.data.dtype == np.int16 and np.array_equal(img.data, src)
    single = EXPECTED['dtype_f4_le'][0]                      # stored as one page
    fn = os.path.join(tmp, 'single.img')
    write_im3(fn, single)
    img = read_image(fn)
    assert img.scan_shape == () and img.npatterns == 1 and np.array_equal(img.data[0], single)


@check('samples/al.img reads as the backend file layout, and like al.tif')
def c_alimg():
    from pyemaps import read_image
    al = HERE.parent / 'samples' / 'al.img'
    img = read_image(al)
    ref = np.fromfile(al, dtype='<f4', offset=8).reshape(200, 200)
    assert img.pattern_shape == (200, 200) and np.array_equal(img.data[0], ref)
    assert np.array_equal(read_image(DATA / 'al.tif').data[0], ref), 'al.tif differs from al.img'


@check('image_readers lists TIFF, DM, EMD, MRC, MIB, PICTURE, NPY and pyEMAPS')
def c_readers():
    from pyemaps import image_readers
    names = dict(image_readers())
    assert set(names) == {'TIFF', 'DM', 'EMD', 'MRC', 'MIB', 'PICTURE', 'NPY', 'pyEMAPS'}, names
    assert names['MRC'] == ['mrc', 'mrcs', 'st'] and names['MIB'] == ['mib'], names
    return str(names)


# ------------------------------------------------------------------ DigitalMicrograph files

DM = HERE / 'dmdata'
DM_MANIFEST = json.loads((DM / 'manifest.json').read_text(encoding='utf-8'))['files']
DM_EXPECTED = np.load(DM / 'expected.npz')
DM_GOOD = sorted(n for n, m in DM_MANIFEST.items() if 'error' not in m)
DM_BAD = sorted(n for n, m in DM_MANIFEST.items() if 'error' in m)


@check(f'{len(DM_GOOD)} DigitalMicrograph files (DM3, DM4) read exactly, with scan shape, '
       'calibration and settings')
def c_dm_good():
    from pyemaps import read_image
    problems, notes = [], []
    for name in DM_GOOD:
        m, want = DM_MANIFEST[name], DM_EXPECTED[name]
        try:
            img = read_image(DM / name)
            conv = as_read_image(want)
            if img.data.dtype != conv.dtype or not np.array_equal(img.data, conv):
                problems.append(f'{name}: pixels differ ({img.data.shape} {img.data.dtype})')
            if list(img.scan_shape) != m['scan_shape'] or img.reader != 'DM':
                problems.append(f'{name}: scan {img.scan_shape}, reader {img.reader}')
            for k, ax in enumerate(m['axes']):
                for key, v in ax.items():
                    got = img.axes[k][key]
                    same = np.isclose(got, v, rtol=1e-6) if isinstance(v, float) else got == v
                    if not same:
                        problems.append(f'{name}: axis {k} {key} {got!r}, expected {v!r}')
            for key, v in m['meta'].items():
                got = img.metadata.get(key)
                same = np.isclose(got, v) if isinstance(v, float) and got is not None else got == v
                if not same:
                    problems.append(f'{name}: metadata {key} {got!r}, expected {v!r}')
            notes.append(f'{name} {img.scan_shape}')
        except Exception as e:
            problems.append(f'{name}: {type(e).__name__}: {e}')
    assert not problems, '; '.join(problems)
    return ', '.join(notes[-4:])


@check(f'{len(DM_BAD)} DigitalMicrograph files with no grayscale image, a truncated one and a '
       'fake .dm4 raise ValueError saying why')
def c_dm_bad(tmp):
    from pyemaps import read_image
    problems = []
    for name in DM_BAD:
        words = DM_MANIFEST[name]['error']
        try:
            read_image(DM / name)
            problems.append(f'{name}: not refused')
        except ValueError as e:
            if not all(w in str(e) for w in words):
                problems.append(f'{name}: message lacks {words}: {e}')
    src = (DM / 'stack_4dstem.dm4').read_bytes()
    cut = os.path.join(tmp, 'cut.dm4')
    Path(cut).write_bytes(src[:len(src) // 3])
    try:
        read_image(cut)
        problems.append('truncated: not refused')
    except ValueError as e:
        if 'truncated' not in str(e):
            problems.append(f'truncated: {e}')
    fake = os.path.join(tmp, 'fake.dm4')
    Path(fake).write_bytes(b'not a DigitalMicrograph file')
    raises(ValueError, lambda: read_image(fake), 'not a DigitalMicrograph file')
    assert not problems, '; '.join(problems)


@check('DigitalMicrograph options: image choice, scan_roi on a stack and a datacube, closed files')
def c_dm_options(tmp):
    from pyemaps import read_image
    fn = DM / 'stack_series.dm3'
    assert read_image(fn).npatterns == 5, 'default: the series, not the overview'
    ov = read_image(fn, dataset='overview')
    assert np.array_equal(ov.data, as_read_image(DM_EXPECTED['stack_series.dm3:overview']))
    assert ov.axes[0]['units'] == 'nm' and ov.axes[0]['scale'] == 0.5, ov.axes
    raises(ValueError, lambda: read_image(fn, dataset='nothere'), 'No image')
    stack = DM_EXPECTED['stack_4dstem.dm4']                      # 3 x 4 scan, row by row
    img = read_image(DM / 'stack_4dstem.dm4', scan_roi=(1, 2, 2, 2))
    assert img.scan_shape == (2, 2) and np.array_equal(img.data, as_read_image(stack[[6, 7, 10, 11]]))
    cube = DM_EXPECTED['cube_qlast.dm4']                         # 3 x 2 scan
    img = read_image(DM / 'cube_qlast.dm4', scan_roi=(1, 0, 2, 1))
    assert img.scan_shape == (2, 1) and np.array_equal(img.data, cube[[2, 4]])
    copy = os.path.join(tmp, 'closed.dm4')
    shutil.copy(DM / 'stack_4dstem.dm4', copy)
    read_image(copy, scan_roi=(0, 0, 1, 2))
    os.remove(copy)
    return 'overview by name; scan_roi (2, 2) from (3, 4); datacube with pattern axes last'


# ------------------------------------------------------------------ MRC, Merlin, pictures, NumPy

IMG = HERE / 'imgdata'
IMG_MANIFEST = json.loads((IMG / 'manifest.json').read_text(encoding='utf-8'))['files']
IMG_EXPECTED = np.load(IMG / 'expected.npz')
IMG_GOOD = sorted(n for n, m in IMG_MANIFEST.items() if 'error' not in m)
IMG_BAD = sorted(n for n, m in IMG_MANIFEST.items() if 'error' in m)
IMG_READER = {'.mrc': 'MRC', '.mrcs': 'MRC', '.mib': 'MIB', '.png': 'PICTURE', '.bmp': 'PICTURE',
              '.jpg': 'PICTURE', '.npy': 'NPY'}


@check(f'{len(IMG_GOOD)} MRC, Merlin, picture and NumPy files read exactly, with scan shape, '
       'calibration and metadata')
def c_img_good():
    from pyemaps import read_image
    problems, readers = [], set()
    for name in IMG_GOOD:
        m, want = IMG_MANIFEST[name], IMG_EXPECTED[name]
        try:
            img = read_image(IMG / name)
            conv = as_read_image(want)
            if img.data.dtype != conv.dtype or not np.array_equal(img.data, conv):
                problems.append(f'{name}: pixels differ ({img.data.shape} {img.data.dtype})')
            expect_reader = IMG_READER[os.path.splitext(name)[1]]
            if list(img.scan_shape) != m['scan_shape'] or img.reader != expect_reader:
                problems.append(f'{name}: scan {img.scan_shape}, reader {img.reader}')
            for k, ax in enumerate(m['axes']):
                for key, v in ax.items():
                    got = img.axes[k][key]
                    same = np.isclose(got, v, rtol=1e-6) if isinstance(v, float) else got == v
                    if not same:
                        problems.append(f'{name}: axis {k} {key} {got!r}, expected {v!r}')
            for key, v in m['meta'].items():
                if img.metadata.get(key) != v:
                    problems.append(f'{name}: metadata {key} {img.metadata.get(key)!r}, expected {v!r}')
            readers.add(img.reader)
        except Exception as e:
            problems.append(f'{name}: {type(e).__name__}: {e}')
    assert not problems, '; '.join(problems)
    return 'readers ' + ', '.join(sorted(readers))


@check(f'{len(IMG_BAD)} MRC, Merlin, picture and NumPy files to refuse raise ValueError saying '
       'why; truncated MRC and Merlin files too')
def c_img_bad(tmp):
    from pyemaps import read_image
    problems = []
    for name in IMG_BAD:
        words = IMG_MANIFEST[name]['error']
        try:
            read_image(IMG / name)
            problems.append(f'{name}: not refused')
        except ValueError as e:
            if not all(w in str(e) for w in words):
                problems.append(f'{name}: message lacks {words}: {e}')
    for name in ('mrc_int16.mrc', 'mib_u16.mib'):
        src = (IMG / name).read_bytes()
        cut = os.path.join(tmp, 'cut_' + name)
        Path(cut).write_bytes(src[:len(src) - 100])
        try:
            read_image(cut)
            problems.append(f'truncated {name}: not refused')
        except ValueError as e:
            if 'truncated' not in str(e):
                problems.append(f'truncated {name}: {e}')
    assert not problems, '; '.join(problems)


@check('Merlin scan_shape and scan_roi, the .hdr settings, MRC and NumPy scan_roi, closed files')
def c_img_options(tmp):
    from pyemaps import read_image
    frames = IMG_EXPECTED['mib_u16.mib']                         # 6 frames
    img = read_image(IMG / 'mib_u16.mib', scan_shape=(2, 3), scan_roi=(0, 1, 2, 2))
    assert img.scan_shape == (2, 2) and np.array_equal(img.data, as_read_image(frames[[1, 2, 4, 5]]))
    hdr = read_image(IMG / 'mib_quad.mib').metadata['hdr']
    assert hdr.get('Counter Depth (number)') == '12', hdr
    stack = IMG_EXPECTED['mrc_int16.mrc']
    img = read_image(IMG / 'mrc_int16.mrc', scan_roi=(1, 2))
    assert np.array_equal(img.data, stack[1:3])
    scan = IMG_EXPECTED['npy_scan.npy']                          # 2 x 3 scan
    img = read_image(IMG / 'npy_scan.npy', scan_roi=(0, 1, 2, 1))
    assert img.scan_shape == (2, 1) and np.array_equal(img.data, as_read_image(scan[[1, 4]]))
    raises(ValueError, lambda: read_image(IMG / 'mrc_int16.mrc', dataset=0), 'dataset is for')
    for name in ('mib_u16.mib', 'mrc_int16.mrc', 'npy_scan.npy', 'pic_gray16.png'):
        copy = os.path.join(tmp, 'closed_' + name)
        shutil.copy(IMG / name, copy)
        read_image(copy)
        gc.collect()
        os.remove(copy)
    return 'Merlin scan (2, 2) from (2, 3); .hdr Counter Depth 12; files closed'


# ------------------------------------------------------------------ EMD files (need h5py)

EMD = HERE / 'emddata'
EMD_MANIFEST = json.loads((EMD / 'manifest.json').read_text(encoding='utf-8'))['files']
EMD_EXPECTED = np.load(EMD / 'expected.npz')
EMD_GOOD = sorted(n for n, m in EMD_MANIFEST.items() if 'error' not in m)
EMD_BAD = sorted(n for n, m in EMD_MANIFEST.items() if 'error' in m)


def emd_file(name):
    m = EMD_MANIFEST[name]
    return EMD / f'{name}.{"h5" if name == "plain_hdf5" else "emd"}'


@check(f'{len(EMD_GOOD)} EMD files (Velox, Berkeley EMD 1.0 and 0.2, py4DSTEM) read exactly, '
       'with calibration and settings')
def c_emd_good():
    from pyemaps import read_image
    problems, notes = [], []
    for name in EMD_GOOD:
        m, want = EMD_MANIFEST[name], EMD_EXPECTED[name]
        try:
            img = read_image(emd_file(name))
            conv = as_read_image(want)
            if img.data.dtype != conv.dtype or not np.array_equal(img.data, conv):
                problems.append(f'{name}: pixels differ ({img.data.shape} {img.data.dtype})')
            if list(img.scan_shape) != m['scan_shape'] or img.reader != 'EMD':
                problems.append(f'{name}: scan {img.scan_shape}, reader {img.reader}')
            for k, ax in enumerate(m['axes']):
                got = img.axes[k]
                for key, v in ax.items():
                    same = np.isclose(got[key], v, rtol=1e-6) if isinstance(v, float) else got[key] == v
                    if not same:
                        problems.append(f'{name}: axis {k} {key} {got[key]!r}, expected {v!r}')
            for key, v in m['meta'].items():
                got = img.metadata.get(key)
                same = np.isclose(got, v) if isinstance(v, float) and got is not None else got == v
                if not same:
                    problems.append(f'{name}: metadata {key} {got!r}, expected {v!r}')
            notes.append(f'{name} {img.scan_shape}')
        except Exception as e:
            problems.append(f'{name}: {type(e).__name__}: {e}')
    assert not problems, '; '.join(problems)
    return ', '.join(notes)


@check(f'{len(EMD_BAD)} EMD/HDF5 files that must be refused raise ValueError saying why')
def c_emd_bad():
    from pyemaps import read_image
    problems = []
    for name in EMD_BAD:
        words = EMD_MANIFEST[name]['error']
        try:
            read_image(emd_file(name))
            problems.append(f'{name}: not refused')
        except ValueError as e:
            if not all(w in str(e) for w in words):
                problems.append(f'{name}: message lacks {words}: {e}')
    assert not problems, '; '.join(problems)


@check('Velox stores rows first: the real DF-S image matches Velox\'s own thumbnail')
def c_emd_velox_orientation():
    import io
    import h5py
    from PIL import Image
    from pyemaps import read_image
    img = read_image(emd_file('velox_iliad_dfs')).data[0].astype(float)
    with h5py.File(emd_file('velox_iliad_dfs'), 'r') as f:
        raw = f['Thumbnail.jpg'][()]
    thumb = np.asarray(Image.open(io.BytesIO(raw.tobytes())).convert('L'), dtype=float)

    def corr(a):
        a = (a - a.min()) / (np.ptp(a) or 1) * 255
        small = np.asarray(Image.fromarray(a.astype(np.uint8)).resize(thumb.shape[::-1]), float)
        return np.corrcoef(small.ravel(), thumb.ravel())[0, 1]
    as_read, transposed = corr(img), corr(img.T)
    assert as_read > 0.95 and transposed < 0.5, (as_read, transposed)
    return f'correlation {as_read:.3f} as read, {transposed:.3f} transposed'


@check('EMD options: dataset choice, scan_roi on a datacube and a Velox series, binning, errors')
def c_emd_options():
    from pyemaps import read_image
    series, overview = EMD_EXPECTED['velox_series'], EMD_EXPECTED['velox_series_overview']
    fn = emd_file('velox_series')
    assert read_image(fn).npatterns == 3, 'default: the series, not the overview'
    ov = read_image(fn, dataset='ffeeddccbbaa99887766554433221100')
    assert np.array_equal(ov.data, overview.astype(np.int16) if overview.max() <= 32767
                          else overview.astype(np.float32)) and ov.metadata['detector'] == 'HAADF'
    assert read_image(fn, dataset=0).pattern_shape in ((37, 41), (64, 48))
    raises(ValueError, lambda: read_image(fn, dataset='nothere'), 'No image dataset')
    raises(ValueError, lambda: read_image(fn, dataset=7), 'dataset must be 0 to 1')
    img = read_image(fn, scan_roi=(1, 2))
    assert np.array_equal(img.data, series[1:3]) and img.scan_shape == (2,)
    cube = EMD_EXPECTED['emd1_datacube']                       # 3 x 4 scan, row by row
    img = read_image(emd_file('emd1_datacube'), scan_roi=(1, 1, 2, 2))
    assert img.scan_shape == (2, 2) and np.array_equal(img.data, cube[[5, 6, 9, 10]])
    img = read_image(emd_file('emd1_datacube'), binning=2)
    assert img.data.shape == (12, 18, 20) and np.isclose(img.axes[0]['scale'], 0.1462)
    raises(ValueError, lambda: read_image(DATA / 'al.tif', dataset=0), 'dataset is for')
    return 'dataset by name and number; scan_roi (2, 2) from (3, 4); binning scales calibration'


@check('EMD files are closed after reading (can be deleted on Windows)')
def c_emd_closed(tmp):
    from pyemaps import read_image
    for name in ('velox_series', 'emd1_datacube'):
        fn = os.path.join(tmp, f'{name}.emd')
        shutil.copy(emd_file(name), fn)
        read_image(fn, scan_roi=(0, 1) if name == 'velox_series' else None)
        os.remove(fn)


MISSING_H5PY = """
import sys
sys.modules['h5py'] = None
from pyemaps import read_image
try:
    read_image({path!r})
except ImportError as e:
    print('IMPORTERROR', e)
"""


@check('without h5py, reading an EMD file says how to install it; TIFF still works')
def c_emd_missing():
    import subprocess
    code = MISSING_H5PY.format(path=str(emd_file('emd1_datacube')))
    code += f"\nprint('TIFF', read_image({str(DATA / 'al.tif')!r}).pattern_shape)\n"
    p = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True)
    line = next((l for l in p.stdout.splitlines() if l.startswith('IMPORTERROR')), '')
    assert 'pyemaps[emd]' in line, line or p.stderr.strip().splitlines()[-1:]
    assert 'TIFF (200, 200)' in p.stdout, p.stdout + p.stderr
    return line[12:]


def have_h5py():
    try:
        import h5py  # noqa: F401
        return True
    except ImportError:
        return False


# ------------------------------------------------------------------ StackImage (full builds)

def stackimage():
    try:
        from pyemaps import StackImage, E_FILE  # noqa: F401
    except ImportError:
        return None
    return StackImage


@check('StackImage.from_file: a single pattern becomes a numpy image')
def c_from_single():
    from pyemaps import StackImage, E_NPY
    fn = str(DATA / 'al.tif')
    si = StackImage.from_file(fn)
    assert si.nformat == E_NPY and si.scan_shape == () and si.source == fn
    assert np.array_equal(si.data, EXPECTED['al'][0])


@check('StackImage.from_file: a scan goes through a byte-exact temporary .im3, removed after')
def c_from_scan(tmp):
    from pyemaps import StackImage, E_SH, write_im3
    si = StackImage.from_file(DATA / 'stem4d_scan.tif')
    assert si.nformat == E_SH and si.scan_shape == (6, 5), (si.nformat, si.scan_shape)
    ref = os.path.join(tmp, 'ref.im3')
    write_im3(ref, EXPECTED['stem4d_scan'])
    tmpfile = si.fname
    assert Path(tmpfile).read_bytes() == Path(ref).read_bytes(), 'temporary .im3 differs'
    assert si._scan_width(0) == 5 and si._scan_width(6) == 6, 'scan width default'
    del si
    gc.collect()
    assert not os.path.exists(tmpfile), 'temporary .im3 not removed'


@check('StackImage.from_file: oversized patterns ask for binning, too many for scan_roi')
def c_from_limits(tmp):
    from pyemaps import StackImage, XDPImageError, stackimg, write_im3
    big = os.path.join(tmp, 'big.im3')
    write_im3(big, np.zeros((530, 600), np.int16))
    raises(XDPImageError, lambda: StackImage.from_file(big), 'binning=2')
    si = StackImage.from_file(big, binning=2)
    assert si.data.shape == (265, 300), si.data.shape
    raises(XDPImageError, lambda: StackImage.from_file(DATA / 'stack_i2.tif'), '100 to 512')

    class Many:
        source, pattern_shape, npatterns, scan_shape = 'scan.tif', (256, 256), 5002, (61, 82)
    raises(XDPImageError, lambda: stackimg._check_stem4d_size(Many()),
           'scan_roi=(row, column, rows, columns)')


@check('convertImage(E_FILE) writes every pattern of a TIFF to a byte-exact .im3')
def c_convert(tmp):
    from pyemaps import StackImage, E_FILE, write_im3
    fn = os.path.join(tmp, 'scan.tif')
    shutil.copy(DATA / 'stem4d_scan.tif', fn)
    out = StackImage.convertImage(fn, nformat=E_FILE)
    ref = os.path.join(tmp, 'scan_ref.im3')
    write_im3(ref, EXPECTED['stem4d_scan'])
    assert out == os.path.join(tmp, 'sh_converted', 'scan.im3'), out
    assert Path(out).read_bytes() == Path(ref).read_bytes(), 'converted file differs'


def main():
    print(f'Python {sys.version.split()[0]}, numpy {np.__version__}')
    with tempfile.TemporaryDirectory() as tmp:
        c_good()
        c_bad()
        c_truncated(tmp)
        c_metadata()
        c_binning()
        c_roi()
        c_errors(tmp)
        c_closed(tmp)
        c_im3(tmp)
        c_alimg()
        c_readers()
        c_dm_good()
        c_dm_bad(tmp)
        c_dm_options(tmp)
        c_img_good()
        c_img_bad(tmp)
        c_img_options(tmp)
        if have_h5py():
            c_emd_good()
            c_emd_bad()
            c_emd_velox_orientation()
            c_emd_options()
            c_emd_closed(tmp)
            c_emd_missing()
        else:
            RESULTS.append(('EMD checks', None, 'skipped: h5py not installed '
                            '(pip install "pyemaps[emd]"; no Windows wheels for Python 3.15 yet)'))
        if stackimage() is not None:
            c_from_single()
            c_from_scan(tmp)
            c_from_limits(tmp)
            c_convert(tmp)
        else:
            RESULTS.append(('StackImage checks', None, 'skipped: free build, no StackImage'))
        gc.collect()

    for name, ok, msg in RESULTS:
        tag = 'PASS' if ok else 'SKIP' if ok is None else 'FAIL'
        print(f'{tag}  {name}: {msg}')
    failed = [r for r in RESULTS if r[1] is False]
    skipped = [r for r in RESULTS if r[1] is None]
    if failed:
        print(f'------ Image reading checks FAILED: {len(failed)} of {len(RESULTS)} ------')
        return 1
    print(f'++++++ Image reading checks SUCCEEDED: {len(RESULTS) - len(skipped)} checks, '
          f'{len(skipped)} skipped ++++++')
    return 0


if __name__ == '__main__':
    os.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')
    os.environ.setdefault('MPLBACKEND', 'Agg')
    sys.exit(main())
