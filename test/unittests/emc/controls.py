from pyemaps import Crystal as cr
from pyemaps import EMC, SIMC

from pyemaps.emcontrols import DEF_EMC, DEF_SIMC, SIMC_DESC

def assert_docstring(k, doc1, doc2):
    assert isinstance(doc1, str) and isinstance(doc1, str) and doc1==doc2,  \
            f"Docstring for property {k} does not match: {doc1} != {doc2}"

def basic():
    
    si = cr.from_builtin()
    emc1, _ = si.generateDP()
    bimg = si.generateBloch()
    emc2 = bimg.blochList[0][0]
    emc=EMC()

# checking EMC objects

    assert emc.xaxis != emc1.xaxis
    
    assert emc.xaxis != emc2.xaxis
    
    for k in DEF_EMC:
        if k != 'simc':
            assert emc._check_def(k) == True 
            if k != 'xaxis':
                assert emc1._check_def(k) == True 
                if k != 'mode' and k != 'cl':
                    assert emc2._check_def(k) == True


    simc = emc.simc
    simc1 = emc1.simc
    simc2 = emc2.simc

# checking SIMC objects
    # assert simc == simc1

    # assert simc2 != simc1
    # assert simc2 != simc

    for k in DEF_SIMC:
        assert simc._check_def(k) == True 
        assert simc1._check_def(k) == True 
    

def doctring_test():
    for k in DEF_EMC:

        kstr = DEF_EMC[k]['desc']
        if k=='tilt':
            str1 = EMC.tilt.__doc__
        elif k=='zone':
            str1 = EMC.zone.__doc__
        elif k=='cl':
            str1 = EMC.cl.__doc__  
        elif k=='vt':
            str1 = EMC.vt.__doc__  
        elif k=='mode':
            str1 = EMC.mode.__doc__ 
        elif k=='dsize':
            str1 = EMC.dsize.__doc__ 
        elif k=='defl':
            str1 = EMC.defl.__doc__ 
        elif k=='xaxis':
            str1 = EMC.xaxis.__doc__ 
        elif k=='aperture':
            str1 = EMC.aperture.__doc__ 
        elif k=='pix_size':
            str1 = EMC.pix_size.__doc__ 
        elif k=='det_size':
            str1 = EMC.det_size.__doc__ 
        elif k =='simc':
            str1 = EMC.simc.__doc__

        assert_docstring(k, str1, kstr)

    for k in SIMC_DESC:

        kstr = SIMC_DESC[k]
        if k=='excitation':
            str1 = SIMC.excitation.__doc__ 
        if k=='gmax':
            str1 = SIMC.gmax.__doc__ 
        if k=='bmin':
            str1 = SIMC.bmin.__doc__ 
        if k=='intensity':
            str1 = SIMC.intensity.__doc__ 
        if k=='gctl':
            str1 = SIMC.gctl.__doc__ 
        if k=='zctl':
            str1 = SIMC.zctl.__doc__ 
        if k=='omega':
            str1 = SIMC.omega.__doc__  
        if k=='sampling':
            str1 = SIMC.sampling.__doc__ 
        if k=='sth':
            str1 =  SIMC.sth.__doc__ 

        assert_docstring(k, str1, kstr)

def main():
    try:
        basic()
    except AssertionError as e:
        print(f'Basic test failed: {e}')
    else:
        print(f'basic test succeeded')

    try:
        doctring_test()
    except AssertionError as e:
        print(f'Docstring test failed: {e}')
    else:
        print(f'Docstring test succeeded')

    print('unit test for EMC and SIMC class basics completed')

if __name__ == '__main__':
    main()
