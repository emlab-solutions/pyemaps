
from pyemaps import showBloch
import os, sys
from pathlib import Path
import pickle
import numpy as np
from sanity_base import get_current_folder, get_crystal_filename, get_cifdata_dir, get_builtin_dir, get_baseline_filename

from sanity_base import feat_list, sample_feat_list, get_baseline_sample_filename, featureInSampleList

def run_samples_baseline(feature):
    print(f'------------------running and comparing with baseline for feature: {feature}----------------')
    try:
        baseline_data_filename = get_baseline_sample_filename(feature, bCreate=False) 
    except FileExistsError as e:
        print(f'test failed: {e}')
        sys.exit(1)

    with open(baseline_data_filename, "rb") as f:
            bdata = pickle.load(f)
       
    if feature == "diff":
       from pyemaps.samples.si_dif import generate_difs
       em_keys = ['tilt', 'zone', 'defl', 'vt', 'cl']
       for k in em_keys:
              dpl = generate_difs(ckey=k, mode=2)
              if not (k, dpl) in bdata:
                     print(f'Baseline match FAILED  for kinematic diffraction sample test for control: {k}.')
                     return
       print(f'++++++Baseline match SUCCEEDED for kinematic diffraction sample test.')

       
    if feature == 'bloch':
       from pyemaps.samples.si_bloch import generate_bloch_images
       em_keys = ['tilt', 'zone']
    
       for k in em_keys:
            imgs = generate_bloch_images(ckey=k)
            if not (k, imgs) in bdata:
                     print(f'Baseline match FAILED  for dynamic diffraction sample test for control: {k}.')
                     return
       print(f'++++++Baseline match SUCCEEDED for dynamic diffraction sample test.')

    if feature == 'lacbed':
        from pyemaps.samples.si_lacbed import generate_lacbed_images
        imgs = generate_lacbed_images()
        if not imgs == bdata:
              print(f'Baseline match FAILED  for LACBED sample test.')
              return
        print(f'++++++Baseline match SUCCEEDED for LACBED sample test.')

    if feature == 'stereo':
        from pyemaps.samples.si_stereo import generate_stereo
        stereo = generate_stereo(ckey='tilt')
        if stereo != bdata:
             print(f'Baseline match FAILED for Stereogram sample test.')
             return
        print(f'Baseline match SUCCEEDED for Stereogram sample test.')

    if feature == 'csf':
        from pyemaps.samples.si_csf import runCSFTests
        csf = runCSFTests(bPrint=False)
        if csf != bdata:
             print(f'Baseline match FAILED for Crystal Structure Factor sample test.')
             return
        print(f'Baseline match SUCCEEDED for Crystal Structure Factor sample test.')

    if feature == 'mxtal':
        from pyemaps.samples.si_constructor import test_mxtal
        mx = test_mxtal(bPrint=False, bSave=False)
        if mx != bdata:
             print(f'Baseline match FAILED for Crystal Structure Calculation sample test.')
             return
        print(f'Baseline match SUCCEEDED for Crystal Structure Calculation sample test.')
    
    if feature == 'scm':
        from pyemaps.samples.si_scm import runSCMFullTests

        scm = runSCMFullTests()
        if not scm[0]['ncb'] == bdata[0]['ncb'] or \
           not np.allclose(scm[0]['cbs'], bdata[0]['cbs']):
             print(f'Baseline match FAILED for Scattering matrix sample test.')
             return
        for s in scm[1]:
              ib, ndim, sm, ev, beams = s['ib'], s['ndim'], s['scm'], s['ev'], s['beams'] 
              bFound = False
              for b in bdata[1]: 
                     bib, bndim, bsm, bev, bbeams = b['ib'], b['ndim'], b['scm'], b['ev'], b['beams']  
                     if bib != ib:
                          continue

                     if ndim != bndim:
                          bFound= False 
                          continue 
                          
                     if not np.allclose(sm, bsm, atol=1.0e-06) or \
                            not np.allclose(ev, bev, atol=1.0e-06) or \
                            not np.allclose(beams, bbeams, atol=1.0e-06) :                          
                          bFound= False 
                          continue
                     bFound = True
              if not bFound:
                     print(f'Baseline match FAILED for Scattering matrix sample test.')
                     return
        print(f'Baseline match SUCCEEDED for Scattering matrix sample test.')   
        
    if feature == 'powder':
        from pyemaps.samples.powder import runPowderTests
        
        dl = runPowderTests(bPrint=False)
        sil, dil = dl
        bsil, bdil = bdata
        if not np.allclose(sil, bsil) or not np.allclose(dil, bdil):
             print(f'Baseline match FAILED for Powder diffraction sample test.')
             return
        print(f'Baseline match SUCCEEDED for Powder diffraction sample test.')   

if __name__ == '__main__':

    import argparse, sys
    # import time

    parser = argparse.ArgumentParser(description="Choice for feature testing: GUI or just baseline comparison")
    parser.add_argument("-s", "--samples", 
                        nargs='?', 
                        const='info',   
                        default=None,   
                        metavar='diff|bloch|stereo|lacbed|lacbed|scm|scf|mxtal|all',
                        help="""Running this tool compares new results with the baseline results.""", 
                        required=False
                        )
    
    args = parser.parse_args()

    sfeature = args.samples 
    
    if featureInSampleList(sfeature) and sfeature != "all":
       run_samples_baseline(sfeature)
    elif sfeature == "all":
       fl = [list(d.keys())[0] for d in sample_feat_list]
       for f in fl:
           run_samples_baseline(f) 