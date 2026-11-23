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
- orientation map: StackImage.mapOrientation on a 2 x 3 scan of four synthetic Aluminium
  patterns at known orientations (zones [111], [112], [114], [012], made from the crystal
  lattice, not the database), al.img and a blank pattern. The synthetic ones must come back
  within 1 degree of their orientation, al.img with the same result as indexImage (the
  baseline), the blank one unindexed, and nothing printed for each pattern.
- rmax and database reach: al.img indexes the same with rmax=None and with the automatic
  radius given explicitly (on an emaps without rmax, setting it says a newer emaps is needed);
  rmax must exceed rmin; no reach warning for al.img with its database, a warning when the
  camera constant makes the pattern reach beyond the database's reflections.

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
# Synthetic orientation map patterns: zone axis and in-plane angle (degrees)
MAP_ZONES = [((1, 1, 1), 17.0), ((1, 1, 2), 141.0), ((1, 1, 4), 233.0), ((0, 1, 2), 302.0)]


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


def synth_pattern(U, recip, size=200, cc=29.0, center=(99.923, 99.919), sigma=3.0):
    '''
    A kinematic FCC spot pattern for orientation U (crystal frame to the image frame: column,
    row, beam), 200 kV, with reflections near the Ewald sphere. *recip* has a*, b*, c* as rows.
    '''
    import numpy as np
    h = np.arange(-8, 9)
    H = np.array(np.meshgrid(h, h, h, indexing='ij')).reshape(3, -1).T
    odd = (H % 2).sum(1)
    H = H[((odd == 0) | (odd == 3)) & np.any(H != 0, axis=1)]      # FCC reflections
    g = H @ recip @ U.T
    gl = np.linalg.norm(g, axis=1)
    k, sg_tol = 1 / 0.0251, 0.02
    s = -(2 * k * g[:, 2] + gl ** 2) / (2 * k)                      # excitation error
    keep = (gl < 1.6) & (np.abs(s) < sg_tol)
    yy, xx = np.mgrid[0:size, 0:size].astype(float)
    img = 3.0 * np.exp(-((xx - center[0]) ** 2 + (yy - center[1]) ** 2) / (2 * (2 * sigma) ** 2))
    for (gx, gy, _), gg, ss in zip(g[keep], gl[keep], s[keep]):
        amp = np.exp(-0.6 * gg ** 2) * np.exp(-(ss / (sg_tol / 2)) ** 2)
        img += amp * np.exp(-((xx - center[0] - cc * gx) ** 2 + (yy - center[1] - cc * gy) ** 2)
                            / (2 * sigma ** 2))
    return (img * 1000).astype(np.float32)


def zone_orientation(zone, angle, basis):
    '''The orientation with the beam along *zone* [uvw], turned *angle* degrees about it.'''
    import numpy as np
    b = np.asarray(zone, float) @ basis
    b /= np.linalg.norm(b)
    x = np.cross(b, [0.3, 0.5, 0.8])
    x /= np.linalg.norm(x)
    y = np.cross(b, x)
    c, s = np.cos(np.radians(angle)), np.sin(np.radians(angle))
    return np.array([c * x + s * y, -s * x + c * y, b])


def cubic_misorientation(U1, U2):
    '''
    Smallest rotation angle (degrees) between two orientations, over the cubic rotations and
    a 180 degree turn about the beam (which a zero-order pattern can't tell apart).
    '''
    import itertools
    import numpy as np
    best = 180.0
    for p in itertools.permutations(range(3)):
        for sg in itertools.product([1, -1], repeat=3):
            S = np.zeros((3, 3))
            S[range(3), p] = sg
            if np.linalg.det(S) < 0:
                continue
            for E in (np.eye(3), np.diag([-1.0, -1.0, 1.0])):
                M = E @ U1 @ S @ U2.T
                best = min(best, np.degrees(np.arccos(np.clip((np.trace(M) - 1) / 2, -1, 1))))
    return best


