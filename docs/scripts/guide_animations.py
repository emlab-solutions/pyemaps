"""
Make the animations of the User Guide pages, Silicon in each:

- stereo_zones.gif, stereo_tilt.gif (Stereodiagrams): the six zone axes of the page's example,
  one after another; [001] as the sample tilts about x, then about y;
- dif_zones.gif, dif_tilt.gif (Kinematic diffraction): the page's example, CBED patterns at its
  six zone axes; the [001] pattern as the sample tilts about x, then about y;
- bloch_thickness.gif, bloch_zones.gif, bloch_tilt.gif (Dynamic diffraction): the page's example
  through the sample thickness; the si_bloch.py sample's six zone axes; [001] as the sample
  tilts about x, then about y (camera length 1000 mm for both, for larger disks).

The diffraction frames are drawn by pyemaps.display, as showDif and showBloch draw them in a
notebook; the stereodiagram frames as showStereo draws them. Run it from anywhere, with emaps
installed; the GIFs are written to docs/source/_static/images:

    python docs/scripts/guide_animations.py                  # all of them
    python docs/scripts/guide_animations.py dif_tilt         # only these
"""
import copy
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patches
from matplotlib.animation import FuncAnimation, PillowWriter
from PIL import Image

from pyemaps import EMC, SIMC, Crystal

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'source', '_static',
                       'images')
SIZE = 5.0            # figure size, inches
DPI = 100             # 500 x 500 pixels, the stereodiagrams
DIF_DPI = 80          # 400 x 400 pixels, the diffraction animations: many frames, kept light
ZLIMIT = 1            # label the poles whose Miller indices are all within this value


def sweep(limit, step):
    """Tilts from 0 to +limit, to -limit and back to 0, about x and then about y."""
    n = int(round(limit / step))
    one = [i * step for i in range(n)] + [limit - i * step for i in range(2 * n)] + \
          [i * step - limit for i in range(n)]
    return [(t, 0.0) for t in one] + [(0.0, t) for t in one]


def write_gif(images, name, interval):
    """Write RGB frames as a looping GIF, *interval* ms each."""
    path = os.path.normpath(os.path.join(OUT_DIR, name))
    frames = [Image.fromarray(im).convert('P', palette=Image.ADAPTIVE, colors=64) for im in images]
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=interval, loop=0,
                   optimize=True, disposal=1)
    print(f'{path}: {len(frames)} frames, {os.path.getsize(path) // 1024} KB')


# --------------------------------------------------------------------------------------------
# kinematic and dynamic diffraction: drawn by pyemaps.display's own plotter
# --------------------------------------------------------------------------------------------
def display_frames(kind, items):
    """
    Draw each item with pyemaps.display's plotter, as showDif ('dif') or showBloch ('bloch')
    draws one plot with its caption, and return the frames as RGB arrays.

    *items*: for 'dif', (emc, pattern, mode, kshow, ishow); for 'bloch', (emc, image, color).
    """
    from pyemaps import display
    ty = display.TY_DIF if kind == 'dif' else display.TY_BLOCH
    plotter = display.DifPlotter()
    plotter.setup(ty, 'Silicon', False, 1, 1, True, False, 'individual',
                  display.DISPLAY_ONE_SIZE / SIZE)
    plotter.fig.set_dpi(DIF_DPI)
    images = []
    for item in items:
        plotter.draw(copy.deepcopy((0,) + tuple(item)))   # the plotter scales what it draws
        plotter.fig.canvas.draw()
        images.append(np.asarray(plotter.fig.canvas.buffer_rgba())[..., :3].copy())
    plt.close(plotter.fig)
    return images


def dif_zones(si):
    """The Kinematic diffraction page's example: CBED patterns at six zone axes, cl 2500."""
    zones = [(0, 0, 1), (1, 1, 2), (1, 1, 1), (1, 3, 3), (0, 1, 2), (0, 1, 3)]
    items = []
    for zone in zones:
        emc, dp = si.generateDP(mode=2, em_controls=EMC(zone=zone, cl=2500))
        items.append((emc, dp, 2, True, True))
    write_gif(display_frames('dif', items), 'dif_zones.gif', 1500)


def dif_tilt(si, limit=2.0, step=0.2):
    """The [001] spot pattern with its Kikuchi lines, without Miller indices, as the sample tilts."""
    items = []
    for t in sweep(limit, step):
        emc, dp = si.generateDP(em_controls=EMC(zone=(0, 0, 1), tilt=t))
        items.append((emc, dp, 1, True, False))
    write_gif(display_frames('dif', items), 'dif_tilt.gif', 120)


