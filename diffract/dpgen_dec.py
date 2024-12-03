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
def add_dpgen(target):
    try:
        from . import dif, dpgen

    except ImportError as e:             
        # return an empty target if non-extant
        return target
    else:
        LOW_RES = dpgen.get_lowres()
        HIGH_RES = dpgen.get_highres()
    
    import numpy as np
    from numpy import asfortranarray as farray
    from .. import DEF_XAXIS, DEF_KV, DEF_ZONE, DEF_CL, \
                   SIMC, EMC

    from .. import DPError

    DPDB_EXT = 'bin'
    MAX_DPDBFN = 256
    DEF_VERTMAT = [[0,0,1],[1,1,1],[0,1,1]]

    def _getDPDBFN(self):
        '''
        Constructs a bloch image output file name.
        
        Refer to :ref:`Environment Variables <Environment Variables>` 
        for how this file name is constructed.

        '''
        
        from ..fileutils import compose_ofn

        cfn = compose_ofn(None, self.name, ty='dpdb')

        l = len(cfn)
        if l > MAX_DPDBFN:
            raise DPError('Diffraction database file name must not excced 256')

        return cfn

    def generateDPDB(self, emc = EMC(),
                           xa = DEF_XAXIS,
                           res = LOW_RES,
                           vertices = DEF_VERTMAT
                    ):
        
        """
        Generate a list diffraction patterns and save them in proprietory
        binary formatted database file with extension .bin.

        The database created will be used for diffraction pattern indexing
        and matchig functions in pyemaps STEM4D module.
        
        The generated database file is saved to directory pointed by environment variable
        *PYEMAPS_DATA* or in current working directory if *PYEMAPS_DATA* is not set.

        :param emc: Control parameters
        :type emc: EMControls, optional

        :param xa: x-axis, optional
        :type xa: three integer tuple.

        :param res: resolution of stereo projection map, ranging from *LOW_RES*=100 to *HIGH_RES*=300 that is
                    the number of sampling points along the radius. The higher the resolution, the more 
                    diffraction patterns are generated in the database file.

        :type res: integer, defaults to 100, optional.

        :param vertices: an array of 3 or 4 zone axis indexes that form an enclosed orientation 
                    surface area within which the diffraction patterns are generated. See the following
                    graphic illustration of the vertices input.

        :type vertices: three integer tuple, optional
        
        :return: a tuple of a status code and database file name
        :rtype: tuple of an integer and a string
        

        Input zone axis indexes define the vertices of the stereo projection map. The default
        for a cubic crystal is *DEF_VERTMAT* = [[0,0,1],[1,1,1],[0,1,1]].

        .. image:: https://github.com/emlab-solutions/imagepypy/raw/main/stereoprojectionmap.png
           :width: 75%
           :align: center

        The diffraction patterns database file produced will be consumed by pyemaps stem4d module
        for experimental diffraction pattern serach and indexing.

        """
        import os
        
        if (res > HIGH_RES) or (res < LOW_RES):
            print(f'Resolution input {res} is out of range: ({LOW_RES}, {HIGH_RES})')
            return -1, None

        self.load()
        dif.initcontrols()
        
        vt = emc.vt
        zone = emc.zone
        emc(xaxis=xa)
        simc = emc.simc

        if vt != DEF_KV:
            dif.setemcontrols(DEF_CL, vt)

        if zone != DEF_ZONE:
            dif.setzone(zone[0], zone[1], zone[2])

        if xa != DEF_XAXIS:
            dif.set_xaxis(1, xa[0], xa[1], xa[2])
        
        self.set_sim_controls(simc=simc)


        # TODO: need to replace hard code of 2 here later
        ret = dif.diffract(2)
        
        if ret == 0:
            print('Error running dif module')
            return -1, None
        vert = np.array(vertices).transpose()    
        vertices = farray(vert, dtype=int)
        
        output_fn = self._getDPDBFN()
        
        final_fp= output_fn+'.' + DPDB_EXT

        ret = dpgen.do_dpgen(res, vertices, output_fn)
        
        #release the memory
        dpgen.cleanup()

        if ret != 0:
            print(f'Error generating diffraction patterns for {self.name}')
            return -1, final_fp

        print('*******************************************************************************')
        print(f'* The diffraction pattern database for {self.name} has been generated successfully')
        print(f'* and saved in:')
        print(f'* {final_fp}')
        print('*******************************************************************************')
        return 0, final_fp
    
    target.generateDPDB = generateDPDB
    target._getDPDBFN = _getDPDBFN

    return target