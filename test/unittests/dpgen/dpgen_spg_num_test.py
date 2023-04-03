from pyemaps import Crystal as cr
from pyemaps import EMC, SIMC
import os


def test_dpgen_spg_225():
    
    si = cr.from_builtin('Aluminium')

    #  first generate a DP database file
    xa0=(2,0,0)
    res = 200
    ret, dbfn = si.generateDPDB(emc=EMC(zone=(0,0,1)), res = res, xa = xa0)
    assert (ret == 0 and os.path.exists(dbfn)), \
                f'Space Group 225 support failed'

    datfn = os.path.splitext(dbfn)[0]+".dat"
    exists = os.path.exists(datfn)

    assert exists == False, \
        f"Space Group 225 support failed"

def test_dpgen_spg_227():
    
    si = cr.from_builtin('Silicon')

    #  first generate a DP database file
    xa0=(2,0,0)
    res = 200
    ret, dbfn = si.generateDPDB(emc=EMC(zone=(0,0,1)), res = res, xa = xa0)
    assert (ret == 0 and os.path.exists(dbfn)), \
                f'Space Group 227 support failed'
        

    datfn = os.path.splitext(dbfn)[0]+".dat"
    exists = os.path.exists(datfn)

    assert exists == False, \
        f"Space Group 227 support failed"
    
def test_dpgen_spg_229():
    
    si = cr.from_builtin('AluminiumOxide')

    #  first generate a DP database file
    xa0=(2,0,0)
    res = 200
    ret, dbfn = si.generateDPDB(emc=EMC(zone=(0,0,1)), res = res, xa = xa0)
    assert (ret != 0 or not os.path.exists(dbfn)), \
                f'Space Group 229 support failed'

    datfn = os.path.splitext(dbfn)[0]+".dat"
    exists = os.path.exists(datfn)

    assert exists == False, \
        f"Space Group 229 support failed"

def test_dpgen_spg_NS():
    
    si = cr.from_builtin('Chromium_BCC')

    #  first generate a DP database file
    xa0=(2,0,0)
    res = 200
    ret, dbfn = si.generateDPDB(emc=EMC(zone=(0,0,1)), res = res, xa = xa0)
    assert (ret == 0 and os.path.exists(dbfn)), \
                f'Failed to disable space Group 167 support'
    
if __name__ == '__main__':
    
    print('\n*****unit test for space group support in module dpgen started*****\n')

    try:
        test_dpgen_spg_225()
    except AssertionError as e:
        print(f'Unit test for space group 225 module dpgen failed: {e}')
    else:
        print('Unit test for space group 225 module dpgen SUCCESSFUL')

    try:
        test_dpgen_spg_227()
    except AssertionError as e:
        print(f'Unit test for space group 227 module dpgen failed: {e}')
    else:
        print('Unit test for space group 227 module dpgen SUCCESSFUL')

    try:
        test_dpgen_spg_229()
    except AssertionError as e:
        print(f'Unit test for space group 229 module dpgen failed: {e}')
    else:
        print('Unit test for space group 229 module dpgen SUCCESSFUL')

    print('\n*****unit test for space group support in module dpgen completed*****\n')