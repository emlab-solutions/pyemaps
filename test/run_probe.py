'''
Checks for pyEMAPS' probe simulations (pyemaps/probe.py, emaps' probe module): the four modes
(Ronchigram, probe, CTF, HREM) and the random potential and exit wave against a stored baseline,
and physical checks that need no baseline.

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
    return {'potential': pot, 'ronchigram': p.ronchigram(pot), 'probe': p.probe(),
            'ctf': p.ctf(), 'probe_cc': chromatic.probe(), 'ctf_cc': chromatic.ctf(),
            'diameter': np.array([p.diameter(50), p.diameter(80)]),
            'exit_wave': wave, 'hrem': p.hrem(wave), 'hrem_cc': chromatic.hrem(wave),
            'hrem_integrated': chromatic.hrem(wave, integrate=True),
            'phase': p.phase_map(), 'stem': chromatic.stem_image(pot), 'mtf': chromatic.mtf(),
            'psf': p.apply_psf(p.hrem(wave), 0.6, 40.0),
            'diameter_interpolated': np.array([p.diameter(50, interpolate=True),
                                               p.diameter(80, interpolate=True)])}


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
    return 'largest relative differences: ' + ', '.join(worst)


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
                     ('plots', c_show)):
        check(name, fn)
    for name, ok, msg in RESULTS:
        print(f'{"PASS" if ok else "FAIL"}  {name}: {msg}')
    failed = [r for r in RESULTS if not r[1]]
    if failed:
        print(f'------ Probe checks FAILED: {len(failed)} of {len(RESULTS)} ------')
        return 1
    print(f'++++++ Probe checks SUCCEEDED: {len(RESULTS)} checks ++++++')
    return 0


if __name__ == '__main__':
    os.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')
    sys.exit(main())