def case_orientmap(dbfn, tmp):
    '''Orientation map of synthetic patterns, al.img and a blank pattern.'''
    import numpy as np
    from pyemaps import StackImage, write_im3, OM_INDEXED, OM_FEW_PEAKS, OM_FAILED
    from pyemaps.orientmap import direct_basis, reciprocal_basis
    from pyemaps.stackimg import stem4d

    headless_plots()
    if not hasattr(stem4d, 'getIndexResult'):
        print('RESULT FAIL this emaps has no orientation mapping (getIndexResult)')
        return
    StackImage.loadDPDB(dbfn)
    ret, gmx = stem4d.getDPDBMetric(9)
    A = direct_basis(gmx)
    B = reciprocal_basis(A)

    al = StackImage(str(ALIMG))
    al.loadImage()
    alimg = np.array(al.data, dtype=np.float32).reshape(200, 200)
    truth = [zone_orientation(z, a, A) for z, a in MAP_ZONES]
    patterns = [synth_pattern(U, B) for U in truth] + [alimg, np.zeros((200, 200), np.float32)]
    scan = os.path.join(tmp, 'map_scan.im3')
    write_im3(scan, np.array(patterns))

    sys.stdout.flush()
    m = StackImage(scan).mapOrientation(dbfn, scan_shape=(2, 3), progress=False, **INDEX_PARAMS)
    sys.stdout.flush()
    print(m)

    def flat(a):
        return a.reshape((-1,) + a.shape[2:])

    status, U = flat(m.status), flat(m.orientation)
    bad = []
    for i, (zone, angle) in enumerate(MAP_ZONES):
        if status[i] != OM_INDEXED:
            bad.append(f'{zone} not indexed (status {status[i]})')
            continue
        mis = cubic_misorientation(truth[i], U[i])
        print(f'MAP {zone}: misorientation {mis:.3f} deg, reliability {flat(m.rindex)[i]:.2f}, '
              f'{flat(m.nindexed)[i]} indexed')
        if mis > 1.0 or not flat(m.reliable())[i]:
            bad.append(f'{zone}: {mis:.2f} deg, reliability {flat(m.rindex)[i]:.2f}')
    print(f'MAPAL {flat(m.dp)[4]} {flat(m.rotation)[4]:.3f} {flat(m.rindex)[4]:.4f} '
          f'{flat(m.nindexed)[4]}')
    if status[5] not in (OM_FEW_PEAKS, OM_FAILED):
        bad.append(f'blank pattern has status {status[5]}')
    if bad:
        print(f'RESULT FAIL {bad}')
    else:
        print(f'RESULT PASS {len(MAP_ZONES)} synthetic orientations within 1 degree; '
              f'blank pattern not indexed')


