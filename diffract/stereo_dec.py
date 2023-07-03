def add_stereo(target):
    def generateStereo(self, xa = (0,2,0), 
                            tilt=(0.0,0.0),
                            zone = (0, 0, 1)):
        """
        Generate stereodiagram.

        :param xa: Crystal horizontal axis in reciprical space
        :type xa: tuple of 3 integers, optional

        :param tilt: Sample tilts in (x,y)
        :type tilt: tuple, optional

        :param zone: Zone axis
        :type zone: tuple, optional

        :return: A list of stereodiagram elements represented by dict object
        :rtype: list of dict object

        Example of the stereodiagram output:

        .. code-block:: json

            [
                {
                    "c": (x,y),              # center
                    "r": rad,                # radius
                    "idx": (h, k, l),        # Miller Index
                }
            ]    

        To display the resulting stereodiagram, use 
        `showStereo <pyemaps.display.html#pyemaps.display.showStereo>`_.
        
        """
        from . import dif, stereo
        
        import numpy as np
        from numpy import asfortranarray as farray

        from ..errors import StereodiagramError 
        # @070323 merge
        from .. import DEF_XAXIS

        dif.initcontrols()
        dif.setzone(zone[0], zone[1], zone[2])        
        
        # @070323 merge
        if xa != DEF_XAXIS:
            dif.set_xaxis(1, xa[0], xa[1], xa[2])
        dif.setsamplecontrols(tilt[0], tilt[1], 0.0, 0.0)

        # load the crystal
        
        self.load()

        ret = dif.diffract(3)
        if ret != 1:
            raise StereodiagramError('Stereodiagram generation failed')

        sl = stereo.get_stereolimit()

        sdata = farray(np.zeros((6, sl)), dtype=float)
      
        sdata, ns, ret = stereo.do_stereogram(sdata)

        if ret != 1:
            raise StereodiagramError('Stereodiagram generation failed')

        stereo_list = []
        for i in range(ns):
            item = {}
            s = sdata[0:, i]
            item['c'] = (s[0], s[1])
            item['r'] = s[2]
            item['idx'] = (s[3], s[4],s[5])
            stereo_list.append(item)

        #release the memory
        dif.diff_internaldelete(0)
        dif.diff_delete()
        
        return stereo_list
        
    target.generateStereo = generateStereo
    
    return target