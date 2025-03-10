"""
.. This file is part of pyEMAPS
 
.. ----

.. pyEMAPS is free software. You can redistribute it and/or modify 
.. it under the terms of the GNU General Public License as published 
.. by the Free Software Foundation, either version 3 of the License, 
.. or (at your option) any later version..

.. pyEMAPS is distributed in the hope that it will be useful,
.. but WITHOUT ANY WARRANTY; without even the implied warranty of
.. MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
.. GNU General Public License for more details.

.. You should have received a copy of the GNU General Public License
.. along with pyEMAPS.  If not, see `<https://www.gnu.org/licenses/>`_.

.. Contact supprort@emlabsoftware.com for any questions and comments.

.. ----

.. Author:     EMLab Solutions, Inc.
.. Date:       May 07, 2022  

"""

import matplotlib, sys, os
hasDisplay = True
if 'linux' in sys.platform and "DISPLAY" not in os.environ:
    hasDisplay = False
    matplotlib.use('Agg')
elif 'win32' in sys.platform:
    matplotlib.use('TkAgg') # make sure that the backend is Tkinker

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import multiprocessing as mp

from pyemaps import BlochListError
from pyemaps import DP

from .fileutils import *

import time

from . import XMAX, YMAX  #(75,75)

DISPLAY_MULTIPLE_SIZE = 500 
DISPLAY_ONE_SIZE = 900
PLOT_MULTIPLIER = 6

clrs = ["#2973A5", "cyan", "limegreen", "yellow", "red"]
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
        print(f'supported python version: == 3.7')
        print(f'Use default dpi of 96 for display')

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
        self.bSave = False
        self.layout = 'individual'
    
    def savePlot(self):
        if self.save:
            save_type = _get_feature(self.type)
            save_to = compose_ofn(None, self.name, ty=save_type)
            plt.savefig(save_to + '.png')
            print(f'image saved to: {save_to}.png')
   
    def terminate(self):
        if self.bClose:
            plt.close(self.fig) #just close the current figure
        # Otherwise:
        # users must close this window after done
            
    def plotKDif(self):
        idx, emc, dp, mode, kshow, ishow = self.difData

        if self.layout == 'table':
            n1, n2 = _getGridPos(idx, 3)
        else:
            n1, n2 = 0, 0

        iax = self.axes[n1, n2]
        iax.clear()
        iax.set_xlim(-XMAX*PLOT_MULTIPLIER, XMAX*PLOT_MULTIPLIER)
        iax.set_ylim(-YMAX*PLOT_MULTIPLIER, YMAX*PLOT_MULTIPLIER)
        iax.set_axis_off()
        iax.set_aspect('equal')

        if dp.nklines > 0:
            intlist = [k.intensity for k in dp.klines]
            lint, hint = min(intlist), max(intlist)

            for kl in dp.klines:
                
                if not kshow:
                    opacity = 0.0 
                else: 
                    opacity = kl.calOpacity(lint,hint)

                kl *=PLOT_MULTIPLIER
                xx = [kl.pt1.x, kl.pt2.x]
                yy = [kl.pt1.y, kl.pt2.y]
            
                iax.plot(xx, yy, 'k', alpha=opacity, linewidth=1.75)
        
        if dp.nhlines > 0:
            intlist = [h.intensity for h in dp.hlines]
            lint, hint = min(intlist), max(intlist)

            for hl in dp.hlines:
                opacity = hl.calOpacity(lint, hint)
                hl *=PLOT_MULTIPLIER
                xx = [hl.pt1.x, hl.pt2.x]
                yy = [hl.pt1.y, hl.pt2.y]
                iax.plot(xx, yy, 'k', alpha=opacity, linewidth=1.75)

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

        idx, emc, img, color = self.difData
        
        if self.layout == 'table':
            n1, n2 = _getGridPos(idx, 3)
        else:
            n1, n2 = 0, 0

        iax = self.axes[n1, n2]
        clrMap = gclrs #default to grey
        if color:
            clrMap = LinearSegmentedColormap.from_list("mycmap", clrs)

        iax.clear()
        iax.set_axis_off()

