# cname = 'BiMnO3'
# cname = 'SiAlONa'
cname = 'Silicon'

MAX_PROCWORKERS = 2
import time
# def getxtl(cname):

def bt_bloch():
    import concurrent.futures
    from pyemaps import Crystal as cryst
    from pyemaps import showBloch, EMC, SIMC, BlochError, EMCError

    cr = cryst.from_builtin(cname)
    
    # zlist = [(1, 0, 0), (1, 0, 1), (0, 0, 1)]
    zlist = [(0, 0, 1)]
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
                      disk_size = 0.05,
                      sampling = 20, 
                      bSave=False))
        
        for f in concurrent.futures.as_completed(fs):
            try:
               bimg = f.result()

            except (BlochError, EMCError) as e:
                print(f'generated an exception: {e.message}') 
                return bimg
            except Exception as e:
                print(f'failed to generate diffraction patterns: {e}') 
                return bimg
            else: 
                
                toc = time.perf_counter()
                print(f'time to run bloch for {cname} is {toc-tic}')
                showBloch(bimg, bSave=True, layout='table') 
            

if __name__ == "__main__":
    
    bt_bloch()