'''
Checks for pyEMAPS' probe simulations (pyemaps/probe.py, emaps' probe module): the four modes
(Ronchigram, probe, CTF, HREM), the random and crystal potentials and the exit wave against a
stored baseline, and physical checks that need no baseline.

    python run_probe.py -bc      # run the checks (ci_sanity's "-bc all" works too)
    python run_probe.py -bg      # regenerate the baseline; only for an intended change

Needs no license; runs in CI. Exits 1 if any check fails. With an emaps that has no probe
module, it prints that the checks were skipped and exits 0.
'''
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BASELINE = HERE / 'baseline' / 'probe' / 'probe_baseline.npz'
RESULTS = []

# A corrected 200 kV probe with the residual aberrations of a real corrector (the probe
# program's data/titan file), on a 64 A map of 128 x 128 pixels.
TITAN = {'a1': (1.349, 146.2), 'a2': (58.94, -131.9), 'a3': (0.3054, -7.5),
         'a4': (35.96, 68.9), 'a5': (0.7825, -114.8), 'b2': (22.89, 141.4),
         's3': (0.1977, -161.2), 'b4': (8.769, 2.8), 'd4': (20.8, -47.0)}


def check(name, fn):
    try:
        out = fn()
        RESULTS.append((name, True, out or ''))
    except Skip as e:
        RESULTS.append((name, None, str(e)))
    except AssertionError as e:
        RESULTS.append((name, False, str(e) or 'assertion failed'))
    except Exception as e:
        RESULTS.append((name, False, f'{type(e).__name__}: {e}'))


def titan_probe(**kwargs):
    from pyemaps import Probe
    settings = dict(kv=200, aperture=25, defocus=-5.14, cs=-0.00355, c5=3.829,
                    aberrations=TITAN, size=64, sampling=128)
    settings.update(kwargs)
    return Probe(**settings)


def results():
    p = titan_probe()
    pot = p.random_potential(density=0.05, z=13, thickness=100, seed=1211)
    chromatic = titan_probe(cc=1.5, energy_spread=0.6, semi_angle=0.2)
    wave = p.exit_wave(pot)
    out = {'potential': pot, 'ronchigram': p.ronchigram(pot), 'probe': p.probe(),
            'ctf': p.ctf(), 'probe_cc': chromatic.probe(), 'ctf_cc': chromatic.ctf(),
            'diameter': np.array([p.diameter(50), p.diameter(80)]),
            'exit_wave': wave, 'hrem': p.hrem(wave), 'hrem_cc': chromatic.hrem(wave),
            'hrem_integrated': chromatic.hrem(wave, integrate=True),
            'phase': p.phase_map(), 'stem': chromatic.stem_image(pot), 'mtf': chromatic.mtf(),
            'psf': p.apply_psf(p.hrem(wave), 0.6, 40.0),
            'diameter_interpolated': np.array([p.diameter(50, interpolate=True),
                                               p.diameter(80, interpolate=True)])}
    # the crystal potential and the multislice need emaps 2.6.0, and the multislice a license
    if has_routine('crystalpotential'):
        out['crystal'] = crystal_map()
    if licensed():
        out.update(multislice_maps())
    return out


def c_baseline():
    base = np.load(BASELINE)
    new = results()
    worst = []
    for name, value in new.items():
        ref = base[name]
        assert value.shape == ref.shape, f'{name}: shape {value.shape}, baseline {ref.shape}'
        rel = np.abs(value - ref).max() / max(np.abs(ref).max(), 1e-30)
        worst.append(f'{name} {rel:.1g}')
        # the same build gives the same numbers; allow rounding from another compiler version
        assert rel <= 1e-5, f'{name} differs from the baseline: largest relative difference {rel:.3g}'
    skipped = [name for name in base.files if name not in new]
    note = f'; not computed here (emaps or license): {", ".join(skipped)}' if skipped else ''
    return 'largest relative differences: ' + ', '.join(worst) + note


def c_normalized():
    p = titan_probe()
    for probe in (p.probe(), titan_probe(cc=1.5, energy_spread=0.6).probe()):
        assert abs(probe.sum() - 1.0) < 1e-4, f'probe sum {probe.sum()}'
        assert probe.min() >= 0.0
    return 'probe intensities sum to 1, with and without Cc'


def c_diffraction_limit():
    # An aberration-free probe is an Airy disk: its size scales as 1 / aperture.
    from pyemaps import Probe
    # 0.12 A pixels: the 50% diameter counts whole pixels, which adds about 6% at this size
    d = [Probe(kv=200, aperture=a, cs=0.0, defocus=0.0, size=30, sampling=256).diameter(50)
         for a in (10.0, 20.0)]
    ratio = d[0] / d[1]
    assert 1.8 < ratio < 2.2, f'50% diameters {d}, ratio {ratio:.3f}, expected about 2'
    # the 50% encircled energy of an Airy disk: radius 0.514 * wavelength / (2 aperture) * 2
    lam = Probe(kv=200).wavelength
    expected = 2 * 0.2572 * lam / 0.010
    assert abs(d[0] - expected) / expected < 0.1, f'{d[0]:.3f} A, Airy {expected:.3f} A'
    return f'50% diameters {d[0]:.3f} and {d[1]:.3f} A (Airy: {expected:.3f} A at 10 mrad)'


