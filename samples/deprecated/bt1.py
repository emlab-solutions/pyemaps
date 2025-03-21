# cname = 'Boron_Tetra'
cname = 'SiAlONa'
MAX_PROCWORKERS = 2
import time
def bt_bloch():
    import concurrent.futures
    from pyemaps import Crystal as cryst
    from pyemaps import showBloch, EMC, SIMC, BlochError, EMCError

    cr = cryst.from_builtin(cname)
    
    # zlist = [(1, 0, 0), (1, 0, 1), (0, 0, 1)]
    zlist = [(1, 1, 1)]
    gmax = 2.0
    sgmin = 0.3
    sgmax = 1.0
    omega = 20
    # sth = (50, 1000, 50)
    # sth = (500, 2000, 250)
    sth = (200, 200, 250)

    simc = SIMC(gmax = gmax, excitation=(sgmin, sgmax))

    emclist = [EMC(cl=200, zone=z, simc=simc) for z in zlist]
    
    fs=[]
    tic = time.perf_counter()
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_PROCWORKERS) as e:

        for ec in emclist:
            fs.append(e.submit(cr.generateBloch, 
                      sample_thickness = sth, 
                      em_controls = ec, 
                      omega = omega, 
                      sampling = 8, 
                      bSave=True))
        
        for f in concurrent.futures.as_completed(fs):
            try:
               bimg = f.result()

            except (BlochError, EMCError) as e:
                print(f'Generated an exception: {e.message}') 
                return bimg
            except Exception as e:
                print(f'Failed to generate diffraction patterns: {e}') 
                return bimg
            else: 
                
                toc = time.perf_counter()
                print(f'Time to run bloch for {cname} is {toc-tic}')
                showBloch(bimg, bSave=True, layout='table') 
            

if __name__ == "__main__":
    
    bt_bloch()