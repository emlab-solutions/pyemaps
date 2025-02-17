import os
from pathlib import Path
import pickle
# from sanity_base import get_current_folder, get_crystal_filename, get_cifdata_dir, get_builtin_dir
from sanity_base import *

def generate_feature_beaseline(cnflist, ty=1, feat_type=feat_list[0]):
    from pyemaps import Crystal as cr
    from pyemaps import DPList,CrystalClassError
    
    # feat_type=feat_list[0]

    failure_cases=[]
    failure_count = 0
    blist = []
    
    baseline_data_filename = get_baseline_feature_filename(feature=feat_type, ttype=ty, bCreate=True)  

    for cfn in cnflist: 
        
        try:    
            cf = cr.from_xtl(cfn) if ty==1 else cr.from_cif(cfn) 
            ffn = get_crystal_filename(cfn) 
            # print(f'Pickle data file name: {baseline_data_filename}')
            if feat_type == feat_list[0]:
                emc, cf_dp = cf.generateDP()
                dpl = DPList(cf.name)
                dpl.add(emc, cf_dp)
                blist.append((ffn, dpl))

            if feat_type == feat_list[1]:
                bimgs = cf.generateBloch()
                blist.append((ffn, bimgs))

            if feat_type == feat_list[2]:
                s = cf.generateStereo()
                blist.append((ffn, s))

            if feat_type==feat_list[3]:
                mx = cf.generateMxtal()
                blist.append((ffn, mx))

        except CrystalClassError as e:
            print(f'Error loading crystal {cfn}')
            failure_count += 1
            failure_cases.append(cfn)
            blist.append((ffn, None))
            continue
        except Exception as e:
                print(f'baseline result generation {cfn} failed with message {e}')
                # failure_count += 1
                # failure_cases.append(cfn)
                blist.append((ffn, None))
                continue
        else:
            print(f"-------generating baseline result for {feat_type} & {cfn} succeeded")
            
    with open(baseline_data_filename, "wb") as f:
        pickle.dump(blist, f)

    return failure_count, failure_cases

def gen_features_baseline(data_ty=1, feat_type = feat_list[0]):
    
    test_cases = get_test_cases(data_ty=data_ty, feat_type=feat_type)

    return generate_feature_beaseline(test_cases, ty=data_ty, feat_type=feat_type)

def print_filelist(fpl):
    flist = []
    for fp in fpl:
        _, f = os.path.split(fp)
        flist.append(f)
    
    print(f'   {flist}')

def gen_samples_baseline(feature):
    print(f'------------------Generating baseline for feature: {feature}----------------')
    try:
        baseline_data_filename = get_baseline_sample_filename(feature) 
    except FileExistsError as e:
        print(f'test failed: {e}')
        sys.exit(1)

    dl=[]
    if feature == "diff":
        from pyemaps.samples.si_dif import generate_difs
        em_keys = ['tilt', 'zone', 'defl', 'vt', 'cl']
        for k in em_keys:
            dpl = generate_difs(ckey=k, mode=2)
            dl.append((k, dpl))
            
    if feature == 'bloch':
        from pyemaps.samples.si_bloch import generate_bloch_images
        em_keys = ['tilt', 'zone']
    
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

    with open(baseline_data_filename, "wb") as f:
        pickle.dump(dl, f)

def gen_unittest_baseline(f):
    print(f'------------------Generating baseline for unittest: {f}----------------')
    try:
        baseline_data_filename = get_baseline_unittest_filename(f, bCreate=True) 
    except FileExistsError as e:
        print(f'test failed: {e}')
        sys.exit(1)

    dl=[]
    if f == "diff":
        from unittests.kdif.sanity_doc import run_kdiffraction
        dl = run_kdiffraction(bShow=False)
            
    if f == 'bloch':
        from unittests.bloch.si_bloch_docs import generate_bloch_images
        dl = generate_bloch_images(bSave=False)

    if f == 'lacbed':
        from unittests.bloch.si_lacbed_docs import generate_lacbed_images
        dl = generate_lacbed_images(bSave=False)

    with open(baseline_data_filename, "wb") as bf:
        pickle.dump(dl, bf)

    print(f'++++++ Unit test baseline updated SUCCESSFULLY for {f} ++++++')

if __name__ == '__main__':
    import argparse, sys

    parser = argparse.ArgumentParser(description="pyEMAPS baseline generation tool.",  
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", 
                        "--feature", 
                        nargs='?', 
                        const='info',   
                        default=None,   
                        metavar='diff|bloch|stereo|mxtal|all',
                        help="""Running this tool generate new baseline results used in sanity test.""", 
                        required=False
                        )
    parser.add_argument("-s", 
                        "--samples", 
                        nargs='?', 
                        const='info',   
                        default=None,   
                        metavar='diff|bloch|stereo|lacbed|lacbed|scm|scf|mxtal|dpgen|all',
                        help="""Running this tool generate new baseline results for all samples code.""", 
                        required=False
                        )
    parser.add_argument("-u", 
                        "--unittest", 
                        nargs='?', 
                        const='info',   
                        default=None,   
                        metavar='diff|bloch|all',
                        help="""Running this tool generate new baseline results for all unit test code.""", 
                        required=False
                        )
    args = parser.parse_args()

    fchoice = args.feature
    fsample = args.samples
    unittest = args.unittest

    if fchoice:
        if fchoice not in feat_list and fchoice != 'all':
            print(f'Invalid feature selecion. It must be one of {feat_list} or all ')
            sys.exit(1)

        if fchoice != 'all':
            for dt in range(1,3):
                fc, fl = gen_features_baseline(data_ty=dt, feat_type = fchoice)

                print(f'\n\n\n<<<<<<<<<<<<<Summary of pyemaps Feature Sanity result Baseline>>>>>>>>>>>>>>>\n\n\n')

                data_type = 'builtin Crystal Data' if dt == 1 else 'CIF Crystal Data'
                print(f"<<{data_type.upper()} Tests>>:")  
                if fc != 0:
                    print(f'    ------ Failure count: {fc} ------')
                    print(f'    Failure cases')
                    print_filelist(fl)   
                else:
                    print(f'    ++++++ All tests passed ++++++')
        else:

            # it is baseline results generation/updates for all features
            for feat in feat_list:
                for dt in range(1,3):
                    fc, fl = gen_features_baseline(data_ty=dt, feat_type = feat)

                    print(f'\n\n\n<<<<<<<<<<<<<Summary of pyemaps Feature Sanity result Baseline>>>>>>>>>>>>>>>\n\n\n')

                    data_type = 'builtin Crystal Data' if dt == 1 else 'CIF Crystal Data'
                    print(f"<<{data_type.upper()} Tests>>:")  
                    if fc != 0:
                        print(f'    ------ Failure count: {fc} ------')
                        print(f'    Failure cases')
                        print_filelist(fl)   
                    else:
                        print(f'    ++++++ All tests passed ++++++')

    if fsample:
        if fsample != 'all' and featureInSampleList(fsample):
            
            gen_samples_baseline(fsample)
        else:
            fl = [list(d.keys())[0] for d in sample_feat_list]
            
            for d in fl:
                gen_samples_baseline(d)

    if unittest:
        if unittest != 'all' and featureInUnittestList(unittest):
            
            gen_unittest_baseline(unittest)
        else:
            fl = [list(d.keys())[0] for d in unittest_feat_list]
            
            for d in fl:
                gen_samples_baseline(d)
