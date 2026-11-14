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
INDEX_MODES = ['file', 'npy32', 'npy64', 'npyF']


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
        sys.exit(0)
    sys.exit(main())
