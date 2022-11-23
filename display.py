# """
# This file is part of pyemaps
# ___________________________
# pyemaps is free software for non-comercial use: you can 
# redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either 
# version 3 of the License, or (at your option) any later version.
# pyemaps is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with pyemaps.  If not, see <https://www.gnu.org/licenses/>.
# Contact supprort@emlabsoftware.com for any questions and comments.
# ___________________________

# Author:     EMLab Solutions, Inc.
# Date:       May 07, 2022    
# """

"""
Display is provided as a helper module. It serves as demonstration
purpose only. It is implemented for a list of pyemaps simulation objects
and multiprocess and pipe python objects. Currently this rendering
functions may not be best fit for single display.

Check :doc:`visualization` for examples of customizing your own 
visualization methods rendering pyemaps simulations results.  

"""
import matplotlib, sys, os
hasDisplay = True
if 'linux' in sys.platform and "DISPLAY" not in os.environ:
    hasDisplay = False
    matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import multiprocessing as mp

from pyemaps import BlochListError
from pyemaps import DP

from .fileutils import *

import time


DISPLAY_MULTIPLE_SIZE = 500 
DISPLAY_ONE_SIZE = 900
PLOT_MULTIPLIER = 6

clrs = ["#2973A5", "cyan", "limegreen", "yellow", "red"]
# clrs=plt.get_cmap('binary')
gclrs=plt.get_cmap('gray')

TY_DIF = 1
TY_BLOCH = 2
TY_STEREO = 3

feat_lookup={'dif': TY_DIF,
             'bloch': TY_BLOCH,
             'stereo':TY_STEREO}

def _get_feature(ty):
    if ty < TY_DIF or ty > TY_STEREO:
        raise ValueError("Feature lookup failed")

    return list(feat_lookup.keys())[list(feat_lookup.values()).index(ty)]

def _find_dpi():
    matplotlib.use('TkAgg')
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

def _isLinux():
    import sys
    return ('linux' in sys.platform)

def _isWin():
    import sys
    return (sys.platform == 'win32')

