
import os
from pyemaps import Crystal as cr
from pyemaps import EMC


def getTestDBFN():
    db_home = os.getenv('PYEMAPS_DATA')
    # return os.path.join(db_home, 'dpdb', 'Gold_FCC-20230220194314.bin')
    return os.path.join(db_home, 'dpdb', 'Gold_FCC-20230306182550.bin')

def getIMSFn():
    db_home = os.getenv('PYEMAPS_DATA')
    # return os.path.join(db_home, 'bloch', 'Silicon-20230123155711.im3')
    # return os.path.join(db_home, 'dpdb', 'ediom', 'ExampleDP_Au_0.im3')
    return os.path.join(db_home, 'dpdb', 'ediom', 'ExampleDP_Au_2.im3')

def getXTemplateFn():
    db_home = os.getenv('PYEMAPS_DATA')
    return os.path.join(db_home, 'dpdb', 'ediom', 'PeakTemplate.im3')
    # return os.path.join(db_home, 'dpdb', 'AuDP0.img')



def getIMSFn():
    db_home = os.getenv('PYEMAPS_DATA')
    # return os.path.join(db_home, 'bloch', 'Silicon-20230123155711.im3')
    # return os.path.join(db_home, 'dpdb', 'ediom', 'ExampleDP_Au_0.im3')
    return os.path.join(db_home, 'dpdb', 'ediom', 'ExampleDP_Au_2.im3')

def test_ediom(cname='Gold_FCC', xifn=None):
    from pyemaps import Crystal as cr
    
    au = cr.from_builtin(cname)

    # #  first generate a DP database file
    # xa0=(2,0,0)
    # res = 200
    # # ret, dbfn = au.generateDPDB(emc=EMC(zone=(0,0,1)), res = res, xa = xa0)

    # if ret != 0:
    #     print(f'failed to generate a dp databaes')
    #     return -1
    
    # locate the experimental image file
    if xifn is None or not os.path.exists(xifn):
        print(f'Experimental image must be provided')
        return -1

    dbfn = getTestDBFN()
    au.indexExpDP(dbfn, xifn, icenter=(65.0, 66.4), Sthreshold=0.8525)

if __name__ == '__main__':
    xifn0 = getIMSFn()
    test_ediom(xifn=xifn0)