
# from pyemaps import showBloch
import sys
import pickle
from sanity_base import *

def compare_unittest_baseline(feature):
    print(f'------------------generating new results and comparing them with baseline for feature: {feature}----------------')
    try:
        baseline_data_filename = get_baseline_unittest_filename(feature, bCreate=False) 
        # Load baseline data
        with open(baseline_data_filename, "rb") as f:
            bdata = pickle.load(f)

    except FileExistsError as e:
        print(f'test failed: {e}')
        sys.exit(1)

    dl = None
    if f == "diff":
        from unittests.kdif.sanity_doc import run_kdiffraction
        dl = run_kdiffraction(bShow=False, bSave=False, bPrint=False)

    if f == 'bloch':
        from unittests.bloch.si_bloch_docs import generate_bloch_images
        dl = generate_bloch_images(bSave=False)

    if f == 'lacbed':
        from unittests.bloch.si_lacbed_docs import generate_lacbed_images
        dl = generate_lacbed_images(bSave=False)

    if dl is not None and not (dl == bdata):
        print(f'++++++ Baseline comparison FAILED for {feature} unit test +++++++')
    else:
        print(f'++++++ Baseline comparison SUCCEEDED for {feature} unit test +++++++')  

def run_unittest_gui(feature = "diff"):
    if feature == "diff":
        from unittests.kdif.sanity_doc import run_kdiffraction
        run_kdiffraction()
            
    if feature == 'bloch':
        import unittests.bloch.si_bloch_docs as bloch
        bloch.main()

    if feature == 'lacbed':
        import unittests.bloch.si_lacbed_docs as lacbed
        lacbed.main()

def run_unittest_aux():
    try:
        import unittests.emc.controls as controls 
        import unittests.package_test.license_test as licence_test
        import unittests.package_test.type_test as type_test 
        controls.main()
        licence_test.main()
        type_test.main()
    except Exception as e:
        print(f'+++++ Auxillary unit tests FAILED: {e} +++++')
    
    print(f'+++++ Auxillary unit tests SUCCEDED +++++\n')

    
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
        dl = run_kdiffraction(bShow=False, bSave=False, bPrint=False)
            
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
    
    import argparse, copy
    
    option_choices_core = [list(d.keys())[0] for d in unittest_feat_list]
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
            gen_unittest_baseline(f)

        if bcom:
            compare_unittest_baseline(f)

        if bgui:
            run_unittest_gui(f)
    else:       
        if bgui:
            run_unittest_aux()
        try:
            for ff in option_choices_core:
                if bgen:
                    gen_unittest_baseline(ff)

                if bcom:
                    compare_unittest_baseline(ff)

                if bgui:
                    run_unittest_gui(ff)
        except Exception as e:
            print(f'+++++ Unit tests FAILED: {e} +++++')
        else:
            print(f'+++++ Unit tests SUCCEEDED +++++\n')
    