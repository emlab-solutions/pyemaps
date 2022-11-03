def add_stereo(target):
    def generateStereo(self, xa = (0,2,0), 
                            tilt=(0.0,0.0),
                            zone = (0, 0, 1)):
        """
        This routine returns a Stereodiagram.

        :param em_control: only tilt and zone in emc affect output
        :param xa: xaxis set by user or default to the above value
        
        """
        from . import dif, stereo
        
        import numpy as np
        from numpy import asfortranarray as farray

        from ..errors import StereodiagramError

        dif.initcontrols()
        dif.setzone(zone[0], zone[1], zone[2])
        dif.set_xaxis(1, xa[0], xa[1], xa[2])
        dif.setsamplecontrols(tilt[0], tilt[1], 0.0, 0.0)

        # load the crystal
        
        self.load()

        ret = dif.diffract(3)
        if ret != 1:
            raise StereodiagramError('Stereodiagram generation failed')

        sl = stereo.get_stereolimit()

        sdata = farray(np.zeros((6, sl)), dtype=float)
      
        sdata, ns, ret = stereo.dostereogram(sdata)

        if ret != 1:
            raise StereodiagramError('Stereodiagram generation failed')

        # print(f'number of spots: {ns}')
        stereo_list = []
        for i in range(ns):
            item = {}
            s = sdata[0:, i]
            item['c'] = (s[0], s[1])
            item['r'] = s[2]
            item['idx'] = (s[3], s[4],s[5])
            stereo_list.append(item)

        return stereo_list
    target.generateStereo = generateStereo
    
    return target