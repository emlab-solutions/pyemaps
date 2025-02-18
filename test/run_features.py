
from pyemaps import showBloch
import os
from pathlib import Path
import pickle
from sanity_base import *


def run_feature_list(cnflist, cdata_ty=TY_BUILTIN, feature=feat_list[0], bShow=False):
    from pyemaps import Crystal as cr
    import time
    from pyemaps import DPList,CrystalClassError

    failure_cases=[]
    failure_count = 0
    
    reslist = []
    res = None
    for cfn in cnflist: 
        
        tic = time.perf_counter()
        try:    
            cf = cr.from_xtl(cfn) if cdata_ty==TY_BUILTIN else cr.from_cif(cfn)                      

            if feature == feat_list[0]:
                emc, cf_dp = cf.generateDP()
                res = DPList(cf.name)
                res.add(emc, cf_dp)

            if feature == feat_list[1]:
                res = cf.generateBloch()

            if feature == feat_list[2]:
                res = cf.generateStereo()
            
            if feature==feat_list[3]:
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
            print(f"-------generating {feature} for {cfn} succeeded with time: {toc - tic:0.4f}")
            # tic = time.perf_counter()
            if not bShow:
                ffn = get_crystal_filename(cfn)
                reslist.append((ffn, res))
            else:
                from pyemaps import showBloch, showDif, showStereo, EMC
                if feature == feat_list[0] and res is not None:
                    showDif(res, bSave = False, bClose=True)
                if feature == feat_list[1] and res is not None:
                    showBloch(res, bSave = False, bClose=True)
                if feature == feat_list[2] and res is not None:
                    showStereo([(EMC(), res)], name=cf.name, bSave=False, bClose=True)
                    
    return failure_count, failure_cases, reslist
    
def gen_feature_baseline(feature=feat_list[0]):
    for t in [TY_BUILTIN, TY_CIF]:
        testcases = get_test_cases(cdata_ty=t, feature = feature)
        fc, fcases, res = run_feature_list(testcases, cdata_ty=t, feature=feature)

        bfilename = get_baseline_feature_filename(feature, t)
        with open(bfilename, "wb") as f:
            pickle.dump(res, f)
        
        print(f'------------------Generating baseline for feature: {feature}----------------')
        if fc != 0:
            print(f'There are failures in generating feature baseline: {fcases}')
        else:
            print(f'++++++ Feature - {feature} baseline generation and update SUCCEEDED ++++++')

def compare_feature_baseline(feature=feat_list[0]):
    import time
    for t in [TY_BUILTIN, TY_CIF]:
        bfilename = get_baseline_feature_filename(feature=feature, cdata_ty=t, bCreate=False)
        # Load baseline data
        with open(bfilename, "rb") as f:
            bdata = pickle.load(f)

        testcases = get_test_cases(cdata_ty=t, feature = feature)
        fc, fcases, res = run_feature_list(testcases, cdata_ty=t, feature=feature)
        headmsg = 'feature - ' + feature + "for " + 'built-in' if t==TY_BUILTIN else 'CIF' + ' Crystals'
        print(f'------------------Running and comparing baseline for {headmsg} ----------------')
        if fc != 0:
            print(f'Failures - {fc}: \n{fcases}')
        else:
            print(f'++++++ Current run SUCCEEDED +++++++')

        if bdata is None:
            print(f'Failed to load basline for feature: {feature}')

        basline_Compare_failure_cases=[]
        basline_Compare_failure_count = 0

        if len(res) != len(bdata):
            print(f'Current result does not compare with baseline.')
            return

        for r in res:
            tic = time.perf_counter()
            if not r in bdata:
                basline_Compare_failure_count +=1
                basline_Compare_failure_cases.append(r[0] + ('.xtl' if t == TY_BUILTIN else '.cif')) 
            toc = time.perf_counter()
            print(f"------- Time in comparing {feature} baseline for {r[0]}: {toc - tic:0.4f}")
        
        if basline_Compare_failure_count != 0:
            print(f'There are failures in comparing with baseline: {basline_Compare_failure_cases}')
        else:
            print(f'++++++ Baseline comparison SUCCEEDED +++++++')


def run_feature_gui(feature=feat_list[0]):
    if feature == 'mxtal':
        return
    # from pyemaps import showBloch, showDif, showStereo
    for t in [TY_BUILTIN, TY_CIF]:
        testcases = get_test_cases(cdata_ty=t, feature = feature)
        fc, fcases, _ = run_feature_list(testcases, cdata_ty=t, feature=feature, bShow =True)
    
        headmsg = 'feature - ' + feature + "for " + 'built-in' if t==TY_BUILTIN else 'CIF' + ' Crystals'
        print(f'------------------Running GUI test for {headmsg} ----------------')
        if fc != 0:
            print(f'Failures - {fc}: \n{fcases}')
        else:
            print(f'++++++ Current run SUCCEEDED +++++++')

# def run_features_test(data_ty=1, feat_type = feat_list[0], baseline = True):
    
