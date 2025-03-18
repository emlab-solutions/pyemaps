
import time

perf_fname_dict = {
    'dif': 'perf_baseline_dif.json',
    'bloch': 'perf_baseline_bloch.json',
    'stereo': 'perf_baseline_stereo.json',
}

def get_baseline_fname(ty='dif'):
    import os
    from pathlib import Path
      
    if ty not in perf_fname_dict:
        return ''

    perf_fname = perf_fname_dict[ty]   
    current_path = Path(os.path.abspath(__file__))
    perf_bfn = os.path.join(current_path.parent.parent.absolute(), 'baseline', 'perf', perf_fname)

    return perf_bfn

def get_perf_baseline(ty='dif'):
    import json
    
    perf_bfn = get_baseline_fname(ty=ty)
    print(f'Baseline file name for {ty}: {perf_bfn}')
    
    with open(perf_bfn) as jf:
        data = json.load(jf)
        
    return dict(data)
            
def gen_perf_baseline(ty='dif'):
    import json

    perf_bfn = get_baseline_fname(ty = ty)
    
    perfl = run_perf(ty=ty, bBaseline = True)

    jdata = json.dumps(perfl)
    jFile = open(perf_bfn, 'w')
    jFile.write(jdata)


            
def update_baseline(ty='dif', data=None):
    import json

    perf_bfn = get_baseline_fname(ty = ty)
    if data is None:
        return
#     # perfl = run_perf(ty=ty, bBaseline = True)

    jdata = json.dumps(data)
    jFile = open(perf_bfn, 'w')
    jFile.write(jdata)     


def run_perf(ty = 'dif', bBaseline = False):
    from pyemaps import Crystal as cr
    
    cblist = cr.list_all_builtin_crystals()

    failure_count=0
    failure_cases=[]
    res_dict = {}

    for c in cblist:
        # debug:
        if 'SiAlONa' in c:
            continue
        # debug:

        tic = time.perf_counter()
        cc = cr.from_builtin(c)

        try:      
            if ty == 'dif':                      
                cc.generateDP()
            
            if ty == 'bloch':
                cc.generateBloch()

            if ty == 'stereo':
                cc.generateStereo()
            
            toc = time.perf_counter()

        except Exception:
            print(f'Failed to measure performance for {ty}')
            failure_count += 1
            failure_cases.append[c]
        else:
            res_dict[c] = float(toc-tic)

    if failure_count == 0:
        print(f'\n---------successfully run builtin crystal for {ty} performance----------\n')
        if bBaseline:
            return res_dict
        
        # load the existing baseline reseult:
        jBaseline = get_perf_baseline(ty=ty)
        for n, v in res_dict.items():
            # print(f'loaded baseline result: {jBaseline.keys()}')
            if n.strip() in jBaseline:
                base = float(jBaseline[n])
                vv = float(v)
                diff = abs(vv-base)
                percent= round(100.0 * (diff/base))
                

                if diff < 0.001:
                    print(f'{ty} = {n}: stays the same for {n}')
                    continue

                if vv > base:
                    print(f'{ty} - {n}: by {diff} or {percent}%')
                    continue

                if vv < base:
                    print(f'{ty} + {n}: by {diff} or {percent}%')
                    continue
            else:
                print(f'{ty} + {n}: ****no baseline perf data compared to current run: {v}')
                # newData = {}
                jBaseline[n] = v
                update_baseline(ty=ty, data = sorted(jBaseline.items()))



    