def case_peaksnr():
    '''
    Peak search on a lattice of spots over a noisy background: without min_snr a low
    threshold also picks up the noise; with it, the spots and little else.
    '''
    import numpy as np
    from io import StringIO
    from contextlib import redirect_stdout
    from pyemaps import StackImage, E_NPY
    from pyemaps.errors import XDPImageError
    from pyemaps.stackimg import stem4d, ediom, _search_peaks

    size, c, sigma = 200, (99.5, 100.5), 3.0
    a = np.radians(17.0)
    u, v = 22.0 * np.array([np.cos(a), np.sin(a)]), 22.0 * np.array([-np.sin(a), np.cos(a)])
    spots = [c + i * u + j * v for i in range(-5, 6) for j in range(-5, 6)]
    spots = np.array([p for p in spots if 15 < np.hypot(*(p - c)) < 90])
    yy, xx = np.mgrid[0:size, 0:size].astype(float)
    img = 10.0 + 200.0 * np.exp(-((xx - c[0]) ** 2 + (yy - c[1]) ** 2) / (2 * 6.0 ** 2))
    for x, y in spots:
        img += 20.0 * np.exp(-((xx - x) ** 2 + (yy - y) ** 2) / (2 * sigma ** 2))
    # spatially correlated noise, like the smooth ripples of a real (median-filtered) detector
    # background: white noise alone seldom looks like a spot, so it wouldn't test min_snr
    noise = np.random.default_rng(7).normal(0.0, 1.0, img.shape)
    f = np.fft.fftfreq(size)
    kernel = np.exp(-2 * (np.pi * 2.5) ** 2 * (f[:, None] ** 2 + f[None, :] ** 2))
    noise = np.real(np.fft.ifft2(np.fft.fft2(noise) * kernel))
    img += noise / noise.std()

    si = StackImage(None, nformat=E_NPY)
    si.data = img.astype(np.float32)
    with redirect_stdout(StringIO()):
        si.loadImage()
    edc = stem4d.cvar.edc
    stem4d.setVerbose(0)

    def search(snr):
        edc.sigma = sigma
        edc.set_center(*c)
        stem4d.prepareSearch(c[0], c[1], 10.0)
        n = _search_peaks(10.0, 0.5, snr)
        if n is None or n <= 0:
            return np.zeros((0, 2))
        ret, kd = ediom.getXKDif(n + 1)
        pk = np.array([(k[0], k[1]) for k in kd], float)
        return pk[np.hypot(pk[:, 0] - c[0], pk[:, 1] - c[1]) > 12]

    def score(pk):
        if len(pk) == 0:
            return 0.0, 0
        d = np.hypot(pk[:, None, 0] - spots[None, :, 0], pk[:, None, 1] - spots[None, :, 1])
        return np.mean(d.min(0) <= 2.0), int(np.sum(d.min(1) > 2.0))

    try:
        loose = search(0.0)
        strict = search(5.0)
    except XDPImageError as e:
        print(f'RESULT FAIL {e}')
        return
    try:
        _search_peaks(10.0, 0.5, -1.0)
        neg = False
    except ValueError:
        neg = True
    rec0, false0 = score(loose)
    rec5, false5 = score(strict)
    print(f'PEAKSNR {len(spots)} spots; min_snr 0: {len(loose)} peaks, recall {rec0:.2f}, '
          f'{false0} false; min_snr 5: {len(strict)} peaks, recall {rec5:.2f}, {false5} false')
    bad = []
    if len(loose) < 2 * len(spots):
        bad.append(f'without min_snr only {len(loose)} peaks: the noise case no longer tests it')
    if rec5 < 0.9 or false5 > 0.1 * len(spots):
        bad.append(f'min_snr 5: recall {rec5:.2f}, {false5} false peaks')
    if not neg:
        bad.append('a negative min_snr was accepted')
    if bad:
        print(f'RESULT FAIL {bad}')
    else:
        print(f'RESULT PASS min_snr 5 finds {rec5:.0%} of {len(spots)} spots with {false5} false '
              f'peaks; without it, {len(loose)} peaks')


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
    ref = lines.get('file')
    results += check_nonsquare(dbfn, ref)
    results += check_orientmap(dbfn, ref)
    results += check_firstpass(dbfn)
    results += check_rmaxreach(dbfn)
    try:
        os.remove(dbfn)
    except OSError:
        pass

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
def baseline_values(lines):
    '''Best matching pattern, rotation, reliability index and peaks indexed from result lines.'''
    def number(key):
        line = summary_line(lines, key)
        return float(line.split(':')[-1].split()[0]) if line else None
    return (number('Best matching database DP'), number('DP rotation angle'),
            number('Reliability index'), number('Number of diffraction peaks indexed'))