def c_symmetric():
    from pyemaps import Probe
    probe = Probe(aperture=15, cs=1.0, defocus=-40, size=40, sampling=128).probe()
    centred = probe[1:, 1:]    # pixel 64 is the center, so drop row and column 0
    diff = np.abs(centred - centred[::-1, ::-1]).max() / probe.max()
    assert diff < 1e-4, f'round probe not centrosymmetric: {diff:.3g}'
    diff = np.abs(centred - centred.T).max() / probe.max()
    assert diff < 1e-4, f'round probe not symmetric about its diagonal: {diff:.3g}'
    return 'a probe with only round aberrations is centrosymmetric'


def c_empty_ronchigram():
    # With no sample, the Ronchigram is the aperture: a bright disk of the aperture's radius.
    from pyemaps import Probe
    p = Probe(kv=200, aperture=20, cs=1.0, size=100, sampling=256)
    ron = p.ronchigram(np.zeros((256, 256)))
    step = 1000 * p.wavelength / p.size              # mrad per pixel
    yy, xx = np.indices(ron.shape)
    r = np.hypot(xx - 128, yy - 128) * step
    inside, outside = ron[r < 18].mean(), ron[r > 22].mean()
    assert outside < 1e-3 * inside, f'outside {outside:.3g}, inside {inside:.3g}'
    spread = ron[r < 18].std() / inside
    assert spread < 1e-3, f'disk not uniform: {spread:.3g}'
    return f'a uniform disk of 20 mrad ({inside:.4g} inside, {outside:.2g} outside)'


def c_ctf():
    from pyemaps import Probe
    p = Probe(kv=200, cs=1.2, size=50, sampling=256)
    p.scherzer(mode=2)
    ctf = p.ctf()
    assert ctf[128, 128] == 0.0, f'CTF at zero frequency {ctf[128, 128]}'
    assert np.abs(ctf).max() <= 1.0
    # at Scherzer focus the CTF has one sign out to near the first zero
    row = ctf[128, 129:]
    k = np.arange(1, row.size + 1) / p.size
    band = row[(k > 0.15) & (k < 0.3)]
    assert np.all(band > 0) or np.all(band < 0), 'CTF changes sign within the Scherzer band'
    damped = Probe(kv=200, cs=1.2, cc=1.5, energy_spread=1.0, semi_angle=0.5,
                   size=50, sampling=256)
    damped.scherzer(mode=2)
    assert np.abs(damped.ctf()).sum() < np.abs(ctf).sum(), 'envelopes don\'t damp the CTF'
    return 'zero at the center, one sign in the Scherzer band, damped by the envelopes'


def hrem_lens(**kwargs):
    # an uncorrected 200 kV TEM at the Scherzer defocus for phase contrast
    from pyemaps import Probe
    p = Probe(kv=200, cs=1.2, size=100, sampling=256, **kwargs)
    p.scherzer(mode=2)
    p.aperture = 20.0
    return p


def c_hrem_plane_wave():
    p = hrem_lens(cc=1.5, energy_spread=0.6, semi_angle=0.2)
    flat = np.ones((256, 256), np.complex64)
    for integrate in (False, True):
        img = p.hrem(flat, integrate=integrate)
        assert np.abs(img - 1.0).max() < 1e-4, f'a plane wave images as {img.min()}..{img.max()}'
    return 'a plane wave images as 1 everywhere, coherent and integrated'


def c_hrem_thon_rings():
    # A weak phase object's image spectrum is its potential's spectrum times CTF^2 (Thon rings).
    p = hrem_lens()
    pot = p.random_potential(density=0.1, z=6, thickness=10, seed=3)
    img = p.hrem(p.exit_wave(pot))
    ctf = p.ctf()
    spec = np.abs(np.fft.fftshift(np.fft.fft2(img - img.mean()))) ** 2
    vspec = np.abs(np.fft.fftshift(np.fft.fft2(pot - pot.mean()))) ** 2
    yy, xx = np.indices(img.shape)
    r = np.hypot(xx - 128, yy - 128).astype(int)
    band = (r > 3) & (r < 0.7 * p.kmax * p.size)          # inside the aperture
    ratio = np.bincount(r[band], spec[band]) / np.maximum(np.bincount(r[band], vspec[band]), 1e-30)
    ctf2 = np.bincount(r[band], ctf[band] ** 2) / np.maximum(np.bincount(r[band]), 1)
    keep = np.bincount(r[band]) > 0
    corr = np.corrcoef(ratio[keep], ctf2[keep])[0, 1]
    assert corr > 0.95, f'image spectrum / potential spectrum vs CTF^2: correlation {corr:.3f}'
    return f'Thon rings follow CTF^2 (correlation {corr:.3f})'


