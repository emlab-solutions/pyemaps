"""
Make the two animated stereodiagrams of the Stereodiagrams page in the User Guide:

- stereo_zones.gif: Silicon at the six zone axes of the page's example, one after another;
- stereo_tilt.gif: Silicon at the [001] zone axis as the sample tilts about x, then about y.

The frames are drawn as pyemaps.display.showStereo draws a stereodiagram. Run it from anywhere,
with emaps installed; the GIFs are written to docs/source/_static/images.

    python docs/scripts/stereo_animations.py
"""
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.animation import FuncAnimation, PillowWriter

from pyemaps import EMC, Crystal

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'source', '_static',
                       'images')
SIZE = 5.0            # figure size, inches
DPI = 100             # 500 x 500 pixels
ZLIMIT = 1            # label the poles whose Miller indices are all within this value


def draw(ax, poles, title, caption):
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


def animate(frames, name, interval):
    """Write the frames, (poles, caption) pairs, as a looping GIF, *interval* ms per frame."""
    fig, ax = plt.subplots(figsize=(SIZE, SIZE), dpi=DPI)
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.02, top=0.92)

    def update(i):
        poles, caption = frames[i]
        draw(ax, poles, 'Silicon', caption)

    anim = FuncAnimation(fig, update, frames=len(frames), interval=interval)
    path = os.path.normpath(os.path.join(OUT_DIR, name))
    anim.save(path, writer=PillowWriter(fps=1000.0 / interval))
    plt.close(fig)
    print(f'{path}: {len(frames)} frames, {os.path.getsize(path) // 1024} KB')


def zone_frames(si):
    """The page's example: the zone axes (i, -i, 1) for i from -3 to 2."""
    frames = []
    for i in range(-3, 3):
        emc = EMC(zone=(i, -i, 1))
        frames.append((si.generateStereo(zone=emc.zone), emc.plot_format()))
    return frames


def tilt_frames(si, limit=20, step=2):
    """[001], tilted about x from 0 to +limit, to -limit and back to 0, then the same about y."""
    up = list(range(0, limit, step))
    sweep = up + [limit - t for t in range(0, 2 * limit, step)] + [t - limit for t in up]
    tilts = [(t, 0) for t in sweep] + [(0, t) for t in sweep]
    frames = []
    for tx, ty in tilts:
        poles = si.generateStereo(zone=(0, 0, 1), tilt=(float(tx), float(ty)))
        frames.append((poles, f'zone=(0,0,1); tilt=({tx:.0f}, {ty:.0f}) degrees'))
    return frames


if __name__ == '__main__':
    si = Crystal.from_builtin('Silicon')
    animate(zone_frames(si), 'stereo_zones.gif', interval=1500)
    animate(tilt_frames(si), 'stereo_tilt.gif', interval=120)
