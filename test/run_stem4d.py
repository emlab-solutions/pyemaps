'''
4D-STEM (stem4d) checks for full builds: image loading, dpgen and indexing.

    python run_stem4d.py -bc     # run every check, compare indexing with the baseline
    python run_stem4d.py -bg     # regenerate the indexing baseline (only when a change is intended)

-bc exits 1 if any check fails, 0 if all pass. A free build has no stem4d, so the script
says so and exits 0.

What it checks:
- image loading: numpy images of every supported dtype, shape and memory layout load
  through StackImage(nformat=E_NPY) and read back from the backend pixel for pixel;
  invalid images raise XDPImageError (pyemaps#89). Small-header (.im3) files with several
  stacks, 16-bit integer and float32, read back pixel for pixel, every stack, both one stack
  at a time and with all stacks loaded. emaps 2.0.0 and earlier read 16-bit pixels as
  32-bit, and crash loading one stack; fixed in the next emaps release.
- dpgen: generating the Aluminium diffraction pattern database succeeds.
- indexing: al.img indexed from its file and from numpy (float32, float64, Fortran
  order) gives the same result lines, and those match baseline/stem4d/al_index.txt
  (pyemaps#87).
- license: on a full build, importing pyemaps.stem4d succeeds.
- TIFF files (tiffdata/, written by tifffile): al.tif opened with StackImage.from_file indexes
  like al.img; a 6 x 5 scan gives the same bright field image from its .im3 and its TIFF (scan
  width from the file); and a TIFF mask converted by convertImage(E_FILE) gives the same
  masked image as an .im3 mask.

Each case runs in its own process, so a crash in the native code fails that case instead
of the whole run. indexImage always shows its plots; the indexing cases draw them off screen,
so the run needs no windows closed and can run unattended.
'''
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ALIMG = HERE.parent / 'samples' / 'al.img'
BASELINE = HERE / 'baseline' / 'stem4d' / 'al_index.txt'

# Indexing parameters for al.img, as in the pyemaps 4D-STEM samples.
INDEX_PARAMS = dict(cc=29.0, sigma=3.0, img_center=(99.923, 99.919), rmin=10,
                    search_box=10.0, scaling_option=(1, 2), filter_threshold=0.0,
                    peak_threshold=0.8)

# name: (shape, dtype, layout); layout C, F (Fortran order) or T (transposed view)
LOAD_CASES = {
    'square_f32':     ((128, 128), 'float32', 'C'),
    'wide_f32':       ((120, 300), 'float32', 'C'),
    'tall_f32':       ((300, 120), 'float32', 'C'),
    'square_f64':     ((128, 128), 'float64', 'C'),
    'square_u8':      ((128, 128), 'uint8',   'C'),
    'square_u16':     ((128, 128), 'uint16',  'C'),
    'square_u32':     ((128, 128), 'uint32',  'C'),
    'square_i32':     ((128, 128), 'int32',   'C'),
    'square_i64':     ((128, 128), 'int64',   'C'),
    'square_bool':    ((128, 128), 'bool',    'C'),
    'fortran_f32':    ((120, 300), 'float32', 'F'),
    'transposed_f32': ((300, 120), 'float32', 'T'),
    'tall_f64':       ((300, 120), 'float64', 'C'),
    'transposed_f64': ((300, 120), 'float64', 'T'),
}
# Invalid images, which must raise XDPImageError.
ERROR_CASES = ['err_complex', 'err_1d', 'err_small', 'err_list']
# Small-header files with several stacks. name: (dtype, rmode); rmode 1 (EL_ONE) loads one
# stack at a time, rmode 2 (EL_MORE) all of them.
SH_CASES = {
    'sh_int16_one':   ('int16',   1),
    'sh_int16_all':   ('int16',   2),
    'sh_float32_one': ('float32', 1),
    'sh_float32_all': ('float32', 2),
}
SH_DIMS = (128, 120, 3)          # width, height, stacks
SH_TYPES = {'int16': 11, 'float32': 12}   # header data type: 10 + E_INT or E_FLOAT, multi-stack
INDEX_MODES = ['file', 'npy32', 'npy64', 'npyF', 'tif']
TIFFDATA = HERE / 'tiffdata'


