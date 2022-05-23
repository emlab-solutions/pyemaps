# -------------------------------------------------------
# liveness test for emaps.dif module
# used in new build of the module
# The EMControls used here is the same as baseline test
# module
# ------------------------------------------------------

MAX_PROCWORKERS = 4
def genCSF(cr=None, kv = 100, smax = 1.0, sftype = 1, aptype = 1 ):
    if not cr:
        return
    sfs = cr.generateCSF(kv, smax, sftype, aptype)
    return (kv, smax, sftype, aptype), sfs

def runCSFTests(name = 'silicon'):
    from pyemaps import Crystal as cryst
    
    import concurrent.futures
    cr = cryst.from_builtin(name)
    print(cr)
    # cr = cryst.from_builtin(name)
    
    # generate diffraction on the crystal instance with all default controls
    # parameters, default controls returned as the first output ignored
    v = 100
    sm = 1.0
    
    fs=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_PROCWORKERS) as e:
       
        for i in [1,2,3,4]:
            for j in [1, 0]:
                f = e.submit(genCSF, cr = cr, kv = v, smax = sm, sftype = i, aptype = j)
                fs.append(f)

        # sfs = si.generateCSF(kv = v, smax = sm, sftype = i, aptype = j)
        # si.printCSF(sfs, kv = v, smax = sm, sftype = i, aptype = j)

    #  for i in range(-3,3):
    #         third = dict(vt = 200 + i*10)
    #         fs.append(e.submit(genDP, cr=cr, dsize=dsize, mode=mode, em_dict=third))
        # fslist = [fss[2] for fss in fs]
        for f in concurrent.futures.as_completed(fs):
            try:
               af, sfs = f.result()
            except Exception as e:
                print('%r generated an exception: %s' % (sfs, e))
                
            # sft = argf[0]
            # apt = argf[1]

            cr.printCSF(sfs, kv = af[0], smax = af[1], sftype = af[2], aptype = af[3])    

def runCSFTests_order(c_name):
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
    

def diff_wrapper(func, *args, **kwargs):
    def diff_wrapped():
        return func(*args, **kwargs)
    return diff_wrapped
# def run_diff_test(name):
#     from pyemaps import dif
#         import numpy as np

#         # TODO, need to record whether DP has been run
#         ret = dif.generate_sf(sftype, aptype)
#         if ret == 0:
#             print(f"Error generating crytsal structure factors data")
#             return
        
#         nb = dif.get_nbeams()
#         hkls = farray(np.zeros((nb, 3), dtype=int))
        
#         ret = dif.get_sfindex(hkls)
#         if ret != 0:
#             print(f"Error generating crytsal structure factors data")
#             return

#         sfs = farray(np.zeros((nb, 4), dtype=float))
#         ret = dif.get_sfrem(sfs)
#         if ret != 0:
#             print(f"Error generating crytsal structure factors data")
#             return

#         for i in range(nb):
#             print(f"SF at {i}: {hkls[i]} {sfs[i]}")
        

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Test the emaps.dif module")
    parser.add_argument("-cr", "--crystal", type=str, nargs="?", const="Diamond", default="Diamond", help="Crystal name to be tested", required=False)
    parser.add_argument("-o", "--order", action="store_true", help="Ordered crystal test or parallel run without order", required=False)
    
    args = parser.parse_args()
    if not args.crystal:
        name = "Diamond"
    else:
        name = args.crystal

    if args.order:
        runCSFTests_order(name)
    else:
        runCSFTests(name)
