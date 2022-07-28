
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
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import multiprocessing as mp

from pyemaps import BlochListError
from pyemaps import DP

import time

DISPLAY_SIZE = 900 # default
PLOT_MULTIPLIER = 6

clrs = ["#2973A5", "cyan", "limegreen", "yellow", "red"]
gclrs=plt.get_cmap('gray')

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

class DifPlotter:
    '''
    diffraction data plotter that receives data from the pipe and
    plot them with pyplot
    '''
    def __init__(self):
        self.name = 'Silicon'
        self.save = 0
        self.difData = None
        self.emc = None

    def terminate(self):
        plt.close('all')

    def plotKDif(self):
        dp, mode, kshow, ishow = self.difData
        
        self.ax.clear()
        
        self.ax.set_axis_off()
        self.ax.set_aspect('equal')
        self.ax.set_title(self.name)

        line_color = 'k' if kshow else 'w'
        for kl in dp.klines:
        
            kl *=PLOT_MULTIPLIER
            xx = [kl.pt1.x, kl.pt2.x]
            yy = [kl.pt1.y, kl.pt2.y]
        
            self.ax.plot(xx, yy, line_color, alpha=0.2)

        for hl in dp.hlines:
            hl *=PLOT_MULTIPLIER
            xx = [hl.pt1.x, hl.pt2.x]
            yy = [hl.pt1.y, hl.pt2.y]
            self.ax.plot(xx, yy, 'k', alpha=0.2)

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
            self.ax.add_patch(dis)
        
            if ishow:
                plt.text(centre[0],centre[1], 
                        str(d.idx),
                        {'color': 'red', 'fontsize': 8},
                        horizontalalignment='center',
                        verticalalignment='bottom' if mode == 1 else 'center')

    def plotDDif(self):
        from matplotlib.colors import LinearSegmentedColormap

        img, color = self.difData

        clrMap = gclrs #default to grey
        if color:
            clrMap = LinearSegmentedColormap.from_list("mycmap", clrs)

        self.ax.clear()
        self.ax.set_axis_off()
        self.ax.set_title(self.name, fontsize=12)
        plt.imshow(img, cmap=clrMap)

    def plotControls(self):
        controls_text = str(self.emc)

        # finding control text plot or coordinates:
        x0, _ = plt.xlim()
        y0, _ = plt.ylim()

        plt.text(x0 + 10, y0 - 10, controls_text,
                {'color': 'grey', 'fontsize': 6}
        )

    def call_back(self):
        while self.pipe.poll():
            command = self.pipe.recv()
            
            if command is None:
                self.terminate()
                return False
            else:
                save_prefix = 'DDif_'
                self.emc, self.name, self.save, self.difData = command

                if isinstance(self.difData[0], DP):
                    self.plotKDif()
                    save_prefix = 'KDif_'
                else:
                    self.plotDDif()
                
            self.plotControls()
            self.fig.canvas.draw_idle()
            
            self.plotControls()

            if self.save:
                plt.savefig(save_prefix + self.name + str(self.save) + '.png')
            plt.pause(0.5)

        return True
    
    def position_fig(self, x, y):
        backend = matplotlib.get_backend()
        if backend == 'TkAgg':
            self.fig.canvas.manager.window.wm_geometry("+%d+%d" % (x, y))

        elif backend == 'WXAgg':
            self.fig.canvas.manager.window.SetPosition((x, y))

        else:
            pass

    def __call__(self, pipe, type):
        self.pipe = pipe
        curr_dpi = find_dpi()
        self.fig, self.ax = plt.subplots(figsize=(DISPLAY_SIZE/curr_dpi,DISPLAY_SIZE/curr_dpi), 
                        dpi=curr_dpi) #setting image size in pixels
        self.position_fig(20, 20)
        self.ax.set_axis_off()
        pyemaps_title = 'PYEMAPS - Kinematic Diffraction' if type == 1 else 'PYEMAPS - Dynamic Diffraction'
        self.fig.canvas.set_window_title(pyemaps_title)
        timer = self.fig.canvas.new_timer(interval=1000)
        timer.add_callback(self.call_back)
        timer.start()

        plt.show()

class NBPlot:
    '''
    Creating a non-bloch plot object with pipe sending diffraction data
    '''
    def __init__(self, type = 1):
        self.plot_pipe, plotter_pipe = mp.Pipe()
        self.plotter = DifPlotter()
        self.plot_process = mp.Process(
            target=self.plotter, args=(plotter_pipe, type), daemon=True)
        self.plot_process.start()

    def plot(self, data = (), finished=False):
        send = self.plot_pipe.send
        if finished:
            send(None)
        else:
            send(data)


def showDif(dpl=None, kshow=True, ishow=True, bSave = False):
    """
    Show kinematic diffractions
    """
    from pyemaps import DPList

    if not dpl or not isinstance(dpl, DPList):
        print('Nothing to plot: must pass a valid Diffraction object')
    
    mode = dpl.mode
    name = dpl.name
    count = 1
    pl = NBPlot(1)
    for c, dp in dpl:       
        save = 0
        if bSave:
            save = count
        d = (c, name, save, (dp, mode, kshow, ishow))
        pl.plot(data = d)
        time.sleep(1.0)
        count += 1

    pl.plot(finished=True)

def showBloch(bimgs, bColor = False, bSave = False):
    """
    Show bloch diffractions
    """
    from pyemaps import BImgList

    if not bimgs or not isinstance(bimgs, BImgList):
        raise BlochListError('showBloch must have BImgList object as its first input')

    name = bimgs.name
    count = 1
    pl = NBPlot(2)
    for c, img in bimgs:       
        save = 0
        if bSave:
            save = count
        d = (c, name, save, (img, bColor))
        pl.plot(data = d)
        time.sleep(0.5)
        count += 1

    pl.plot(finished=True)