class DifPlotter:
    # '''
    # diffraction data plotter that receives data from the pipe and
    # plot them with pyplot
    # '''
    def __init__(self):
        self.name = 'Silicon'
        self.save = 0
        self.difData = None
        self.emc = None
        self.cShow = True
        self.layout = 'individual'
    
    def savePlot(self):
        if self.save:
            save_type = _get_feature(self.type)
            save_to = compose_ofn(None, self.name, ty=save_type)
            plt.savefig(save_to + '.png')
            print(f'image saved to: {save_to}.png')
   
    def terminate(self):
        # self.savePlot()
        plt.close(self.fig) #just close the current figure
            
    def plotKDif(self):
        idx, emc, dp, mode, kshow, ishow = self.difData
        
        if self.layout == 'table':
            n1, n2 = _getGridPos(idx, 3)
        else:
            n1, n2 = 0, 0

        iax = self.axes[n1, n2]
        iax.clear()
        
        iax.set_axis_off()
        iax.set_aspect('equal')
        # iax.set_title(self.name)

        line_color = 'k' if kshow else 'w'
        for kl in dp.klines:
        
            kl *=PLOT_MULTIPLIER
            xx = [kl.pt1.x, kl.pt2.x]
            yy = [kl.pt1.y, kl.pt2.y]
        
            iax.plot(xx, yy, line_color, alpha=0.35, linewidth=1.75)

        for hl in dp.hlines:
            hl *=PLOT_MULTIPLIER
            xx = [hl.pt1.x, hl.pt2.x]
            yy = [hl.pt1.y, hl.pt2.y]
            iax.plot(xx, yy, 'k', alpha=0.35, linewidth=1.75)

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
            iax.add_patch(dis)
        
            if ishow:
                iax.text(centre[0],centre[1], 
                        str(d.idx),
                        {'color': 'red', 'fontsize': 8},
                        horizontalalignment='center',
                        verticalalignment='bottom' if mode == 1 else 'center')
           
        if self.cShow:
            self.plotControls(emc,iax)


    def plotDDif(self):
        from matplotlib.colors import LinearSegmentedColormap

        idx, emc, img, color, tag = self.difData
        
        if self.layout == 'table':
            n1, n2 = _getGridPos(idx, 3)
        else:
            n1, n2 = 0, 0

        iax = self.axes[n1, n2]
        clrMap = gclrs #default to grey
        if color:
            # clrMap=clrs
            clrMap = LinearSegmentedColormap.from_list("mycmap", clrs)

        iax.clear()
        iax.set_axis_off()

        iax.set_title(tag)

        iax.imshow(img, cmap=clrMap)
        if self.cShow:
            self.plotControls(emc,iax)


    def plotControls(self, emc, ax):
        controls_text = str(emc)

        # finding control text plot or coordinates:
        x0= 0
        y0= 0

        if self.type != TY_STEREO:
            x0, _ = ax.get_xlim()
            y0, _ = ax.get_ylim()

            ax.text(x0, y0, controls_text,
                    {'color': 'grey', 'fontsize': 6}
            )
            return


        ax.text( -1.0, -1.0, controls_text,
                    {'color': 'grey', 'fontsize': 6}
                )

    def plotStereo(self):
        idx, emc, sdata, ishow, zl= self.difData 
        
        
        if self.layout == 'table':
            n1, n2 = _getGridPos(idx, 3)
        else:
            n1, n2 = 0, 0

        iax = self.axes[n1, n2]
        iax.clear()
        
        iax.set_axis_off()
        # iax.set_title(self.name, color='blue')

        # adding a unit disk
        unitdis = patches.Circle((0.0, 0.0), 
                            1.0, 
                            fill=False, 
                            linewidth = 0.5, 
                            alpha=1.0, 
                            color='blue')
        iax.add_patch(unitdis)

        for s in sdata:
            c, r, idx = s['c'], s['r'], s['idx']
            radius =float(r)
            index = (int(idx[0]), int(idx[1]), int(idx[2]))
            centre = (float(c[0]), float(c[1]))
            dis = patches.Circle(centre, 
                                radius, 
                                fill=True, 
                                linewidth = 0.5, 
                                alpha=1.0, 
                                fc='blue')
            iax.add_patch(dis)
        
            if ishow:
                if abs(index[0]) <= zl and \
                   abs(index[1]) <= zl and \
                   abs(index[2]) <= zl:

                    iax.text(centre[0],centre[1], 
                            str(index),
                            {'color': 'red', 'fontsize': 8},
                            horizontalalignment='center',
                            verticalalignment='bottom')

            # set the limits
        iax.set_xlim([-1.0, 1.0])
        iax.set_ylim([-1.0, 1.0])
        
        tag = 'zone: ' + str(emc.zone)
        iax.set_title(tag)

        if self.cShow:
            self.plotControls(emc,iax)

    def call_back(self):
        
        while self.pipe.poll():
            command = self.pipe.recv()
            
            if command is None:
                self.terminate()
                return False
            elif command == ():
                self.savePlot()
            else:
                self.difData = command
                
                if self.type == 1: #diffraction plot type
                    self.plotKDif()
            
                elif self.type == 2: #bloch type plot
                    self.plotDDif()

                elif self.type == 3: #stereo type plot
                    self.plotStereo()

                else:
                    raise ValueError("No data to plot")
                
                self.fig.canvas.draw_idle()  

                plt.pause(1.0)

        return True

    def showImage(self):
        if _isLinux() and not hasDisplay:
            return
        plt.show()
        

    def position_fig(self, x, y):
        backend = matplotlib.get_backend()
        if backend == 'TkAgg':
            self.fig.canvas.manager.window.wm_geometry("+%d+%d" % (x, y))

        elif backend == 'WXAgg':
            self.fig.canvas.manager.window.SetPosition((x, y))
        else:
            pass


    def __call__(self, pipe, type, name, bSave, n1, n2, cShow, layout):
        import sys
        
        self.pipe = pipe
        self.name = name
        self.save = bSave
        self.layout = layout
        self.cShow = cShow

        if sys.platform == 'win32':
            curr_dpi = _find_dpi()
        else:
            curr_dpi = 96
            
        if layout == 'table':
            display_size = DISPLAY_MULTIPLE_SIZE * n2
        else:
            display_size = DISPLAY_ONE_SIZE

        self.fig, self.axes = plt.subplots(figsize=(display_size/curr_dpi,
                                                    display_size/curr_dpi), 
                                            squeeze=False, 
                                            clip_on=True,
                                            nrows=n1, 
                                            ncols=n2) #setting image size in pixels
        for x in self.axes.ravel():
            x.axis("off")
            x.set_aspect('equal')
            
        if hasDisplay:
            self.position_fig(20, 20)
        
        if type == 1:
            pyemaps_title = 'PYEMAPS - Kinematic Diffraction' 

        elif type == 2:
            pyemaps_title = 'PYEMAPS - Dynamic Diffraction'

        elif type == 3:
            pyemaps_title = 'PYEMAPS -Stereodiagram'
        else:
            raise ValueError("Unsupported data type")
        
        self.type = type

        if hasDisplay:
            if self.fig.canvas.manager is not None:
                self.fig.canvas.manager.set_window_title(pyemaps_title)
            else:
                self.fig.canvas.set_window_title(pyemaps_title)

        self.fig.suptitle(self.name, ha='center', fontsize=24)
        # self.fig.tight_layout()
        
        timer = self.fig.canvas.new_timer(interval=1500)
        timer.add_callback(self.call_back)
        timer.start()
        
        self.showImage()

