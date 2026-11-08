# cname = 'BiMnO3'
cname = 'SiAlONa'
# cname = 'Silicon'

MAX_PROCWORKERS = 2
import os
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

def get_stress_baseline_filename(cn, bCreate=True):
    import os
    from pathlib import Path
    current_path = Path(os.path.abspath(__file__))

    bdir = os.path.join(current_path.parent.parent.parent.absolute(), 'baseline', 'stress', 'bloch')
    if bCreate and not os.path.exists(bdir):
        os.makedirs(bdir, exist_ok=True)
    return os.path.join(bdir, cn+'.im3')

def list_bloch_images(cn):
    import os
    bdir = ef.find_pyemaps_datahome(home_type="bloch")
    return set(f for f in os.listdir(bdir) if f.startswith(cn+'-') and f.endswith('.im3'))

def compare_im3(fn, bfn):
    '''
    Compares a new raw bloch image file with the baseline, byte for byte.
    The threaded bloch run is deterministic, so any difference is a change in results.
    '''
    import numpy as np

    with open(fn, 'rb') as f:
        new = f.read()
    with open(bfn, 'rb') as f:
        base = f.read()

    if new == base:
        return True

    if len(new) != len(base) or new[:8] != base[:8]:
        print(f'image header or size differs: {len(new)} bytes vs baseline {len(base)} bytes')
        return False

    # 8 byte header, then float32 slices of 512x512
    a = np.frombuffer(new[8:], dtype=np.float32).reshape(-1, 512, 512).astype(np.float64)
    b = np.frombuffer(base[8:], dtype=np.float32).reshape(-1, 512, 512).astype(np.float64)
    for k in range(b.shape[0]):
        d = np.abs(a[k] - b[k])
        m = np.abs(b[k]).max()
        print(f'slice {k}: {int(np.count_nonzero(d))} pixels differ, '
              f'max difference {d.max():.4g} ({100.0*d.max()/m:.3g}% of baseline max), '
              f'total intensity {100.0*(a[k].sum()-b[k].sum())/b[k].sum():+.3g}%')
    return False

def bt_bloch(bBaseline=False):
    '''
    Runs the stress test and returns the raw bloch image file it saved, or None on failure.
    bBaseline: True - also save the rendered image as PNG and close the plot (baseline runs)
    '''
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
    sth = (200, 250, 500)

    simc = SIMC(gmax = gmax, excitation=(sgmin, sgmax))

    emclist = [EMC(cl=400, zone=z, simc=simc) for z in zlist]
    
    session_tic = time.perf_counter()
    bstressdir= os.path.join(ef.find_pyemaps_datahome(home_type="bloch"), "stress")
    if not os.path.exists(bstressdir):
         os.makedirs(bstressdir, exist_ok=True)
    bstress_fn = os.path.join(bstressdir, cname+".txt")
    bimgs_before = list_bloch_images(cname)

    with open(bstress_fn, 'w') as logf, stdout_redirector(logf):
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
                            bSave=True)
              
              except (BlochError, EMCError) as e:
                     print(f'   generated an exception: {e.message}')
                     return None
              except Exception as e:
                     print(f'   failed to generate diffraction patterns: {e}')
                     return None
              else:
                     zone_toc = time.perf_counter()
                     if bBaseline:
                            showBloch(bimg, bSave=True, bClose=True)
                     else:
                            showBloch(bimg, bClose=False)
              
          bext_output = bcap.getvalue()
          print(f'   Bloch extension message: {bext_output}')
          print(f'   time to run bloch for {cname} is {zone_toc-zone_tic}')
            
     
       session_toc = time.perf_counter()
       print(f'Total time to run bloch this session: {session_toc-session_tic}')

    new_imgs = list_bloch_images(cname) - bimgs_before
    if len(new_imgs) != 1:
        print(f'expected one new bloch image file for {cname}, found: {sorted(new_imgs)}')
        return None
    return os.path.join(ef.find_pyemaps_datahome(home_type="bloch"), new_imgs.pop())

if __name__ == "__main__":
    import argparse, shutil

    parser = argparse.ArgumentParser(description="Bloch stress test: visual run, or baseline generation/comparison")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-bg", "--baseline_generation", action='store_true',
                        help="Runs the stress test and saves its raw image as the new baseline.")
    group.add_argument("-bc", "--baseline_comparison", action='store_true',
                        help="Runs the stress test and compares its raw image with the baseline.")
    args = parser.parse_args()

    if not (args.baseline_generation or args.baseline_comparison):
        bt_bloch()
        sys.exit(0)

    imgfn = bt_bloch(bBaseline=True)
    if imgfn is None:
        print(f'++++++ Bloch stress test FAILED for {cname}: no image generated +++++++')
        sys.exit(1)

    if args.baseline_generation:
        bfn = get_stress_baseline_filename(cname, bCreate=True)
        shutil.copyfile(imgfn, bfn)
        print(f'++++++ Bloch stress test baseline updated SUCCESSFULLY for {cname}: {bfn} ++++++')
        sys.exit(0)

    bfn = get_stress_baseline_filename(cname, bCreate=False)
    if not os.path.exists(bfn):
        print(f'++++++ Bloch stress test FAILED for {cname}: no baseline at {bfn} +++++++')
        sys.exit(1)

    if compare_im3(imgfn, bfn):
        print(f'++++++ Baseline comparison SUCCEEDED for {cname} bloch stress test +++++++')
    else:
        print(f'++++++ Baseline comparison FAILED for {cname} bloch stress test: {imgfn} +++++++')
        sys.exit(1)