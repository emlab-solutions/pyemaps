# -------------------------------------------------------
# liveness test for emaps.dif module
# used in new build of the module
# The EMControls used here is the same as baseline test
# module
# ------------------------------------------------------
c_name = 'Silicon'

def runCSFTests():
    from pyemaps import Crystal as cr
    si = cr.from_builtin(c_name)
    
    print(si)
    # generate diffraction on the crystal instance with all default controls
    # parameters, default controls returned as the first output ignored
    v = 100
    sm = 1.0

    for i in [1,2,3,4]:
        for j in [1, 0]:
            sfs = si.generateCSF(kv = v, smax = sm, sftype = i, aptype = j)
            si.printCSF(sfs, kv = v, smax = sm, sftype = i, aptype = j)

if __name__ == "__main__":
    runCSFTests()
