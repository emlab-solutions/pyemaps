
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
       from pyemaps.samples.si_dif import generate_kinematic_patterns, CONTROLS
       for k in CONTROLS:
              dpl = generate_kinematic_patterns(k, mode=2)
              if not (k, dpl) in bdata:
                print(f'--------Baseline match FAILED  for kinematic diffraction sample test for control: {k}.')
                return
       print(f'++++++Baseline match SUCCEEDED for kinematic diffraction sample test.')

       
    if feature == 'bloch':
       from pyemaps.samples.si_bloch import generate_bloch_images, CONTROLS
    
       for k in CONTROLS:
            imgs = generate_bloch_images(k)
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
        from pyemaps.samples.si_stereo import generate_stereodiagrams
        stereo = generate_stereodiagrams('tilt')
        if stereo != bdata:
             print(f'--------Baseline match FAILED for Stereogram sample test.')
             return
        print(f'++++++Baseline match SUCCEEDED for Stereogram sample test.')

    if feature == 'csf':
        from pyemaps.samples.si_csf import generate_structure_factors
        csf = generate_structure_factors(verbose=False)[(4, 0)]
        if csf != bdata:
             print(f'--------Baseline match FAILED for Crystal Structure Factor sample test.')
             return
        print(f'++++++Baseline match SUCCEEDED for Crystal Structure Factor sample test.')

    if feature == 'mxtal':
        from pyemaps.samples.si_constructor import build_supercell
        mx = build_supercell(verbose=False, save=False)
        if mx != bdata:
             print(f'--------Baseline match FAILED for Crystal Structure Calculation sample test.')
             return
        print(f'++++++Baseline match SUCCEEDED for Crystal Structure Calculation sample test.')
    
    if feature == 'scm':
        from pyemaps.samples.si_scm import all_scattering_matrices
        SCM_TOLERANCE= 1.0e-04
        scm = all_scattering_matrices()

        if not scm[0]['ncb'] == bdata[0]['ncb'] or \
           scm[0]['cbs'].shape != bdata[0]['cbs'].shape or \
           not np.array_equal(np.sort(scm[0]['cbs'], axis=0), np.sort(bdata[0]['cbs'], axis=0)):
            print(f'--------Baseline match FAILED for Scattering matrix sample test: number of incident beams not matching')
            return
        
        nscm = scm[1]['nscm']
        bnscm = bdata[1]['nscm']
        if nscm != bnscm:
            print(f'--------Baseline match FAILED for Scattering matrix sample test: number of scattering matrices not matching: {nscm} != {bnscm}')
            return
        
        for s in scm[1]['lscm']:
            ib, ndim, sm, ev, beams = s['ib'], s['ndim'], s['scm'], s['ev'], s['beams'] 
            bFound = False
            for b in bdata[1]['lscm']: 
                bib, bndim, bsm, bev, bbeams = b['ib'], b['ndim'], b['scm'], b['ev'], b['beams']  
                if bib != ib:
                    continue
                else:
                    bFound = True

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

                # # Create a matrix with eigen values as diagnal elements

                # evm = np.diag(ev)
                # bevm = np.diag(bev)

                # # Find the inverses of the eigenvectors matrices
                # det_sm = np.linalg.det(sm)
                # if np.abs(det_sm) < 1e-05:
                #     print(f'----Baseline match FAILED: invalid eigenvector vectors generated.')
                #     return
                # sm_inv = np.linalg.inv(sm)

                # det_bsm = np.linalg.det(bsm)
                # if np.abs(det_bsm) < 1e-05:
                #     print(f'----Baseline match FAILED: invalid eigenvector matrix from baseline.')
                #     return
                # bsm_inv = np.linalg.inv(bsm)
                
                # # Compute the original matrices from emaps backend
                # AA = np.linalg.multi_dot([sm_inv, evm, sm])
                # BB = np.linalg.multi_dot([bsm_inv, bevm, bsm])

                # P = np.dot(sm, bsm_inv)
                # AA_constructed = np.linalg.multi_dot([P, BB, np.linalg.inv(P)])
                
                # if not np.allclose(AA, AA_constructed, atol=SCM_TOLERANCE):
                #     # mismatch = ~np.isclose(AA,BB, atol=SCM_TOLERANCE)
                #     # print("Mismatched indices:", np.where(mismatch))
                #     # print("Current mismatched values:", AA[mismatch])
                #     # print("basline mismatched values:", BB[mismatch])
                #     print(f'----Baseline match FAILED for Scattering matrix sample test at {ib}') 
                #     return

                break  

            if not bFound:
                print(f'----Baseline match FAILED for Scattering matrix sample test: Incident Beams at {ib} not found in baseline')  
        
        nib = scm[2]['nib']
        bnib = bdata[2]['nib']

        if nib != bnib:
            print(f'--------Baseline match FAILED for Scattering matrix sample test: number of incident beams not matching: {nib} != {bnib}')
            return
        
        for ibt in scm[2]['libt']:
            bFound = False
            for bibt in bdata[2]['libt']: 
                if ibt['ib'] != bibt['ib']:
                    continue 
                else:
                    bFound = True

                if not np.allclose(ibt['tilt'], bibt['tilt'], atol=SCM_TOLERANCE):  
                    print(f'----Baseline match FAILED for Scattering matrix sample test: Incident Beams at {ib} tilt does not match: {ibt} != {bibt}')
                    return
                break

            if not bFound:
                print(f'----Baseline match FAILED for Scattering matrix sample test: Incident Beams at {ib} not found in baseline')
              
        print(f'++++++Baseline match SUCCEEDED for Scattering matrix sample test.')   

    if feature == 'powder':
        from pyemaps.samples.powder import generate_powder_profiles
        
        dl = generate_powder_profiles(verbose=False)
        sil, dil = dl
        bsil, bdil = bdata
        if not np.allclose(sil, bsil) or not np.allclose(dil, bdil):
             print(f'--------Baseline match FAILED for Powder diffraction sample test.')
             return
        
        print(f'++++++Baseline match SUCCEEDED for Powder diffraction sample test.')   

    # if feature == 'dpgen':    TODO later
    #     from pyemaps.samples.al_dpgen import generate_database
    #     import filecmp

    #     fn = generate_database()
        
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
    try:
        if feature == "diff":
            from pyemaps.samples.si_dif import generate_kinematic_patterns, CONTROLS
            
            for k in CONTROLS:
                dpl = generate_kinematic_patterns(k, mode=2)
                dl.append((k, dpl))
                
        if feature == 'bloch':
            from pyemaps.samples.si_bloch import generate_bloch_images, CONTROLS
            
            for k in CONTROLS:
                imgs = generate_bloch_images(k)
                dl.append((k, imgs))

        if feature == 'lacbed':
            from pyemaps.samples.si_lacbed import generate_lacbed_images
            imgs = generate_lacbed_images()
            dl=imgs

        if feature == 'stereo':
            from pyemaps.samples.si_stereo import generate_stereodiagrams
            dl = generate_stereodiagrams('tilt')

        if feature == 'csf':
            from pyemaps.samples.si_csf import generate_structure_factors
            dl = generate_structure_factors(verbose=False)[(4, 0)]

        if feature == 'mxtal':
            from pyemaps.samples.si_constructor import build_supercell
            dl = build_supercell(verbose=False, save=False)
        
        if feature == 'scm':
            from pyemaps.samples.si_scm import all_scattering_matrices
            dl = all_scattering_matrices()

        if feature == 'powder':
            from pyemaps.samples.powder import generate_powder_profiles
            dl = generate_powder_profiles(verbose=False)

        # if feature == 'dpgen':  -----TODO, later
        #     from pyemaps.samples.al_dpgen import generate_database
        #     fn = generate_database()
        #     if fn is None:
        #         print(f'++++++Failed to generate diffraction database.+++++')
        #         return
        #     if fn.lower() != baseline_data_filename.lower():
        #         import shutil
        #         shutil.copy(fn, baseline_data_filename)
        # print(f'baseline data file name: {baseline_data_filename}, {dl}')
        with open(baseline_data_filename, "wb") as f:
            pickle.dump(dl, f)
            
    except Exception as e:
        print(f"------Generating baseline results for {feature} FAILED.")
        return

    print(f"++++++Generating baseline results for {feature} SUCCEEDED.")

