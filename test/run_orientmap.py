'''
Checks for pyEMAPS' orientation maps (pyemaps/orientmap.py): the crystal frame, rotation
fitting, Euler angles, inverse pole figure colours, saving and plotting.

    python run_orientmap.py        # any arguments (such as ci_sanity's "-bc all") are ignored

Needs no license; runs in CI. Exits 1 if any check fails. Mapping real scans needs a full
build and is checked by run_stem4d.py.
'''
import os
import sys
import tempfile

import numpy as np

RESULTS = []
RNG = np.random.default_rng(20261118)


def check(name, fn):
    try:
        out = fn()
        RESULTS.append((name, True, out or ''))
    except AssertionError as e:
        RESULTS.append((name, False, str(e) or 'assertion failed'))
    except Exception as e:
        RESULTS.append((name, False, f'{type(e).__name__}: {e}'))


def metric(a, b, c, al, be, ga):
    al, be, ga = np.radians([al, be, ga])
    return np.array([[a * a, a * b * np.cos(ga), a * c * np.cos(be)],
                     [a * b * np.cos(ga), b * b, b * c * np.cos(al)],
                     [a * c * np.cos(be), b * c * np.cos(al), c * c]])


def random_rotation():
    q = RNG.normal(size=4)
    w, x, y, z = q / np.linalg.norm(q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def with_beam(b):
    '''An orientation matrix whose beam direction (crystal frame) is *b*.'''
    b = np.asarray(b, float) / np.linalg.norm(b)
    x = np.cross(b, [0.3, 0.5, 0.8])
    x /= np.linalg.norm(x)
    return np.array([x, np.cross(b, x), b])


CUBIC = dict(basis=np.eye(3) * 4.0493, corners=[[0, 0, 1], [1, 1, 1], [0, 1, 1]])


def make_map(orients, status=None, rindex=None, nindexed=None, **kw):
    from pyemaps.orientmap import OrientationMap
    n = len(orients)
    args = dict(CUBIC)
    args.update(kw)
    return OrientationMap((1, n),
                          status=np.zeros(n) if status is None else status,
                          dp=np.arange(n), rotation=np.zeros(n), correlation=np.ones(n),
                          map_peak=np.ones(n),
                          rindex=np.full(n, 20.0) if rindex is None else rindex,
                          npeaks=np.full(n, 10),
                          nindexed=np.full(n, 8) if nindexed is None else nindexed,
                          orientation=np.array(orients), **args)


def c_basis():
    from pyemaps.orientmap import direct_basis, reciprocal_basis
    for cell in [(4.0493, 4.0493, 4.0493, 90, 90, 90), (3.25, 3.25, 5.21, 90, 90, 120),
                 (5.1, 6.3, 7.7, 81, 97, 103)]:
        G = metric(*cell)
        A = direct_basis(G)
        assert np.allclose(A @ A.T, G), f'{cell}: A A^T != G'
        assert abs(A[0, 1]) < 1e-12 and abs(A[0, 2]) < 1e-12 and abs(A[1, 2]) < 1e-12, 'a along x, b in xy'
        B = reciprocal_basis(A)
        assert np.allclose(A @ B.T, np.eye(3)), 'reciprocal basis'
    return 'cubic, hexagonal and triclinic cells'


def c_fit_rotation():
    from pyemaps.orientmap import fit_rotation
    worst = 0.0
    for _ in range(20):
        R = random_rotation()
        # coplanar points, as in a zero-order Laue zone pattern
        P = np.c_[RNG.normal(size=(6, 2)), np.zeros(6)] @ random_rotation().T
        R2 = fit_rotation(P, P @ R.T)
        assert np.isclose(np.linalg.det(R2), 1.0), 'not a proper rotation'
        worst = max(worst, np.abs(P @ R2.T - P @ R.T).max())
    assert worst < 1e-9, f'worst residual {worst}'
    return f'20 random rotations of coplanar points, worst residual {worst:.1e}'


def c_image_rotation():
    from pyemaps.orientmap import image_rotation
    # stem4d (DFPgaussian): column = x cos a + y sin a, row = -x sin a + y cos a
    x, y, a = 0.3, -0.7, 37.0
    c, s = np.cos(np.radians(a)), np.sin(np.radians(a))
    v = image_rotation(a) @ [x, y, 0.0]
    assert np.allclose(v[:2], [x * c + y * s, -x * s + y * c])
    return 'matches the stem4d pattern rotation'


def c_euler():
    from pyemaps.orientmap import euler_from_matrix, matrix_from_euler
    Us = np.array([random_rotation() for _ in range(200)])
    back = matrix_from_euler(euler_from_matrix(Us))
    assert np.allclose(back, Us, atol=1e-9), 'round trip through Euler angles'
    assert np.allclose(euler_from_matrix(np.eye(3)), 0.0), 'identity'
    # Bunge: g = Rz(phi2) Rx(Phi) Rz(phi1); phi1 = 30 alone turns sample x into crystal (cos30, -sin30)
    g = matrix_from_euler([30.0, 0.0, 0.0]).T
    assert np.allclose(g @ [1, 0, 0], [np.cos(np.radians(30)), -np.sin(np.radians(30)), 0]), 'Bunge convention'
    e = euler_from_matrix(matrix_from_euler([10.0, 0.0, 25.0]))
    assert np.allclose(e, [35.0, 0.0, 0.0]), f'Phi = 0 puts phi1 + phi2 in phi1: {e}'
    return '200 random orientations; identity; Bunge convention; Phi = 0'


def c_ipf_corners():
    m = make_map([with_beam(b) for b in ([0, 0, 1], [0, 1, 1], [1, 1, 1], [0, 0, -1])])
    rgb = m.ipf_colors()[0]
    expect = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 0, 0]]
    assert np.allclose(rgb, expect, atol=1e-6), f'corner colours {np.round(rgb, 3).tolist()}'
    # the corners' order in the database doesn't matter
    m2 = make_map([with_beam([0, 1, 1])], corners=[[1, 1, 1], [0, 1, 1], [0, 0, 1]])
    assert np.allclose(m2.ipf_colors()[0, 0], [0, 1, 0]), '[011] green whatever the order'
    mid = make_map([with_beam([1, 2, 6])]).ipf_colors()[0, 0]
    assert mid.max() == 1.0 and (mid > 0.05).all(), f'inside the triangle: a mix, {mid}'
    return '[001] red, [011] green, [111] blue, -[001] red; mixes inside'


