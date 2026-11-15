'''
Checks for reading experimental images from files (pyemaps.expimage, StackImage.from_file).

    python run_expimage.py        # any arguments (such as ci_sanity's "-bc all") are ignored

Needs RosettaSciIO (pip install "pyemaps[io]"), but no license, so it runs in CI. Exits 1 if
any check fails. A format whose writer can't be installed on this Python (h5py on 3.15, for
example) is skipped and reported, not failed.

What it checks:
- pyEMAPS' small-header files (.im3, .img) and al.img read back exactly.
- Patterns written in RosettaSciIO's formats (TIFF, HSPY, ZSPY, MRCZ, NumPy, EMD, Ripple,
  Semper) read back exactly: values, orientation, scan order and scan shape.
- Data types: 16-bit integers stay int16, other integers that fit become int16, the rest
  float32; NaN is refused.
- binning averages blocks and scales the calibration; scan_roi reads part of a scan.
- The dataset choice (the scan rather than its navigation image), and axes without scan flags.
- Errors: a missing file, an unknown extension or reader, a spectrum, complex data, bad
  options, and a missing RosettaSciIO or reader package, each with a clear message.
- StackImage.from_file and convertImage(E_RSCIIO), on full builds: single patterns, stacks
  through a temporary .im3 (byte-exact, removed afterwards), the scan width, and the size
  checks that ask for binning or scan_roi.
'''
import gc
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rsc_fixtures                                    # noqa: E402

RESULTS = []


def check(name):
    def wrap(fn):
        def run(*args):
            try:
                out = fn(*args)
                ok, msg = (True, out or '') if not isinstance(out, tuple) else out
            except rsc_fixtures.WriterUnavailable as e:
                ok, msg = None, f'skipped: {e}'
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


def rng(seed=3):
    return np.random.default_rng(seed)


# ------------------------------------------------------------------ checks

@check('small-header stack (.im3) reads back exactly')
def c_im3(tmp):
    from pyemaps import read_image, write_im3
    src = (rng().random((3, 21, 17)) * 4000 - 1000).astype(np.int16)
    fn = os.path.join(tmp, 'stack.im3')
    write_im3(fn, src)
    img = read_image(fn)
    assert img.reader == 'pyEMAPS' and img.scan_shape == (3,), (img.reader, img.scan_shape)
    assert img.data.dtype == np.int16 and np.array_equal(img.data, src)
    return f'{img}'


@check('small-header single image (.img) reads back exactly')
def c_img(tmp):
    from pyemaps import read_image, write_im3
    src = rng().random((19, 23)).astype(np.float32)
    fn = os.path.join(tmp, 'single.img')
    write_im3(fn, src)
    img = read_image(fn)
    assert img.reader == 'pyEMAPS' and img.scan_shape == () and img.npatterns == 1
    assert np.array_equal(img.data[0], src)


@check('samples/al.img reads as the backend file layout')
def c_alimg(tmp):
    from pyemaps import read_image
    al = HERE.parent / 'samples' / 'al.img'
    img = read_image(al)
    ref = np.fromfile(al, dtype='<f4', offset=8).reshape(200, 200)
    assert img.pattern_shape == (200, 200) and np.array_equal(img.data[0], ref)


def roundtrip(tmp, ext, src, nav, expect_dtype):
    from pyemaps import read_image
    fn = os.path.join(tmp, f'rt_{ext}_{src.ndim}d.{ext}')
    rsc_fixtures.write(fn, src, nav=nav, scale=0.02, units='1/nm')
    img = read_image(fn)
    rows, cols = src.shape[-2:]
    want = src.reshape(-1, rows, cols).astype(expect_dtype)
    assert img.data.dtype == expect_dtype, f'dtype {img.data.dtype}, expected {expect_dtype}'
    assert img.data.shape == want.shape, f'shape {img.data.shape}, expected {want.shape}'
    assert np.array_equal(img.data, want), 'values or order differ'
    if nav:
        assert img.scan_shape == src.shape[:nav], f'scan {img.scan_shape}, expected {src.shape[:nav]}'
    return f'{img.reader}: {img.npatterns} x {img.pattern_shape} {img.data.dtype}, scan {img.scan_shape}'


