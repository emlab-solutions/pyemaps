
"""
This file is part of pyemaps
___________________________

pyemaps is free software for non-comercial use: you can 
redistribute it and/or modify it under the terms of the GNU General 
Public License as published by the Free Software Foundation, either 
version 3 of the License, or (at your option) any later version.

pyemaps is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pyemaps.  If not, see <https://www.gnu.org/licenses/>.

Contact supprort@emlabsoftware.com for any questions and comments.
___________________________

This sample code is to demostrate using pyemaps to generate and render
kinematic diffraction patterns while changing with sample tilt in 
x direction 

Author:     EMLab Solutions, Inc.
Date:       May 07, 2022    

"""
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from pyemaps.errors import BlochListError

DISPLAY_SIZE = 900 # default
PLOT_MULTIPLIER = 6

def find_dpi():
    dpi = 96 #default
    try:
        import tkinter as tk
    except ImportError:
        return dpi

    root = tk.Tk()
    root.withdraw()    
    try:
        import ctypes
    except ImportError as e:
        print(f'failed to find display resolution') 
        print(f'supported python version: >= 3.6')
        print(f'Use default dpi of 96')

        return dpi

    width_px = root.winfo_screenwidth()
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    w = user32.GetSystemMetrics(0)
    
    dpi = w*96/width_px
    return dpi

def position_fig(f, x, y):
    backend = matplotlib.get_backend()
    if backend == 'TkAgg':
        f.canvas.manager.window.wm_geometry("+%d+%d" % (x, y))

    elif backend == 'WXAgg':
        f.canvas.manager.window.SetPosition((x, y))

    else:
        pass

def showDif(dpl=None, kshow=True, ishow=True):
    from pyemaps import DPList

    if not dpl or not isinstance(dpl, DPList):
        print('Nothing to plot: must pass a valid Diffraction object')

    curr_dpi = find_dpi()

    fig, ax = plt.subplots(figsize=(DISPLAY_SIZE/curr_dpi,DISPLAY_SIZE/curr_dpi), 
                        dpi=curr_dpi) #setting image size in pixels
    position_fig(fig, 20, 20)                      
    fig.canvas.set_window_title('PYEMAPS - Kinematic Diffraction') 
    
    mode = dpl.mode
    name = dpl.name

    for c, dp in dpl:
        ax.set_axis_off()
        ax.set_title(name)
        ax.set_aspect('equal')
    
        line_color = 'k' if kshow else 'w'
    
        for kl in dp.klines:
            
            kl *=PLOT_MULTIPLIER
            xx = [kl.pt1.x, kl.pt2.x]
            yy = [kl.pt1.y, kl.pt2.y]
            
            ax.plot(xx, yy, line_color, alpha=0.2)

        for hl in dp.hlines:
            hl *=PLOT_MULTIPLIER
            xx = [hl.pt1.x, hl.pt2.x]
            yy = [hl.pt1.y, hl.pt2.y]
            ax.plot(xx, yy, 'k', alpha=0.2)

        for d in dp.disks:
            d *= PLOT_MULTIPLIER
            centre = (d.c.x, d.c.y)
            
            bFill = True if mode == 1 else False
            dis = patches.Circle(centre, 
                                d.r, 
                                fill=bFill, 
                                linewidth = 0.5, 
                                alpha=1.0, 
                                fc='blue')
            ax.add_patch(dis)
        
            if ishow:
                plt.text(centre[0],centre[1], 
                        str(d.idx),
                        {'color': 'red', 'fontsize': 8},
                        horizontalalignment='center',
                        verticalalignment='bottom' if mode == 1 else 'center')

        controls_text = []
        
        controls_text.append(str(c))

        # finding control text plot or coordinates:
        x0, _ = plt.xlim()
        y0, _ = plt.ylim()

        plt.text(x0 + 10, y0 - 10, str(c),
                {'color': 'grey', 'fontsize': 6}
        )
        plt.draw()
        plt.pause(1)
        ax.cla()
    plt.close()

def showBloch(bimgs, bColor = False, bSave = False):
    """
    plot one powder diffraction
    """
    # from pyemaps import BlochImgs

    from matplotlib.colors import LinearSegmentedColormap
    from pyemaps import BImgList

    # TODO validating input of bimgs
    if not bimgs or not isinstance(bimgs, BImgList):
        raise BlochListError('showBloch must have BImgList object as its first input')

    curr_dpi = find_dpi()

    clrs = ["#2973A5", "cyan", "limegreen", "yellow", "red"]
    gclrs=plt.get_cmap('gray')

    clrMap = gclrs #default to grey
    if bColor:
        clrMap = LinearSegmentedColormap.from_list("mycmap", clrs)

    curr_dpi = find_dpi()

    curr_dpi = find_dpi()

    fig, ax = plt.subplots(figsize=(DISPLAY_SIZE/curr_dpi,DISPLAY_SIZE/curr_dpi), 
                        dpi=curr_dpi) #setting image size in pixels
    position_fig(fig, 20, 20)

    fig.canvas.set_window_title('PYEMAPS - Dynamic Diffraction') 
    
    count = 1
    for c, img in bimgs:
        ax.set_axis_off()
        ax.set_title(bimgs.name, fontsize=12)
        plt.imshow(img, cmap=clrMap)
        x0, _ = plt.xlim()
        y0, _ = plt.ylim()

        plt.text(x0 + 10, y0 - 10, str(c),
                {'color': 'grey', 'fontsize': 8}
        )
        plt.draw() 
        if bSave:
            plt.savefig(bimgs.name + str(count) + '.png')
        plt.pause(1)
        ax.cla()
        count += 1
    plt.close()