def make_image(shape, dtype, layout):
    import numpy as np
    rng = np.random.default_rng(18)
    base = shape if layout != 'T' else shape[::-1]
    a = (rng.random(base) * 200).astype(dtype)
    if layout == 'F':
        a = np.asfortranarray(a)
    elif layout == 'T':
        a = a.T
    return a


# ------------------------------------------------------------------ child cases

def case_load(name):
    import numpy as np
    from pyemaps import StackImage, E_NPY

    a = make_image(*LOAD_CASES[name])
    si = StackImage(None, nformat=E_NPY)
    si.data = a
    si.loadImage()
    ncol, nrow, _ = si.dim
    back = np.array(si.data, dtype=np.float64)
    if (nrow, ncol) != a.shape or back.size != a.size:
        print(f'RESULT FAIL dims {nrow}x{ncol}, expected {a.shape[0]}x{a.shape[1]}')
        return
    expected = a.astype(np.float32).astype(np.float64)
    ndiff = int(np.count_nonzero(back.reshape(nrow, ncol) != expected))
    print(f'RESULT {"PASS" if ndiff == 0 else "FAIL"} {nrow}x{ncol}, {ndiff} pixels differ')


def case_error(name):
    import numpy as np
    from pyemaps import StackImage, XDPImageError, E_NPY

    si = StackImage(None, nformat=E_NPY)
    try:
        if name == 'err_complex':
            si.data = np.zeros((128, 128), dtype=np.complex64)
        elif name == 'err_1d':
            si.data = np.zeros(16384, dtype=np.float32)
        elif name == 'err_small':
            si.data = np.zeros((50, 50), dtype=np.float32)
        elif name == 'err_list':
            si.data = [[1.0] * 128] * 128
        si.loadImage()
    except XDPImageError as e:
        print(f'RESULT PASS XDPImageError: {e.message}')
        return
    except Exception as e:
        print(f'RESULT FAIL raised {type(e).__name__}, not XDPImageError: {e}')
        return
    print('RESULT FAIL no error raised')


def make_sh_file(path, dtype):
    '''
    Write a small-header file with SH_DIMS stacks of *dtype* pixels: an 8-byte header of four
    little-endian shorts (width, height, stacks, data type), then the stacks, row by row.
    Returns the stacks as an array.
    '''
    import numpy as np
    width, height, nstacks = SH_DIMS
    rng = np.random.default_rng(23)
    stacks = (rng.random((nstacks, height, width)) * 2000 - 500).astype(dtype)
    with open(path, 'wb') as f:
        f.write(np.array([width, height, nstacks, SH_TYPES[dtype]], dtype='<i2').tobytes())
        f.write(stacks.astype(np.dtype(dtype).newbyteorder('<')).tobytes())
    return stacks


def case_sh(name):
    import tempfile
    import numpy as np
    from pyemaps import StackImage

    dtype, rmode = SH_CASES[name]
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, f'{name}.im3')
        stacks = make_sh_file(path, dtype)
        bad = []
        for i, expected in enumerate(stacks, start=1):
            si = StackImage(path)
            si.loadImage(rmode=rmode, stack=i)
            back = np.array(si.data, dtype=np.float64)
            if not np.array_equal(back, expected.astype(np.float64).ravel()):
                bad.append(i)
        ncol, nrow, nl = si.dim
    if (ncol, nrow, nl) != SH_DIMS:
        print(f'RESULT FAIL dims {(ncol, nrow, nl)}, expected {SH_DIMS}')
    elif bad:
        print(f'RESULT FAIL stacks {bad} of {len(stacks)} differ from the file')
    else:
        print(f'RESULT PASS {len(stacks)} stacks of {nrow}x{ncol} {dtype} read back exactly')


def headless_plots():
    '''
    Draw plots off screen. indexImage always shows its plots, and pyemaps' display.py
    selects TkAgg on Windows when it's imported, so each plot opened a window that had to
    be closed by hand. Switch to Agg after that import, and make plt.show close the figures.
    '''
    import pyemaps.display  # noqa: F401  (selects TkAgg on Windows)
    import matplotlib.pyplot as plt
    plt.switch_backend('Agg')
    plt.show = lambda *args, **kwargs: plt.close('all')


