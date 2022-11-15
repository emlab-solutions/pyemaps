
def add_dpgen(target):
    def generateDPDB(self, res =1):
        """
        Generate a list diffraction paterns and save them in proprietory
        binary formatted database file.

        The database created will be used for diffraction pattern indexing
        and recognition functions.

        This feature is accessible for paid customers only.

        :param res: resolution of the diffraction pattern
        :type res: integer

        
        """
        try:
            from . import dif, dpgen

        except ImportError as e:               
            print(f"Error: required module pyemaps.dpgen or pyemaps.dif not found")
        
        import numpy as np
        from numpy import asfortranarray as farray
        
        dp_res_lookup = [('small', 0.01),
                        ('medium', 0.005),
                        ('large', 0.0025)]

        dif.initcontrols()
        
        self.load()
            
        dif.set_xaxis(1, 2, 0, 0)
        ret = dif.diffract(2)
        
        if ret == 0:
            print('Error running dif module')
            return -1

        vertices0 = np.array([[0,0,1],[1,1,1],[0,1,1]])
        vertices = farray(vertices0.transpose(), dtype=int)

        sres, fres = dp_res_lookup[res-1]
        output_fn = self.name +'_' + sres

        print(f"input for do_gen: {vertices},{output_fn}")
        ret = dpgen.do_dpgen(fres, vertices, output_fn)
        if ret != 0:
            print(f'Error running generating diffraction patterns for {self.name}')
            return -1

        ret = dpgen.readbin_new(output_fn+' ', "bin"+' ')
        if ret != 0: 
            print(f'Error running generating diffraction patterns for {self.name}')
            return -1

        #release the memory
        dif.diff_internaldelete(0)
        dif.diff_delete()

        return 0
    
    target.generateDPDB = generateDPDB

    return target