def c_hrem_integrate():
    # Without Cc, the sum over energies is the coherent image.
    p = hrem_lens(energy_spread=0.6, semi_angle=0.2)
    wave = p.exit_wave()
    a, b = p.hrem(wave), p.hrem(wave, integrate=True)
    diff = np.abs(a - b).max() / np.abs(a).max()
    assert diff < 1e-5, f'without Cc, integrated and coherent differ by {diff:.3g}'
    try:
        hrem_lens(energy_spread=0.0).hrem(wave, integrate=True)
    except ValueError:
        pass
    else:
        raise AssertionError('integrate without an energy spread raised no ValueError')
    return 'without Cc the energy sum is the coherent image; it needs an energy spread'


def c_potential():
    p = titan_probe()
    a = p.random_potential(seed=7)
    assert np.array_equal(a, p.random_potential(seed=7)), 'same seed, different potential'
    assert not np.array_equal(a, p.random_potential(seed=8)), 'different seeds, same potential'
    assert a.min() >= 0.0 and a.max() > 0.0
    thicker = p.random_potential(seed=7, thickness=200)
    ratio = thicker.mean() / a.mean()
    assert 1.8 < ratio < 2.2, f'twice the thickness gives {ratio:.3f} times the potential'
    return 'reproducible by seed; proportional to the thickness'


def c_settings():
    from pyemaps import Probe
    p = Probe(kv=200, cs=1.2)
    s = p.scherzer()
    lam = p.wavelength
    assert abs(lam - 0.025079) < 1e-6, f'wavelength {lam}'
    assert abs(s['defocus'] + np.sqrt(1.2e7 * lam) / 10) < 1e-9
    assert abs(p.aperture - (4 / 1.2e7 / lam ** 3) ** 0.25 * lam * 1000) < 1e-9
    c = Probe(kv=300, c5=5.0)
    h = c.haider()
    assert c.cs < 0 and c.defocus > 0 and h['aperture'] > 30
    for bad in (lambda: Probe(cs=0).scherzer(), lambda: Probe().haider(),
                lambda: Probe().set_aberration('q7', 1.0), lambda: Probe(sampling=127).probe(),
                lambda: Probe().ronchigram(np.zeros((8, 8))), lambda: Probe().diameter(0)):
        try:
            bad()
        except ValueError:
            continue
        raise AssertionError('an invalid setting raised no ValueError')
    return f'wavelength {lam:.6f} A, Scherzer and Haider settings, invalid settings refused'


def c_from_file():
    from pyemaps import Probe
    text = ('#microscope parameters\nkv 300\naperture 21.5\ndf_nm -3.2\nc3_mm 0.002\n'
            'c5_mm 2.5\na1_nm 1.2 30\nb2 20 -45\nend\n')
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'mic.txt')
        with open(path, 'w') as f:
            f.write(text)
        p = Probe.from_file(path, size=50, sampling=128)
        with open(path, 'w') as f:
            f.write('kv 200\nfocus 3\n')
        try:
            Probe.from_file(path)
        except ValueError as e:
            assert 'line 2' in str(e), str(e)
        else:
            raise AssertionError('an unknown line was accepted')
    assert (p.kv, p.aperture, p.defocus, p.cs, p.c5) == (300, 21.5, -3.2, 0.002, 2.5)
    assert p.aberrations['a1'] == (1.2, 30.0) and p.aberrations['b2'] == (20.0, -45.0)
    assert (p.size, p.sampling) == (50, 128)
    # the program's other settings: semi, kmax (as the aperture), dim and sam
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'mic.txt')
        with open(path, 'w') as f:
            f.write('kv 300\nsemi 0.5\nkmax 0.5\ndim 50\nsam 128\ntilt 0.2 30\n')
        q = Probe.from_file(path)
    assert (q.semi_angle, q.size, q.sampling, q.tilt) == (0.5, 50.0, 128, (0.2, 30.0))
    assert abs(q.kmax - 0.5) < 1e-9, q.kmax
    return 'program parameter files read, all settings; unknown lines refused with their number'