def case_index(mode, dbfn, npyfile):
    import numpy as np
    from pyemaps import StackImage, E_NPY

    headless_plots()

    if mode == 'file':
        si = StackImage(str(ALIMG))
    elif mode == 'tif':
        si = StackImage.from_file(TIFFDATA / 'al.tif')
    else:
        arr = np.load(npyfile)
        if mode == 'npy64':
            arr = arr.astype(np.float64)
        elif mode == 'npyF':
            arr = np.asfortranarray(arr)
        si = StackImage(None, nformat=E_NPY)
        si.data = arr
    sys.stdout.flush()
    ret = si.indexImage(dbfn, **INDEX_PARAMS)
    sys.stdout.flush()
    print(f'INDEXRET {ret}', flush=True)
    if mode == 'file':
        # Save the loaded pixels for the numpy runs.
        ncol, nrow, _ = si.dim
        np.save(npyfile, np.array(si.data, dtype=np.float32).reshape(nrow, ncol))


# ------------------------------------------------------------------ parent

def case_files(tmp):
    '''Bright field and masked images from a TIFF scan and its .im3, and a converted mask.'''
    import numpy as np
    from pyemaps import StackImage, E_FILE, write_im3

    expected = np.load(TIFFDATA / 'expected.npz')
    flat = expected['stem4d_scan']                           # 30 patterns: a 6 x 5 scan
    im3 = os.path.join(tmp, 'scan.im3')
    write_im3(im3, flat)
    tif = str(TIFFDATA / 'stem4d_scan.tif')

    bdf = dict(center=(64.0, 60.0), rads=(0.0, 12.0))
    _, ref = StackImage(im3).generateBDF(scol=5, **bdf)
    ref = np.array(ref)
    _, from_tif = StackImage.from_file(tif).generateBDF(**bdf)       # scol from the file
    bad = [] if np.array_equal(np.array(from_tif), ref) else ['bright field']

    mask_im3 = os.path.join(tmp, 'mask.im3')
    write_im3(mask_im3, expected['stem4d_mask'][0])
    mask_tif = os.path.join(tmp, 'mask.tif')
    with open(TIFFDATA / 'stem4d_mask.tif', 'rb') as src, open(mask_tif, 'wb') as dst:
        dst.write(src.read())
    converted = StackImage.convertImage(mask_tif, nformat=E_FILE)
    _, m1 = StackImage(im3).generateMaskedImage(mask_im3, scancol=5)
    _, m2 = StackImage(im3).generateMaskedImage(converted, scancol=5)
    if m1 is None or not np.array_equal(np.array(m1), np.array(m2)):
        bad.append('mask')
    if bad:
        print(f'RESULT FAIL differs from the .im3 results: {bad}')
    else:
        print(f'RESULT PASS bright field from .im3 and TIFF identical ({ref.size} pixels, '
              f'sum {ref.sum():.6g}); TIFF mask converted, masked image identical')


def run_child(*args):
    p = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--case', *args],
                       capture_output=True, text=True, cwd=HERE)
    return p.returncode, p.stdout, p.stderr


def child_failure(code, err):
    last = err.strip().splitlines()[-1] if err.strip() else 'no output'
    return f'process exited with {code & 0xFFFFFFFF:#x}: {last}'


def index_result_lines(out):
    '''
    The indexing result lines, without timings, file names or the license banner.
    Python and the C++ engine print through separate buffers, so the order of their lines
    can shift; comparisons sort the lines first. Any changed value still shows up.
    '''
    keep = []
    for line in out.splitlines():
        s = line.rstrip()
        if not s.strip() or s.startswith('INDEXRET'):
            continue
        if re.search(r'time|elapsed|\bsec\b|saved|\.dat|\.bin|license', s, re.I):
            continue
        keep.append(s)
    return keep


def check_license():
    try:
        from pyemaps import stem4d  # noqa: F401
    except Exception as e:
        return False, f'importing pyemaps.stem4d failed: {type(e).__name__}: {e}'
    return True, 'pyemaps.stem4d imported'