def bloch_thickness(si):
    """The Dynamic diffraction page's example, every 50 Å from 500 to 1750 Å."""
    emc = EMC(zone=(1, 1, 1), vt=100, cl=1000, simc=SIMC(excitation=(0.3, 1.0), bmin=0.1))
    images = si.generateBloch(sampling=40, em_controls=emc, sample_thickness=(500, 1750, 50))
    images.sort()
    items = [(e, img, True) for e, img in images.blochList]
    write_gif(display_frames('bloch', items), 'bloch_thickness.gif', 250)


def bloch_zones(si):
    """The si_bloch.py sample's zone axis series, (0, i, 1), 1750 Å thick, with larger disks (cl 1000)."""
    items = []
    for i in range(-3, 3):
        res = si.generateBloch(sampling=20, sample_thickness=(1750, 1750, 100),
                               em_controls=EMC(zone=(0, i, 1), cl=1000))
        e, img = res.blochList[0]
        items.append((e, img, True))
    write_gif(display_frames('bloch', items), 'bloch_zones.gif', 1500)


def bloch_tilt(si, limit=1.5, step=0.15):
    """[001], 1750 Å thick, as the sample tilts."""
    items = []
    for t in sweep(limit, step):
        res = si.generateBloch(sampling=20, sample_thickness=(1750, 1750, 100),
                               em_controls=EMC(zone=(0, 0, 1), cl=1000, tilt=t))
        e, img = res.blochList[0]
        items.append((e, img, True))
    write_gif(display_frames('bloch', items), 'bloch_tilt.gif', 120)


# --------------------------------------------------------------------------------------------
# stereodiagrams: drawn as showStereo draws them
# --------------------------------------------------------------------------------------------
def draw_stereo(ax, poles, title, caption):
    """Draw one stereodiagram, as showStereo does."""
    ax.clear()
    ax.set_axis_off()
    ax.set_aspect('equal')
    ax.set_xlim(-1.08, 1.08)
    ax.set_ylim(-1.12, 1.08)
    ax.add_patch(patches.Circle((0.0, 0.0), 1.0, fill=False, linewidth=0.5, color='blue'))
    for p in poles:
        centre = (float(p['c'][0]), float(p['c'][1]))
        index = tuple(int(i) for i in p['idx'])
        ax.add_patch(patches.Circle(centre, float(p['r']), fill=True, linewidth=0.5, fc='blue'))
        if all(abs(i) <= ZLIMIT for i in index):
            ax.text(centre[0], centre[1], str(index), {'color': 'red', 'fontsize': 8},
                    horizontalalignment='center', verticalalignment='bottom')
    ax.set_title(title, fontsize=14)
    ax.text(0.0, -1.1, caption, color='grey', fontsize=9, ha='center', va='center')


def animate_stereo(frames, name, interval):
    """Write the frames, (poles, caption) pairs, as a looping GIF, *interval* ms per frame."""
    fig, ax = plt.subplots(figsize=(SIZE, SIZE), dpi=DPI)
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.02, top=0.92)

    def update(i):
        poles, caption = frames[i]
        draw_stereo(ax, poles, 'Silicon', caption)

    anim = FuncAnimation(fig, update, frames=len(frames), interval=interval)
    path = os.path.normpath(os.path.join(OUT_DIR, name))
    anim.save(path, writer=PillowWriter(fps=1000.0 / interval))
    plt.close(fig)
    print(f'{path}: {len(frames)} frames, {os.path.getsize(path) // 1024} KB')


def stereo_zones(si):
    """The Stereodiagrams page's example: the zone axes (i, -i, 1) for i from -3 to 2."""
    frames = []
    for i in range(-3, 3):
        emc = EMC(zone=(i, -i, 1))
        frames.append((si.generateStereo(zone=emc.zone), emc.plot_format()))
    animate_stereo(frames, 'stereo_zones.gif', 1500)


def stereo_tilt(si, limit=20, step=2):
    """[001], tilted about x from 0 to +limit, to -limit and back to 0, then the same about y."""
    frames = []
    for tx, ty in sweep(limit, step):
        poles = si.generateStereo(zone=(0, 0, 1), tilt=(float(tx), float(ty)))
        frames.append((poles, f'zone=(0,0,1); tilt=({tx:.0f}, {ty:.0f}) degrees'))
    animate_stereo(frames, 'stereo_tilt.gif', 120)


ANIMATIONS = {f.__name__: f for f in (stereo_zones, stereo_tilt, dif_zones, dif_tilt,
                                       bloch_thickness, bloch_zones, bloch_tilt)}

if __name__ == '__main__':
    si = Crystal.from_builtin('Silicon')
    for n in sys.argv[1:] or list(ANIMATIONS):
        ANIMATIONS[n](si)
