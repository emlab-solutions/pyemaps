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
def add_stereo(target):
    def generateStereo(self, xa = (0,2,0), 
                            tilt=(0.0,0.0),
                            zone = (0, 0, 1)):
        """
        Calculate the crystal's stereographic projection (stereodiagram).

        :param xa: the crystal's horizontal axis in reciprocal space, as three integers.
        :type xa: tuple of int, optional
        :param tilt: sample tilt ``(x, y)``.
        :type tilt: tuple of float, optional
        :param zone: zone axis, as three integers.
        :type zone: tuple of int, optional
        :return: the projected poles, one dictionary each:

            .. code-block:: python

                {
                    'c': (x, y),          # center
                    'r': r,               # radius
                    'idx': (h, k, l)      # Miller indices
                }

        :rtype: list of dict
        :raise ~pyemaps.errors.StereodiagramError: if the calculation fails.

        To display the result, use :py:func:`~pyemaps.display.showStereo`.
        """
        from . import dif, stereo
        
        import numpy as np
        from numpy import asfortranarray as farray

        from ..errors import StereodiagramError 
        from .. import DEF_XAXIS

        dif.initcontrols()
        dif.setzone(zone[0], zone[1], zone[2])        
        
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