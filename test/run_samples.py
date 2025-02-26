
from pyemaps import showBloch
import os, sys
from pathlib import Path
import pickle
import numpy as np
from sanity_base import *

def compare_samples_baseline(feature):
    print(f'------------------generating new results and comparing them with baseline for feature: {feature}----------------')
    try:
        baseline_data_filename = get_baseline_sample_filename(feature, bCreate=False) 
    except FileExistsError as e:
        print(f'test failed: {e}')
        sys.exit(1)

    if feature != 'dpgen':
        with open(baseline_data_filename, "rb") as f:
                bdata = pickle.load(f)
        
    if feature == "diff":
       from pyemaps.samples.si_dif import generate_difs, em_keys
       for k in em_keys:
              dpl = generate_difs(ckey=k, mode=2)
              if not (k, dpl) in bdata:
                print(f'--------Baseline match FAILED  for kinematic diffraction sample test for control: {k}.')
                return
       print(f'++++++Baseline match SUCCEEDED for kinematic diffraction sample test.')

       
    if feature == 'bloch':
       from pyemaps.samples.si_bloch import generate_bloch_images, em_keys
    
       for k in em_keys:
            imgs = generate_bloch_images(ckey=k)
            if not (k, imgs) in bdata:
                print(f'--------Baseline match FAILED  for dynamic diffraction sample test for control: {k}.')
                return
       print(f'++++++Baseline match SUCCEEDED for dynamic diffraction sample test.')

    if feature == 'lacbed':
        from pyemaps.samples.si_lacbed import generate_lacbed_images
        imgs = generate_lacbed_images()
        if imgs != bdata:
            print(f'--------Baseline match FAILED  for LACBED sample test.')
            return
        print(f'++++++Baseline match SUCCEEDED for LACBED sample test.')

    if feature == 'stereo':
        from pyemaps.samples.si_stereo import generate_stereo
        stereo = generate_stereo(ckey='tilt')
        if stereo != bdata:
             print(f'--------Baseline match FAILED for Stereogram sample test.')
             return
        print(f'++++++Baseline match SUCCEEDED for Stereogram sample test.')

    if feature == 'csf':
        from pyemaps.samples.si_csf import runCSFTests
        csf = runCSFTests(bPrint=False)
        if csf != bdata:
             print(f'--------Baseline match FAILED for Crystal Structure Factor sample test.')
             return
        print(f'++++++Baseline match SUCCEEDED for Crystal Structure Factor sample test.')

    if feature == 'mxtal':
        from pyemaps.samples.si_constructor import test_mxtal
        mx = test_mxtal(bPrint=False, bSave=False)
        if mx != bdata:
             print(f'--------Baseline match FAILED for Crystal Structure Calculation sample test.')
             return
        print(f'++++++Baseline match SUCCEEDED for Crystal Structure Calculation sample test.')
    
    if feature == 'scm':
        from pyemaps.samples.si_scm import runSCMFullTests
        SCM_TOLERANCE= 1.0e-04
        scm = runSCMFullTests()

        if not scm[0]['ncb'] == bdata[0]['ncb'] or \
           scm[0]['cbs'].shape != bdata[0]['cbs'].shape or \
           not np.array_equal(np.sort(scm[0]['cbs'], axis=0), np.sort(bdata[0]['cbs'], axis=0)):
             print(f'--------Baseline match FAILED for Scattering matrix sample test: number of incident beams not matching')
             return
             
        for s in scm[1]:
              ib, ndim, sm, ev, beams = s['ib'], s['ndim'], s['scm'], s['ev'], s['beams'] 
            #   bFound = False
              for b in bdata[1]: 
                bib, bndim, bsm, bev, bbeams = b['ib'], b['ndim'], b['scm'], b['ev'], b['beams']  
                if bib != ib:
                    continue

                if ndim != bndim:
                    print(f'----Baseline match FAILED for Scattering matrix sample test: scattering matrix dimensions differ')
                    return 
                
                if ev.shape != bev.shape or not np.allclose(np.sort(ev, axis=0), np.sort(bev, axis=0), atol=SCM_TOLERANCE):  
                    print(f'----Baseline match FAILED for Scattering matrix sample test: Eigen values at {ib} does not match: {ev} != {bev}')
                    return 

                if beams.shape != bbeams.shape or not np.array_equal(np.sort(beams, axis=0), np.sort(bbeams, axis=0)):   
                    print(f'----Baseline match FAILED for Scattering matrix sample test: Beams at {ib} does not match: {beams} != {bbeams}')
                    return
                
                if sm.shape != bsm.shape:  
                    print(f'----Baseline match FAILED for Scattering matrix shape differ at {ib}')
                    return 
                    
                # norm_sm = sm / np.linalg.norm(sm, axis=0)
                # norm_bsm = bsm / np.linalg.norm(bsm, axis=0)

                # if norm_sm.shape != norm_bsm.shape:  
                #     print(f'----Baseline match FAILED for Scattering matrix shape differ after normalization at {ib}')
                #     return     
                
                # sort_norm_sm = np.abs(np.sort(norm_sm, axis=0))
                # sort_norm_bsm = np.abs(np.sort(norm_bsm, axis=0))

                # if not np.allclose(sort_norm_sm, sort_norm_bsm, atol=SCM_TOLERANCE):
                #     mismatch = ~np.isclose(sort_norm_sm,sort_norm_bsm, atol=SCM_TOLERANCE)
                #     print("Mismatched indices:", np.where(mismatch))
                #     print("Current mismatched values:", sort_norm_sm[mismatch])
                #     print("basline mismatched values:", sort_norm_bsm[mismatch])
                #     print(f'----Baseline match FAILED for Scattering matrix sample test at {ib}') 
                    # return

                # Create a matrix with eigen values as diagnal elements

                evm = np.diag(ev)
                bevm = np.diag(bev)

                # Find the inverses of the eigenvectors matrices
                det_sm = np.linalg.det(sm)
                if np.abs(det_sm) < 1e-05:
                    print(f'----Baseline match FAILED: invalid eigenvector vectors generated.')
                    return
                sm_inv = np.linalg.inv(sm)

                det_bsm = np.linalg.det(bsm)
                if np.abs(det_bsm) < 1e-05:
                    print(f'----Baseline match FAILED: invalid eigenvector matrix from baseline.')
                    return
                bsm_inv = np.linalg.inv(bsm)
                
                # Compute the original matrices from emaps backend
                AA = np.linalg.multi_dot([sm_inv, evm, sm])
                BB = np.linalg.multi_dot([bsm_inv, bevm, bsm])

                if ib == (0,0):
                    print(f'current matrix: {AA}')
                    print(f'baseline matrix: {BB}')
                
                if not np.allclose(AA, BB, atol=SCM_TOLERANCE):
                    mismatch = ~np.isclose(AA,BB, atol=SCM_TOLERANCE)
                    print("Mismatched indices:", np.where(mismatch))
                    print("Current mismatched values:", AA[mismatch])
                    print("basline mismatched values:", BB[mismatch])
                    print(f'----Baseline match FAILED for Scattering matrix sample test at {ib}') 
                    return

                break    
                
        print(f'++++++Baseline match SUCCEEDED for Scattering matrix sample test.')   

    if feature == 'powder':
        from pyemaps.samples.powder import runPowderTests
        
        dl = runPowderTests(bPrint=False)
        sil, dil = dl
        bsil, bdil = bdata
        if not np.allclose(sil, bsil) or not np.allclose(dil, bdil):
             print(f'--------Baseline match FAILED for Powder diffraction sample test.')
             return
        print(f'++++++Baseline match SUCCEEDED for Powder diffraction sample test.')   

    # if feature == 'dpgen':    TODO later
    #     from pyemaps.samples.al_dpgen import al_dpdb
    #     import filecmp

    #     fn = al_dpdb()
        
    #     if not filecmp.cmp(fn, baseline_data_filename):
    #          print(f'Baseline match FAILED for diffraction patterns database sample test.')
    #          return
    #     print(f'Baseline match SUCCEEDED for diffraction patterns database sample test.')     
         

