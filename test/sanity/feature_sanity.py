
from pyemaps import showBloch
import os
from pathlib import Path
import pickle
from sanity_base import get_current_folder, get_crystal_filename, get_cifdata_dir, get_builtin_dir, get_baseline_filename
from sanity_base import feat_list

def run_feat_list(cnflist, ty=1, bShow=True, bSave=False, feat_type=feat_list[0], baseline=True):
    from pyemaps import Crystal as cr
    import time
    from pyemaps import DPList,CrystalClassError, EMC,showBloch, showDif, showStereo
    # from pyemaps import BlochImgs

    failure_cases=[]
    failure_count = 0

    basline_Compare_failure_cases=[]
    basline_Compare_failure_count = 0
    
    if baseline:
        bShow=False 
        bSave=False
        bfilename = get_baseline_filename(feat_type, ty)
        # Load baseline data
        with open(bfilename, "rb") as f:
            bdata = pickle.load(f)
        # for d in bdata:
        #     if d[0] == '1010100':
        #         l=len(d[1]['xyz'])
        #         print(f'data for {d[0]}: {l}')
        #         sys.exit()

    res = None
    for cfn in cnflist: 
        
        tic = time.perf_counter()
        try:    
            cf = cr.from_xtl(cfn) if ty==1 else cr.from_cif(cfn)                      

            if feat_type == feat_list[0]:
                emc, cf_dp = cf.generateDP()
                res = DPList(cf.name)
                res.add(emc, cf_dp)

            if feat_type == feat_list[1]:
                res = cf.generateBloch()

            if feat_type == feat_list[2]:
                res = cf.generateStereo()
            
            if feat_type==feat_list[3]:
                res = cf.generateMxtal()

            toc = time.perf_counter()
        except CrystalClassError as e:
            print(f'Error loading crystal {cfn}')
            failure_count += 1
            failure_cases.append(cfn)
            continue
        except Exception as e:
                print(f'Loading {cfn} failed')
                failure_count += 1
                failure_cases.append(cfn)
                continue
        else:
            print(f"-------generating {feat_type} for {cfn} succeeded with time: {toc - tic:0.4f}")
            if baseline:
                ffn = get_crystal_filename(cfn)
                
                msg = 'Kinematic diffraction'
                if feat_type == feat_list[1]:
                    msg = 'Dynamic diffraction'
                
                if feat_type == feat_list[2]:
                    msg = 'StereoDiagram'
                
                if feat_type == feat_list[3]:
                    msg = 'Crystal structure'

                # comparing the latest results with baseline
                if not (ffn, res) in bdata:
                    basline_Compare_failure_count += 1
                    basline_Compare_failure_cases.append(cfn)
                    print(f'{msg} result comparisom with baseline failed for: {cfn}')
                # elif feat_type == feat_list[3]:
                #     bfound = False
                #     for (fn, m) in bdata:
                #         if fn == ffn:
                #             bfound = True
                #             if cf.compareXYZ(m, res):
                #                 print(f'{msg} result matches baseline for: {cfn}')
                #             else:
                #                 print(f'{msg} result matches baseline for: {cfn}')
                #     if not bfound:
                #         print(f'{msg} result not found in baseline for: {cfn}')
                                
                else:    
                    print(f'{msg} result matches baseline for: {cfn}')

                tic = time.perf_counter()
                print(f"-------comparing basline {feat_type} for {cfn} succeeded with time: {tic-toc:0.4f}\n")
                  
                continue    
            if bShow:
                if feat_type == feat_list[1]:
                    if res is not None:
                        showBloch(res, bSave = bSave, bClose=True)
                    else:
                        failure_count += 1
                        failure_cases.append(cfn)
                        print('Bloch image invalid')
                if feat_type == feat_list[0]:
                    showDif(res, bSave=bSave, bClose=True)

                if feat_type == feat_list[2]:
                    showStereo([(EMC(), res)], name=cf.name, bSave=bSave, bClose=True)
                    
    return failure_count, failure_cases, basline_Compare_failure_count, basline_Compare_failure_cases