def c_ipf_background():
    from pyemaps.orientmap import OM_FEW_PEAKS
    nan = np.full((3, 3), np.nan)
    m = make_map([with_beam([0, 0, 1])] * 3 + [nan],
                 status=[0, 0, 0, OM_FEW_PEAKS], rindex=[20.0, 2.0, 20.0, 0.0],
                 nindexed=[8, 8, 2, 0])
    assert m.reliable().tolist() == [[True, False, False, False]], m.reliable()
    rgb = m.ipf_colors(background=(1, 1, 1))
    assert np.allclose(rgb[0, 1:], 1.0) and np.allclose(rgb[0, 0], [1, 0, 0])
    assert np.isnan(m.euler_angles()[0, 3]).all(), 'not indexed: NaN Euler angles'
    return 'low reliability, too few indexed and unindexed patterns get the background'


def c_region4():
    from pyemaps.orientmap import _region_weights
    c = np.array([[0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1.0]])
    c /= np.linalg.norm(c, axis=1, keepdims=True)
    w = _region_weights(c, c)
    assert np.allclose(w, np.eye(4), atol=1e-6), f'corners {np.round(w, 3)}'
    centre = c.mean(0) / np.linalg.norm(c.mean(0))
    wc = _region_weights(centre[None], c)[0]
    assert np.allclose(wc.sum(), 1) and (wc > 0.15).all(), f'centre {wc}'
    return 'four-corner regions: each corner is its own colour'


