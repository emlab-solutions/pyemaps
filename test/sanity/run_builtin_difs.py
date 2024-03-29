from numpy import asfortranarray as farray
from numpy import array
from pyemaps import ddiffs, dif
# from emaps import bloch
import numpy as np
import os
import matplotlib
import matplotlib.pyplot as plt
import math
import timeit

from pyemaps.emcontrols import DEF_CBED_DSIZE
from pyemaps.errors import CrystalClassError
MAX_PROCWORKERS = 4

def bloch_wrapper(func, *args, **kwargs):
    def bloch_wrapped():
        return func(*args, **kwargs)
    return bloch_wrapped

def run_builtin_bloch(sampling = 8, dsize = 0.15, thickness = 800):
    import concurrent.futures
    from pyemaps import Crystal as cryst
    from pyemaps import EMC, EMCError,BlochListError
    from pyemaps import showBloch
    # from pyemaps import BImgList

    cnames = cryst.list_all_builtin_crystals()
    fs = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_PROCWORKERS) as e:

        for n in cnames:
            print(f'--------------Loading crystal: {n}')
            cr = cryst.from_builtin(n)
            fs.append(e.submit(cr.generateBlochImgs, disk_size=dsize, 
                sampling = sampling, sample_thickness = (thickness, thickness, 100), em_controls = EMC()))

        count = 0
        for f in concurrent.futures.as_completed(fs):
            
            try:
               bimgs = f.result()
            except (EMCError, BlochListError, CrystalClassError) as e:
                print(f'{f} generated an exception: {e.message}')
            except:
                print('failed to generate bloch diffraction patterns')
            else:    
                showBloch(bimgs)
                count += 1

        print(f'Successful bloch runs: {count}')

def run_builtin_dif(mode = 1, dsize= 0.05):
    import concurrent.futures
    from pyemaps import Crystal as cryst
    from pyemaps import EMC, DPError, EMCError
    from pyemaps import showDif

    cnames = cryst.list_all_builtin_crystals()
    count = 0
    for n in cnames:
        cr = cryst.from_builtin(n)
        if mode == 2 and not dsize:
            ds = DEF_CBED_DSIZE
        else:
            ds = dsize

        try:
            dpl = cr.generateDif(mode = mode, dsize=ds, em_controls = EMC())
        except (EMCError, DPError) as e:
                print(f'Error generating diffraction: {e.message}')
        except:
            print('failed to generate diffraction patterns')  
        else: 
            showDif(dpl)
            count += 1

    print(f'Successful bloch runs: {count}')

def run_builtin_bloch_np(sampling = 8, thickness = 200, bSave = False, bShow=False):
    from pyemaps import Crystal as cryst
    from pyemaps import EMC, DPError, EMCError,BlochListError
    from pyemaps import showBloch
    import time

    cnames = cryst.list_all_builtin_crystals()
    count = 0
    th_start = thickness
    th_step = 100
    th_end = th_start + 800

    st = (th_start, th_end, th_step)

    print(f'Sample thickness range: {st}')
    
    s_start = sampling
    s_end = s_start + 20
    s_step = 1
    for s in range(s_start, s_end+1, s_step):
        print(f'Sampling: {s}')
        for n in cnames:
         if n == 'BiMnO3':
            cr = cryst.from_builtin(n)
            print(f'--------------Loading crystal: {n}')
            tic = toc = 0.0
            try:
                tic = time.perf_counter()
                bis = cr.generateBlochImgs(sampling = s, 
                        sample_thickness = st)
                toc = time.perf_counter()
            except (EMCError, BlochListError, DPError) as e:
                    print(f'{bis} generated an exception: {e.message}')
            except:
                print('failed to generate bloch diffraction patterns')  
            else: 
                if bShow:
                    showBloch(bis, bSave=bSave)
                count += 1

            print(f'*************Successful bloch runs at sampling points of {s}: {count} in {toc - tic:0.4f} seconds')

if __name__=="__main__":
    # run_builtin_dif()
    # run_builtin_bloch()
    run_builtin_bloch_np(bShow=True)