def c_errors_not_crashes():
    # Bugs that crashed Python or gave silent wrong answers: each is now a clear error.
    import subprocess
    from pyemaps import Probe
    # maps too large: a Python error, not a crash. 65536 pixels overflowed 32-bit integers;
    # the work maps of 32768 x 32768 need about 40 GB, which normally fails to allocate.
    code = ('from pyemaps import Probe\n'
            'for n in (65536, 32768):\n'
            '    try:\n'
            '        Probe(size=100, sampling=n).probe()\n'
            '    except (ValueError, MemoryError) as e:\n'
            '        print("refused:", n, type(e).__name__)\n')
    res = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True)
    assert res.returncode == 0 and 'refused: 65536' in res.stdout, \
        f'exit {res.returncode}: {res.stdout[-200:]} {res.stderr[-200:]}'
    # a probe wider than the map, and one inside a pixel: no diameter instead of the map's width
    for lens, msg in ((Probe(kv=200, aperture=2, cs=1.2, size=10, sampling=64), 'larger size'),
                      (Probe(kv=300, aperture=40, cs=0, size=200, sampling=256), 'smaller pixels')):
        for interpolate in (False, True):
            try:
                lens.diameter(80 if msg == 'larger size' else 50, interpolate=interpolate)
            except ValueError as e:
                assert msg in str(e), str(e)
            else:
                raise AssertionError(f'diameter gave a value where it should say "{msg}"')
    # more than 1e8 atoms: an error, not an empty potential from an integer overflow
    try:
        Probe(size=5000, sampling=64).random_potential(density=0.1, thickness=1000)
    except ValueError as e:
        assert '1e8 atoms' in str(e), str(e)
    else:
        raise AssertionError('a potential of 2.5e9 atoms raised no error')
    # seeds: 2**31 - 1 is the generator's fixed point
    for seed in (0, 2**31 - 1, 2**40):
        try:
            Probe(sampling=64).random_potential(seed=seed)
        except ValueError:
            continue
        raise AssertionError(f'seed {seed} raised no ValueError')
    assert Probe(sampling=64).random_potential(seed=2**31 - 2).max() > 0
    # a copy keeps its own aberrations
    import copy
    a = Probe()
    b = copy.copy(a)
    b.set_aberration('a1', 10, 0)
    assert a.aberrations['a1'] == (0.0, 0.0), a.aberrations['a1']
    return ('large map, probe outside the map or inside a pixel, 1e8 atoms, seeds and copies: '
            'errors or correct results')