def case_firstpass(dbfn):
    '''
    Noisy [111] patterns whose spots are wider than the starting search kernel: no spot reaches
    the default peak threshold with that kernel, so the search's first pass (which picks the spot
    the kernel is refined from) finds nothing. It must retry looser, and the patterns must map.
    '''
    import numpy as np
    from numpy.lib.stride_tricks import sliding_window_view
    from pyemaps import StackImage, write_im3, OM_INDEXED
    from pyemaps.orientmap import direct_basis, reciprocal_basis
    from pyemaps.stackimg import stem4d

    headless_plots()
    StackImage.loadDPDB(dbfn)
    ret, gmx = stem4d.getDPDBMetric(9)
    A = direct_basis(gmx)
    B = reciprocal_basis(A)
    rng = np.random.default_rng(3)
    truth = [zone_orientation((1, 1, 1), 17.0 + 7.0 * i, A) for i in range(12)]
    pats = np.array([rng.poisson(synth_pattern(U, B) / 1000.0 * 200.0 + 5.0) for U in truth],
                    dtype=np.float32)

    # the starting kernel: a Gaussian whose full width at half maximum is sigma
    sigma = INDEX_PARAMS['sigma']
    n = 2 * int(sigma * 3 / 2) + 1
    yy, xx = np.mgrid[0:n, 0:n] - n // 2
    K = np.exp(-4 * np.log(2) * (xx ** 2 + yy ** 2) / sigma ** 2)
    Kc = K - K.mean()
    best = []
    for p in pats:
        w = sliding_window_view(p.astype(float), (n, n))
        wc = w - w.mean(axis=(2, 3), keepdims=True)
        den = np.sqrt((wc ** 2).sum(axis=(2, 3))) * np.sqrt((Kc ** 2).sum())
        c = (wc * Kc).sum(axis=(2, 3)) / np.maximum(den, 1e-12)
        best.append(c.max())
    # keep the patterns where no spot reaches the threshold with the starting kernel: without
    # the fallback their search fails outright
    thr = INDEX_PARAMS['peak_threshold']
    keep = [i for i in range(len(pats)) if best[i] < thr]
    if len(keep) < 4:
        print(f'RESULT FAIL the case no longer tests the fallback: only {len(keep)} patterns have '
              f'no spot matching the starting kernel at {thr}')
        return
    pats, truth, best = pats[keep], [truth[i] for i in keep], [best[i] for i in keep]

    scan = os.path.join(os.path.dirname(dbfn), f'firstpass_{os.getpid()}.im3')
    write_im3(scan, pats)
    try:
        m = StackImage(scan).mapOrientation(dbfn, scan_shape=(1, len(pats)), progress=False,
                                            **INDEX_PARAMS)
    finally:
        os.remove(scan)
    errs = [cubic_misorientation(truth[i], m.orientation[0, i])
            if m.status[0, i] == OM_INDEXED else 180.0 for i in range(len(pats))]
    if max(errs) > 1.0:
        print(f'RESULT FAIL errors {np.round(errs, 2).tolist()} deg (best starting-kernel '
              f'match {max(best):.2f})')
    else:
        print(f'RESULT PASS {len(pats)} noisy [111] patterns within 1 degree at peak_threshold '
              f'{thr}, though no spot matches the starting kernel above {max(best):.2f}')


def case_rmaxreach(dbfn):
    '''
    rmax: None (the automatic outer radius) and the same radius given explicitly index al.img
    the same, and rmax must exceed rmin; an emaps without rmax says it needs a newer one. The
    database-reach check: quiet for al.img with this database, a warning when the camera
    constant makes the pattern reach beyond the database's reflections.
    '''
    import warnings
    import numpy as np
    from pyemaps import StackImage
    from pyemaps.errors import XDPImageError
    from pyemaps.stackimg import _check_reach, _outer_radius

    headless_plots()
    si = StackImage(str(ALIMG))
    kw = dict(INDEX_PARAMS, scan_shape=(1, 1), progress=False)
    bad = []
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        m0 = si.mapOrientation(dbfn, **kw)
    if any(issubclass(x.category, UserWarning) for x in w):
        bad.append(f'unexpected warning for al.img: {w[0].message}')
    auto = _outer_radius(INDEX_PARAMS['img_center'], si.dim, None)
    try:
        m1 = si.mapOrientation(dbfn, rmax=auto, **kw)
        same = all(np.array_equal(getattr(m0, f), getattr(m1, f))
                   for f in ('dp', 'rotation', 'rindex', 'nindexed'))
        if not same:
            bad.append(f'rmax={auto:.2f} (the automatic radius) indexes differently from rmax=None')
        if m1.params.get('rmax') != auto:
            bad.append(f'params record rmax {m1.params.get("rmax")}')
        rmax_note = f'rmax=None and rmax={auto:.1f} index alike'
    except XDPImageError as e:
        if 'newer emaps' not in str(e):
            bad.append(f'rmax: {e}')
        rmax_note = 'this emaps has no rmax, and says so'
    try:
        si.mapOrientation(dbfn, rmax=INDEX_PARAMS['rmin'], **kw)
        bad.append('rmax equal to rmin was accepted')
    except ValueError:
        pass
    StackImage.loadDPDB(dbfn)
    quiet = _check_reach(dbfn, INDEX_PARAMS['cc'], INDEX_PARAMS['img_center'], si.dim, None)
    with warnings.catch_warnings(record=True):
        warnings.simplefilter('always')
        loud = _check_reach(dbfn, 10.0, INDEX_PARAMS['img_center'], si.dim, None)
    if quiet is not None:
        bad.append(f'reach warning for al.img: {quiet}')
    if loud is None or 'gmax' not in loud:
        bad.append('no reach warning with cc 10, which needs 6.7 1/Å')
    print(f'RESULT FAIL {bad}' if bad else
          f'RESULT PASS {rmax_note}; reach warning only when the database falls short')