def c_beam_indices():
    m = make_map([with_beam([1, 1, 2])], basis=np.diag([3.0, 4.0, 5.0]),
                 corners=[[0, 0, 1], [1, 0, 0], [0, 1, 0]])
    uvw = m.beam_indices()[0, 0]
    # beam along Cartesian (1,1,2) is [1/3, 1/4, 2/5] in lattice units
    expect = np.array([1 / 3, 1 / 4, 2 / 5]) / (2 / 5)
    assert np.allclose(uvw, expect), uvw
    return 'zone axis indices from the crystal frame'


def c_hexagonal():
    from pyemaps.orientmap import direct_basis, reciprocal_basis
    # dpgen gives the region corners and beam directions in reciprocal lattice components
    A = direct_basis(metric(3.25, 3.25, 5.21, 90, 90, 120))
    B = reciprocal_basis(A)
    corners = [[0, 0, 1], [1, 1, 1], [0, 1, 1]]
    beams = [np.array(c, float) @ B for c in corners]
    m = make_map([with_beam(b) for b in beams], basis=A, corners=corners)
    rgb = m.ipf_colors()[0]
    assert np.allclose(np.sort(rgb, axis=0), np.sort(np.eye(3), axis=0), atol=1e-6) and \
        np.allclose(rgb.max(axis=1), 1.0) and np.allclose(rgb.sum(axis=1), 1.0), rgb
    labels = [t for _, t in m.color_key()[2]]
    assert labels[0] == '[0 0 1]', labels            # c* is along c in a hexagonal cell
    assert any('normal' in t for t in labels), labels   # (1 1 1) normal isn't a small [uvw]
    return f'each corner its own colour; labels {labels}'


def c_save_load():
    from pyemaps.orientmap import OrientationMap
    m = make_map([random_rotation() for _ in range(6)], database='x.bin',
                 params={'cc': 29.0, 'img_center': (99.9, 99.9)})
    with tempfile.TemporaryDirectory() as tmp:
        fn = os.path.join(tmp, 'map.npz')
        m.save(fn)
        m2 = OrientationMap.load(fn)
    for f in ('status', 'dp', 'rotation', 'correlation', 'map_peak', 'rindex', 'npeaks',
              'nindexed', 'orientation', 'basis', 'corners'):
        assert np.array_equal(getattr(m, f), getattr(m2, f)), f
    assert m2.params == m.params and m2.database == 'x.bin' and m2.scan_shape == (1, 6)
    return 'every field round trips'


def c_show():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    m = make_map([random_rotation() for _ in range(4)])
    for kind in ('ipf', 'rindex', 'correlation', 'nindexed', 'npeaks', 'status'):
        fig = m.show(kind, show=False)
        plt.close(fig)
    try:
        m.show('nonsense', show=False)
    except ValueError:
        pass
    else:
        raise AssertionError('an unknown kind is accepted')
    xy, rgb, labels = m.color_key()
    assert len(labels) == 3 and labels[0][1] == '[0 0 1]', labels
    return 'every kind plots; the key labels the corners'


def main():
    for name, fn in (('direct and reciprocal bases from the metric', c_basis),
                     ('rotation fitting', c_fit_rotation),
                     ('stem4d pattern rotation', c_image_rotation),
                     ('Bunge Euler angles', c_euler),
                     ('IPF colours at the corners', c_ipf_corners),
                     ('unreliable patterns', c_ipf_background),
                     ('four-corner regions', c_region4),
                     ('beam direction indices', c_beam_indices),
                     ('a hexagonal crystal: corners in reciprocal components', c_hexagonal),
                     ('save and load', c_save_load),
                     ('plots', c_show)):
        check(name, fn)
    for name, ok, msg in RESULTS:
        print(f'{"PASS" if ok else "FAIL"}  {name}: {msg}')
    failed = [r for r in RESULTS if not r[1]]
    if failed:
        print(f'------ Orientation map checks FAILED: {len(failed)} of {len(RESULTS)} ------')
        return 1
    print(f'++++++ Orientation map checks SUCCEEDED: {len(RESULTS)} checks ++++++')
    return 0


if __name__ == '__main__':
    os.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')
    sys.exit(main())
