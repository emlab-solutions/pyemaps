from pyemaps import Crystal as cr
from pyemaps import EMC, SIMC

FREE_RES_HIGH = 300
FULL_RES_HIGH = 500

def test_dpgen_free():
    from pyemaps import dpgen
    
    high_res = dpgen.get_highres()
    assert high_res == FREE_RES_HIGH, \
                       f"*dpgen* module is NOT FREE" 

def test_dpgen_full():
    from pyemaps import dpgen
    
    high_res = dpgen.get_highres()
    assert high_res == FULL_RES_HIGH, \
                       f"*dpgen* module is NOT FULL" 
# def test_crystal_free():
#     from pyemaps import Crystal as cr

if __name__ == '__main__':
    # basic()
    # doctring_test()
    # print('unit test for EMC and SIMC class basics successful')
    test_dpgen_free()
    test_dpgen_full()