def check_loading():
    results = []
    for name in LOAD_CASES:
        code, out, err = run_child('load', name)
        line = next((l for l in out.splitlines() if l.startswith('RESULT')), None)
        ok = code == 0 and line is not None and line.startswith('RESULT PASS')
        results.append((f'load {name}', ok, line[7:] if line else child_failure(code, err)))
    for name in ERROR_CASES:
        code, out, err = run_child('error', name)
        line = next((l for l in out.splitlines() if l.startswith('RESULT')), None)
        ok = code == 0 and line is not None and line.startswith('RESULT PASS')
        results.append((f'load {name}', ok, line[7:] if line else child_failure(code, err)))
    for name in SH_CASES:
        code, out, err = run_child('sh', name)
        line = next((l for l in out.splitlines() if l.startswith('RESULT')), None)
        ok = code == 0 and line is not None and line.startswith('RESULT PASS')
        results.append((f'load {name}', ok, line[7:] if line else child_failure(code, err)))
    return results


# al.img (200 x 200) placed in larger canvases: (rows, columns) and its top-left (row, column).
NONSQUARE_CASES = {
    'wide':     ((200, 300), (0, 50)),
    'tall':     ((300, 200), (50, 0)),
    'wide_off': ((220, 330), (13, 71)),
    'tall_off': ((330, 220), (71, 13)),
    'square300_wide': ((300, 300), (0, 50)),     # the 'wide' pattern on a square canvas
}
RESULT_KEYS = ('Best matching database DP', 'DP rotation angle', 'Reliability index',
               'Number of diffraction peaks indexed', 'correlation maximum')


def case_nonsquare(name, dbfn):
    '''Index al.img placed in a larger canvas, with the pattern center moved to match.'''
    import numpy as np
    from pyemaps import StackImage, E_NPY

    headless_plots()
    al = StackImage(str(ALIMG))
    al.loadImage()
    ncol, nrow, _ = al.dim
    a = np.array(al.data, dtype=np.float32).reshape(nrow, ncol)
    (rows, cols), (r0, c0) = NONSQUARE_CASES[name]
    img = np.full((rows, cols), np.median(np.r_[a[0], a[-1], a[:, 0], a[:, -1]]), np.float32)
    img[r0:r0 + nrow, c0:c0 + ncol] = a
    si = StackImage(None, nformat=E_NPY)
    si.data = img
    params = dict(INDEX_PARAMS)
    params['img_center'] = (params['img_center'][0] + c0, params['img_center'][1] + r0)
    sys.stdout.flush()
    ret = si.indexImage(dbfn, **params)
    sys.stdout.flush()
    print(f'INDEXRET {ret}', flush=True)


def result_values(lines):
    '''The values of RESULT_KEYS in indexing output lines, as strings (None if missing).'''
    return [next((l.split(':')[-1].split()[0] for l in lines if k in l), None) for k in RESULT_KEYS]


def check_nonsquare(dbfn, ref):
    '''
    Non-square patterns used to overrun the indexing buffers (heap corruption) or index a
    cut-short pattern. Placed in a non-square canvas, al.img must index as it does alone: same
    pattern and peaks, rotation within 0.05 degree. The wide canvas must also give exactly the
    result of the same pattern on a square canvas of the same width.
    '''
    results, got = [], {}
    for name in NONSQUARE_CASES:
        code, out, err = run_child('nonsquare', name, dbfn)
        ret_line = next((l for l in out.splitlines() if l.startswith('INDEXRET')), None)
        if code == 0 and ret_line == 'INDEXRET 0':
            got[name] = result_values(index_result_lines(out))
        else:
            results.append((f'non-square {name}', False, ret_line or child_failure(code, err)))
    base = result_values(ref) if ref is not None else None
    for name, v in got.items():
        if name.startswith('square') or base is None:
            continue
        (rows, cols), _ = NONSQUARE_CASES[name]
        ok = (v[0] == base[0] and v[3] == base[3] and abs(float(v[1]) - float(base[1])) < 0.05
              and float(v[2]) >= 5.0)
        msg = (f'{rows} x {cols}: pattern {v[0]}, rotation {v[1]}, reliability {v[2]}, {v[3]} indexed'
               + ('' if ok else f'; al.img alone: {base[:4]}'))
        results.append((f'non-square {name}', ok, msg))
    if 'wide' in got and 'square300_wide' in got:
        same = got['wide'] == got['square300_wide']
        results.append(('non-square wide == square canvas', same, 'identical' if same else
                        f"{got['wide']} vs {got['square300_wide']}"))
    return results