def run_features_test(data_ty=1, bShow=True, bSave=False, feat_type = feat_list[0], baseline = True):
    
    # print(f'Before test call')
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
    return run_feat_list(test_cases, ty=data_ty, bShow = bShow, bSave=bSave, feat_type=feat_type, baseline=baseline)

def print_filelist(fpl):
    flist = []
    for fp in fpl:
        _, f = os.path.split(fp)
        flist.append(f)
    
    print(f'   {flist}')
    
if __name__ == '__main__':

    import argparse, sys
    # import time

    parser = argparse.ArgumentParser(description="Choice for feature testing: GUI or just baseline comparison")
    parser.add_argument("-b", "--baseline", 
                        nargs='?', 
                        const='info',   
                        default=None,   
                        metavar='diff|bloch|stereo|mxtal|all',
                        help="""Running this tool compares new results with the baseline results.""", 
                        required=False
                        )
    # parser.add_argument("-b", "--baseline",
    #                     default=False, 
    #                     action='store_true',
    #                     help="Comparing baseline results without displaying", 
    #                     required=False)
    
    args = parser.parse_args()

    base = args.baseline

    # print(f'call with baseline arguement: {base}')

    bline = True
    f = feat_list[0]
    if base is None:
        bline = False
    else:
        f = base
        if f not in feat_list and f != 'all':
            print(f'Option value invalide!')
            sys.exit(1)
    res = {}
    fres=[]
    
    if f == 'all':
        for fl in feat_list:
            res[fl]=[]
            for dt in range(1,3):
                fc, fcase, bcc, bccase = run_features_test(data_ty=dt, bShow = True, feat_type = fl, baseline= bline)
                fres.append((fc, fcase, bcc, bccase))

            print(f'\n\n\n<<<<<<<<<<<<<Summary of pyemaps Feature Sanity Runs - {fl}>>>>>>>>>>>>>>>\n\n\n')
            print(f"\n\n{fl} Feature Test Results:")  
            for dt in range(1,3):
                fc, fcase, bcc, bccase = fres[dt-1]
                data_type = 'builtin Crystal Data' if dt == 1 else 'CIF Crystal Data'
                print(f"<<{data_type.upper()} Tests>>:")  
                if fc != 0:
                    print(f'    ------ Current Run Failure count: {fc} ------')
                    print(f'    Failure cases')
                    print_filelist(fcase)   
                else:
                    print(f'    ++++++ All tests run successfully ++++++')

                if bcc != 0:
                    print(f'    ------Baseline Result Comparison Failure Count: {bcc} ------')
                    print(f'    Failure cases')
                    print_filelist(bccase)   
                else:
                    print(f'    ++++++ Success! All tests matches baseline ++++++')
    else:
        for dt in range(1,3):
            fc, fcase, bcc, bccase = run_features_test(data_ty=dt, bShow = True, feat_type = f, baseline= bline)
            fres.append((fc, fcase, bcc, bccase))

        print(f'\n\n\n<<<<<<<<<<<<<Summary of pyemaps Feature Sanity Runs - {f}>>>>>>>>>>>>>>>\n\n\n')
        print(f"\n\n{f} Feature Test Results:")  
        for dt in range(1,3):
            fc, fcase, bcc, bccase = fres[dt-1]
            data_type = 'builtin Crystal Data' if dt == 1 else 'CIF Crystal Data'
            print(f"<<{data_type.upper()} Tests>>:")  
            if fc != 0:
                print(f'    ------ Current Run Failure count: {fc} ------')
                print(f'    Failure cases')
                print_filelist(fcase)   
            else:
                print(f'    ++++++ All tests run successfully ++++++')

            if bcc != 0:
                print(f'    ------Baseline Result Comparison Failure Count: {bcc} ------')
                print(f'    Failure cases')
                print_filelist(bccase)   
            else:
                print(f'    ++++++ Success! All tests matches baseline ++++++')