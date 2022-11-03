
def add_mxtal(target):
    from . import dif
    from .. import ID_MATRIX, MLEN, DEF_CELLBOX, \
                  DEF_XZ, DEF_ORSHIFT, DEF_TRSHIFT,DEF_LOCASPACE
    from .. import MxtalError
    from ..fileutils import compose_ofn
    DEF_DISTANCE = 0.0

    def print_xyz(self, xyzdict):
        '''
        Save mxtal data in .xyz format
        '''
        if xyzdict is None or 'xyz' not in xyzdict:
            raise MxtalError("Invalid mxtal data")

        xyzlist = xyzdict['xyz']

        if 'cell' not in xyzdict:
            raise MxtalError("Invalid mxtal data, must have cell constant data")
        
        slines = []
        nxyz = len(xyzlist)

        slines.append(str(nxyz))      
        c0, c1, c2, c3, c4, c5 = xyzdict['cell']
        slines.append(str(f'\t {c0} {c1} {c2} {c3} {c4} {c5}'))
        for xyz in xyzlist:
            s, x, y, z = xyz['symb'], xyz['x'], xyz['y'], xyz['z']
            sx = '{0: < #014.10f}'. format(float(x))
            sy = '{0: < #014.10f}'. format(float(y))
            sz = '{0: < #014.10f}'. format(float(z))
            
            slines.append(str(f'{s:<10}\t{sx} {sy} {sz}'))
        print('\n'.join(slines))

            
    def write_xyz(self, xyzdict, fn=None):
        '''
        Save mxtal data into a file <fn>
        if fn is None: autogenerate file name by crystal name and time stamp
        if fn is not None, the file will be generate placed in in the fn path if exists
        or in pyemaps data home directory otherwise
        
        '''
        if 'xyz' not in xyzdict:
            return -1
        xyzlist = xyzdict['xyz']

        if 'cell' not in xyzdict:
            return -1
        slines = []
        nxyz = len(xyzlist)

        xyzfn = compose_ofn(fn, self.name, ty='mxtal') +'.xyz'
        
        try:
            with open(xyzfn, 'w') as f:
                slines.append(str(nxyz))      
                c0, c1, c2, c3, c4, c5 = xyzdict['cell']
                slines.append(str(f'\t {c0} {c1} {c2} {c3} {c4} {c5}'))
                for xyz in xyzlist:
                    s, x, y, z = xyz['symb'], xyz['x'], xyz['y'], xyz['z']
                    sx = '{0: < #014.10f}'. format(float(x))
                    sy = '{0: < #014.10f}'. format(float(y))
                    sz = '{0: < #014.10f}'. format(float(z))
                    
                    slines.append(str(f'{s:<10}\t{sx} {sy} {sz}'))
                # print(f'writing data: {slines}')
                f.writelines('\n'.join(slines))
        except (FileNotFoundError, IOError, PermissionError) as e:
            print(f'Error writing xyz data file {fn}')
            return -1
        except Exception:
            return -1
        else:
            print(f'Successfully saved mxtal data in file: {xyzfn}')
            return 0

    def generateMxtal(self, 
                      trMatrix = ID_MATRIX, 
                      trShift = DEF_TRSHIFT, #Transformation shift
                      cellbox = DEF_CELLBOX,
                      xz = DEF_XZ,
                      orShift = DEF_ORSHIFT, #Origin shift
                      locASpace = DEF_LOCASPACE,
                      bound = None): #location in A Space
        
        import numpy as np
        from numpy import asfortranarray as farray
        from . import mxtal as MX

        dif.initcontrols()
        
        self.load(cty=1)
            
        tmat = farray(np.array(trMatrix))
        
        pxz = farray(np.array(xz))

        if bound is not None:
            ret = MX.do_mxtal(tmat, trShift, cellbox[0], cellbox[1],
                            pxz[0], pxz[1], orShift, locASpace, bound)
        else:
            ret = MX.do_mxtal(tmat, trShift, cellbox[0], cellbox[1],
                            pxz[0], pxz[1], orShift, locASpace)
        
        if ret != 1:
            raise MxtalError('Failed to starting mxtal module')
        
        na = MX.get_nxyz()
        
        if na <=0:
            raise MxtalError('Failed to generate data')

        xyz, ret = MX.get_xyzdata(na)
    
        if ret != 1:
            raise MxtalError('Failed to retrieve data')

        sym = farray(np.empty((MLEN, na), dtype='c'))
        sym, ret = MX.get_symdata(sym)
    
        if ret != 1:
            raise MxtalError('Failed to retrieve data')

        tsym = np.transpose(sym)
        txyz = np.transpose(xyz)
        
        retxyz = []
        for i in range(na):          
            s = bytearray(tsym[i]).decode('utf-8').strip(" \x00")
            
            x, y, z = txyz[i]
            retxyz.append(dict(symb = s, x= x, y=y, z=z))

        # cell = np.array([0.0]*6)
        nc = 6
        cell, ret = MX.get_cellconst(nc)

        if ret !=0:
            raise MxtalError(f'Failed to retrieve cell constants: {ret}')

        # clean up
        MX.cleanup()
        return dict( xyz = retxyz, cell=cell)

    target.generateMxtal = generateMxtal
    target.print_xyz = print_xyz
    target.write_xyz =write_xyz
    return target