def c_phase_map():
    from pyemaps import Probe
    # no envelopes: no Cc, and a point source (semi_angle 0)
    p = Probe(kv=200, aperture=20, cs=1.2, defocus=-40, semi_angle=0.0,
              aberrations={'a1': (5, 30)}, size=50, sampling=256)
    chi, ctf = p.phase_map(), p.ctf()
    n = p.sampling
    yy, xx = np.indices(chi.shape)
    inside = np.hypot(xx - n // 2, yy - n // 2) / p.size < p.kmax    # inside the aperture
    diff = np.abs(np.sin(chi[inside]) - ctf[inside]).max()
    assert diff < 1e-4, f'sin(chi) and the CTF differ by {diff:.3g} inside the aperture'
    assert chi[n // 2, n // 2] == 0.0
    return f'sin(chi) is the CTF without envelopes (within {diff:.1g} inside the aperture)'


def c_stem_mtf_psf():
    from pyemaps import Probe
    n = 256
    p = Probe(kv=200, aperture=20, cs=1.2, defocus=-40, size=50, sampling=n)
    probe = p.probe()
    mtf = p.mtf()
    ref = np.abs(np.fft.fftshift(np.fft.fft2(probe)))
    assert abs(mtf[n // 2, n // 2] - 1) < 1e-5
    assert np.abs(mtf - ref).max() < 1e-5, 'MTF differs from |FFT(probe)|'
    point = np.zeros((n, n), np.float32)
    point[n // 2, n // 2] = 1.0
    assert np.abs(p.stem_image(point) - probe).max() < 1e-5 * probe.max(), \
        'the STEM image of a point is not the probe'
    v = p.random_potential(seed=5)
    conv = np.real(np.fft.ifft2(np.fft.fft2(v) * np.fft.fft2(np.fft.ifftshift(probe))))
    assert np.abs(p.stem_image(v) - conv).max() < 1e-5 * conv.max(), \
        'the STEM image is not the convolution'
    img = p.hrem()
    assert np.abs(p.apply_psf(img, 0.0, 5.0) - img).max() < 1e-5
    assert np.array_equal(p.apply_psf(img), p.apply_psf(img, 0.6, 400.0)), 'PSF defaults'
    w = np.fft.fftshift(np.fft.fftfreq(n))
    wx, wy = np.meshgrid(w, w)
    filt = 0.7 / (1 + 30 * (wx ** 2 + wy ** 2)) + 0.3
    ref = np.real(np.fft.ifft2(np.fft.fft2(img) * np.fft.ifftshift(filt)))
    assert np.abs(p.apply_psf(img, 0.7, 30) - ref).max() < 1e-5 * ref.max(), \
        'the PSF differs from its transfer function'
    return 'MTF = |FFT(probe)|; STEM image = probe convolved with the sample; PSF filter'


def c_focal_series_optimize():
    from pyemaps import Probe
    p = Probe(kv=200, cs=1.2, size=25.6, sampling=256)
    s = p.scherzer()
    series = p.focal_series([-60, s['defocus'], -50], 'probe')
    assert series.shape == (3, 256, 256) and p.defocus == s['defocus']
    assert np.array_equal(series[1], p.probe())
    # the interpolated diameter changes smoothly with the defocus
    sizes = []
    for df in np.linspace(-56, -54, 5):
        p.defocus = df
        sizes.append(p.diameter(50, interpolate=True))
    assert len(set(np.round(sizes, 6))) == 5, f'interpolated diameters plateau: {sizes}'
    # the optimizer removes added astigmatism and finds a defocus near Scherzer's
    p.defocus = -30.0
    p.set_aberration('a1', 15.0, 40.0)
    before = p.diameter(50, interpolate=True)
    r = p.optimize(vary=('defocus', 'a1'))
    assert r['a1'][0] < 1.0, f"a1 left at {r['a1'][0]:.2f} nm"
    assert -60 < r['defocus'] < -45, f"defocus {r['defocus']:.1f} nm"
    assert r['diameter'] < before
    return (f"a focal series; interpolated diameters move smoothly; optimize: a1 15 -> "
            f"{r['a1'][0]:.2f} nm, d50 {before:.2f} -> {r['diameter']:.2f} A")


class Skip(Exception):
    """A check that can't run here, such as a licensed one without a license."""


def has_routine(name):
    # whether this emaps has the backend routine (2.6.0 and later for the crystal ones)
    from pyemaps import probe as probe_module
    return probe_module.probesim is not None and hasattr(probe_module.probesim, name)


_LICENSED = None


def licensed():
    # whether the multislice runs here: emaps 2.6.0 or later and an active license
    global _LICENSED
    if _LICENSED is None:
        _LICENSED = False
        if has_routine('msexitwave'):
            from pyemaps import Crystal, LicenseError, Probe
            try:
                Probe(size=10.8614, sampling=32).crystal_exit_wave(
                    Crystal.from_builtin('Silicon'), thickness=5.4307)
                _LICENSED = True
            except LicenseError:
                pass
    return _LICENSED


def require(name):
    if not has_routine(name):
        raise Skip(f'this emaps has no {name} (emaps 2.6.0 and later)')


def require_license():
    require('msexitwave')
    if not licensed():
        raise Skip('no active pyEMAPS license: the multislice is a licensed feature')


def multislice_maps():
    # silicon [110], 12 a across, fitted: exit waves at 50 and 200 A, and a corrected probe's
    # Ronchigram at 100 A
    from pyemaps import Crystal, Probe
    si = Crystal.from_builtin('Silicon')
    a = float(si.cell.a)
    p = Probe(kv=200, size=12 * a, sampling=256)
    waves = p.crystal_exit_wave(si, zone=(1, 1, 0), thickness=[50, 200], fit=True)
    c = Probe(kv=200, aperture=25, c5=3.829, size=12 * a, sampling=256)
    c.haider(optimum_aperture=False)
    return {'ms_exit_wave': waves,
            'ms_ronchigram': c.crystal_ronchigram(si, zone=(1, 1, 0), thickness=100, fit=True)}


def c_crystal_fit():
    require('crystalpotential')
    from pyemaps import Crystal, Probe
    si = Crystal.from_builtin('Silicon')
    a = float(si.cell.a)
    # Si [110] repeats every a/sqrt(2) along [1-10] and a along [001]; along [110] the
    # face-centering halves the cell vector
    r = Probe().crystal_repeats(si, zone=(1, 1, 0), max_size=80)
    lengths = sorted(np.hypot(*v) for v in r['repeats'])
    assert np.allclose(lengths, [a / np.sqrt(2), a], atol=1e-4), r['repeats']
    assert abs(r['period'] - a / np.sqrt(2)) < 1e-4, r['period']
    assert r['x_axis'] == (0, 0, 1), r['x_axis']
    fits = [(s, e) for s, e in r['sizes'] if abs(s - 12 * a) < 0.01]
    assert fits and abs(fits[0][1] - 0.00173) < 5e-5, r['sizes']
    r001 = Probe().crystal_repeats(si, zone=(0, 0, 1), max_size=12)
    assert abs(r001['period'] - a) < 1e-4 and abs(r001['sizes'][0][0] - a) < 1e-3, r001
    # fitted, the map has no seam: the map twice as large is the small one 2 x 2
    small = Probe(size=12 * a, sampling=128).crystal_potential(si, zone=(1, 1, 0), thickness=30,
                                                               fit=True)
    large = Probe(size=24 * a, sampling=256).crystal_potential(si, zone=(1, 1, 0), thickness=30,
                                                               fit=True)
    tiled = np.tile(small, (2, 2))
    rel = np.abs(large - tiled).max() / large.max()
    assert rel < 1e-4, f'fitted maps differ from their tiling by {rel:.2g}'
    plain = Probe(size=24 * a, sampling=256).crystal_potential(si, zone=(1, 1, 0), thickness=30)
    plain_small = Probe(size=12 * a, sampling=128).crystal_potential(si, zone=(1, 1, 0),
                                                                     thickness=30)
    seam = np.abs(plain - np.tile(plain_small, (2, 2))).max() / plain.max()
    return (f'Si [110]: repeats {lengths[0]:.4f} and {lengths[1]:.4f} A, period '
            f'{r["period"]:.4f} A, 12a fits with {100 * fits[0][1]:.3f}% strain; fitted maps tile '
            f'exactly ({rel:.1g}), unfitted ones differ by {seam:.2f} at the seam')


def c_multislice():
    require_license()
    from pyemaps import Crystal, Probe
    si = Crystal.from_builtin('Silicon')
    a = float(si.cell.a)
    period = a / np.sqrt(2)
    # 0.13 A pixels: the band limit, 2.6 1/A, keeps nearly all that silicon scatters
    p = Probe(kv=200, size=12 * a, sampling=512)
    lines = []
    # one slice without the band limit is the projection: exit_wave of crystal_potential, and
    # the probe module's Ronchigram
    one = p.crystal_exit_wave(si, zone=(1, 1, 0), thickness=period, slice_thickness=period,
                              fit=True, bandlimit=False)
    pot = p.crystal_potential(si, zone=(1, 1, 0), thickness=period, fit=True)
    d = np.abs(one - p.exit_wave(pot)).max()
    assert d < 1e-5, f'one slice differs from exit_wave by {d:.2g}'
    c = Probe(kv=200, aperture=25, c5=3.829, size=12 * a, sampling=512)
    c.haider(optimum_aperture=False)
    r1 = c.crystal_ronchigram(si, zone=(1, 1, 0), thickness=period, slice_thickness=period,
                              fit=True, bandlimit=False)
    ref = c.ronchigram(pot)
    dr = np.abs(r1 - ref).max() / ref.max()
    assert dr < 1e-5, f'one slice differs from ronchigram by {dr:.2g}'
    lines.append(f'one slice = exit_wave ({d:.1g}) and ronchigram ({dr:.1g})')
    # a list of thicknesses gives the same waves as one at a time
    both = p.crystal_exit_wave(si, zone=(1, 1, 0), thickness=[50, 200], fit=True)
    for k, t in enumerate((50, 200)):
        assert np.array_equal(both[k], p.crystal_exit_wave(si, zone=(1, 1, 0), thickness=t,
                                                           fit=True)), f'{t} A differs'
    # the total intensity is kept, but for what the crystal scatters beyond the band limit
    norm = float(np.mean(np.abs(both[1]) ** 2))
    assert 0.98 < norm <= 1.0 + 1e-6, f'mean intensity {norm:.4f} at 200 A'
    # and so do long lists, for both methods: emaps once passed the unused output array with
    # one element per thickness declared but one allocated, so a long list overran the stack
    # and returned zero waves
    q = Probe(kv=200, aperture=3.0, size=4 * a, sampling=128)
    many = np.arange(10, 510, 10)
    for method in (q.crystal_exit_wave, q.crystal_ronchigram):
        out = method(si, zone=(0, 0, 1), thickness=many, x_axis=(1, 0, 0))
        for k in (0, 24, 49):
            alone = method(si, zone=(0, 0, 1), thickness=many[k], x_axis=(1, 0, 0))
            assert np.array_equal(out[k], alone), \
                f'{method.__name__}: {many[k]} A of a list of 50 differs from a single run'
    lines.append(f'thickness lists (2 and 50) = single runs; mean intensity {norm:.4f} at 200 A')

    # Bloch waves (emaps): beam intensities of Si [001] at the exact zone axis. Bloch includes
    # absorption and fewer beams, so they agree within about 10%
    from pyemaps import EMC, SIMC
    q = Probe(kv=200, size=8 * a, sampling=256)
    waves = q.crystal_exit_wave(si, zone=(0, 0, 1), thickness=[100, 200], x_axis=(1, 0, 0))
    si.beginBloch(sampling=2, em_controls=EMC(zone=(0, 0, 1), vt=200, simc=SIMC(gmax=2.0)))
    worst = 0.0
    try:
        for k, t in enumerate((100, 200)):
            n, scm, ev, beams = si.getSCMatrix(ib_coords=(0, 0), sample_thickness=t)
            beams = np.asarray(beams)
            beams = beams if beams.shape[-1] == 3 else beams.T
            index = {tuple(int(v) for v in b): i for i, b in enumerate(beams)}
            amp = np.asarray(scm)[:, index[(0, 0, 0)]]
            f = np.fft.fft2(waves[k]) / waves[k].size
            for h, kk in ((0, 0), (2, 2), (4, 0)):
                ms = abs(f[(8 * kk) % 256, (8 * h) % 256]) ** 2
                bl = abs(amp[index[(h, kk, 0)]]) ** 2
                worst = max(worst, abs(ms - bl) / bl)
                assert abs(ms - bl) <= 0.1 * bl + 0.002, \
                    f'{h}{kk}0 at {t} A: multislice {ms:.4f}, Bloch {bl:.4f}'
    finally:
        si.endBloch()
    lines.append(f'Si [001] 000, 220, 400 at 100 and 200 A within {100 * worst:.0f}% of Bloch')
    return '; '.join(lines)


def c_license():
    # without a license: the multislice and the database generator refuse, with LicenseError,
    # and the free crystal potential still works. LOCALAPPDATA points the license check at an
    # empty folder, in a subprocess, so the real license isn't touched
    require('msexitwave')
    import subprocess
    code = ('from pyemaps import Crystal, LicenseError, Probe\n'
            'si = Crystal.from_builtin("Silicon")\n'
            'p = Probe(size=10.8614, sampling=32)\n'
            'for name, f in (("exit", lambda: p.crystal_exit_wave(si, thickness=5.4307)),\n'
            '                ("ronchigram", lambda: p.crystal_ronchigram(si, thickness=5.4307)),\n'
            '                ("dpgen", lambda: si.generateDPDB())):\n'
            '    try:\n'
            '        f()\n'
            '        print("ran:", name)\n'
            '    except LicenseError:\n'
            '        print("refused:", name)\n'
            'print("free potential:", float(p.crystal_potential(si).max()) > 0)\n')
    with tempfile.TemporaryDirectory() as empty:
        env = dict(os.environ, LOCALAPPDATA=empty)
        res = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True,
                             env=env, cwd=empty)
    out = res.stdout
    for name in ('exit', 'ronchigram', 'dpgen'):
        assert f'refused: {name}' in out, f'{name} without a license: {out[-300:]} {res.stderr[-300:]}'
    assert 'free potential: True' in out, out[-300:]
    return ('without a license, crystal_exit_wave, crystal_ronchigram and generateDPDB raise '
            'LicenseError; crystal_potential still works')


def crystal_map():
    # silicon along [110], with [001] across: 12 a is 17 repeats along y within 0.2%
    from pyemaps import Crystal, Probe
    si = Crystal.from_builtin('Silicon')
    p = Probe(kv=200, size=12 * float(si.cell.a), sampling=256)
    return p.crystal_potential(si, zone=(1, 1, 0), thickness=30.0)


def c_crystal_potential():
    require('crystalpotential')
    from pyemaps import Crystal, Probe
    from pyemaps.probe import _slab_atoms
    lines = []
    # 1. The map's Fourier coefficients, per unit thickness, are emaps' electron structure
    # factors in volts: along [001], with a map of 8 cells and a slab of 10.
    for name, hkls in (('Silicon', ((2, 2, 0), (4, 0, 0))), ('Aluminium', ((2, 0, 0), (2, 2, 0)))):
        c = Crystal.from_builtin(name)
        a = float(c.cell.a)
        p = Probe(kv=200, size=8 * a, sampling=128)
        v = p.crystal_potential(c, zone=(0, 0, 1), thickness=10 * a, x_axis=(1, 0, 0))
        f = np.fft.fft2(v) / v.size / (10 * a)
        csf = c.generateCSF(kv=200, smax=1.0, sftype=2, aptype=0)
        table = {tuple(sorted(abs(int(i)) for i in d['hkl'])): complex(d['amp_re'], d['phase_im'])
                 for d in csf[1:]}
        for h, k, l in hkls:
            got = f[8 * k % 128, 8 * h % 128]
            ref = table[tuple(sorted((h, k, l)))]
            assert abs(got - ref) <= 1e-4 * abs(ref), \
                f'{name} {h}{k}{l}: map {got:.5f} V, emaps structure factor {ref:.5f} V'
            lines.append(f'{name} {h}{k}{l} {got.real:.4f} V')
        # the mean inner potential doesn't depend on the thickness
        thin = p.crystal_potential(c, zone=(0, 0, 1), thickness=5 * a, x_axis=(1, 0, 0))
        mip, mip_thin = v.mean() / (10 * a), thin.mean() / (5 * a)
        assert abs(mip - mip_thin) <= 1e-5 * mip, f'{name}: mean inner potential {mip}, {mip_thin}'
        # moving the crystal by whole pixels moves the map
        moved = p.crystal_potential(c, zone=(0, 0, 1), thickness=10 * a, x_axis=(1, 0, 0),
                                    shift=(3 * p.size / 128, 5 * p.size / 128))
        assert np.allclose(moved, np.roll(v, (5, 3), axis=(0, 1)), rtol=0,
                           atol=1e-4 * v.max()), f'{name}: shift doesn\'t move the map'
        lines.append(f'mean inner potential {mip:.2f} V')

    # 2. The slab's atoms are mxtal's, in an oblique cell with mixed sites (Li2MnO3, monoclinic)
    c = Crystal.from_builtin('Li2MnO3')
    size, depth, zone = 15.0, 10.0, (1, 1, 0)
    mine = np.concatenate([xyz for xyz, _ in _slab_atoms(c, zone, None, size, depth).values()])
    from pyemaps.probe import _lattice, _perpendicular
    lat = _lattice(c.cell)
    ez = np.asarray(zone, float) @ lat
    ez /= np.linalg.norm(ez)
    ex = _perpendicular(zone, lat) @ lat
    ex -= (ex @ ez) * ez
    ex /= np.linalg.norm(ex)
    cell = lat @ np.array([ex, np.cross(ez, ex), ez]).T
    corners = np.array([[i * size, j * size, k * depth]
                        for i in (0, 1) for j in (0, 1) for k in (0, 1)]) @ np.linalg.inv(cell)
    mx = c.generateMxtal(cellbox=[list(np.floor(corners.min(0)) - 1),
                                  list(np.ceil(corners.max(0)) + 1)],
                         xz=[list(ex @ np.linalg.inv(lat)), list(map(float, zone))])
    theirs = np.array([at.coord for at in mx.acoordList], dtype=float)
    inside = np.all((theirs >= 1e-3) & (theirs < np.array([size, size, depth]) - 1e-3), axis=1)
    theirs = theirs[inside]
    mine_in = mine[np.all((mine >= 1e-3) & (mine < np.array([size, size, depth]) - 1e-3), axis=1)]
    d1 = np.min(np.linalg.norm(mine_in[:, None] - theirs[None], axis=2), axis=1)
    d2 = np.min(np.linalg.norm(theirs[:, None] - mine_in[None], axis=2), axis=1)
    assert d1.max() < 1e-3 and d2.max() < 1e-3, \
        f'slab atoms and mxtal differ by up to {max(d1.max(), d2.max()):.3g} A'
    lines.append(f'Li2MnO3 [110] slab = mxtal ({len(theirs)} positions)')

    # 3. errors
    si = Crystal.from_builtin('Silicon')
    p = Probe(size=20, sampling=64)
    for kwargs in ({'zone': (0, 0, 0)}, {'thickness': 0}, {'x_axis': (0, 0, 3)},
                   {'thickness': 1e9}):
        try:
            p.crystal_potential(si, **kwargs)
        except ValueError:
            continue
        raise AssertionError(f'no error for {kwargs}')
    return '; '.join(lines)


def c_show():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    p = titan_probe()
    fig, axes = plt.subplots(1, 4)
    p.show(p.ronchigram(), 'ronchigram', ax=axes[0])
    p.show(p.probe(), 'probe', ax=axes[1])
    p.show(p.ctf(), 'ctf', ax=axes[2])
    p.show(p.hrem(), 'hrem', ax=axes[3])
    assert axes[0].get_xlabel() == 'mrad' and axes[2].get_xlabel() == '1/Å'
    assert axes[3].get_xlabel() == 'Å'
    plt.close(fig)
    return 'Ronchigram, probe, CTF and HREM image displayed with their axes'


def main():
    from pyemaps import probe as probe_module
    if probe_module.probesim is None:
        print('++++++ Probe checks SKIPPED: this emaps has no probe module ++++++')
        return 0
    if '-bg' in sys.argv[1:]:
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(BASELINE, **results())
        print(f'Baseline written: {BASELINE}')
        return 0
    for name, fn in (('baseline', c_baseline),
                     ('normalized probes', c_normalized),
                     ('diffraction limit', c_diffraction_limit),
                     ('round probe symmetry', c_symmetric),
                     ('Ronchigram without a sample', c_empty_ronchigram),
                     ('CTF', c_ctf),
                     ('HREM of a plane wave', c_hrem_plane_wave),
                     ('HREM Thon rings', c_hrem_thon_rings),
                     ('HREM energy sum', c_hrem_integrate),
                     ('random potential', c_potential),
                     ('settings', c_settings),
                     ('parameter files', c_from_file),
                     ('errors, not crashes or wrong answers', c_errors_not_crashes),
                     ('phase map', c_phase_map),
                     ('STEM image, MTF and PSF', c_stem_mtf_psf),
                     ('focal series and optimizer', c_focal_series_optimize),
                     ('crystal potential', c_crystal_potential),
                     ('seam-free crystal maps', c_crystal_fit),
                     ('multislice', c_multislice),
                     ('licensed features without a license', c_license),
                     ('plots', c_show)):
        check(name, fn)
    for name, ok, msg in RESULTS:
        print(f'{"SKIP" if ok is None else "PASS" if ok else "FAIL"}  {name}: {msg}')
    failed = [r for r in RESULTS if r[1] is False]
    skipped = [r for r in RESULTS if r[1] is None]
    if failed:
        print(f'------ Probe checks FAILED: {len(failed)} of {len(RESULTS)} ------')
        return 1
    note = f', {len(skipped)} skipped' if skipped else ''
    print(f'++++++ Probe checks SUCCEEDED: {len(RESULTS) - len(skipped)} checks{note} ++++++')
    return 0


if __name__ == '__main__':
    os.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')
    sys.exit(main())
