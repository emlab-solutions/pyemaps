
import os
from pyemaps import Crystal as cr
from pyemaps import EMC


def getTestDBFN():
    db_home = os.getenv('PYEMAPS_DATA')
    # return os.path.join(db_home, 'dpdb', 'Gold_FCC-20230220194314.bin')
    return os.path.join(db_home, 'dpdb', 'Gold_FCC-20230313104014.bin')

# def getIMSFn():
#     db_home = os.getenv('PYEMAPS_DATA')
#     # return os.path.join(db_home, 'bloch', 'Silicon-20230123155711.im3')
#     return os.path.join(db_home, 'dpdb', 'ediom', 'ExampleDP_Au_0.im3')
#     # return os.path.join(db_home, 'dpdb', 'ediom', 'ExampleDP_Au_2.im3')

def getXTemplateFn():
    db_home = os.getenv('PYEMAPS_DATA')
    return os.path.join(db_home, 'dpdb', 'ediom', 'PeakTemplate.im3')
    # return os.path.join(db_home, 'dpdb', 'AuDP0.img')



def getIMSFn():
    db_home = os.getenv('PYEMAPS_DATA')
    # return os.path.join(db_home, 'bloch', 'Silicon-20230123155711.im3')
    # return os.path.join(db_home, 'dpdb', 'ediom', 'ExampleDP_Au_0.im3')
    return os.path.join(db_home, 'dpdb', 'ediom', 'ExampleDP_Au_1.img')
    # return os.path.join(db_home, 'dpdb', 'ediom', 'ExampleDP_Au_2.im3')

def test_ediom_npy(cname='Gold_FCC'):
    from pyemaps import Crystal as cr
    from pyemaps import ediom
    import numpy as np
   
    
    au = cr.from_builtin(cname)

    #  first generate a DP database file
    # xa0=(2,0,0)
    # res = 200
    # ret, dbfn = au.generateDPDB(emc=EMC(zone=(0,0,1)), res = res, xa = xa0)

    # if ret != 0:
    #     print(f'failed to generate a dp databaes')
    #     return -1
    
    # locate the experimental image file
    # edc0=ediom.cvar.edc
    # edc0.set_center(65.34, 67.01)

    dbfn = getTestDBFN()
    # au.importSHExpImage(xifn, bShow=True)
    # au.importRawExpImage(xifn, 8, 2, 128, 128, 1, bShow=True)
    n = 128
    img_arr = np.array(np.zeros((n,n), dtype=np.float32))
    for i in range(n):
        for j in range(n):
            img_arr[i][j] = np.random.uniform(0.01, 1.0)
        
    try:
        au.importExpImageFromNPY(img_arr, bShow=True)
    except Exception as e:
        au.release_ediom()
        raise ValueError from e

    au.indexExpDP(dbfn, img_center=(65.34, 67.01), peak_threshold=0.825)
    
    au.showMatchedDBDP()
    au.printDetails()

    au.release_ediom()

def test_ediom_from_SHfile(cname='Gold_FCC', xifn=None):
    from pyemaps import Crystal as cr
    from pyemaps import ediom
    import numpy as np
   
    
    au = cr.from_builtin(cname)

    #  first generate a DP database file
    # xa0=(2,0,0)
    # res = 200
    # ret, dbfn = au.generateDPDB(emc=EMC(zone=(0,0,1)), res = res, xa = xa0)

    # if ret != 0:
    #     print(f'failed to generate a dp databaes')
    #     return -1
    
    # locate the experimental image file
    # edc0=ediom.cvar.edc
    # edc0.set_center(65.34, 67.01)

    if xifn is None or not os.path.exists(xifn):
        print(f'Experimental image must be provided')
        return -1

    dbfn = getTestDBFN()
    
    # au.importRawExpImage(xifn, 8, 2, 128, 128, 1, bShow=True)     
    try:
       au.importSHExpImage(xifn, bShow=True)
    except Exception as e:
        au.release_ediom()
        raise ValueError from e

    au.indexExpDP(dbfn, img_center=(65.34, 67.01), peak_threshold=0.825)
    
    au.showMatchedDBDP()
    au.printDetails()

    au.release_ediom()

def test_ediom_from_Rawfile(cname='Gold_FCC', xifn=None):
    from pyemaps import Crystal as cr
    from pyemaps import ediom
    import numpy as np
   
    
    au = cr.from_builtin(cname)

    #  first generate a DP database file
    # xa0=(2,0,0)
    # res = 200
    # ret, dbfn = au.generateDPDB(emc=EMC(zone=(0,0,1)), res = res, xa = xa0)

    # if ret != 0:
    #     print(f'failed to generate a dp databaes')
    #     return -1
    
    # locate the experimental image file
    # edc0=ediom.cvar.edc
    # edc0.set_center(65.34, 67.01)

    if xifn is None or not os.path.exists(xifn):
        print(f'Experimental image must be provided')
        return -1

    dbfn = getTestDBFN()
      
    try:
       au.importRawExpImage(xifn, 8, 2, 128, 128, 1, bShow=True)
    except Exception as e:
        au.release_ediom()
        raise ValueError from e

    au.indexExpDP(dbfn, img_center=(65.34, 67.01), peak_threshold=0.825)
    
    au.showMatchedDBDP()
    au.printDetails()

    au.release_ediom()
#   
if __name__ == '__main__':
    xifn0 = getIMSFn()
    test_ediom_from_Rawfile(xifn=xifn0)
    test_ediom_from_SHfile(xifn=xifn0)
    test_ediom_npy()