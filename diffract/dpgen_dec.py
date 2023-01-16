
def add_dpgen(target):
    try:
        from . import dif, dpgen

    except ImportError as e:               
        print(f"Error: required module pyemaps.dpgen or pyemaps.dif not found")
    else:
        LOW_RES = dpgen.get_lowres()
        HIGH_RES = dpgen.get_highres()
    
    import numpy as np
    from numpy import asfortranarray as farray
    from .. import DEF_XAXIS

    from .. import DPError

    DPDB_EXT = 'bin'
    MAX_DPDBFN = 256
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
        
        # # fortran string
        # ffn = farray(np.empty((256), dtype='c'))
        # for i in range(l):
        #     ffn[i] = cfn[i]

        return cfn

    def generateDPDB(self, xa = DEF_XAXIS, res = LOW_RES):
        
        """
        Generate a list diffraction paterns and save them in proprietory
        binary formatted database file.

        The database created will be used for diffraction pattern indexing
        and recognition functions.

        This feature is accessible for paid customers only.

        :param res: resolution of the diffraction pattern
        :type res: integer

        
        """
        import os
        
        # dp_res_lookup = [('small', 0.01),
        #                 ('medium', 0.0025),
        #                 ('large', 0.001)]
        if (res > HIGH_RES) or (res < LOW_RES):
            print(f'Resolution input {res}is out of range: ({LOW_RES}, {HIGH_RES})')
            return -1

        dif.initcontrols()
        
        self.load()
        
        if xa != DEF_XAXIS:
            dif.set_xaxis(1, xa[0], xa[1], xa[2])

        # TODO: need to replace hard code of 2 here later
        ret = dif.diffract(2)
        
        if ret == 0:
            print('Error running dif module')
            return -1

        vertices0 = np.array([[0,0,1],[1,1,1],[0,1,1]])
        vertices = farray(vertices0, dtype=int)
        
        output_fn = self._getDPDBFN()

        ret = dpgen.do_dpgen(res, vertices, output_fn)
        
        #release the memory
        dpgen.cleanup()

        if ret != 0:
            print(f'Error running generating diffraction patterns for {self.name}')
            return -1

        ret = dpgen.readbin_new(output_fn, DPDB_EXT)
        if ret != 0: 
            print(f'Error running generating diffraction patterns for {self.name}')
            return -1

        final_fp= output_fn+'.' + DPDB_EXT
        print(f'output dpgen file: {final_fp}')

        return 0
    
    target.generateDPDB = generateDPDB
    target._getDPDBFN = _getDPDBFN

    return target