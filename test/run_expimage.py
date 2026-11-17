'''
Checks for reading experimental images from files (pyemaps.expimage, pyemaps.tiffreader,
StackImage.from_file).

    python run_expimage.py        # any arguments (such as ci_sanity's "-bc all") are ignored

Needs no license and no other package, so it runs in CI. Exits 1 if any check fails.

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


@check('image_readers lists TIFF and pyEMAPS')
def c_readers():
    from pyemaps import image_readers
    names = dict(image_readers())
    assert names == {'TIFF': ['tif', 'tiff'], 'pyEMAPS': ['im3', 'img']}, names
    return str(names)


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