def gen_samples_baseline(feature):
    print(f'------------------Generating baseline for feature: {feature}----------------')
    try:
        baseline_data_filename = get_baseline_sample_filename(feature) 
    except FileExistsError as e:
        print(f'test failed: {e}')
        sys.exit(1)

    dl=[]
    if feature == "diff":
        from pyemaps.samples.si_dif import generate_difs, em_keys
        
        for k in em_keys:
            dpl = generate_difs(ckey=k, mode=2)
            dl.append((k, dpl))
            
    if feature == 'bloch':
        from pyemaps.samples.si_bloch import generate_bloch_images, em_keys
        
        for k in em_keys:
            imgs = generate_bloch_images(ckey=k)
            dl.append((k, imgs))

    if feature == 'lacbed':
        from pyemaps.samples.si_lacbed import generate_lacbed_images
        imgs = generate_lacbed_images()
        dl=imgs

    if feature == 'stereo':
        from pyemaps.samples.si_stereo import generate_stereo
        dl = generate_stereo(ckey='tilt')

    if feature == 'csf':
        from pyemaps.samples.si_csf import runCSFTests
        dl = runCSFTests(bPrint=False)

    if feature == 'mxtal':
        from pyemaps.samples.si_constructor import test_mxtal
        dl = test_mxtal(bPrint=False, bSave=False)
    
    if feature == 'scm':
        from pyemaps.samples.si_scm import runSCMFullTests
        dl = runSCMFullTests()

    if feature == 'powder':
        from pyemaps.samples.powder import runPowderTests
        dl = runPowderTests(bPrint=False)

    # if feature == 'dpgen':  -----TODO, later
    #     from pyemaps.samples.al_dpgen import al_dpdb
    #     fn = al_dpdb()
    #     if fn is None:
    #         print(f'++++++Failed to generate diffraction database.+++++')
    #         return
    #     if fn.lower() != baseline_data_filename.lower():
    #         import shutil
    #         shutil.copy(fn, baseline_data_filename)
    # print(f'baseline data file name: {baseline_data_filename}, {dl}')
    with open(baseline_data_filename, "wb") as f:
        pickle.dump(dl, f)

