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
GNU General Public License for more details. see 
<https://www.gnu.org/licenses/>.

For how to install pyemaps, go to https://emlab-solutions.github.io/pyemaps/ 
Contact supprort@emlabsoftware.com for any questions and comments.
___________________________

This sample code demonstrates how pyemaps can be integrated into 
DigitalMicrograph to render the diffraction patterns for silicon crystal.

Author:     EMLab Solutions, Inc.
Date:       May 07, 2022    

"""
from pyemaps import Crystal as cryst
from pyemaps import EMC,DEF_CBED_DSIZE
import sys

MAX_PROCWORKERS = 4

def run_si_sample(mode = 1):
    # create a crystal class instance and load it with builtin silican data
    si = cryst.from_builtin('Silicon')
    # print(si)

    dsize = 0.0
    if mode == 2: # CBED mode
        dsize = DEF_CBED_DSIZE

    # run diffraction on the crystal instance with all default controls
    # parameters
    emc, si_dp = si.generateDP(mode = mode, dsize = dsize)
    # print(si_dp)
    return emc, si_dp
    
def plot_si_dp(dp, mode = 1, name = 'Silicon', ctrl = None):
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import matplotlib.transforms as mtransforms
    import numpy as np
    
    fig, ax = plt.subplots()
    fig.canvas.set_window_title('Kinematical Diffraction')

    ax.set_title(f"{name}")
    ax.set_aspect('equal')
    ax.set_axis_off()
    
    for kl in dp.klines:
        xx = [kl.pt1.x, kl.pt2.x]
        yy = [kl.pt1.y, kl.pt2.y]
        ax.plot(xx, yy, 'k', alpha=0.2)

    for hl in dp.hlines:
        xx = [hl.pt1.x, hl.pt2.x]
        yy = [hl.pt1.y, hl.pt2.y]
        ax.plot(xx, yy, 'k', alpha=0.2)

    for d in dp.disks:
        c0, c1, r,i1, i2, i3 = d
        # idx = '' + str(d.idx)
        bFill = True if mode == 1 else False
        dis = patches.Circle((c0,c1), r, fill=bFill, linewidth = 0.5, alpha=1.0, fc='blue')
        ax.add_patch(dis)
        # ax.annotate(idx,centre,)
        yoffset = 0.0 if mode == 2 else r/2
        trans_offset = mtransforms.offset_copy(ax.transData, fig=fig,
                                   x=0.0, y=yoffset, units='points')

        plt.text(c0,c1, 
                str(d.idx),
                {'color': 'red', 'fontsize': 6},
                horizontalalignment='center',
                verticalalignment='bottom' if mode == 1 else 'center',
                transform=trans_offset)
    
    if not ctrl:
        ctrl = EMC() #default em controls

    controls_text = []
    # controls_text.append('Mode: Normal' if self.mode == 1 else 'Mode: CBED')
    controls_text.append(str(ctrl))

    # finding control text plgit ot coordinates:
    x0, _ = plt.xlim()
    y0, _ = plt.ylim()

    plt.text(x0 + 10, y0 + 10,  
            '\n'.join(controls_text),
            {'color': 'grey', 'fontsize': 6}
    )

    fig.canvas.draw()
    
    X = np.array(fig.canvas.renderer._renderer)

    if mode == 1:

        R = X[:,:,0]

        G = X[:,:,1]

        B = X[:,:,2]


        Mono = 0.2989*R + 0.5870*G + 0.1140*B 

        # Show as DM image

        DM.CreateImage( Mono ).ShowImage()
    
    if mode == 2: # show CBED DP in color
        r_ = DM.CreateImage(X[:,:,0].copy())

        g_ = DM.CreateImage(X[:,:,1].copy())

        b_ = DM.CreateImage(X[:,:,2].copy())

        # Build one-liner DM-script to show RGB image 
        dms = 'rgb(' + r_.GetLabel() + ',' + g_.GetLabel() + ',' + b_.GetLabel() + ').ShowImage()'

        DM.ExecuteScriptString(dms)

        # Always delete Py_Image references in the script

        del r_

        del g_

        del b_
        
    myImage = DM.FindFrontImage()
    
    mdString = 'Normal' if mode == 1 else 'CBED'
    title = str(f'Kinematic Diffraction Simulation:  {name} in {mdString} Mode')
    myImage.SetName(title)
   
sys.argv.extend(['-a', ' '])        # Required for Matplotlib to work

# Safety-check: Ensure this is called on the main-thread of GMS

if ( False == DM.IsScriptOnMainThread() ):

 print( ' MatplotLib scripts require to be run on the main thread.' )

 exit()

#DP in normal mode
c, si_dp = run_si_sample()
plot_si_dp(si_dp, ctrl = c)

#DP in CBED mode
c, si_dp = run_si_sample(mode = 2)
plot_si_dp(si_dp, mode = 2, ctrl = c)