def run_indexing():
    '''Generate the Aluminium database and index al.img every way. Returns (results, lines).'''
    import tempfile
    from io import StringIO
    from contextlib import redirect_stdout
    from pyemaps import Crystal, EMC

    results = []
    with redirect_stdout(StringIO()):
        ret, dbfn = Crystal.from_builtin('Aluminium').generateDPDB(
            emc=EMC(zone=(0, 0, 1)), res=200, xa=(2, 0, 0))
    ok = ret == 0 and dbfn and os.path.exists(dbfn)
    results.append(('dpgen Aluminium database', ok, os.path.basename(dbfn) if ok else f'returned {ret}'))
    if not ok:
        return results, None

    lines = {}
    with tempfile.TemporaryDirectory() as tmp:
        npyfile = os.path.join(tmp, 'al.npy')
        for mode in INDEX_MODES:
            code, out, err = run_child('index', mode, dbfn, npyfile)
            ret_line = next((l for l in out.splitlines() if l.startswith('INDEXRET')), None)
            ok = code == 0 and ret_line == 'INDEXRET 0'
            if ok:
                lines[mode] = index_result_lines(out)
            msg = (f'{len(lines[mode])} result lines' if ok else
                   ret_line or child_failure(code, err))
            results.append((f'index al.img ({mode})', ok, msg))
            if mode == 'file' and not ok:
                break
    results += check_nonsquare(dbfn, lines.get('file'))
    try:
        os.remove(dbfn)
    except OSError:
        pass

    ref = lines.get('file')
    for mode in INDEX_MODES[1:]:
        if mode in lines and ref is not None:
            same = sorted(lines[mode]) == sorted(ref)
            results.append((f'index {mode} == file', same,
                            'identical' if same else 'result lines differ from the file run'))
    return results, ref


def case_rowcol(tmp):
    '''
    Bright/dark field and masked images of a non-square scan (3 x 5) of non-square patterns
    (120 x 170), against the same sums in numpy. Every pattern is different and asymmetric, so
    swapped rows and columns, in the scan or in a pattern, give a different image.
    '''
    import numpy as np
    from io import StringIO
    from contextlib import redirect_stdout
    from pyemaps import StackImage, write_im3

    headless_plots()
    sr, sc, pr, pc = 3, 5, 120, 170
    yy, xx = np.mgrid[0:pr, 0:pc]
    rng = np.random.default_rng(5)
    spot = np.hypot(xx - 100, yy - 40) < 12
    pats = np.array([10.0 + rng.random((pr, pc)) + (k + 1) * 50.0 * spot + 7.0 * (xx > 150)
                     for k in range(sr * sc)], dtype=np.float32)
    scan = os.path.join(tmp, 'rowcol.im3')
    write_im3(scan, pats)
    bad = []

    # whole-pixel and fractional detectors: the centre and radii used to be cut to whole pixels
    for (cx, cy), (r1, r2) in (((100.0, 40.0), (5.0, 15.0)), ((100.4, 39.6), (5.5, 14.7))):
        si = StackImage.from_file(scan, scan_shape=(sr, sc))
        with redirect_stdout(StringIO()):
            ret, data = si.generateBDF(center=(cx, cy), rads=(r1, r2), bShow=False)
        r = np.hypot(xx - cx, yy - cy)
        want = pats[:, (r >= r1) & (r <= r2)].sum(axis=1).reshape(sr, sc)
        got = np.array(data, dtype=np.float64).reshape(si.dim[1], si.dim[0]) if ret == 0 else None
        if got is None or got.shape != (sr, sc) or not np.allclose(got, want, rtol=1e-5):
            bad.append(f'generateBDF centre {(cx, cy)} radii {(r1, r2)}: '
                       f'{None if got is None else got.shape}')

    # float and 16-bit integer masks: integer masks used to be read as floats
    mask = (xx > 120) & (yy < 30)
    want = pats[:, mask].sum(axis=1).reshape(sr, sc)
    for dtype in (np.float32, np.int16):
        mfile = os.path.join(tmp, f'rowcol_mask_{np.dtype(dtype).name}.im3')
        write_im3(mfile, mask.astype(dtype))
        si = StackImage.from_file(scan, scan_shape=(sr, sc))
        with redirect_stdout(StringIO()):
            ret, data = si.generateMaskedImage(mfile, bShow=False)
        got = np.array(data, dtype=np.float64).reshape(si.dim[1], si.dim[0]) if ret == 0 else None
        if got is None or got.shape != (sr, sc) or not np.allclose(got, want, rtol=1e-5):
            bad.append(f'generateMaskedImage, {np.dtype(dtype).name} mask: '
                       f'{None if got is None else got.shape}')

    if bad:
        print(f'RESULT FAIL {bad}')
    else:
        print(f'RESULT PASS bright/dark field (whole-pixel and fractional detector) and masked '
              f'images (float and int16 mask) of a {sr} x {sc} scan of {pr} x {pc} patterns '
              f'match numpy')


