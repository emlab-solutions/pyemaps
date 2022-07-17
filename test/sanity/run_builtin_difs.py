from numpy import asfortranarray as farray
from numpy import array
from pyemaps import dif,bloch
# from emaps import bloch
import numpy as np
import os
import matplotlib
import matplotlib.pyplot as plt
import math
import timeit

from pyemaps.emcontrols import DEF_CBED_DSIZE
MAX_PROCWORKERS = 4

def bloch_wrapper(func, *args, **kwargs):
    def bloch_wrapped():
        return func(*args, **kwargs)
    return bloch_wrapped

def run_builtin_bloch(sampling = 8, dsize = 0.15, thickness = 800):
    import concurrent.futures
    from pyemaps import Crystal as cryst
    from pyemaps import EMC, EMCError
    from pyemaps import showBloch

    cnames = cryst.list_all_builtin_crystals()
    fs = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_PROCWORKERS) as e:

        for n in cnames:
            print(f'--------------Loading crystal: {n}')
            cr = cryst.from_builtin(n)
            fs.append(e.submit(cr.generateBloch, disk_size=dsize, 
                sampling = sampling, thickness = thickness, em_controls = EMC()))
        count = 0
        for f in concurrent.futures.as_completed(fs):
            imgs = []
            try:
               emc, img = f.result()
            except (EMCError) as e:
                print(f'{f} generated an exception: {e.message}')
            except:
                print('failed to generate diffraction patterns')
            else:    
                imgs.append((emc, img))
                showBloch(imgs, name='Bloch', bColor=True)
                count += 1

        print(f'Successful bloch runs: {count}')

def run_builtin_dif(mode = 1, dsize= 0.05):
    import concurrent.futures
    from pyemaps import Crystal as cryst
    from pyemaps import EMC, DPError, EMCError
    from pyemaps import showDif, DPList

    cnames = cryst.list_all_builtin_crystals()
    count = 0
    for n in cnames:
        cr = cryst.from_builtin(n)
        if mode == 2 and not dsize:
            ds = DEF_CBED_DSIZE
        else:
            ds = dsize

        try:
            emc, cdp = cr.generateDP(mode = mode, dsize=ds, em_controls = EMC())
        except (EMCError, DPError) as e:
                print(f'{f} generated an exception: {e.message}')
        except:
            print('failed to generate diffraction patterns')  
        else: 
            dpl = DPList('Test', mode) 
            dpl.add(emc, cdp)
            showDif(dpl)
            count += 1

    print(f'Successful bloch runs: {count}')

# def runtime_beam_fit(beams,rtimes):
#     x = beams
#     y = rtimes

#     z = np.polyfit(x,y,7)
#     f = np.poly1d(z)

#     # calculate new x's and y's
#     xmin = min(x)
#     xmax = max(x)
#     x_new = np.linspace(xmin, xmax, 50)
#     y_new = f(x_new)

#     plt.plot(x,y,'o', x_new, y_new)
#     plt.xlim([0, xmax ])
    
#     plt.show()

if __name__=="__main__":
    # run_builtin_dif()
    run_builtin_bloch()