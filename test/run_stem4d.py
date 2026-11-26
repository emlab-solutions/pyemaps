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
- phase map: StackImage.mapPhases on a 3 x 3 scan of synthetic Aluminium and Copper
  patterns (both FCC, 4.05 and 3.61 A) and a blank one, against both phases' databases: at
  least 3 in 4 of the Al and Cu patterns decided, every decided one right, the blank one without
  a phase, nothing printed for each pattern, and PhaseMap save and load agreeing. Without a
  license (LOCALAPPDATA at an empty folder), phaseMapBegin returns the no-license code.
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


def scan_groups(rng, rows=12, cols=12, size=128):
    """
    A synthetic scan of three groups of patterns, in vertical bands of the scan: square
    lattices at 0 and 30 degrees and a hexagonal one. Each pattern has its own brightness,
    background and counting noise. Returns (patterns, truth labels 0-2, flat).
    """
    import numpy as np
    yy, xx = np.mgrid[0:size, 0:size].astype(float)
    c = (size - 1) / 2

    def lattice(a, angle, gamma):
        th, g = np.radians(angle), np.radians(gamma)
        u = a * np.array([np.cos(th), np.sin(th)])
        v = a * np.array([np.cos(th + g), np.sin(th + g)])
        img = 6.0 * np.exp(-((xx - c) ** 2 + (yy - c) ** 2) / (2 * 3.0 ** 2))
        for h in range(-6, 7):
            for k in range(-6, 7):
                if h == 0 and k == 0:
                    continue
                x, y = c + h * u[0] + k * v[0], c + h * u[1] + k * v[1]
                if abs(x - c) < c - 4 and abs(y - c) < c - 4:
                    img += np.exp(-((xx - x) ** 2 + (yy - y) ** 2) / (2 * 2.0 ** 2))
        return img

    kinds = [lattice(14, 0, 90), lattice(14, 30, 90), lattice(15, 10, 60)]
    truth = np.repeat(np.arange(cols) * 3 // cols, 1)[np.newaxis].repeat(rows, 0)
    pats = []
    for g in truth.ravel():
        img = kinds[g] * rng.uniform(150, 300) + rng.uniform(5, 50)
        pats.append(rng.poisson(img).astype(np.float32))
    return np.array(pats), truth, (rows, cols)


def masked_pearson(a, b, m):
    import numpy as np
    x, y = a[m].astype(float), b[m].astype(float)
    x, y = x - x.mean(), y - y.mean()
    d = np.sqrt((x * x).sum() * (y * y).sum())
    return 0.0 if d == 0 else float((x * y).sum() / d)


def bilinear_polar(img, ccol, crow, dtheta):
    """The polar transform in numpy, as the docs describe it."""
    import numpy as np
    rows, cols = img.shape
    nr = int(np.floor(min(ccol, crow, cols - 1 - ccol, rows - 1 - crow))) + 1
    nt = int(np.floor(360.0 / dtheta + 1e-6))
    r = np.arange(nr)[:, None]
    th = np.radians(np.arange(nt) * dtheta)[None, :]
    x, y = ccol + r * np.cos(th), crow - r * np.sin(th)
    i = np.clip(np.floor(x).astype(int), 0, cols - 2)
    j = np.clip(np.floor(y).astype(int), 0, rows - 2)
    du, dv = x - i, y - j
    a = img.astype(float)
    return ((1 - dv) * (1 - du) * a[j, i] + dv * (1 - du) * a[j + 1, i] + dv * du * a[j + 1, i + 1]
            + (1 - dv) * du * a[j, i + 1])


def case_scananalysis(tmp):
    """
    The scan-analysis routines (ports of the DigitalMicrograph plug-in's functions in
    stem4d's StackDP.cpp) on a synthetic scan of three known groups, against numpy: averages,
    averages by label, the correlation map, similar-pattern groups, classification and polar
    transforms, for float and 16-bit scans.
    """
    import numpy as np
    from io import StringIO
    from contextlib import redirect_stdout
    from pyemaps import StackImage, write_im3, polar_transform

    rng = np.random.default_rng(7)
    pats, truth, scan = scan_groups(rng)
    npat, size = len(pats), pats.shape[1]
    yy, xx = np.mgrid[0:size, 0:size]
    c = (size - 1) / 2
    mask = np.hypot(xx - c, yy - c) > 8                 # leave the direct beam out
    bad = []
    out = StringIO()
    with redirect_stdout(out):
        f32 = os.path.join(tmp, 'groups.im3')
        write_im3(f32, pats)
        si = StackImage(f32)

        # the average, and averages by label
        avg = si.averagePattern()
        d = np.abs(avg - pats.astype(float).mean(0)).max() / pats.max()
        if d > 1e-6:
            bad.append(f'averagePattern differs from numpy by {d:.2g}')
        lab = truth.copy()
        lab[0, 0] = -1                                  # left out
        lab[lab == 2] = 7                               # labels needn't be consecutive
        means, values, counts = si.averageByLabel(lab)
        flat = lab.ravel()
        if list(values) != [0, 1, 7] or list(counts) != [np.sum(flat == v) for v in (0, 1, 7)]:
            bad.append(f'averageByLabel labels {list(values)}, counts {list(counts)}')
        else:
            for m, v in zip(means, values):
                d = np.abs(m - pats[flat == v].astype(float).mean(0)).max() / pats.max()
                if d > 1e-6:
                    bad.append(f'averageByLabel mean of {v} differs from numpy by {d:.2g}')

        # the correlation map: a Pearson coefficient over the mask, so a constant added to the
        # template changes nothing
        k0 = 5
        cmap = si.correlationMap(pats[k0] + 1000.0, mask=mask, scan_shape=scan)
        ref = np.array([masked_pearson(p, pats[k0], mask) for p in pats]).reshape(scan)
        d = np.abs(cmap - ref).max()
        if cmap.shape != scan or d > 1e-5:
            bad.append(f'correlationMap {cmap.shape} differs from numpy by {d:.2g}')
        if abs(cmap.flat[k0] - 1) > 1e-5:
            bad.append(f'a pattern correlates {cmap.flat[k0]:.6f} with itself plus a constant')

        # similar-pattern groups: each group must hold one kind of pattern
        g1, c1 = si.findSimilar(threshold=0.5, mask=mask, seed=3, scan_shape=scan)
        g2, _ = si.findSimilar(threshold=0.5, mask=mask, seed=3, scan_shape=scan)
        g3, _ = si.findSimilar(threshold=0.5, mask=mask, seed=11, scan_shape=scan)
        if not np.array_equal(g1, g2):
            bad.append('findSimilar gave different groups for the same seed')
        for name, g in (('seed 3', g1), ('seed 11', g3)):
            impure = [int(v) for v in np.unique(g) if len(np.unique(truth[g == v])) > 1]
            grouped = np.mean([np.sum(g == v) > 1 for v in g.ravel()])
            if impure:
                bad.append(f'findSimilar {name}: groups {impure} mix kinds of pattern')
            if grouped < 0.9:
                bad.append(f'findSimilar {name}: only {grouped:.0%} of the patterns grouped')
        seeds = g1.ravel() == np.arange(npat)
        if not np.allclose(c1.ravel()[seeds & (np.bincount(g1.ravel(), minlength=npat) > 1)], 1):
            bad.append('a seed does not correlate 1 with itself')

        # classification by the averages of the true groups
        means, _, _ = si.averageByLabel(truth)
        cl, cc = si.classifyPatterns(means, mask=mask, scan_shape=scan)
        if not np.array_equal(cl, truth):
            bad.append(f'classifyPatterns got {np.sum(cl != truth)} patterns wrong')
        ref = np.array([[masked_pearson(p, m, mask) for m in means] for p in pats])
        d = np.abs(cc.ravel() - ref.max(1)).max()
        if d > 1e-5:
            bad.append(f'classifyPatterns correlations differ from numpy by {d:.2g}')

        # polar transforms: numpy's bilinear interpolation, the shape to the nearest edge, the
        # single-pattern call, and a ring pattern turning into constant rows
        ccol, crow, dth = 60.3, 70.7, 2.0
        pol = si.polarTransform((ccol, crow), dth)
        one = si.polarTransform((ccol, crow), dth, pattern=9)
        ref = bilinear_polar(pats[9], ccol, crow, dth)
        nr = int(np.floor(min(ccol, crow, size - 1 - ccol, size - 1 - crow))) + 1
        if pol.shape != (npat, nr, 180) or one.shape != ref.shape:
            bad.append(f'polar shapes {pol.shape}, {one.shape}; expected ({npat}, {nr}, 180)')
        else:
            d = np.abs(one - ref).max() / ref.max()
            if d > 1e-5 or not np.array_equal(pol[9], one):
                bad.append(f'polarTransform differs from numpy by {d:.2g}')
            single = polar_transform(pats[9], (ccol, crow), dth)
            if not np.allclose(single, one, rtol=0, atol=1e-3):
                bad.append('polar_transform differs from polarTransform')
        ring = np.cos(np.hypot(xx - 63.5, yy - 63.5) / 3.0)
        rp = polar_transform(ring, (63.5, 63.5), 1.0)
        spread = rp[1:].std(axis=1).max()
        if spread > 0.05:
            bad.append(f'a ring pattern varies by {spread:.3f} along its rows')

        # a 16-bit scan gives the same results
        i16 = os.path.join(tmp, 'groups16.im3')
        write_im3(i16, pats.astype(np.int16))
        si16 = StackImage(i16)
        d1 = np.abs(si16.averagePattern() - avg).max() / pats.max()
        d2 = np.abs(si16.correlationMap(pats[k0], mask=mask, scan_shape=scan) - cmap).max()
        if d1 > 1e-6 or d2 > 1e-5:
            bad.append(f'the 16-bit scan differs: average {d1:.2g}, correlation {d2:.2g}')

        # wrong sizes are refused
        for what, call in (('template', lambda: si.correlationMap(pats[0][:-1])),
                           ('centre', lambda: si.polarTransform((size + 5, 10))),
                           ('labels', lambda: si.averageByLabel(truth.ravel()[:-1]))):
            try:
                call()
                bad.append(f'a wrong {what} was accepted')
            except ValueError:
                pass
    if bad:
        print(f'RESULT FAIL {bad}')
    else:
        print(f'RESULT PASS {npat} patterns of 3 kinds: averages, correlations and polar '
              f'transforms match numpy; findSimilar groups are pure ({len(np.unique(g1))} '
              f'groups), classifyPatterns gets all {npat} right; 16-bit scans agree')


def write_im3_double(path, pats):
    """A stack of doubles in pyEMAPS' small-header format (type 14), which write_im3 doesn't
    write."""
    import numpy as np
    n, rows, cols = pats.shape
    with open(path, 'wb') as f:
        f.write(np.array([cols, rows, n, 14], dtype='<i2').tobytes())
        f.write(np.ascontiguousarray(pats, dtype='<f8').tobytes())


def scan_results(si, scan, mask, pats):
    """Every scan-analysis result for the scan_groups scan, by name."""
    import numpy as np
    from pyemaps import polar_transform
    truth = np.repeat(np.arange(scan[1]) * 3 // scan[1], 1)[np.newaxis].repeat(scan[0], 0)
    r = {'average': si.averagePattern()}
    means, _, _ = si.averageByLabel(truth)
    r['by_label'] = means
    r['correlation'] = si.correlationMap(pats[5], mask=mask, scan_shape=scan)
    r['groups'], r['group_corr'] = si.findSimilar(threshold=0.5, mask=mask, seed=3,
                                                  scan_shape=scan)
    r['classes'], r['class_corr'] = si.classifyPatterns(means, mask=mask, scan_shape=scan)
    r['polar'] = si.polarTransform((60.3, 70.7), 2.0)
    r['polar_one'] = polar_transform(pats[9], (60.3, 70.7), 2.0)
    return r


def group_problems(name, g, truth, rows_only=False):
    """What's wrong with findSimilar's groups g: mixed kinds of pattern, a label that isn't a
    seed of its own group, or (rows_only) a group spanning scan rows."""
    import numpy as np
    bad = []
    flat = g.ravel()
    if not np.array_equal(flat[flat], flat):
        bad.append(f'{name}: a group is named after a pattern outside it')
    impure = [int(v) for v in np.unique(g) if len(np.unique(truth[g == v])) > 1]
    if impure:
        bad.append(f'{name}: groups {impure[:5]} mix kinds of pattern')
    if rows_only:
        spread = [int(v) for v in np.unique(g) if len(np.unique(np.nonzero(g == v)[0])) > 1]
        if spread:
            bad.append(f'{name}: groups {spread[:5]} span scan rows')
    return bad


def case_scanmore(tmp):
    """
    More scan-analysis checks: a scan of doubles gives exactly the results of the same scan in
    floats, and findSimilar's reach and fraction behave as documented.
    """
    import numpy as np
    from io import StringIO
    from contextlib import redirect_stdout
    from pyemaps import StackImage, write_im3

    pats, truth, scan = scan_groups(np.random.default_rng(7))
    size = pats.shape[1]
    yy, xx = np.mgrid[0:size, 0:size]
    mask = np.hypot(xx - (size - 1) / 2, yy - (size - 1) / 2) > 8
    bad = []
    with redirect_stdout(StringIO()):
        f32, f64 = os.path.join(tmp, 'groups.im3'), os.path.join(tmp, 'groups64.im3')
        write_im3(f32, pats)
        write_im3_double(f64, pats)
        si, si64 = StackImage(f32), StackImage(f64)
        r32 = scan_results(si, scan, mask, pats)
        r64 = scan_results(si64, scan, mask, pats)
        from emaps.stem4d import stem4d
        dtype = stem4d.cvar.ximg.h.type
        differ = [k for k in r32 if not np.array_equal(r32[k], r64[k])]
        if dtype != 14:
            bad.append(f'the double scan loaded as type {dtype}, not 14')
        if differ:
            bad.append(f'the double scan differs from the float one in {differ}')

        # reach 1: a search stops after two misses, so with the kinds in vertical bands of
        # the scan, no group reaches past its band in its own scan row
        default = r32['groups']
        short, _ = si.findSimilar(threshold=0.5, mask=mask, seed=3, reach=1, scan_shape=scan)
        bad += group_problems('reach 1', short, truth, rows_only=True)
        if len(np.unique(short)) <= len(np.unique(default)):
            bad.append(f'reach 1 gave {len(np.unique(short))} groups, the default '
                       f'{len(np.unique(default))}: it should split them')
        # fraction 1: every pattern a group hasn't taken is tried as a seed
        every, _ = si.findSimilar(threshold=0.5, mask=mask, seed=3, fraction=1.0,
                                  scan_shape=scan)
        bad += group_problems('fraction 1', every, truth)
        bad += group_problems('the default', default, truth)
        # a threshold no pattern reaches leaves every pattern alone
        alone, corr = si.findSimilar(threshold=0.9999, mask=mask, seed=3, scan_shape=scan)
        if not np.array_equal(alone.ravel(), np.arange(alone.size)) or np.any(corr > 1):
            bad.append('threshold 0.9999 still grouped patterns')
        for what, kw in (('threshold 0', {'threshold': 0}), ('threshold 1', {'threshold': 1}),
                         ('fraction 0', {'fraction': 0}), ('reach 0', {'reach': 0})):
            try:
                si.findSimilar(mask=mask, scan_shape=scan, **kw)
                bad.append(f'{what} was accepted')
            except ValueError:
                pass
    if bad:
        print(f'RESULT FAIL {bad}')
    else:
        print(f'RESULT PASS a scan of doubles gives results identical to floats; findSimilar: '
              f'reach 1 splits the {len(np.unique(default))} groups into '
              f'{len(np.unique(short))} within scan rows, fraction 1 gives '
              f'{len(np.unique(every))} pure groups, threshold 0.9999 none; bad settings refused')


def case_scanresults(tmp, out):
    """Every scan-analysis result, saved to *out* (.npz), for the thread-count comparison."""
    import numpy as np
    from io import StringIO
    from contextlib import redirect_stdout
    from pyemaps import StackImage, write_im3

    pats, _, scan = scan_groups(np.random.default_rng(7))
    size = pats.shape[1]
    yy, xx = np.mgrid[0:size, 0:size]
    mask = np.hypot(xx - (size - 1) / 2, yy - (size - 1) / 2) > 8
    with redirect_stdout(StringIO()):
        f = os.path.join(tmp, f'groups_{os.environ.get("OMP_NUM_THREADS", "all")}.im3')
        write_im3(f, pats)
        r = scan_results(StackImage(f), scan, mask, pats)
    np.savez(out, **r)
    print(f'RESULT PASS {len(r)} results saved')


def case_scanlicense(tmp):
    """Without a license the scan-analysis routines refuse, with a license message."""
    import numpy as np
    from pyemaps import XDPImageError, polar_transform
    try:
        polar_transform(np.ones((64, 64)), (31.5, 31.5))
        print('RESULT FAIL polar_transform ran without a license')
    except XDPImageError as e:
        if 'license' in str(e).lower():
            print('RESULT PASS without a license, polar_transform raises XDPImageError: '
                  f'{str(e)[:60]}...')
        else:
            print(f'RESULT FAIL the error does not mention the license: {e}')


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
    results += check_phasemap(dbfn)
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


def case_phasemap(dbfn, tmp):
    '''Phase map of a synthetic Aluminium and Copper scan (both FCC, 4.05 and 3.61 A).'''
    import numpy as np
    from pyemaps import Crystal, EMC, StackImage, write_im3, PhaseMap
    from pyemaps.stackimg import stem4d

    headless_plots()
    if not hasattr(stem4d, 'phaseMapBegin'):
        print('RESULT SKIP this emaps has no phase mapping')
        return
    from io import StringIO
    from contextlib import redirect_stdout
    with redirect_stdout(StringIO()):
        ret, cudb = Crystal.from_builtin('Copper_FCC').generateDPDB(
            emc=EMC(zone=(0, 0, 1)), res=200, xa=(2, 0, 0))
    if ret != 0:
        print(f'RESULT FAIL dpgen Copper_FCC returned {ret}')
        return
    # a 3 x 3 scan: Al and Cu patterns at known zones, and a blank one
    lattice = {'Al': 4.0493, 'Cu': 3.6149}
    grains = [('Al', (1, 1, 1), 17.0), ('Cu', (1, 1, 2), 141.0), ('Al', (0, 1, 2), 302.0),
              ('Cu', (1, 1, 1), 64.0), ('Al', (1, 1, 2), 200.0), ('Cu', (0, 1, 2), 12.0),
              ('Al', (1, 1, 4), 233.0), ('Cu', (1, 1, 4), 101.0)]
    truth, patterns = [], []
    for name, zone, angle in grains:
        basis = np.eye(3) * lattice[name]
        U = zone_orientation(zone, angle, basis)
        patterns.append(synth_pattern(U, np.linalg.inv(basis).T))
        truth.append(name)
    patterns.append(np.zeros((200, 200), np.float32))
    scan = os.path.join(tmp, 'phase_scan.im3')
    write_im3(scan, np.array(patterns))

    sys.stdout.flush()
    pm = StackImage(scan).mapPhases({'Al': dbfn, 'Cu': cudb}, scan_shape=(3, 3),
                                    progress=False, **INDEX_PARAMS)
    sys.stdout.flush()
    print(pm)
    names = np.array(pm.names)
    phase, decided = pm.phase.ravel(), pm.decided().ravel()
    bad = []
    for i, name in enumerate(truth):
        got = names[phase[i]] if phase[i] >= 0 else '-'
        print(f'PHASE {name} {grains[i][1]}: {got}, confidence {pm.confidence.ravel()[i]:.3f}, '
              f'spacing {np.round(pm.spacing.reshape(-1, 2)[i], 3)}')
        if decided[i] and got != name:
            bad.append(f'{name} {grains[i][1]} decided as {got}')
    n_decided = int(np.count_nonzero(decided[:len(truth)]))
    if n_decided < 0.75 * len(truth):
        bad.append(f'only {n_decided} of {len(truth)} decided')
    if decided[-1]:
        bad.append('the blank pattern has a phase')
    # save and load
    path = os.path.join(tmp, 'phases.npz')
    pm.save(path)
    back = PhaseMap.load(path)
    same = (back.names == pm.names and np.array_equal(back.phase, pm.phase)
            and np.array_equal(back.spacing, pm.spacing)
            and np.array_equal(back.maps[1].rotation, pm.maps[1].rotation))
    if not same:
        bad.append('save and load differ')
    try:
        os.remove(cudb)
    except OSError:
        pass
    if bad:
        print(f'RESULT FAIL {bad}')
    else:
        print(f'RESULT PASS {n_decided} of {len(truth)} Al and Cu patterns decided, all '
              f'correctly; the blank one has no phase; save and load agree')


def case_phaselicense():
    '''Without a license (LOCALAPPDATA at an empty folder), phase mapping refuses.'''
    from pyemaps.stackimg import stem4d
    if not hasattr(stem4d, 'phaseMapBegin'):
        print('RESULT SKIP this emaps has no phase mapping')
        return
    code = stem4d.phaseMapBegin(4, 2)
    print(f'RESULT {"PASS" if code == stem4d.LICENSE_NONEXISTENT else "FAIL"} '
          f'phaseMapBegin without a license returned {code}')


def check_phasemap(dbfn):
    '''The phase map case, and phase mapping without a license.'''
    import tempfile
    results = []
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        code, out, err = run_child('phasemap', dbfn, tmp)
    line = next((l for l in out.splitlines() if l.startswith('RESULT')), None)
    if line is not None and line.startswith('RESULT SKIP'):
        return results
    ok = code == 0 and line is not None and line.startswith('RESULT PASS')
    results.append(('phase map', ok, line[7:] if line else child_failure(code, err)))
    noisy = [l for l in out.splitlines()
             if l.startswith('*****') or 'Number of peaks found' in l or 'No diffraction peaks' in l]
    results.append(('phase map: quiet', not noisy,
                    'no per-pattern output' if not noisy else f'{len(noisy)} lines printed: {noisy[0]}'))
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as empty:
        env = dict(os.environ, LOCALAPPDATA=empty)
        p = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--case',
                            'phaselicense'], capture_output=True, text=True, cwd=HERE, env=env)
    line = next((l for l in p.stdout.splitlines() if l.startswith('RESULT')), None)
    results.append(('phase map without a license', line is not None and
                    line.startswith('RESULT PASS'),
                    line[7:] if line else child_failure(p.returncode, p.stderr)))
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