def run_sample_gui(feature = "diff"):
    if feature == "diff":
        import pyemaps.samples.si_dif as diff
        diff.main()
            
    if feature == 'bloch':
        import pyemaps.samples.si_bloch as bloch
        bloch.main()

    if feature == 'lacbed':
        import pyemaps.samples.si_lacbed as lacbed
        lacbed.main()

    if feature == 'stereo':
        import pyemaps.samples.si_stereo as stereo
        stereo.main()

    if feature == 'csf':
        import pyemaps.samples.si_csf as csf
        csf.runCSFTests()

    if feature == 'mxtal':
        import pyemaps.samples.si_constructor as mxtal
        mxtal.test_mxtal()
    
    if feature == 'scm':
        import pyemaps.samples.si_scm as scm 
        scm.runSCMTests()

    if feature == 'powder':
        import pyemaps.samples.powder as powder
        powder.main()

if __name__ == '__main__':
    
    import argparse, copy
    
    option_choices_core = [list(d.keys())[0] for d in sample_feat_list]
    option_choices= copy.deepcopy(option_choices_core)
    option_choices.append('all')

    parser = argparse.ArgumentParser(description="Choice for feature testing: GUI or just baseline comparison")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-bg", "--baseline_generation", 
                        nargs='?', 
                        const='info',   
                        default=None,   
                        metavar='diff|bloch|stereo|lacbed|lacbed|scm|scf|mxtal|all',
                        help="""Running this tool compares new results with the baseline results.""", 
                        required=False
                        )
    group.add_argument("-bc", "--baseline_comparison", 
                        nargs='?', 
                        const='info',   
                        default=None,   
                        metavar='diff|bloch|stereo|lacbed|lacbed|scm|scf|mxtal|all',
                        help="""Running this tool dhow gui results.""", 
                        required=False
                        )
    group.add_argument("-gr", "--gui_run", 
                        nargs='?', 
                        const='info',   
                        default=None,   
                        metavar='diff|bloch|stereo|lacbed|lacbed|scm|scf|mxtal|all',
                        help="""Running this tool dhow gui results.""", 
                        required=False
                        )
    args = parser.parse_args()

    bgen = args.baseline_generation 
    bcom = args.baseline_comparison 
    bgui = args.gui_run  

    if bgen is None and bcom is None and bgui is None:
         parser.print_help()
         sys.exit('No valid option provided.')

    f = bgen or bcom or bgui
    
    if f not in option_choices:
         parser.print_help()
         sys.exit('No valid option value provided.')

    if f in option_choices_core: 
        if bgen:
            gen_samples_baseline(f)

        if bcom:
            compare_samples_baseline(f)

        if bgui:
            run_sample_gui(f)
    else:       
        for ff in option_choices_core:
            if bgen:
                gen_samples_baseline(ff)

            if bcom:
                compare_samples_baseline(ff)

            if bgui:
                run_sample_gui(ff)
    