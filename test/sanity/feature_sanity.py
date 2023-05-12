
from pyemaps import showBloch
import os
from pathlib import Path


feat_list=[
            'dif', 
           'bloch', 
           'stereo', 
           'mxtal'
           ]

def get_cifdata_dir():

    current_path = Path(os.path.abspath(__file__))

    test_path = current_path.parent.parent.absolute()

    return os.path.join(test_path, 'cifdata')


def get_builtin_dir():
    import pyemaps
    from pathlib import Path

    return(Path(pyemaps.__file__).parent.absolute())

def run_feat_list(cnflist, ty=1, bShow=True, bSave=False, feat_type='dif'):
    from pyemaps import Crystal as cr
    import time
    from pyemaps import DPList,CrystalClassError, EMC,showBloch, showDif, showStereo
    # from pyemaps import BlochImgs

    failure_cases=[]
    failure_count = 0
    
    for cfn in cnflist: 
        # if 'Aluminium.xtl' not in cfn:
        #     continue
        tic = time.perf_counter()
        try:    
            cf = cr.from_xtl(cfn) if ty==1 else cr.from_cif(cfn)                  
            if feat_type == 'bloch':
                bimgs = cf.generateBloch()

            if feat_type == 'dif':
                emc, cf_dp = cf.generateDP()
                dpl = DPList(cf.name)
                dpl.add(emc, cf_dp)

            if feat_type == 'stereo':
                s = cf.generateStereo()
            
            if feat_type=='mxtal':
                mx = cf.generateMxtal()

            toc = time.perf_counter()
        except CrystalClassError as e:
            print(f'Error loading crystal {cfn}')
            failure_count += 1
            failure_cases.append(cfn)
            continue
        except Exception:
                failure_count += 1
                failure_cases.append(cfn)
                continue
        else:
            print(f"-------generating {feat_type} for {cfn} succeeded with time: {toc - tic:0.4f}")
            if bShow:
                if feat_type == 'bloch':
                    if bimgs is not None:
                        showBloch(bimgs, bSave = bSave, bClose=True)
                    else:
                        failure_count += 1
                        failure_cases.append(cfn)
                        print('Bloch image invalid')
                if feat_type == 'dif':
                    showDif(dpl, bSave=bSave, bClose=True)
                if feat_type == 'stereo':
                    showStereo([(EMC(), s)], name=cf.name, bSave=bSave, bClose=True)

    return failure_count, failure_cases

def run_features_test(data_ty=1, bShow=True, bSave=False, feat_type = 'dif'):
    
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

    return run_feat_list(test_cases, ty=data_ty, bShow = bShow, bSave=bSave, feat_type=feat_type)

def run_metrics():
    from pyemaps import Crystal as cr
    si = cr.from_builtin('Silicon')
    
    vd = si.d2r()
    print(f'\nDefault real space to reciprocal space transform: \n{vd}')
    vd = si.r2d()
    print(f'\nDefault reciprocal space to real space transform: \n{vd}')

    # real to reciprocal transformation
    v = (1.0, 1.0, 2.0)
    v_recip = si.d2r(v) 
    print(f'\nReal space to reciprocal space transform for {v}:\n{v_recip}')
  
    
    #reciprocal to real transformation
    v_ = si.r2d(v_recip) # v_ ~= v
    print(f'\nReciprocal space to real space transform for {v_recip}:\n{v_}')

    #angle in real space
    v1 = (1.0, 1.0, 2.0)
    v2 = (1.0, 1.0, 1.0)
    real_a = si.angle(v1, v2)
    print(f'\nAngle in real space by vectors {v1} and {v2}: \n{real_a} \u00B0')

    #angle in reciprocal space
    recip_a = si.angle(v1, v2, ty = 1)
    print(f'\nAngle in reciprocal space by vectors {v1} and {v2}: \n{recip_a} \u00B0')

    #vector length in real space
    r_vlen = si.vlen(v)
    print(f'\nLength in real space for vector {v}:\n{r_vlen} in \u212B')

    #vector length in reciprocal space
    recip_vlen = si.vlen(v, ty = 1)
    print(f'\nLength in reciprocal space for vector {v}:\n{recip_vlen} in 1/\u212B')

    #wave length with high voltage of 200 V
    print(f'\nWave length with high voltage of 200 kV:\n{si.wavelength(200)} \u212B')

def print_filelist(fpl):
    flist = []
    for fp in fpl:
        _, f = os.path.split(fp)
        flist.append(f)
    
    print(f'   {flist}')
    
if __name__ == '__main__':

    # run_metrics()
    res = {}
    for f in feat_list:
        res[f]=[]
        for dt in range(1,3):
            fc, fl = run_features_test(data_ty=dt, bShow = True, feat_type = f)
            res[f].append((fc, fl))

    print(f'\n\n\n<<<<<<<<<<<<<Summary of pyemaps Feature Sanity Runs>>>>>>>>>>>>>>>\n\n\n')

    for f in feat_list:
        fres = res[f]
        print(f"\n\n{f} Feature Test Results:")  
        for dt in range(1,3):
            fc, fl = fres[dt-1]
            data_type = 'builtin Crystal Data' if dt == 1 else 'CIF Crystal Data'
            print(f"<<{data_type.upper()} Tests>>:")  
            if fc != 0:
                print(f'    ------ Failure count: {fc} ------')
                print(f'    Failure cases')
                print_filelist(fl)   
            else:
                print(f'    ++++++ All tests passed ++++++')
