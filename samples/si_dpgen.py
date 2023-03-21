
def si_dpdb(cname='Silicon'):
    from pyemaps import Crystal as cr
    from pyemaps import EMC, SIMC
    # import numpy as np
    import os
   
    
    cryst = cr.from_builtin(cname)

    #  first generate a DP database file
    xa0=(2,0,0)   # x-axis, will be folded into EMC object
    res = 200     # 
    ret, dbfn = cryst.generateDPDB(emc=EMC(zone=(0,0,1), 
                                   simc=SIMC(gmax=3.9)), 
                                   xa = xa0,
                                   res = res)

    if ret != 0:
        print(f'failed to generate a dp databaes')
        return -1

    if dbfn is None or not os.path.exists(dbfn):
        print(f'Error finding generated DP database file')
        return -1


if __name__ == '__main__':
    si_dpdb()