class NBPlot:
    # '''
    # Creating a non-bloch plot object with a pipe object sending diffraction data
    # to difPlotter
    # '''
    def __init__(self, type = TY_DIF, n = 1, name='', bSave=False, cShow = True, layout='individual'):

        if layout == 'table':
            n1, n2 = _getGridDims(n, 3)
        else:
            n1, n2 = 1, 1

        self.plot_pipe, plotter_pipe = mp.Pipe()
        self.plotter = DifPlotter()
        self.plot_process = mp.Process(
            target=self.plotter, 
            args=(plotter_pipe, 
                  type,
                  name,
                  bSave,
                  n1,
                  n2,
                  cShow, 
                  layout), 
            daemon=True)

        self.plot_process.start()

    def plot(self, data = (), finished=False):
        send = self.plot_pipe.send
        if finished:
            send(None)
        else:
            send(data)

def showDif(dpl=None, kshow=True, ishow=True, bSave = False, layout='individual', cShow=True):
   
    """
    Render kinematic diffraction pattern generated by pyemaps.

    :param dpl: Kinematic difraction pattern object list `DPList <pyemaps.kdiffs.html#pyemaps.kdiffs.DPList>`_
    :type dpl: DPList
    :param kshow: Whether to display Kikuchi lines.
    :type kshow: bool 
    :param ishow: Whether to display Miller indexes.
    :type ishow: bool 
    :param bSave: Whether to save the diplay into a .png image file.
    :type bSave: bool  
    :param layout: layout format. individual (default): plotting one by one, table: plotting in a table of 3 columns  
    :type layout: str, optional 
    :param cShow: Plot control annotation. `True` (default): plot the control parameters on lower left corner; `False` do not plot.
    :type zlimit: bool, optional
    
    """
    from pyemaps import DPList

    if not dpl or not isinstance(dpl, DPList):
        print('Nothing to plot: must pass a valid Diffraction object')
    
    mode = dpl.mode
    name = dpl.name
    if _isLinux() and not hasDisplay: bSave = True 
    #always save to file on linux as it may just the commandline
    n = len(dpl.diffList)

    pl = NBPlot(TY_DIF, n, name, bSave, cShow, layout)
    for i, cdp in enumerate(dpl.diffList):
        c, dp = cdp  
        d = (i, c, dp, mode, kshow, ishow)
        pl.plot(data = d)
        time.sleep(1.0)
    pl.plot()
    time.sleep(1.0)

    pl.plot(finished=True)

