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
        """
        Compose the output file name for a diffraction pattern database, without the ``.bin``
        extension. See :ref:`Environment Variables <Environment Variables>`.
        """
        
        from ..fileutils import compose_ofn

        cfn = compose_ofn(None, self.name, ty='dpdb')

        l = len(cfn)
        if l > MAX_DPDBFN:
            raise DPError('Diffraction database file name must not excced 256')

        return cfn

    def generateDPDB(self, emc = None,
                           xa = DEF_XAXIS,
                           res = LOW_RES,
                           vertices = DEF_VERTMAT
                    ):
        
        """
        Generate a database of kinematic diffraction patterns for this crystal, over a range of
        orientations, and save it to a ``.bin`` file. 4D-STEM pattern indexing
        (:py:meth:`~pyemaps.stackimg.StackImage.indexImage`) uses it. This is a licensed feature.

        The file is saved in the ``dpdb`` folder of the pyEMAPS data folder; see
        :ref:`Environment Variables <Environment Variables>`.

        :param emc: microscope and simulation controls. Its accelerating voltage, zone axis and
            simulation controls are used.
        :type emc: :py:class:`~pyemaps.emcontrols.EMControl`, optional
        :param xa: the crystal's horizontal axis, as three integers. Defaults to ``(0, 0, 0)``,
            which lets the backend choose it.
        :type xa: tuple of int, optional
        :param res: resolution of the stereographic projection map: the number of sampling points
            along its radius, from 100 to 500. Higher resolutions put more patterns in the database.
            Defaults to 100.
        :type res: int, optional
        :param vertices: three or four zone axes, each ``[h, k, l]``, that enclose the orientation
            range to cover (see the figure below). Defaults to ``[[0,0,1], [1,1,1], [0,1,1]]``, the
            standard triangle for a cubic crystal.
        :type vertices: list of list of int, optional
        :return: ``(status, file_name)``: 0 and the database file's path on success, or -1 and
            ``None`` (or the intended path) on failure. A message is printed either way.
        :rtype: tuple

        .. image:: https://github.com/emlab-solutions/imagepypy/raw/main/stereoprojectionmap.png
           :width: 75%
           :align: center
        """
        import os
        
        if (res > HIGH_RES) or (res < LOW_RES):
            print(f'Resolution input {res} is out of range: ({LOW_RES}, {HIGH_RES})')
            return -1, None

        if emc is None:
            emc = EMC()

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