FORMAT_CASES = [
    # extension, data, scan axes, dtype read back
    ('tif',  lambda: rng(1).random((26, 31)).astype(np.float32),                0, np.float32),
    ('tif',  lambda: (rng(2).random((5, 26, 31)) * 3e4).astype(np.int16),       1, np.int16),
    ('hspy', lambda: (rng(3).random((3, 4, 22, 27)) * 6e4).astype(np.uint16),   2, np.float32),
    ('zspy', lambda: (rng(4).random((3, 4, 22, 27)) * 3e4).astype(np.int16),    2, np.int16),
    ('mrcz', lambda: rng(5).random((4, 24, 19)).astype(np.float32),             1, np.float32),
    ('npy',  lambda: rng(6).random((24, 19)).astype(np.float64),                0, np.float32),
    ('npy',  lambda: (rng(10).random((3, 4, 22, 27)) * 3e4).astype(np.int16),  2, np.int16),
    ('emd',  lambda: (rng(7).random((24, 19)) * 100).astype(np.int32),          0, np.int16),
    ('rpl',  lambda: rng(8).random((24, 19)).astype(np.float32),                0, np.float32),
    ('unf',  lambda: rng(9).random((24, 19)).astype(np.float32),                0, np.float32),
]


def make_format_check(ext, make, nav, dtype):
    @check(f'{ext} {"scan" if nav == 2 else "series" if nav == 1 else "pattern"} '
           f'reads back exactly')
    def c(tmp):
        return roundtrip(tmp, ext, make(), nav, dtype)
    return c


@check('data types: uint8 and bool to int16, large uint16 to float32')
def c_dtypes(tmp):
    from pyemaps import read_image
    for name, src, want in (('u8', (rng().random((20, 20)) * 255).astype(np.uint8), np.int16),
                            ('bool', rng().random((20, 20)) > 0.5, np.int16),
                            ('u16big', np.full((20, 20), 40000, np.uint16), np.float32)):
        fn = os.path.join(tmp, f'dt_{name}.tif')
        rsc_fixtures.write(fn, src)
        img = read_image(fn)
        assert img.data.dtype == want, f'{name}: {img.data.dtype}, expected {want}'
        assert np.array_equal(img.data[0], src.astype(want)), f'{name}: values differ'


@check('binning averages blocks, drops the remainder and scales the calibration')
def c_binning(tmp):
    from pyemaps import read_image
    src = (rng().random((6, 41, 50)) * 1000).astype(np.uint16)
    fn = os.path.join(tmp, 'bin.tif')
    rsc_fixtures.write(fn, src, nav=1, scale=0.01, units='1/nm')
    img = read_image(fn, binning=2)
    want = src[:, :40, :50].reshape(6, 20, 2, 25, 2).astype(np.float64).mean(axis=(2, 4))
    assert img.pattern_shape == (20, 25) and img.data.dtype == np.float32
    assert np.allclose(img.data, want, rtol=0, atol=1e-3), 'block means differ'
    assert abs(img.axes[0]['scale'] - 0.02) < 1e-9 and 'nm' in img.axes[0]['units'], img.axes
    return f'{img.pattern_shape}, axes {img.axes[0]}'


@check('scan_roi reads part of a 2-D scan and of a series')
def c_roi(tmp):
    from pyemaps import read_image
    scan = (rng().random((3, 4, 20, 22)) * 1000).astype(np.int16)
    fn = os.path.join(tmp, 'roi.npy')
    rsc_fixtures.write(fn, scan, nav=2)
    img = read_image(fn, scan_roi=(1, 1, 2, 3))
    assert img.scan_shape == (2, 3) and np.array_equal(img.data, scan[1:3, 1:4].reshape(6, 20, 22))
    series = (rng().random((6, 20, 22)) * 1000).astype(np.int16)
    fn = os.path.join(tmp, 'roi.tif')
    rsc_fixtures.write(fn, series, nav=1)
    img = read_image(fn, scan_roi=(2, 3))
    assert img.scan_shape == (3,) and np.array_equal(img.data, series[2:5])


@check('dataset choice: the scan over its navigation image; axes without scan flags')
def c_pick():
    from pyemaps import expimage
    nav_img = dict(data=np.zeros((8, 56)), axes=[dict(size=8, navigate=False),
                                                   dict(size=56, navigate=False)])
    scan = dict(data=np.zeros((2, 5, 14, 12), np.float32),
                axes=[dict(size=2, navigate=True), dict(size=5, navigate=True),
                      dict(size=14, navigate=False), dict(size=12, navigate=False)])
    data, nav, _, _ = expimage._pick_image([nav_img, scan], None, 'x')
    assert data.shape == (2, 5, 14, 12) and nav == (2, 5), 'did not pick the scan'
    data, nav, _, _ = expimage._pick_image([nav_img, scan], 0, 'x')
    assert data.shape == (8, 56) and nav == (), 'signal=0 not honoured'
    unflagged = dict(data=np.zeros((4, 4, 19, 19)), axes=[dict(size=n) for n in (4, 4, 19, 19)])
    data, nav, _, _ = expimage._pick_image([unflagged], None, 'x')
    assert nav == (4, 4), f'scan {nav} from axes without flags'