# image intensity check: 
# if intensity is below threshold, 
# don't display the image
        imax = img.max()
        if imax < 1.0e-10:
            ishape = np.shape(img)
            img = np.zeros(ishape)
            wmsg = "No intensity detected at: \n\n" + emc.plot_format()
            iax.text(ishape[0]/2,ishape[1]/2, 
                        wmsg,
                        {'color': 'white', 'fontsize': 10},
                        horizontalalignment='center',
                        verticalalignment='center')

        iax.imshow(img, 
                #    norm=colors.LogNorm(vmin=imin, vmax=imax),  --- logrithmatic image normalization, not used now
                   cmap=clrMap)
        if self.cShow:
            self.plotControls(emc,iax)


    def plotControls(self, emc, ax):
        controls_text = emc.plot_format()

        # finding control text plot or coordinates:
        x0= x1 = 0.0
        y0= 0.0

        x0, x1 = ax.get_xlim()
        y0, y1 = ax.get_ylim()

        width = x1-x0
        height = (y1-y0)/8

        textrec = patches.Rectangle((x0, y0-height), 
                                        width, height,
                                        linewidth=0.0,
                                        fill = False)
        ax.add_patch(textrec)

        ax.text(x0 + 0.5*width, y0 - 0.5*height, controls_text,
                {'color': 'grey', 'fontsize': 6},
                ha='center',
                va='center')
                

    def plotStereo(self):
        idx, emc, sdata, ishow, zl= self.difData 
        
        
        if self.layout == 'table':
            n1, n2 = _getGridPos(idx, 3)
        else:
            n1, n2 = 0, 0

        iax = self.axes[n1, n2]
        iax.clear()
        
        iax.set_axis_off()

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


    def __call__(self, pipe, type, name, bSave, n1, n2, cShow, bClose, layout):
        import sys
        
        self.pipe = pipe
        self.name = name
        self.save = bSave
        self.layout = layout
        self.cShow = cShow
        self.bClose = bClose
        
        if sys.platform == 'win32':
            curr_dpi = _find_dpi()
        else:
            curr_dpi = 96
            
        if layout == 'table':
            display_size = DISPLAY_MULTIPLE_SIZE * n2
        else:
            display_size = DISPLAY_ONE_SIZE

        self.fig, self.axes = plt.subplots(nrows=n1,
                                           ncols=n2,
                                           figsize=(display_size/curr_dpi,
                                                    display_size/curr_dpi), 
                                           squeeze=False) #setting image size in pixels
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

        self.fig.suptitle(self.name, va='top', fontsize=24)
        
        timer = self.fig.canvas.new_timer(interval=1500)
        timer.add_callback(self.call_back)
        timer.start()
        
        self.showImage()

class NBPlot:
    # '''
    # Creating a non-bloch plot object with a pipe object sending diffraction data
    # to difPlotter
    # '''
    def __init__(self, type = TY_DIF, n = 1, name='', bSave=False, cShow = True, bClose = False, layout='individual'):

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
                  bClose,
                  layout), 
            daemon=False)

        self.plot_process.start()

    def plot(self, data = (), finished=False):
        send = self.plot_pipe.send
        if finished:
            send(None)
        else:
            send(data)

def showDif(dpl=None, 
            cShow=True,
            kShow=True, 
            iShow=True, 
            layout='individual',
            bSave = False,
            bClose = False):
   
    """
    Render kinematic diffraction pattern generated by pyemaps.

    :param dpl: Kinematic difraction pattern object list `DPList <pyemaps.kdiffs.html#pyemaps.kdiffs.DPList>`_
    :type dpl: DPList

    :param cShow: Plot control annotation. `True` (default): plot the control parameters on lower left corner; `False` do not plot.
    :type cShow: bool, optional

    :param kShow: Whether to display Kikuchi lines.
    :type kShow: bool 

    :param iShow: Whether to display Miller indexes.
    :type iShow: bool 

    :param layout: layout format. individual (default): plotting one by one, table: plotting in a table of 3 columns  
    :type layout: str, optional 

    :param bSave: Whether to save the diplay into a .png image file.
    :type bSave: bool    

    :param bClose: Whether to close plotting window when finished. Default: False - users must close it. 
    :type bClose: bool, optional  
    
    """
    from pyemaps import DPList

    if not dpl or not isinstance(dpl, DPList):
        print('Nothing to plot: must pass a valid Diffraction object')
    
    mode = dpl.mode
    name = dpl.name
    if _isLinux() and not hasDisplay: bSave = True 
    #always save to file on linux as it may just the commandline
    n = len(dpl.diffList)

    pl = NBPlot(TY_DIF, n, name, bSave, cShow, bClose, layout)
    for i, cdp in enumerate(dpl.diffList):
        c, dp = cdp  
        d = (i, c, dp, mode, kShow, iShow)
        pl.plot(data = d)
        time.sleep(1.0)
    pl.plot()
    time.sleep(1.0)

    pl.plot(finished=True)

