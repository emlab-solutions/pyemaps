
def add_powder(target):
   
    try:
        from . import powder

    except ImportError as e:               
        print(f"Error: required module pyemaps.powder not found")
        
    def plotPowder(self, pw):

        """
        Show powder diffraction

        :param pw: Required. Powder diffraction data
        :type pw: array

        (TODO: link to an pwoder plot example)

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

        :param kv: Optional. Accelaration voltage in kilo-volts.
        :type kv: int or float

        :param t2max: Optional. Maximum scattering angle.
        :type t2max: float

        :param smax: Optional. Maximum Sin(theta)/Wavelength.
        :type smax: float

        :param smax: Optional. Maximum Sin(theta)/Wavelength.
        :type smax: float

        :param eta: Optional. the mixing coefficient between gaussian and lorentzian in a pseudo-Voight peak function.
        :type eta: float

        :param gamma: Optional. Diffraction peaks half maximum half width.
        :type gamma: float

        :param absp: Optional. With Absoption structure factor (1 -default) or not (0).
        :type absp: int

        :param isbgdon: Optional. Background on or not (default no background).
        :type isbgdon: int

        :param bamp: Optional. Background amplitude.
        :type bamp: float

        :param bgamma: Optional. Background width.
        :type bgamma: float

        :param bmfact: Optional. Background exponential damping factor.
        :type bmfact: float

        :return: rawP
        :rtype: array

        .. note::

        The function returns an array of 2 x 1000 containing 
        the powder diffraction for loaded crystal.
        
        The first 1000 is the scattering angle 2theta and the second 
        the intensity  
        
        '''     
        import numpy as np
        from numpy import asfortranarray as farray
        
        self.load()
          
        rawP = farray(np.zeros((2,1000), dtype=np.double))
       
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