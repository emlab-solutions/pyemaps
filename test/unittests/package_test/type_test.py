from pyemaps import Crystal as cr
from pyemaps import EMC, SIMC

RELEASE_BUILD_ERRMSG = '*dpgen* module is likely NOT A RELEASE build or its a debug build'
FREE_BUILD_ERRMSG = '*dpgen* module is likely NOT A FREE package build'
FULL_BUILD_ERRMSG = '*dpgen* module is likely NOT A FULL package build'

FREE_RES_HIGH = 300
FULL_RES_HIGH = 500

def test_dpgen_free():
    from pyemaps import dpgen
    
    high_res = dpgen.get_highres()
    # check if the module in the package is free
    assert high_res == FREE_RES_HIGH, \
                       f"{FREE_BUILD_ERRMSG}" 

def test_dpgen_full():
    from pyemaps import dpgen
    
    # check if the module in the package is free
    high_res = dpgen.get_highres()
    assert high_res == FULL_RES_HIGH, \
                       f"{FULL_BUILD_ERRMSG}" 
    

def test_dpgen_release():
    
    from pyemaps import Crystal as cr
    import os
    
    si = cr.from_builtin('Silicon')

    #  first generate a DP database file
    xa0=(2,0,0)
    res = 200
    ret, dbfn = si.generateDPDB(emc=EMC(zone=(0,0,1)), res = res, xa = xa0)
    assert (ret == 0 and os.path.exists(dbfn)), \
                f'Generation of DPDB for Silicon failed'
        

    datfn = os.path.splitext(dbfn)[0]+".dat"
    exists = os.path.exists(datfn)

    assert exists == False, \
        f"{RELEASE_BUILD_ERRMSG}"


if __name__ == '__main__':
    
    print('\n*****unit test for package types started*****\n')
    try:
        test_dpgen_release()
    except AssertionError as e:
        print(f'Unit test for RELEASE (non-debug) build failed for module dpgen: {e}')
    else:
        print('Module dpgen build is non-debug or release')
    
    try:
        test_dpgen_free()
    except AssertionError as e:
        print(f'Unit test a FREE build failed for module dpgen: {e}')
    else:
        print('Module dpgen is build as free package')

    try:
        test_dpgen_full()
    except AssertionError as e:
        print(f'Unit test for a paid build failed for module dpgen: {e}')
    else:
        print('Module dpgen is build as paid package')

    print('\n*****unit test for package types completed*****\n')