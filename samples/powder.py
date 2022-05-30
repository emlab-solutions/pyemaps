'''
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

Author:     EMLab Solutions, Inc.
Date:       May 31, 2022    


This sample code is to render kinematic diffraction patterns generated
by pyemaps by changing zone axis
'''

def plot2Powder(pw1, pw2):
    """
    plot multiple powder diffraction in one plt plot
    """

    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(nrows = 2)
    fig.canvas.set_window_title('PYEMAPS')      
    
    ax1.plot(pw1[0], pw1[1], 'r')
    ax1.set_title('Silicon')
    ax2.plot(pw2[0], pw2[1], 'b')
    ax2.set_title('Diamond')
    
    ax1.set_ylabel('Intensity')
    ax2.set_ylabel('Intensity /w Absorption')
    ax2.set_xlabel('Scattering Angle 2\u03F4 (Rad)')

    fig.suptitle("Electron Powder Diffraction", fontsize=14, fontweight='bold')
    plt.subplots_adjust(hspace = 0.4)

    plt.show()

def runPowderTests():
    from pyemaps import Crystal as cryst
    import time

    si = cryst.from_builtin('Silicon')
    print(si)
    psi = si.generatePowder() 

    # si.plotPowder(psi)
    di = cryst.from_builtin('Diamond')
    print(di)
    pdi = di.generatePowder(absp = 1)

    plot2Powder(psi, pdi)

if __name__ == "__main__":
    
    runPowderTests()