def check_rowcol():
    import tempfile
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        code, out, err = run_child('rowcol', tmp)
    line = next((l for l in out.splitlines() if l.startswith('RESULT')), None)
    ok = code == 0 and line is not None and line.startswith('RESULT PASS')
    return [('non-square scan images', ok, line[7:] if line else child_failure(code, err))]


def check_files():
    import tempfile
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        code, out, err = run_child('files', tmp)
    line = next((l for l in out.splitlines() if l.startswith('RESULT')), None)
    ok = code == 0 and line is not None and line.startswith('RESULT PASS')
    return [('TIFF files', ok, line[7:] if line else child_failure(code, err))]


def summary_line(lines, key):
    return next((l.strip() for l in lines if key in l), '')


def main():
    import argparse
    parser = argparse.ArgumentParser(description='4D-STEM (stem4d) checks for full builds')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-bc', '--baseline_comparison', action='store_true',
                       help='run every check and compare indexing with the baseline')
    group.add_argument('-bg', '--baseline_generation', action='store_true',
                       help='regenerate the indexing baseline')
    args = parser.parse_args()

    from pyemaps import PKG_TYPE, TYPE_FREE
    if PKG_TYPE == TYPE_FREE:
        print('stem4d is not in the free package; nothing to check.')
        return 0

    results = [('license', *check_license())]
    if results[0][1]:
        results += check_loading()
        index_results, ref = run_indexing()
        results += index_results
        results += check_files()
        results += check_rowcol()
    else:
        ref = None

    if args.baseline_generation:
        if ref is None or not all(ok for _, ok, _ in results):
            for name, ok, msg in results:
                print(f'{"PASS" if ok else "FAIL"}  {name}: {msg}')
            print('++++++ stem4d baseline NOT generated: a check failed +++++++')
            return 1
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE.write_text('\n'.join(ref) + '\n', encoding='utf-8')
        print(f'++++++ stem4d baseline written: {BASELINE} +++++++')
        return 0

    if ref is not None:
        if not BASELINE.exists():
            results.append(('index matches baseline', False, f'no baseline at {BASELINE}'))
        else:
            base = BASELINE.read_text(encoding='utf-8').splitlines()
            same = sorted(ref) == sorted(base)
            msg = 'identical' if same else 'differs:\n' + '\n'.join(
                __import__('difflib').unified_diff(base, ref, 'baseline', 'this run', lineterm=''))
            results.append(('index matches baseline', same, msg))
        for key in ('Number of diffraction peaks indexed', 'correlation maximum', 'Reliability index'):
            print(f'  {summary_line(ref, key)}')

    for name, ok, msg in results:
        print(f'{"PASS" if ok else "FAIL"}  {name}: {msg}')
    failed = [name for name, ok, _ in results if not ok]
    if failed:
        print(f'++++++ stem4d checks FAILED: {len(failed)} of {len(results)} +++++++')
        return 1
    print(f'++++++ stem4d checks SUCCEEDED: {len(results)} checks +++++++')
    return 0


if __name__ == '__main__':
    os.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')
    if len(sys.argv) > 2 and sys.argv[1] == '--case':
        kind, rest = sys.argv[2], sys.argv[3:]
        if kind == 'load':
            case_load(*rest)
        elif kind == 'error':
            case_error(*rest)
        elif kind == 'sh':
            case_sh(*rest)
        elif kind == 'index':
            case_index(*rest)
        elif kind == 'files':
            case_files(*rest)
        elif kind == 'nonsquare':
            case_nonsquare(*rest)
        elif kind == 'rowcol':
            case_rowcol(*rest)
        sys.exit(0)
    sys.exit(main())
