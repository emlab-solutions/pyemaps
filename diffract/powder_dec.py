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
        Plot a powder diffraction profile from :py:meth:`~pyemaps.crystals.Crystal.generatePowder`.

        :param pw: the profile: a 2 × N array of scattering angles and intensities.
        :type pw: numpy.ndarray, required
        :raise ValueError: if *pw* doesn't have two rows.
        """
        import numpy as np
        import matplotlib.pyplot as plt

        xdim, _ = np.shape(pw)
        if xdim !=2:
            raise ValueError("Failed to plot: data error")
        
        fig, ax = plt.subplots()
        # canvas.set_window_title was removed in matplotlib 3.6
        if fig.canvas.manager is not None:
            fig.canvas.manager.set_window_title('PYEMAPS')
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
        """
        Calculate the crystal's electron powder diffraction profile.

        :param kv: accelerating voltage, in kV.
        :type kv: int or float, optional
        :param t2max: largest scattering angle 2θ, in radians.
        :type t2max: float, optional
        :param smax: largest sin(θ)/λ, in 1/Å.
        :type smax: float, optional
        :param eta: mixing coefficient of the pseudo-Voigt peak shape, from 0 to 1:
            ``eta * Lorentzian + (1 - eta) * Gaussian``. 1 is purely Lorentzian, 0 purely
            Gaussian.
        :type eta: float, optional
        :param gamma: peak full width at half maximum, in radians.
        :type gamma: float, optional
        :param absp: 1 to include absorption structure factors, 0 (the default) not to.
        :type absp: int, optional
        :param bg: add a background.
        :type bg: bool, optional
        :param bamp: background amplitude.
        :type bamp: float, optional
        :param bgamma: background width.
        :type bgamma: float, optional
        :param bmfact: background exponential damping factor.
        :type bmfact: float, optional
        :return: a 2 × 1000 array: the first row holds the scattering angles 2θ (radians), the
            second the intensities. If the calculation fails, a message is printed and the array
            is all zeros.
        :rtype: numpy.ndarray

        To plot the result, pass it to :py:meth:`~pyemaps.crystals.Crystal.plotPowder`.
        """
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