def showBloch(bimgs, 
              cShow=True, 
              bColor = False, 
              layout='individual', 
              bSave = False,
              bClose = False):
    """
    Render dynamic diffraction pattern generated by pyemaps.

    :param bimgs: Optional. Dynamic difraction pattern object list `BImgList <pyemaps.ddiffs.html#pyemaps.ddiffs.BlochImgs>`_
    :type bimgs: BlochImgs 

    :param cShow: Plot control annotation. `True` (default): plot the control parameters on lower left corner; `False` do not plot.
    :type cShow: bool, optional

    :param bColor: Optional. Whether to display the image in predefined color map.
    :type bColor: bool 

    :param layout: layout format. individual (default): plotting one by one, table: plotting in a table of 3 columns  
    :type layout: str, optional

    :param bSave: Optional. Whether to save the image into a .im3 image file.
    :type bSave: bool    

    :param bClose: Whether to close plotting window when finished. Default: False - users must close it. 
    :type bClose: bool, optional  
    
    """
    from pyemaps import BImgList

    if not bimgs or not isinstance(bimgs, BImgList):
        raise BlochListError('showBloch must have BImgList object as its first input')

    name = bimgs.name
   
    if _isLinux() and not hasDisplay: bSave = True 
    #always save to file on linux as it may just the commandline

    n = len(bimgs.blochList)
    pl = NBPlot(TY_BLOCH, n, name, bSave, cShow, bClose, layout)

    for i, cimg in enumerate(bimgs.blochList):
        c, img = cimg  
        
        d = (i, c, img, bColor)
        pl.plot(data = d)
        time.sleep(1.0)

    pl.plot()
    time.sleep(1.0)

    pl.plot(finished=True)

def showStereo(slist, name, 
               cShow= True,         #em_controls annotated or not
               iShow = False,       #display miller indexes or not
               zLimit = 2,          # miller indexes limit (absolute value)
               layout='individual', # individual or table display format
               bSave=False,         # save the rendering to a file or not
               bClose = False):     # close the plotting window when done  
    
    """
    Render stereodiagram generated by pyemaps.

    :param slist: Stereodiagram output from `generateStereo <pyemaps.crystals.html#pyemaps.crystals.Crystal.generateStereo>`_.
    :type slist: list, required

    :param cShow: Plot control annotation. `True` (default): plot the control parameters on lower left corner; `False` do not plot.
    :type cShow: bool, optional

    :param iShow: Whether to display Miller indexes or not.
    :type iShow: bool, optional

    :param zLimit: Miller indexes cutoff number.
    :type zLimit: int, optional 

    :param layout: layout format. individual (default): plotting one by one in sequence, table: plotting in a table of 3 columns  
    :type layout: str, optional 

    :param bSave: Whether to save the image into a .png image file.
    :type bSave: bool, optional  
    
    :param bClose: Whether to close plotting window when finished. Default: False - users must close it. 
    :type bClose: bool, optional  



    .. note::

        When zlimit is set at 2, it is applied to all elements of each 
        Miller index. For example, (3, 1, 0) will not be rendered.  
    
    """
    if _isLinux() and not hasDisplay: bSave = True 
    #always save to file on linux as it may just the commandline
    
    n = len(slist)
    
    pl = NBPlot(TY_STEREO, n, name, bSave, cShow, bClose, layout)
    for i, ss in enumerate(slist):  
        c, s = ss
        d = (i, c, s, iShow, zLimit)
        pl.plot(data = d)
        time.sleep(1.0)
    pl.plot()
    time.sleep(1.0)
    pl.plot(finished=True)

def _getGridDims(n, nCol = 3):
   
    nr = n % nCol

    nrows = n // nCol
    
    if nr != 0:
        nrows += 1

    ncols = nr
    if n >= 3:
        ncols = 3
        
    return nrows, ncols