def run_sample_gui(feature = "diff"):
    if feature == "diff":
        import pyemaps.samples.si_dif as diff
        diff.main()
            
    if feature == 'bloch':
        import pyemaps.samples.si_bloch as bloch
        bloch.main()

    if feature == 'lacbed':
        # Like si_lacbed.main(), but also save the images as a PNG. LACBED gives one
        # image per diffracted beam, and the individual layout saves only the last
        # one, so use the table layout to save all the beams in one image.
        from pyemaps.samples.si_lacbed import generate_lacbed_images
        imgs = generate_lacbed_images(save=True)
        if imgs:
            showBloch(imgs, layout='table', bSave=True, bClose=True)

    if feature == 'stereo':
        # Like si_stereo.main(), but also save the stereodiagrams as PNGs.
        from pyemaps import showStereo
        from pyemaps.samples.si_stereo import generate_stereodiagrams
        showStereo(generate_stereodiagrams('tilt'), name='Silicon', layout='table',
                   iShow=True, bSave=True, bClose=True, zLimit=1)
        showStereo(generate_stereodiagrams('zone'), name='Silicon',
                   iShow=True, bSave=True, bClose=True, zLimit=1)

    if feature == 'csf':
        import pyemaps.samples.si_csf as csf
        csf.main()

    if feature == 'mxtal':
        import pyemaps.samples.si_constructor as mxtal
        mxtal.main()
    
    if feature == 'scm':
        import pyemaps.samples.si_scm as scm 
        scm.main()

    if feature == 'powder':
        # plot2Powder has no save option. It draws in this process, so save the
        # figure as a PNG just before it's shown. plt.pause calls show again,
        # so save each figure once.
        import matplotlib.pyplot as plt
        from pyemaps.fileutils import compose_ofn
        import pyemaps.samples.powder as powder
        show = plt.show
        saved = set()
        def save_then_show(*args, **kwargs):
            fig = plt.gcf()
            if fig.number not in saved:
                saved.add(fig.number)
                fn = compose_ofn(None, 'Silicon-Diamond', ty='powder') + '.png'
                fig.savefig(fn)
                print(f'image saved to: {fn}')
            return show(*args, **kwargs)
        plt.show = save_then_show
        try:
            powder.main()
        finally:
            plt.show = show

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
    