def check_rmaxreach(dbfn):
    code, out, err = run_child('rmaxreach', dbfn)
    line = next((l for l in out.splitlines() if l.startswith('RESULT')), None)
    ok = code == 0 and line is not None and line.startswith('RESULT PASS')
    return [('rmax and database reach', ok, line[7:] if line else child_failure(code, err))]


def check_firstpass(dbfn):
    code, out, err = run_child('firstpass', dbfn)
    line = next((l for l in out.splitlines() if l.startswith('RESULT')), None)
    ok = code == 0 and line is not None and line.startswith('RESULT PASS')
    return [('peak search first-pass fallback', ok, line[7:] if line else child_failure(code, err))]


def check_orientmap(dbfn, ref):
    '''The orientation map case; al.img in the map must match the indexImage result.'''
    import tempfile
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        code, out, err = run_child('orientmap', dbfn, tmp)
    line = next((l for l in out.splitlines() if l.startswith('RESULT')), None)
    ok = code == 0 and line is not None and line.startswith('RESULT PASS')
    results = [('orientation map', ok, line[7:] if line else child_failure(code, err))]
    al = next((l.split()[1:] for l in out.splitlines() if l.startswith('MAPAL')), None)
    if ref is not None and al is not None:
        dp, rot, rindex, nidx = baseline_values(ref)
        got = (int(al[0]), float(al[1]), float(al[2]), int(al[3]))
        same = (got[0] == dp and abs(got[1] - rot) < 0.01 and abs(got[2] - rindex) < 0.01
                and got[3] == nidx)
        msg = f'pattern {got[0]}, rotation {got[1]:.3f}, reliability {got[2]:.4f}, {got[3]} indexed'
        if not same:
            msg += f'; indexImage: {dp}, {rot}, {rindex}, {nidx}'
        results.append(('orientation map: al.img as indexImage', same, msg))
    noisy = [l for l in out.splitlines()
             if l.startswith('*****') or 'Number of peaks found' in l or 'No diffraction peaks' in l
             or 'Error while searching' in l]
    results.append(('orientation map: quiet', not noisy,
                    'no per-pattern output' if not noisy else f'{len(noisy)} lines printed: {noisy[0]}'))
    return results


def check_files():
    import tempfile
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        code, out, err = run_child('files', tmp)
    line = next((l for l in out.splitlines() if l.startswith('RESULT')), None)
    ok = code == 0 and line is not None and line.startswith('RESULT PASS')
    return [('TIFF files', ok, line[7:] if line else child_failure(code, err))]


def check_peak_snr():
    code, out, err = run_child('peaksnr')
    line = next((l for l in out.splitlines() if l.startswith('RESULT')), None)
    ok = code == 0 and line is not None and line.startswith('RESULT PASS')
    return [('peak search min_snr', ok, line[7:] if line else child_failure(code, err))]


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
        results += check_peak_snr()
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
        elif kind == 'firstpass':
            case_firstpass(*rest)
        elif kind == 'orientmap':
            case_orientmap(*rest)
        elif kind == 'peaksnr':
            case_peaksnr()
        elif kind == 'rmaxreach':
            case_rmaxreach(*rest)
        sys.exit(0)
    sys.exit(main())