#     # print(f'Before test call')
#     # if data_ty ==1:
#     #     data_dir = os.path.join(get_builtin_dir(), "cdata")
#     #     data_ext = '.xtl'
#     # else:
#     #     data_dir = get_cifdata_dir()
#     #     data_ext = '.cif'
 
#     # test_cases = []
        
#     # for f in os.listdir(data_dir):
#     #     if f.endswith(data_ext):
#     #         test_cases.append(os.path.join(data_dir, f))
#     test_cases = get_test_cases(data_ty=data_ty, feat_type=feat_type)
#     return run_feat_list(test_cases, ty=data_ty, bShow = bShow, bSave=bSave, feat_type=feat_type, baseline=baseline)

def print_filelist(fpl):
    flist = []
    for fp in fpl:
        _, f = os.path.split(fp)
        flist.append(f)
    
    print(f'   {flist}')
    
if __name__ == '__main__':

    import argparse, sys
    # import time

    import argparse, copy
    
    option_choices_core =feat_list
    option_choices= copy.deepcopy(option_choices_core)
    option_choices.append('all')

    parser = argparse.ArgumentParser(description="Choice for feature testing: GUI or just baseline comparison")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-bg", "--baseline_generation", 
                        nargs='?', 
                        const='info',   
                        default=None,   
                        metavar='diff|bloch|stereo|mxtal|all',
                        help="""Running this tool compares new results with the baseline results.""", 
                        required=False
                        )
    group.add_argument("-bc", "--baseline_comparison", 
                        nargs='?', 
                        const='info',   
                        default=None,   
                        metavar='diff|bloch|stereo|mxtal|all',
                        help="""Running this tool compares new results with the baseline results.""", 
                        required=False
                        )
    group.add_argument("-gr", "--gui_run", 
                        nargs='?', 
                        const='info',   
                        default=None,   
                        metavar='diff|bloch|stereo|mxtal|all',
                        help="""Running this tool compares new results with the baseline results.""", 
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
            gen_feature_baseline(f)

        if bcom:
            compare_feature_baseline(f)

        if bgui:
            run_feature_gui(f)
    else:       
        for ff in option_choices_core:
            if bgen:
                gen_feature_baseline(ff)

            if bcom:
                compare_feature_baseline(ff)

            if bgui:
                run_feature_gui(ff)

    # bline = True
    # f = feat_list[0]
    # if base is None:
    #     bline = False
    # else:
    #     f = base
    #     if f not in feat_list and f != 'all':
    #         print(f'Option value invalide!')
    #         sys.exit(1)
    # res = {}
    # fres=[]
    
    # if f == 'all':
    #     for fl in feat_list:
    #         res[fl]=[]
    #         for dt in range(1,3):
    #             fc, fcase, bcc, bccase = run_features_test(data_ty=dt, bShow = True, feat_type = fl, baseline= bline)
    #             fres.append((fc, fcase, bcc, bccase))

    #         print(f'\n\n\n<<<<<<<<<<<<<Summary of pyemaps Feature Sanity Runs - {fl}>>>>>>>>>>>>>>>\n\n\n')
    #         print(f"\n\n{fl} Feature Test Results:")  
    #         for dt in range(1,3):
    #             fc, fcase, bcc, bccase = fres[dt-1]
    #             data_type = 'builtin Crystal Data' if dt == 1 else 'CIF Crystal Data'
    #             print(f"<<{data_type.upper()} Tests>>:")  
    #             if fc != 0:
    #                 print(f'    ------ Current Run Failure count: {fc} ------')
    #                 print(f'    Failure cases')
    #                 print_filelist(fcase)   
    #             else:
    #                 print(f'    ++++++ All tests run successfully ++++++')

    #             if bcc != 0:
    #                 print(f'    ------Baseline Result Comparison Failure Count: {bcc} ------')
    #                 print(f'    Failure cases')
    #                 print_filelist(bccase)   
    #             else:
    #                 print(f'    ++++++ Success! All tests matches baseline ++++++')
    # else:
    #     for dt in range(1,3):
    #         fc, fcase, bcc, bccase = run_features_test(data_ty=dt, bShow = True, feat_type = f, baseline= bline)
    #         fres.append((fc, fcase, bcc, bccase))

    #     print(f'\n\n\n<<<<<<<<<<<<<Summary of pyemaps Feature Sanity Runs - {f}>>>>>>>>>>>>>>>\n\n\n')
    #     print(f"\n\n{f} Feature Test Results:")  
    #     for dt in range(1,3):
    #         fc, fcase, bcc, bccase = fres[dt-1]
    #         data_type = 'builtin Crystal Data' if dt == 1 else 'CIF Crystal Data'
    #         print(f"<<{data_type.upper()} Tests>>:")  
    #         if fc != 0:
    #             print(f'    ------ Current Run Failure count: {fc} ------')
    #             print(f'    Failure cases')
    #             print_filelist(fcase)   
    #         else:
    #             print(f'    ++++++ All tests run successfully ++++++')

    #         if bcc != 0:
    #             print(f'    ------Baseline Result Comparison Failure Count: {bcc} ------')
    #             print(f'    Failure cases')
    #             print_filelist(bccase)   
    #         else:
    #             print(f'    ++++++ Success! All tests matches baseline ++++++')