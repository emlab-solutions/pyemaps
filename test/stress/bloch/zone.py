# cname = 'BiMnO3'
cname = 'SiAlONa'
# cname = 'Silicon'

MAX_PROCWORKERS = 2
import time
import sys
from pyemaps import fileutils as ef

from contextlib import contextmanager

@contextmanager
def stdout_redirector(stream):
    old_stdout = sys.stdout
    sys.stdout = stream
    try:
        yield
    finally:
        sys.stdout = old_stdout

# def getxtl(cname):
def find_stress_crystal(cn):
    import os
    from pathlib import Path
    current_path = Path(os.path.abspath(__file__))

    tp_path = current_path.parent.parent.parent.parent.absolute()
    return os.path.join(tp_path, 'cdata', cn+'.xtl')
    

def bt_bloch():
    from pyemaps import Crystal as cryst
    from pyemaps import showBloch, EMC, SIMC, BlochError, EMCError
    from datetime import date, datetime
    import os
    from io import StringIO
    
    today = date.today()
    d1 = today.strftime("%d/%m/%Y")
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    cn = find_stress_crystal(cname)
# !    cr = cryst.from_builtin(cname)
    print(f'stress test crystal file name found: {cn}')
    cr = cryst.from_xtl(cn)    
    # zlist = [(1, 0, 0), (1, 0, 1), (0, 0, 1), (1, 1, 0)]
    zlist = [(1, 1, 0)]
    gmax = 2.0
    sgmin = 0.3
    sgmax = 1.0
    omega = 20
    # sth = (50, 1000, 50)
    # sth = (500, 2000, 250)
    sth = (200, 200, 250)

    simc = SIMC(gmax = gmax, excitation=(sgmin, sgmax))

    emclist = [EMC(cl=200, zone=z, simc=simc) for z in zlist]
    
    session_tic = time.perf_counter()
    bstressdir= os.path.join(ef.find_pyemaps_datahome(home_type="bloch"), "stress")
    if not os.path.exists(bstressdir):
         os.makedirs(bstressdir, exist_ok=True)
    bstress_fn = os.path.join(bstressdir, cname+".txt")
   
    with open(bstress_fn, 'w') as sys.stdout:
       print(f'---Running bloch for {cname} on {d1} at {dt_string}')
       for ec in emclist:
          print(f'EMControl variable: zone = {ec.zone}')
          zone_tic = time.perf_counter()
          # Redirect sys.stdout to a StringIO object
          bcap = StringIO()
          with stdout_redirector(bcap):
              
              try:
                     
                     bimg = cr.generateBloch(sample_thickness = sth, 
                            em_controls = ec, 
                            omega = omega, 
                            disk_size = 0.05,
                            sampling = 10, 
                            bSave=False)
              
              except (BlochError, EMCError) as e:
                     print(f'   generated an exception: {e.message}') 
                     return bimg
              except Exception as e:
                     print(f'   failed to generate diffraction patterns: {e}') 
                     return bimg
              else:
                     zone_toc = time.perf_counter()
                     showBloch(bimg, bClose=True) 
              
          bext_output = bcap.getvalue()
          print(f'   Bloch extension message: {bext_output}')
          print(f'   time to run bloch for {cname} is {zone_toc-zone_tic}')
            
     
       session_toc = time.perf_counter()
       print(f'Total time to run bloch this session: {session_toc-session_tic}')

if __name__ == "__main__":
    
    bt_bloch()