def showBloch(bimgs, bColor = False, bSave = False, layout='individual', cShow=True):
    
    """
    Render dynamic diffraction pattern generated by pyemaps.

    :param bimgs: Optional. Dynamic difraction pattern object list `BImgList <pyemaps.ddiffs.html#pyemaps.ddiffs.BlochImgs>`_
    :type bimgs: BlochImgs
    :param bColor: Optional. Whether to display the image in predefined color map.
    :type bColor: bool 
    :param bSave: Optional. Whether to save the image into a .im3 image file.
    :type bSave: bool  
    :param layout: layout format. individual (default): plotting one by one, table: plotting in a table of 3 columns  
    :type layout: str, optional 
    :param cShow: Plot control annotation. `True` (default): plot the control parameters on lower left corner; `False` do not plot.
    :type zlimit: bool, optional
    
    """
    from pyemaps import BImgList

    if not bimgs or not isinstance(bimgs, BImgList):
        raise BlochListError('showBloch must have BImgList object as its first input')

    name = bimgs.name
   
    if _isLinux() and not hasDisplay: bSave = True 
    #always save to file on linux as it may just the commandline

    n = len(bimgs.blochList)
    pl = NBPlot(TY_BLOCH, n, name, bSave, cShow, layout)
    for i, cimg in enumerate(bimgs.blochList):
        c, img = cimg  
        tag = 'Sample Thickness: ' + str(500+i*250)
        d = (i, c, img, bColor, tag)
        pl.plot(data = d)
        time.sleep(1.0)

    pl.plot()
    time.sleep(1.0)

    pl.plot(finished=True)

def showStereo(slist, name, iShow = False, bSave=False, zLimit = 2, layout='individual', cShow=True):
    
    """
    Render stereodiagram generated by pyemaps.

    :param slist: Stereodiagram output from `generateStereo <pyemaps.crystals.html#pyemaps.crystals.Crystal.generateStereo>`_.
    :type slist: list, required
    :param iShow: Whether to display Miller indexes or not.
    :type iShow: bool, optional
    :param bSave: Whether to save the image into a .png image file.
    :type bSave: bool, optional  
    :param zlimit: Miller indexes cutoff number.
    :type zlimit: int, optional  
    :param layout: layout format. individual (default): plotting one by one in sequence, table: plotting in a table of 3 columns  
    :type layout: str, optional 
    :param cShow: Plot control annotation. `True` (default): plot the control parameters on lower left corner; `False` do not plot.
    :type zlimit: bool, optional

    .. note::

        When zlimit is set at 2, it is applied to all elements of each 
        Miller index. For example, (3, 1, 0) will not be rendered.  
    
    """
    if _isLinux() and not hasDisplay: bSave = True 
    #always save to file on linux as it may just the commandline
    
    n = len(slist)
    
    pl = NBPlot(TY_STEREO, n, name, bSave, cShow, layout)
    for i, ss in enumerate(slist):  
        c, s = ss
        d = (i, c, s, iShow, zLimit)
        pl.plot(data = d)
        time.sleep(1.0)
    pl.plot()
    time.sleep(1.0)
    pl.plot(finished=True)

def _getGridDims(n, nCol = 3):
   
    # print(f'found grid input: {n}, {nCol}')
    nr = n % nCol

    nrows = n // nCol
    
    if nr != 0:
        nrows += 1

    ncols = nr
    if n >= 3:
        ncols = 3
    # print(f'found grid: {nrows}, {ncols}')
    return nrows, ncols


def _getGridPos(i, nCols = 3):
    
    ncols = i % nCols

    nrows = i // nCols

    return nrows, ncols