
def test_dpgen_al(cname='Aluminium'):
    from pyemaps import Crystal as cr
    from pyemaps import EMC, SIMC
    # import numpy as np
    import os
   
    
    cryst = cr.from_builtin(cname)

    #  first generate a DP database file
    xa0=(2,0,0)
    res = 200
    ret, dbfn = cryst.generateDPDB(emc=EMC(zone=(0,0,1), simc=SIMC(gmax=3.9)), res = res, xa = xa0)

    if ret != 0:
        print(f'failed to generate a dp databaes')
        return -1
    
    # locate the experimental image file
    # edc0=ediom.cvar.edc
    # edc0.set_center(65.34, 67.01)

    if dbfn is None or not os.path.exists(dbfn):
        print(f'Error finding generated DP database file')
        return -1


if __name__ == '__main__':
    test_dpgen_al()