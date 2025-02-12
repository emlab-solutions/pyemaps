import os
from pathlib import Path
import pickle
from sanity_base import get_current_folder, get_crystal_filename, get_cifdata_dir, get_builtin_dir
from sanity_base import feat_list, sample_feat_list, get_baseline_sample_filename

def generate_feature_beaseline(cnflist, ty=1, feat_type=feat_list[0]):
    from pyemaps import Crystal as cr
    from pyemaps import DPList,CrystalClassError
    
    # feat_type=feat_list[0]

    failure_cases=[]
    failure_count = 0
    blist = []

    baseline_dir = os.path.join(get_current_folder(), 'baseline', feat_type)
    if not os.path.exists(baseline_dir):
        os.makedirs(baseline_dir, exist_ok=True)
    
    baseline_data_filename = os.path.join(baseline_dir, 'builtin.pkl' if ty==1 else 'cif.pkl')  

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
    
    if data_ty ==1:
        data_dir = os.path.join(get_builtin_dir(), "cdata")
        data_ext = '.xtl'
    else:
        data_dir = get_cifdata_dir()
        data_ext = '.cif'
 
    test_cases = []
        
    for f in os.listdir(data_dir):
        if f.endswith(data_ext):
            test_cases.append(os.path.join(data_dir, f))

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
        # baseline_data_filename = get_baseline_sample_filename('diff', 'si_dif')
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
        # baseline_data_filename = os.path.join(baseline_dir, 'si_lacbed' + '.pkl')
        imgs = generate_lacbed_images()
        dl=imgs

    if feature == 'stereo':
        from pyemaps.samples.si_stereo import generate_stereo
        # baseline_data_filename = os.path.join(baseline_dir, 'si_stereo' + '.pkl')
        dl = generate_stereo(ckey='tilt')

    if feature == 'csf':
        from pyemaps.samples.si_csf import runCSFTests
        # baseline_data_filename = os.path.join(baseline_dir, 'si_csf' + '.pkl')
        dl = runCSFTests(bPrint=False)

    if feature == 'mxtal':
        from pyemaps.samples.si_constructor import test_mxtal
        # baseline_data_filename = os.path.join(baseline_dir, 'si_constructor' + '.pkl')
        dl = test_mxtal(bPrint=False, bSave=False)
    
    if feature == 'scm':
        from pyemaps.samples.si_scm import runSCMFullTests
        # baseline_data_filename = os.path.join(baseline_dir, 'si_scm' + '.pkl')
        dl = runSCMFullTests()

    if feature == 'powder':
        from pyemaps.samples.powder import runPowderTests
        # baseline_data_filename = os.path.join(baseline_dir, 'powder' + '.pkl')
        dl = runPowderTests(bPrint=False)

    with open(baseline_data_filename, "wb") as f:
        pickle.dump(dl, f)

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
                        metavar='diff|bloch|stereo|lacbed|lacbed|scm|scf|mxtal|all',
                        help="""Running this tool generate new baseline results for all samples code.""", 
                        required=False
                        )
    args = parser.parse_args()

    fchoice = args.feature
    fsample = args.samples

    if fchoice:
        if fchoice not in feat_list and fchoice is not 'all':
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
        if fsample != 'all':
            print(f'feature provided: {fsample}' )
            gen_samples_baseline(fsample)
        else:
            fl = [list(d.keys())[0] for d in sample_feat_list]
            
            for d in fl:
                gen_samples_baseline(d)