def _getGridPos(i, nCols = 3):
    
    ncols = i % nCols

    nrows = i // nCols

    return nrows, ncols

# image display for stem4d module


def normalizeImage(img):
    if img is None:
        print("Probe error: image file empty")
        return False
    y0 = np.mean(img, dtype=np.float32)
    medImg = np.std(img, dtype=np.float32)

    Ymin1 = y0 - 3.0 * medImg
    Ymin = np.amin(img)
    if Ymin < Ymin1: Ymin = Ymin1

    Ymax1 = y0 + 3.0 * medImg
    Ymax = np.amax(img)
    if Ymax > Ymax1: Ymax = Ymax1

    if Ymin >= Ymax:
        print("not finding right min-max: ")
        return False
    ran = Ymax-Ymin

    img[img < Ymin] = Ymin
    img[img > Ymax] = Ymax
    img = (img - Ymin)/ran
    return True

def displayXImage(img, 
                fsize=(0,0), 
                bColor= False, 
                isMask = False, 
                bIndexed=False, 
                iShow = False, 
                ds = None,
                suptitle = ''):   
        """
        Internal stem4d helper function displaying image.

        :return:  
        :rtype: None
        
        """
        
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        from matplotlib.colors import LinearSegmentedColormap
        clrs = ["#2973A5", "cyan", "limegreen", "yellow", "red"]
        qedDPI = 600
        gclrs=plt.get_cmap('gray')
        STEM4D_TITLE = 'pyEMAPS 4DSTEM'

        nr,nc = fsize

        if isMask:
            bsize = (0.5, 0.5*int(nr/nc))
        else:
            bsize = (1.0, 1.0*int(nr/nc))

        fig, ax = plt.subplots(figsize=bsize, dpi=qedDPI)
        
        fig.canvas.set_window_title(STEM4D_TITLE)
        # ax.set_xlabel(suptitle, fontsize=1.5)
        fig.suptitle(suptitle, va='top', fontsize=1.5)
        
        clrMap = gclrs #default to grey
        if bColor:
            clrMap = LinearSegmentedColormap.from_list("mycmap", clrs)
        plt.imshow(img, cmap = clrMap)

        ax.set_axis_off()
        
        count = 0
        if ds is not None:
            for d in ds:
                cx, cy, rad, indx, itype = d
                
                if bIndexed and itype != 2 and count != 0:
                    continue

                centre = (cx, cy)
                
                circle = plt.Circle(centre, rad, 
                                    fill=False, 
                                    linewidth = 0.1, 
                                    # alpha=0.6, 
                                    color='white')
                ax.add_patch(circle)
                count += 1

                if iShow:
                    ax.text(centre[0],centre[1], 
                        str(indx),
                        {'color': 'red', 'fontsize': 1.4},
                        horizontalalignment='center',
                        verticalalignment='bottom')
                    
        plt.show()

def plot2Powder(pw1, pw2, bClose=True):
    """
    plot two powder diffractions in one matplotlib plot using from the
    powder diffraction data generated from `generatePowder <pyemaps.crystals.html#pyemaps.crystals.Crystal.generatePowder>`_

    :param pw1: powder diffraction data of an array of 2 x 1000
    :type pw1: numpy array, required

    :param pw1: powder diffraction data of an array of 2 x 1000
    :type pw1: numpy array, required

    :param bClose: boolean value indicating closure of the diffraction powder plot after about 3 seconds desplay.
    :type bClose: Boolean, optional


    """

    fig, (ax1, ax2) = plt.subplots(nrows = 2)
    
    title = 'pyEMAPS - Powder Diffraction'
    if fig.canvas.manager is not None:
        fig.canvas.manager.set_window_title(title)
    else:
        fig.canvas.set_window_title(title)    
    
    ax1.plot(pw1[0], pw1[1], 'r')
    ax1.set_title('Silicon')
    ax2.plot(pw2[0], pw2[1], 'b')
    ax2.set_title('Diamond')
    
    ax1.set_ylabel('Intensity')
    ax2.set_ylabel('Intensity /w Absorption')
    ax2.set_xlabel('Scattering Angle 2\u03F4 (Rad)')

    fig.suptitle("Electron Powder Diffraction", fontsize=14, fontweight='bold')
    plt.subplots_adjust(hspace = 0.4)

    plt.show(block=False)
    if bClose:
       plt.pause(3)
       plt.close() 