@check('errors: missing file, unknown extension or reader, spectrum, complex, NaN, options')
def c_errors(tmp):
    from pyemaps import read_image
    raises(FileNotFoundError, lambda: read_image(os.path.join(tmp, 'nope.tif')), 'not found')
    odd = os.path.join(tmp, 'x.xyz')
    Path(odd).write_bytes(b'0' * 64)
    raises(ValueError, lambda: read_image(odd), 'No reader for .xyz')
    tif = os.path.join(tmp, 'err.tif')
    rsc_fixtures.write(tif, np.zeros((20, 20), np.float32))
    raises(ValueError, lambda: read_image(tif, reader='nonsense'), 'Unknown reader')
    raises(ValueError, lambda: read_image(tif, binning=0), 'binning')
    raises(ValueError, lambda: read_image(tif, binning=1.5), 'binning')
    raises(ValueError, lambda: read_image(tif, scan_roi=(0, 1)), 'single pattern')
    msa = os.path.join(tmp, 'spectrum.msa')
    rsc_fixtures.write(msa, np.arange(64, dtype=np.float32))
    raises(ValueError, lambda: read_image(msa), 'no 2-D image', 'spectrum')
    cplx = os.path.join(tmp, 'complex.npy')
    np.save(cplx, np.zeros((20, 20), np.complex64))
    raises(ValueError, lambda: read_image(cplx), 'no 2-D image')
    nan = os.path.join(tmp, 'nan.tif')
    a = np.zeros((20, 20), np.float32)
    a[3, 4] = np.nan
    rsc_fixtures.write(nan, a)
    raises(ValueError, lambda: read_image(nan), 'NaN')
    scan = os.path.join(tmp, 'errscan.tif')
    rsc_fixtures.write(scan, np.zeros((4, 20, 20), np.int16), nav=1)
    raises(ValueError, lambda: read_image(scan, scan_roi=(3, 2)), 'outside')
    raises(ValueError, lambda: read_image(scan, scan_roi=(0, 0, 1, 1)), 'scan_roi=(first, count)')


def make_release_check(ext, shape, nav, roi):
    @check(f'{ext}: the file is released after reading part of it lazily')
    def c(tmp):
        from pyemaps import read_image
        fn = os.path.join(tmp, f'release.{ext}')
        rsc_fixtures.write(fn, np.zeros(shape, np.int16), nav=nav)
        img = read_image(fn, scan_roi=roi)
        moved = fn + '.moved'
        os.rename(fn, moved)          # fails on Windows while the file is open
        os.rename(moved, fn)
        return f'{img.npatterns} patterns read'
    return c


RELEASE_CASES = [('tif', (6, 20, 20), 1, (1, 3)), ('hspy', (3, 4, 20, 20), 2, (1, 1, 2, 2)),
                 ('zspy', (3, 4, 20, 20), 2, (0, 0, 2, 2))]


FIRST_READ = '''
import os, sys
sys.path.insert(0, {here!r})
import numpy as np
import rsc_fixtures
fn = {path!r}
rsc_fixtures.write(fn, np.ones((24, 19), np.float32))
from pyemaps import read_image
read_image(fn)
raw = fn[:-3] + 'raw'
os.rename(raw, raw + '.moved')     # fails on Windows while the file is open
os.rename(raw + '.moved', raw)
print('RELEASED')
'''


@check('rpl: the first read in a new process releases its memory-mapped file')
def c_first_read(tmp):
    fn = os.path.join(tmp, 'first.rpl')
    p = subprocess.run([sys.executable, '-c', FIRST_READ.format(here=str(HERE), path=fn)],
                       capture_output=True, text=True)
    assert 'RELEASED' in p.stdout, (p.stderr.strip().splitlines() or ['no output'])[-1]


MISSING = '''
import sys
sys.modules[{module!r}] = None      # as if the package weren't installed
from pyemaps import read_image
try:
    read_image({path!r})
except ImportError as e:
    print('IMPORTERROR', e)
'''


@check('a missing RosettaSciIO, or reader package, says what to install')
def c_missing(tmp):
    tif = os.path.join(tmp, 'missing.tif')
    rsc_fixtures.write(tif, np.zeros((20, 20), np.float32))
    msgs = []
    for module, words in (('rsciio', ['pyemaps[io]']), ('tifffile', ['tifffile', 'pip install'])):
        p = subprocess.run([sys.executable, '-c', MISSING.format(module=module, path=tif)],
                           capture_output=True, text=True)
        line = next((l for l in p.stdout.splitlines() if l.startswith('IMPORTERROR')), '')
        assert line and all(w in line for w in words), \
            f'without {module}: {line or p.stderr.strip().splitlines()[-1:]}'
        msgs.append(line[12:])
    return ' | '.join(msgs)


