"""
Make the card thumbnails of the landing page and the Examples page: one picture per subject, drawn
at the cards' shape, with no titles, captions or axis labels, zoomed to what the card is about.
Both pages' cards show them in a header 170 pixels high and about 280 wide, so the thumbnails are
560 x 340 pixels, twice that for sharp screens; a card of the same subject on either page uses the
same thumbnail.

The pictures come from pyEMAPS's own calculations, with the samples' settings. The 4D-STEM maps
and the multislice need an active pyEMAPS license. Run it from anywhere, with emaps installed;
the thumbnails are written to docs/source/_static/images/cards:

    python docs/scripts/card_thumbnails.py              # all of them
    python docs/scripts/card_thumbnails.py ctf hrem     # only these subjects
"""
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patches

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.normpath(os.path.join(HERE, '..', 'source', '_static', 'images', 'cards'))
IMAGES = os.path.normpath(os.path.join(HERE, '..', 'source', '_static', 'images'))
SAMPLES = os.path.normpath(os.path.join(HERE, '..', '..', 'samples'))

SIZE = (560, 340)       # the cards' header shape, at twice its pixels
DPI = 100


# --------------------------------------------------------------------------------------------
# drawing helpers
# --------------------------------------------------------------------------------------------
def canvas(size, background='white'):
    """A figure of *size* pixels with one axes filling it, no frame."""
    w, h = size
    fig = plt.figure(figsize=(w / DPI, h / DPI), dpi=DPI, facecolor=background)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_axis_off()
    ax.set_facecolor(background)
    return fig, ax


def save(fig, name):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, name + '.png')
    fig.savefig(path, dpi=DPI, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f'{path}: {os.path.getsize(path) // 1024} KB')


def fit_window(half, size):
    """x and y half-widths of a window *half* across its shorter side, at the shape of *size*."""
    w, h = size
    return (half * w / h, half) if w >= h else (half, half * h / w)


def crop_to(image, size, zoom=1.0):
    """The centre of a 2-D or RGB array, at the shape of *size*, magnified by *zoom*."""
    rows, cols = image.shape[:2]
    w, h = size
    if cols / rows > w / h:             # wider than the frame: crop the sides
        ch, cw = rows, rows * w / h
    else:
        cw, ch = cols, cols * h / w
    ch, cw = int(round(ch / zoom)), int(round(cw / zoom))
    r0, c0 = (rows - ch) // 2, (cols - cw) // 2
    return image[r0:r0 + ch, c0:c0 + cw]


def show_image(image, size, name, cmap='gray', zoom=1.0, background='black', **kw):
    fig, ax = canvas(size, background)
    ax.imshow(crop_to(image, size, zoom), cmap=cmap, interpolation=kw.pop('interpolation', 'antialiased'),
              aspect='auto', **kw)
    save(fig, name)


# --------------------------------------------------------------------------------------------
# subjects: each draws one picture at each requested size
# --------------------------------------------------------------------------------------------
def kinematic(sizes):
    """Silicon's kinematic pattern at [001]: Kikuchi lines and diffracted beams."""
    from pyemaps import Crystal, EMC
    _, dp = Crystal.from_builtin('Silicon').generateDP(em_controls=EMC(zone=(0, 0, 1)))
    reach = max(max(abs(d.c.x), abs(d.c.y)) for d in dp.disks)
    for size, name in sizes:
        fig, ax = canvas(size)
        hx, hy = fit_window(0.62 * reach, size)
        ax.set_xlim(-hx, hx)
        ax.set_ylim(-hy, hy)
        ints = [k.intensity for k in dp.klines]
        lo, hi = min(ints), max(ints)
        for k in dp.klines:
            ax.plot([k.pt1.x, k.pt2.x], [k.pt1.y, k.pt2.y], color='black', linewidth=1.6,
                    alpha=float(k.calOpacity(lo, hi)))
        for d in dp.disks:
            ax.add_patch(patches.Circle((d.c.x, d.c.y), d.r * 1.6, fc='#1f4fd1', ec='none'))
        save(fig, name)


def bloch(sizes):
    """Silicon's Bloch-wave CBED pattern at [001], 1750 Å thick, in grey scale (showBloch's default)."""
    from pyemaps import Crystal, EMC
    res = Crystal.from_builtin('Silicon').generateBloch(
        sampling=20, sample_thickness=(1750, 1750, 100), em_controls=EMC())
    image = np.asarray(res.blochList[0][1])
    for size, name in sizes:
        show_image(image, size, name, cmap='gray', zoom=1.45, background='black')


def stereo(sizes):
    """Silicon's stereodiagram at [001], the poles only."""
    from pyemaps import Crystal
    poles = Crystal.from_builtin('Silicon').generateStereo(zone=(0, 0, 1))
    for size, name in sizes:
        fig, ax = canvas(size)
        hx, hy = fit_window(0.78, size)
        ax.set_xlim(-hx, hx)
        ax.set_ylim(-hy, hy)
        ax.add_patch(patches.Circle((0, 0), 1.0, fill=False, linewidth=1.2, color='#1f4fd1'))
        for p in poles:
            ax.add_patch(patches.Circle((float(p['c'][0]), float(p['c'][1])),
                                        float(p['r']) * 1.5, fc='#1f4fd1', ec='none'))
        save(fig, name)


def powder(sizes):
    """Silicon's electron powder profile: the curve only."""
    from pyemaps import Crystal
    x, y = np.asarray(Crystal.from_builtin('Silicon').generatePowder())
    keep = x <= 0.045
    x, y = x[keep], y[keep] / y[keep].max()
    for size, name in sizes:
        fig, ax = canvas(size)
        ax.fill_between(x, 0, y, color='#d62728', alpha=0.15, linewidth=0)
        ax.plot(x, y, color='#d62728', linewidth=2.0)
        ax.set_xlim(x[0], x[-1])
        ax.set_ylim(-0.03, 1.08)
        save(fig, name)


