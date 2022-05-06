"""
# This file is part of pyemaps
# ___________________________
#
# pyemaps is free software for non-comercial use: you can 
# redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either 
# version 3 of the License, or (at your option) any later version.
#
# pyemaps is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyemaps.  If not, see <https://www.gnu.org/licenses/>.
#
# Contact supprort@emlabsoftware.com for any questions and comments.
# ___________________________

An example of using pyemaps crystal and diffraction modules to 
1) create a crystal from built-in data for Silicon 
2) generate kinematical diffraction patterns
3) display the diffraction pattern using pyemaps's built-in plot function 

See https://emlab-solutions.github.io/pyemaps/ for pemaps usage

"""


from pyemaps import DEF_CONTROLS
import sys

MAX_PROCWORKERS = 4
XMAX, YMAX = 75, 75
DIFF_MODE = ('Normal', 'CBED')

def run_si_sample():
    #import Crystal class from pyemaps as cryst
    from pyemaps import Crystal as cryst

    # create a crystal class instance and load it with builtin silican data
    si = cryst.from_builtin('silicon')
    # print(si)

    # run diffraction on the crystal instance with all default controls
    # parameters
    si_dp = si.gen_diffPattern()
    # print(si_dp)
    return si_dp
    
def plot_si_dp(dp, mode = 1, name = 'silicon', ctrl = DEF_CONTROLS):
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import matplotlib.transforms as mtransforms
    import numpy as np
    
    # x, y = self._get_plot_coords()
    
    fig, ax = plt.subplots()
    fig.canvas.set_window_title('Kinematical Diffraction')
    # figManager = plt.get_current_fig_manager()
    # figManager.full_screen_toggle()

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
                {'color': 'red', 'fontsize': 8},
                horizontalalignment='center',
                verticalalignment='bottom' if mode == 1 else 'center',
                transform=trans_offset)

        controls_text = []
        controls_text.append('Diffraction Mode: Normal' if mode == 1 else 'Diffraction Mode: Normal')
        controls_text.append('Zone: ' + str(ctrl['zone']))
        controls_text.append('Tilt: ' + str(ctrl['tilt']))
        controls_text.append('Camera Length: ' + str(ctrl['cl']))
        controls_text.append('Voltage: ' + str(ctrl['vt']))
        
        plt.text(-XMAX + 5, -YMAX + 5,  
                '\n'.join(controls_text),
                {'color': 'grey', 'fontsize': 6}
        )

    fig.canvas.draw()

    
    X = np.array(fig.canvas.renderer._renderer)
    
    # Create DM images for each color

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
    #dif_img_disp = myImage.GetImageDisplay(0)
    title = str(f'Kinematic Diffraction Simulation:  {name} in {DIFF_MODE[mode-1]} Mode')
    myImage.SetName(title)

    


sys.argv.extend(['-a', ' '])        # Required for Matplotlib to work

# Safety-check: Ensure this is called on the main-thread of GMS

if ( False == DM.IsScriptOnMainThread() ):

 print( ' MatplotLib scripts require to be run on the main thread.' )

 exit()

si_dp = run_si_sample()
plot_si_dp(si_dp)