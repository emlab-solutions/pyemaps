
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
        and matchig functions in pyemaps EDIOM module.
        
        The generated database file is saved to directory pointed by environment variable
        PYEMAPS_DATA or in current working directory.

        :param emc: Control parameters
        :type emc: EMControls, optional

        :param xa: x-axis, optional
        :type xa: three integer tuple.

        :param res: resolution of diffraction patterns to be generated ranges from 100 to 300, 
                    The higher the resolution, the more diffraction patterns is generated. 
        :type res: integer, defaults to 100, optional.

        :param vertices: an array of 3 or 4 vectors that form a closed polygon within which 
                        the diffraction patterns are generated.
        :type vertices: three integer tuple, optional
        
        :return: a tuple of a status code and database file name
        :rtype: tuple of an integer and a string
        

    .. note::

        The vectors forming the vertices of a polygon region are indexes on the stereodiagram.
        See this image for illustration for selecting these vertices.

        The diffraction patterns database file produced will be consumed by pyemaps ediom module
        for experimental diffraction pattern serach adn indexing.

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
            print(f'Error running generating diffraction patterns for {self.name}')
            return -1, final_fp

        print('*******************************************************************************')
        print(f'* The DP database for {self.name} has been generated successfully')
        print(f'* and saved in:')
        print(f'* {final_fp}')
        print('*******************************************************************************')
        return 0, final_fp
    
    target.generateDPDB = generateDPDB
    target._getDPDBFN = _getDPDBFN

    return target