def check_scananalysis():
    import tempfile
    results = []
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        code, out, err = run_child('scananalysis', tmp)
    line = next((l for l in out.splitlines() if l.startswith('RESULT')), None)
    ok = code == 0 and line is not None and line.startswith('RESULT PASS')
    results.append(('scan analysis', ok, line[7:] if line else child_failure(code, err)))
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        empty = os.path.join(tmp, 'nolicense')
        os.makedirs(empty)
        env = dict(os.environ, LOCALAPPDATA=empty)
        p = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--case',
                            'scanlicense', tmp], capture_output=True, text=True, cwd=HERE,
                           env=env)
    line = next((l for l in p.stdout.splitlines() if l.startswith('RESULT')), None)
    ok = p.returncode == 0 and line is not None and line.startswith('RESULT PASS')
    results.append(('scan analysis without a license', ok,
                    line[7:] if line else child_failure(p.returncode, p.stderr)))

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        code, out, err = run_child('scanmore', tmp)
    line = next((l for l in out.splitlines() if l.startswith('RESULT')), None)
    ok = code == 0 and line is not None and line.startswith('RESULT PASS')
    results.append(('scan analysis: doubles and findSimilar settings', ok,
                    line[7:] if line else child_failure(code, err)))

    # the results mustn't depend on the number of threads
    import numpy as np
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        saved, ok = {}, False
        for n in ('1', '4'):
            out_file = os.path.join(tmp, f'threads{n}.npz')
            p = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--case',
                                'scanresults', tmp, out_file], capture_output=True, text=True,
                               cwd=HERE, env=dict(os.environ, OMP_NUM_THREADS=n))
            if p.returncode != 0 or not os.path.exists(out_file):
                msg = f'{n} threads: {child_failure(p.returncode, p.stderr)}'
                break
            with np.load(out_file) as z:
                saved[n] = {k: z[k] for k in z.files}
        else:
            differ = [k for k in saved['1'] if not np.array_equal(saved['1'][k], saved['4'][k])]
            ok = not differ
            msg = (f'{len(saved["1"])} results identical with OMP_NUM_THREADS 1 and 4' if ok
                   else f'1 and 4 threads differ in {differ}')
    results.append(('scan analysis: thread count', ok, msg))
    return results


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
        results += check_scananalysis()
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
        elif kind == 'phasemap':
            case_phasemap(*rest)
        elif kind == 'phaselicense':
            case_phaselicense()
        elif kind == 'peaksnr':
            case_peaksnr()
        elif kind == 'rmaxreach':
            case_rmaxreach(*rest)
        elif kind == 'scananalysis':
            case_scananalysis(*rest)
        elif kind == 'scanlicense':
            case_scanlicense(*rest)
        elif kind == 'scanmore':
            case_scanmore(*rest)
        elif kind == 'scanresults':
            case_scanresults(*rest)
        sys.exit(0)
    sys.exit(main())
