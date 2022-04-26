"""
Sample code to demostrate using pyemaps to generate kinematic diffraction patterns chaning with
sample tilt in x direction between range of
    (-1,1)
with step of 0.5
"""
MAX_PROCWORKERS = 4

def gen_control_vectors():
    cvars=[(x*0.5,0.0, 0, 0, 1) for x in range(-2, 3)]
    
    return cvars


def generate_difs(name = 'silicon', mode = 1):
    from pyemaps import DP
    from pyemaps import DPList
    from pyemaps import Crystal as cryst
    from pyemaps import DEF_CONTROLS
    
    import concurrent.futures
    import sys

    cr = cryst.from_builtin(name)

    if mode == 2:
        dsize = 0.16
    else:
        dsize = None

    
    fs=[]
    difs = DPList(cr.name, mode = mode)
    v = gen_control_vectors()
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_PROCWORKERS) as e:
        for tx,ty, z1, z2, z3 in v:
            fs.append((tx, ty, z1,z2,z3, \
            e.submit(cr.gen_diffPattern, (z1,z2,z3), mode,tx,ty,0.0,0.0,None,None,dsize)))

    for tx, ty, z1, z2, z3, f in fs:
        diffP = f.result()
        cntrl = dict(tilt = (tx,ty),
                     zone = (z1,z2,z3),
                     cl = DEF_CONTROLS['cl'],
                     vt = DEF_CONTROLS['vt'],
                     defl = DEF_CONTROLS['defl'] 
                     )

        # diffP = DP(diff_dict)
        difs.add(cntrl, diffP)
    return difs