def crystal(sizes):
    """The silicon supercell picture, cropped to the card."""
    image = plt.imread(os.path.join(IMAGES, 'mxtal01.png'))[..., :3]
    for size, name in sizes:
        show_image(image, size, name, zoom=1.12)


def ronchigram(sizes):
    """The Ronchigram of an uncorrected lens, with an open aperture: its aberration rings."""
    from pyemaps import Probe
    lens = Probe(kv=200, cs=1.2, size=100, sampling=512)
    lens.aperture = 25.0
    image = lens.ronchigram()
    for size, name in sizes:
        show_image(image, size, name, zoom=1.9)


def stem_probe(sizes):
    """The corrected STEM probe, on a log scale to show its tails."""
    from pyemaps import Probe
    lens = Probe(kv=200, aperture=25, c5=3.829, size=25.6, sampling=512)
    lens.haider(optimum_aperture=False)
    lens.set_aberration('a1', 6.0, 40.0)             # a little astigmatism, for its shape
    image = np.log10(lens.probe() + 1e-9)
    for size, name in sizes:
        show_image(image, size, name, cmap='inferno', zoom=3.2, vmin=image.max() - 4.5)


def ctf(sizes):
    """The contrast transfer function of an uncorrected lens near Scherzer defocus, in 2-D."""
    from pyemaps import Probe
    tem = Probe(kv=200, cs=1.2, cc=1.5, energy_spread=0.7, semi_angle=0.2, size=200, sampling=1024)
    tem.scherzer(mode=2)
    tem.defocus = tem.defocus - 40.0                 # further underfocus: more rings
    image = tem.ctf()
    for size, name in sizes:
        show_image(image, size, name, cmap='RdBu_r', zoom=4.5, vmin=-1, vmax=1,
                   background='white')


def hrem(sizes):
    """Thon rings: the diffractogram of an HREM image of amorphous carbon."""
    from pyemaps import Probe
    lens = Probe(kv=200, cs=1.2, cc=1.5, energy_spread=0.7, semi_angle=0.2, size=100, sampling=512)
    lens.scherzer(mode=2)
    lens.defocus = lens.defocus - 30.0
    lens.aperture = 40.0
    carbon = lens.random_potential(density=0.1, z=6, thickness=50, seed=7)
    image = lens.hrem(lens.exit_wave(carbon))
    gram = np.log1p(np.abs(np.fft.fftshift(np.fft.fft2(image - image.mean()))))
    for size, name in sizes:
        show_image(gram, size, name, zoom=2.6, vmin=np.percentile(gram, 30),
                   vmax=np.percentile(gram, 99.7))


def multislice(sizes):
    """Silicon [110], 300 Å thick, by multislice: its CBED pattern."""
    from pyemaps import Crystal, Probe
    si = Crystal.from_cif(os.path.join(SAMPLES, 'Si_COD_2102763.cif'))
    a = float(si.cell.a)
    probe = Probe(kv=200, aperture=3.0, cs=1.2, defocus=0.0, size=24 * a, sampling=1024)
    pattern = probe.crystal_ronchigram(si, zone=(1, 1, 0), thickness=300, fit=True)
    image = np.log10(pattern + pattern.max() * 1e-5)
    for size, name in sizes:
        show_image(image, size, name, cmap='magma', zoom=2.6)


def al_ediom(sizes):
    """The sample image al.img: an experimental Aluminium diffraction pattern."""
    from pyemaps import read_image
    image = np.asarray(read_image(os.path.join(SAMPLES, 'al.img')).data, dtype=float)
    image = image.reshape(image.shape[-2:]) if image.ndim > 2 else image
    image = np.log1p(image - image.min())
    for size, name in sizes:
        show_image(image, size, name, cmap='gray', zoom=1.25,
                   vmin=np.percentile(image, 20), vmax=np.percentile(image, 99.8))


def _quiet_sample(module):
    """Import a 4D-STEM sample with its plot turned off."""
    import importlib
    sys.path.insert(0, SAMPLES)
    mod = importlib.import_module(module)
    mod.show = lambda *a, **k: None
    return mod


def orientmap(sizes):
    """The orientation map of the al_orientmap.py sample's synthetic scan, in IPF colours."""
    m = _quiet_sample('al_orientmap').map_scan()
    colours = m.ipf_colors()
    for size, name in sizes:
        show_image(colours, size, name, interpolation='nearest')


def phasemap(sizes):
    """The phase map of the al_cu_phasemap.py sample's synthetic scan of aluminium and copper."""
    pm = _quiet_sample('al_cu_phasemap').map_scan()
    colours = pm.phase_colors()
    for size, name in sizes:
        show_image(colours, size, name, interpolation='nearest')


# subject: the function that draws it; the thumbnail is <subject>.png
SUBJECTS = {
    'kinematic': kinematic,
    'bloch': bloch,
    'stereo': stereo,
    'powder': powder,
    'crystal': crystal,
    'ronchigram': ronchigram,
    'stem_probe': stem_probe,
    'ctf': ctf,
    'hrem': hrem,
    'multislice': multislice,
    'al_ediom': al_ediom,
    'orientmap': orientmap,
    'phasemap': phasemap,
}

if __name__ == '__main__':
    names = sys.argv[1:] or list(SUBJECTS)
    for n in names:
        SUBJECTS[n]([(SIZE, n)])
