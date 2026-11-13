# This file is part of pyEMAPS.
#
# pyEMAPS is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# pyEMAPS is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with pyEMAPS.
# If not, see <https://www.gnu.org/licenses/>.
#
# Author: EMLab Solutions, Inc. Questions and comments: support@emlabsoftware.com

"""pyEMAPS diffraction in DigitalMicrograph (DM).

This sample runs inside DM. It draws Silicon's kinematic diffraction patterns, in CBED and
normal modes, as DM image annotations: Kikuchi lines, diffracted beams (disks) labeled with
their Miller indices and, in CBED mode, HOLZ lines. It then saves dynamic diffraction images
for ErbiumPyrogermanate in a raw image file that DM can import.

pyEMAPS must be installed in DM's Python environment, and that Python must be a version
pyEMAPS supports. Run this script from DM's Python script window.
"""
import numpy as np
import DigitalMicrograph as DM

from pyemaps import EMC, XMAX, YMAX, Crystal

# pyEMAPS diffraction patterns span [-XMAX, XMAX] x [-YMAX, YMAX]. SCALE enlarges them into
# DM image pixels.
SCALE = 4

# Diffraction modes, and their names for the image titles.
NORMAL, CBED = 1, 2
MODE_NAMES = {NORMAL: 'Normal', CBED: 'CBED'}

# DM component types for AddNewComponent.
LINE = 2
OVAL = 6

# Line colors (red, green, blue), from the strongest to the weakest lines.
KIKUCHI_COLORS = ((0.3, 0.3, 0.3), (0.6, 0.6, 0.6), (0.8, 0.8, 0.8), (0.9, 0.9, 0.9))
HOLZ_COLORS = ((0.1, 0.7, 0.3), (0.1, 0.7, 0.6), (0.1, 0.7, 0.8), (0.1, 0.7, 0.9))


def to_image(x, y):
    """Convert a point in pattern coordinates into DM image pixels."""
    return (x + XMAX) * SCALE, (y + YMAX) * SCALE


def lock(component):
    """Stop the user from resizing, moving or deleting a DM component."""
    component.SetResizable(False)
    component.SetMovable(False)
    component.SetDeletable(False)


def line_color(intensity, colors):
    """Pick a line's color from `colors` by its intensity, which is 0 to 5."""
    level = intensity / 5
    if level > 0.8:
        return colors[0]
    if level > 0.6:
        return colors[1]
    if level > 0.4:
        return colors[2]
    return colors[3]


def draw_lines(display, lines, colors, background=None):
    """Draw Kikuchi or HOLZ lines, each colored by its intensity."""
    for x1, y1, x2, y2, intensity in lines:
        line = display.AddNewComponent(LINE, *to_image(x1, y1), *to_image(x2, y2))
        lock(line)
        line.SetForegroundColor(*line_color(intensity, colors))
        if background is not None:
            line.SetBackgroundColor(*background)


def draw_disks(display, disks, mode):
    """Draw the diffracted beams as disks, each labeled with its Miller indices."""
    for x, y, r, h, k, l in disks:
        cx, cy = to_image(x, y)
        radius = r * SCALE

        disk = display.AddNewComponent(OVAL, cx - radius, cy - radius, cx + radius, cy + radius)
        lock(disk)
        disk.SetForegroundColor(0.0, 0.0, 1.0)     # blue
        disk.SetBackgroundColor(0.5, 0.5, 0.75)    # light blue
        disk.SetFillMode(1 if mode == NORMAL else 2)

        # The label goes above the disk in normal mode, and on its center in CBED mode.
        # Measure the label's size with a throwaway annotation first.
        text = f'{h} {k} {l}'
        top, left, bottom, right = DM.NewTextAnnotation(0, 0, text, 10).GetRect()
        width, height = right - left, bottom - top

        label_left = cx - width / 2
        label_top = cy - radius - height if mode == NORMAL else cy - height / 2
        label = DM.NewTextAnnotation(label_left, label_top, text, 10)
        display.AddChildAtEnd(label)
        lock(label)
        label.SetForegroundColor(0.9, 0.0, 0.0)    # red
        label.SetBackgroundColor(1.0, 1.0, 0.5)    # light yellow


def show_pattern(pattern, mode=NORMAL, name='Diamond'):
    """Draw a kinematic diffraction pattern in a new DM image.

    :param pattern: a kinematic diffraction pattern from Crystal.generateDP.
    :param mode: the pattern's diffraction mode, NORMAL or CBED.
    :param name: the crystal name, for the image title.
    :return: 0 on success, 1 for an unsupported mode.
    """
    if mode not in MODE_NAMES:
        print(f'Diffraction mode {mode} is not supported')
        return 1

    # A new DM image with a white background.
    shape = (2 * XMAX * SCALE, 2 * YMAX * SCALE)
    image = DM.CreateImage(np.full(shape, 255.0, dtype=np.float32))
    image.ShowImage()
    image.SetName(f'Kinematic Diffraction Simulation: {name} in {MODE_NAMES[mode]} Mode')

    display = image.GetImageDisplay(0)
    draw_lines(display, pattern.klines, KIKUCHI_COLORS, background=(0.2, 0.2, 0.5))
    draw_disks(display, pattern.disks, mode)
    if mode == CBED:
        draw_lines(display, pattern.hlines, HOLZ_COLORS)

    # Release the Python reference to the image; DM keeps showing it.
    del image
    return 0


def show_silicon_patterns():
    """Generate Silicon's kinematic diffraction patterns and draw them in DM."""
    name = 'Silicon'
    crystal = Crystal.from_builtin(name)
    print(crystal)

    emc = EMC(tilt=(-0.2, 0.5), zone=(1, -1, 2))
    _, pattern = crystal.generateDP(mode=CBED, dsize=0.2, em_controls=emc)
    show_pattern(pattern, mode=CBED, name=name)

    _, pattern = crystal.generateDP()    # normal mode, default controls
    show_pattern(pattern, name=name)


def save_bloch_images():
    """Generate ErbiumPyrogermanate's dynamic diffraction images and save them.

    With bSave=True, pyEMAPS saves the images in a raw image file and prints its path.
    Import that file in DM to view the images.
    """
    name = 'ErbiumPyrogermanate'
    crystal = Crystal.from_builtin(name)
    print(crystal)

    emc = EMC(tilt=(-0.2, 0.5), zone=(1, -1, 2))
    try:
        crystal.generateBloch(em_controls=emc, bSave=True)
    except Exception as e:
        print(f'Failed to run the dynamic diffraction simulation for {name}: {e}')


def main():
    show_silicon_patterns()
    save_bloch_images()


if __name__ == '__main__':
    main()
