"""
# This file is part of pyemaps
# ___________________________
#
# This program is free software for non-comercial use: you can 
# redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either 
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Contact supprort@emlabsoftware.com for any questions and comments.
# ___________________________

An example of using pyemaps crystal and diffraction modules to 
1) create a crystal from built-in data for Silicon 
2) generate kinematical diffraction patterns
3) display the diffraction pattern using pyemaps's built-in plot function 

Usage:
a) install pyemaps diffraction and crystal modules:
    pip install pyemaps
b) run  
    python si_diff.py

"""
from pyemaps import DEF_CONTROLS
MAX_PROCWORKERS = 4
XMAX, YMAX = 75, 75
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

 

    # The array is (Y,X,C) with C being the color channel

    # Get individual colors

    R = X[:,:,0]

    G = X[:,:,1]

    B = X[:,:,2]

     

    # DM Python does not support RGB image creation yet

    # Convert this to a greyscale image simple array

    Mono = 0.2989*R + 0.5870*G + 0.1140*B 

     

    # Show as DM image

    DM.CreateImage( Mono ).ShowImage()
        #plt.show()
    
    
si_dp = run_si_sample()
plot_si_dp(si_dp)
