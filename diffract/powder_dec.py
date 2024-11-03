'''
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

.. Author:             EMLab Solutions, Inc.
.. Date Created:       May 07, 2022  

'''
def add_powder(target):
   
    try:
        from . import powder

    except ImportError as e:               
        print(f"Error: required module pyemaps.powder not found")
        
    def plotPowder(self, pw):

        """
        Show powder diffraction created from 
        `generatePowder <pyemaps.crystals.html#pyemaps.crystals.Crystal.generatePowder>`_.

        :param pw: Powder diffraction data
        :type pw: array, required

        """
        import numpy as np
        import matplotlib.pyplot as plt

        xdim, _ = np.shape(pw)
        if xdim !=2:
            raise ValueError("Failed to plot: data error")
        
        fig, ax = plt.subplots()
        fig.canvas.set_window_title('PYEMAPS')    
        fig.suptitle("Electron Powder Diffraction", fontsize=14, fontweight='bold')

        ax.set_title(self.name)
        
        ax.set_ylabel('Intensity')
        ax.set_xlabel('Scattering Angle 2\u03F4 (Rad)')
        ax.plot(pw[0], pw[1], 'b')

        plt.show()

    def generatePowder(self,
            kv = 100, 
            t2max = 0.05, 
            smax = 1.0, 
            eta = 1.0, 
            gamma = 0.001, 
            absp = 0, 
            bg = False,
            bamp = 0.35, 
            bgamma = 0.001, 
            bmfact = 0.02):
        '''
        Generates powder diffraction.

        :param kv: Accelaration voltage in kilo-volts.
        :type kv: int or float, optional

        :param t2max: Maximum scattering angle.
        :type t2max: float, optional

        :param smax: Maximum Sin(theta)/Wavelength.
        :type smax: float, optional

        :param smax: Maximum Sin(theta)/Wavelength.
        :type smax: float, optional

        :param eta: the mixing coefficient between gaussian and lorentzian in a pseudo-Voight peak function.
        :type eta: float, optional

        :param gamma: Diffraction peaks half maximum half width.
        :type gamma: float, optional

        :param absp: With Absoption structure factor (1 -default) or not (0).
        :type absp: int, optional

        :param isbgdon: Background on or not (default no background).
        :type isbgdon: int, optional

        :param bamp: Background amplitude.
        :type bamp: float, optional

        :param bgamma: Background width.
        :type bgamma: float, optional

        :param bmfact: Background exponential damping factor.
        :type bmfact: float, optional

        :return: an array of 2 x 1000 with the first row representing the scattering angle 2theta and the second the intensity
        :rtype: array

        '''     
        import numpy as np
        from numpy import asfortranarray as farray
        
        self.load()
          
        rawP = farray(np.zeros((2,1000), dtype=np.float32))
       
        ret = powder.generate_powder(rawP, kv=kv, t2max=t2max, 
                smax = smax, eta=eta, gamma=gamma, isab = absp, 
                isbgdon = bg, bamp = bamp, bgamma = bgamma, 
                bmfact = bmfact)

        if ret != 0:
            print(f'Error generating powder data for {self.name}')

        return rawP
    
    target.generatePowder = generatePowder
    target.plotPowder = plotPowder

    return target