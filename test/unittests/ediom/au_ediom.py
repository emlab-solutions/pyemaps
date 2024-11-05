
import os
from pyemaps import Crystal as cr
from pyemaps import EMC

db_home = os.getenv('PYEMAPS_DATA')

def getTestDBFN():
    # db_home = os.getenv('PYEMAPS_DATA')
    # return os.path.join(db_home, 'dpdb', 'Gold_FCC-20230220194314.bin')
    return os.path.join(db_home, 'dpdb', 'Aluminium-20230320200733.bin')

def getTestGoldDBFN():
    return os.path.join(db_home, 'dpdb', 'Gold_FCC-20230220194314.bin')
# def getIMSFn():
#     db_home = os.getenv('PYEMAPS_DATA')
#     # return os.path.join(db_home, 'bloch', 'Silicon-20230123155711.im3')
#     return os.path.join(db_home, 'dpdb', 'ediom', 'ExampleDP_Au_0.im3')
#     # return os.path.join(db_home, 'dpdb', 'ediom', 'ExampleDP_Au_2.im3')

def getXTemplateFn():
    # db_home = os.getenv('PYEMAPS_DATA')
    return os.path.join(db_home, 'dpdb', 'ediom', 'PeakTemplate.im3')
    # return os.path.join(db_home, 'dpdb', 'AuDP0.img')

def getGoldImage():
    return os.path.join(db_home, 'dpdb', 'ediom', 'ExampleDP_Au_0.im3')

def getIMSFn():
    # db_home = os.getenv('PYEMAPS_DATA')
    # return os.path.join(db_home, 'bloch', 'Silicon-20230123155711.im3')
    # return os.path.join(db_home, 'dpdb', 'ediom', 'ExampleDP_Au_0.im3')
    # return os.path.join(db_home, 'dpdb', 'ediom', 'ExampleDP_Au_1.img')
    return os.path.join(db_home, 'dpdb', 'ediom', 'dp50.img')
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

    au.indexExpDP(dbfn, img_center=(65.34, 67.01), peak_threshold=0.8)
    
    au.showMatchedDBDP()
    au.printDPIndexDetails()

    au.release_ediom()

def test_ediom_from_SHfile_al():
    from pyemaps import Crystal as cr
    from pyemaps import ediom
    import numpy as np
   
    
    
    cryst = cr.from_builtin("Aluminium")

    #  first generate a DP database file
    # xa0=(2,0,0)
    # res = 200
    # ret, dbfn = cryst.generateDPDB(emc=EMC(zone=(0,0,1)), res = res, xa = xa0)

    # if ret != 0:
    #     print(f'failed to generate a dp databaes')
    #     return -1
    
    # locate the experimental image file
    # edc0=ediom.cvar.edc
    # edc0.set_center(65.34, 67.01)
    dpdbfn = getTestDBFN()
    ret, mr, mc =cryst.loadDPDB(dbfn = dpdbfn, bShowDBMap=True)
    
    if ret != 0 or mr <= 0 or mc <=0:
        print(f"Error loading DP database from file {dpdbfn}")
        cryst.release_ediom()
        exit(1)

    xifn = getIMSFn()
    try:
       cryst.importSHExpImage(xifn, bShow=True)
    except Exception as e:
        cryst.release_ediom()
        raise ValueError from e

    cc0 = 29.0
    sigma0 = 3.0
    imc = (99.923, 99.919)
    # filter_opt/ion =

    cryst.indexExpDP(cc=cc0,
                     sigma = sigma0,
                     img_center=imc,
                     rmin=10,
                     search_box = 10.0,
                     scaling_option = (1,2), 
                     filter_threshold = 0.0,
                     peak_threshold=0.8,
                     bDebug=False)
    
    cryst.showMatchedDBDP()
    cryst.showMatchingIndexMap(mr, mc)

    cryst.printDPIndexDetails()

    cryst.release_ediom()

def test_ediom_from_Rawfile(cname='Gold_FCC', xifn=None):
    from pyemaps import Crystal as cr
    from pyemaps import ediom
    import numpy as np
   
    
    cryst = cr.from_builtin(cname)

    #  first generate a DP database file
    xa0=(2,0,0)
    res = 200
    ret, dbfn = cryst.generateDPDB(emc=EMC(zone=(0,0,1)), res = res, xa = xa0)

    if ret != 0:
        print(f'failed to generate a dp databaes')
        return -1
    
    # locate the experimental image file
    # edc0=ediom.cvar.edc
    # edc0.set_center(65.34, 67.01)

    if xifn is None or not os.path.exists(xifn):
        print(f'Experimental image must be provided')
        return -1

    # dbfn = getTestDBFN()
      
    try:
       cryst.importRawExpImage(xifn, 8, 2, 128, 128, 1, bShow=True)
    except Exception as e:
        cryst.release_ediom()
        raise ValueError from e
    cc0 = 29.0
    sigma0 = 3.0
    imc = (99.923, 99.919)

    cryst.indexExpDP(dbfn, 
                     cc=cc0,
                     sigma = sigma0,
                     img_center=imc,
                     rmin=10,
                     search_box = 10.0,
                     scaling_option = (1,2), 
                     filter_threshold = 0.1,
                     peak_threshold=0.7)
    
    cryst.showMatchedDBDP()
    cryst.printDPIndexDetails()

    cryst.release_ediom()
#  

def test_ediom_from_SHfile_gold():
    from pyemaps import Crystal as cr
    from pyemaps import ediom
    import numpy as np
   
    
    au = cr.from_builtin('Gold_FCC')

    xifn = getGoldImage()
    dbfn = getTestGoldDBFN()
    
    # au.importRawExpImage(xifn, 8, 2, 128, 128, 1, bShow=True)     
    try:
       au.importSHExpImage(xifn, bShow=True)
    except Exception as e:
        au.release_ediom()
        raise ValueError from e

    au.indexExpDP(dbfn, img_center=(65.34, 67.01), peak_threshold=0.8)
    
    au.showMatchedDBDP()
    au.printDPIndexDetails()

    au.release_ediom()

if __name__ == '__main__':
    xifn0 = getIMSFn()
    # test_ediom_from_Rawfile(xifn=xifn0)
    test_ediom_from_SHfile_al()
    # test_ediom_npy()

    # test_ediom_from_SHfile_gold()