@check('image_readers lists pyEMAPS and RosettaSciIO readers')
def c_readers():
    from pyemaps import image_readers
    names = dict(image_readers())
    assert 'pyEMAPS' in names and 'TIFF' in names and 'tif' in names['TIFF'], list(names)[:5]
    return f'{len(names)} readers'


# ---- StackImage (full builds)

def stackimage():
    try:
        from pyemaps import StackImage, E_NPY, E_SH, E_RSCIIO  # noqa: F401
    except ImportError:
        return None
    return StackImage


@check('StackImage.from_file: a single pattern becomes a numpy image')
def c_from_single(tmp):
    from pyemaps import StackImage, E_NPY
    src = (rng().random((120, 130)) * 1000).astype(np.int16)
    fn = os.path.join(tmp, 'single.tif')
    rsc_fixtures.write(fn, src)
    si = StackImage.from_file(fn)
    assert si.nformat == E_NPY and si.scan_shape == () and si.source == fn
    assert np.array_equal(si.data, src)


@check('StackImage.from_file: a scan goes through a byte-exact temporary .im3, removed after')
def c_from_scan(tmp):
    from pyemaps import StackImage, E_SH, write_im3
    src = (rng().random((3, 4, 110, 120)) * 1000).astype(np.int16)
    fn = os.path.join(tmp, 'scan.npy')
    rsc_fixtures.write(fn, src, nav=2)
    si = StackImage.from_file(fn)
    assert si.nformat == E_SH and si.scan_shape == (3, 4), (si.nformat, si.scan_shape)
    ref = os.path.join(tmp, 'ref.im3')
    write_im3(ref, src.reshape(12, 110, 120))
    tmpfile = si.fname
    assert Path(tmpfile).read_bytes() == Path(ref).read_bytes(), 'temporary .im3 differs'
    assert si._scan_width(0) == 4 and si._scan_width(6) == 6, 'scan width default'
    del si
    gc.collect()
    assert not os.path.exists(tmpfile), 'temporary .im3 not removed'


@check('StackImage.from_file: oversized patterns ask for binning, too many for scan_roi')
def c_from_limits(tmp):
    from pyemaps import StackImage, XDPImageError, stackimg
    fn = os.path.join(tmp, 'big.tif')
    rsc_fixtures.write(fn, np.zeros((530, 600), np.int16))
    raises(XDPImageError, lambda: StackImage.from_file(fn), 'binning=2')
    si = StackImage.from_file(fn, binning=2)
    assert si.data.shape == (265, 300), si.data.shape
    small = os.path.join(tmp, 'small.tif')
    rsc_fixtures.write(small, np.zeros((80, 120), np.int16))
    raises(XDPImageError, lambda: StackImage.from_file(small), '100 to 512')

    class Many:
        source, pattern_shape, npatterns, scan_shape = 'scan.mib', (256, 256), 5002, (61, 82)
    raises(XDPImageError, lambda: stackimg._check_stem4d_size(Many()),
           'scan_roi=(row, column, rows, columns)')


@check('convertImage(E_RSCIIO) writes every pattern to a byte-exact .im3')
def c_convert(tmp):
    from pyemaps import StackImage, E_RSCIIO, write_im3
    src = (rng().random((5, 104, 112)) * 1000).astype(np.int16)
    fn = os.path.join(tmp, 'series.tif')
    rsc_fixtures.write(fn, src, nav=1)
    out = StackImage.convertImage(fn, nformat=E_RSCIIO)
    ref = os.path.join(tmp, 'series_ref.im3')
    write_im3(ref, src)
    assert out == os.path.join(tmp, 'sh_converted', 'series.im3'), out
    assert Path(out).read_bytes() == Path(ref).read_bytes(), 'converted file differs'


def main():
    try:
        import rsciio
    except ImportError:
        print('------ Image reading checks FAILED: RosettaSciIO is not installed '
              '(pip install "pyemaps[io]") ------')
        return 1
    print(f'RosettaSciIO {rsciio.__version__}, Python {sys.version.split()[0]}')
    with tempfile.TemporaryDirectory() as tmp:
        c_im3(tmp)
        c_img(tmp)
        c_alimg(tmp)
        for case in FORMAT_CASES:
            make_format_check(*case)(tmp)
        c_dtypes(tmp)
        c_binning(tmp)
        c_roi(tmp)
        for case in RELEASE_CASES:
            make_release_check(*case)(tmp)
        c_first_read(tmp)
        c_pick()
        c_errors(tmp)
        c_missing(tmp)
        c_readers()
        if stackimage() is not None:
            c_from_single(tmp)
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
