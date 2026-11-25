
import time

perf_fname_dict = {
    'dif': 'perf_baseline_dif.json',
    'bloch': 'perf_baseline_bloch.json',
    'stereo': 'perf_baseline_stereo.json',
    'probe': 'perf_baseline_probe.json',
}

BLOCH_SKIP = ['SiAlONa']

# The probe module's components, at three map sizes: each case is timed as the best of
# PROBE_REPEAT runs, since each takes milliseconds to seconds.
PROBE_SIZES = (256, 512, 1024)
PROBE_REPEAT = 3


def probe_cases():
    '''
    The probe timing cases, {name: function}, or {} with an emaps without the probe module.
    Names are <component>_<sampling>.
    '''
    try:
        from pyemaps import Probe
        from pyemaps import probe as probe_module
    except ImportError:
        return {}
    if probe_module.probesim is None:
        return {}

    cases = {}
    for n in PROBE_SIZES:
        lens = Probe(kv=200, aperture=25, cs=0.01, c5=3.0, size=0.2 * n, sampling=n)
        chromatic = Probe(kv=200, aperture=25, cs=0.01, c5=3.0, cc=1.5, energy_spread=0.6,
                          semi_angle=0.2, size=0.2 * n, sampling=n)
        potential = lens.random_potential()
        wave = lens.exit_wave(potential)
        intensity = lens.probe()
        cases.update({
            f'potential_{n}': lambda lens=lens: lens.random_potential(),
            f'exit_wave_{n}': lambda lens=lens, v=potential: lens.exit_wave(v),
            f'ronchigram_{n}': lambda lens=lens, v=potential: lens.ronchigram(v),
            f'probe_{n}': lambda lens=lens: lens.probe(),
            f'probe_cc_{n}': lambda lens=chromatic: lens.probe(),
            f'diameter_{n}': lambda lens=lens, p=intensity: lens.diameter(50, p),
            f'ctf_{n}': lambda lens=chromatic: lens.ctf(),
            f'hrem_{n}': lambda lens=chromatic, w=wave: lens.hrem(w),
            f'hrem_integrated_{n}': lambda lens=chromatic, w=wave: lens.hrem(w, integrate=True),
        })
    return cases


def time_probe_case(fn):
    best = None
    for _ in range(PROBE_REPEAT):
        tic = time.perf_counter()
        fn()
        dt = time.perf_counter() - tic
        best = dt if best is None else min(best, dt)
    return best

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
    
    with open(perf_bfn) as jf:
        data = json.load(jf)
    
    return data
            
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

    if ty == 'probe':
        cases = probe_cases()
        if not cases:
            print('probe: skipped, this emaps has no probe module')
            return res_dict if bBaseline else None
        cblist = []
        for name, fn in cases.items():
            try:
                res_dict[name] = float(time_probe_case(fn))
            except Exception as e:
                print(f'Failed to measure performance for probe {name}: {e}')
                failure_count += 1
                failure_cases.append(name)

    for c in cblist:
        # SiAlONa is the Bloch stress test's crystal (stress/bloch/zone.py): its Bloch run
        # takes minutes, so the Bloch timings leave it out.
        if ty == 'bloch' and c in BLOCH_SKIP:
            continue
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
            failure_cases.append(c)
        else:
            res_dict[c] = float(toc-tic)

    if failure_count == 0:
        print(f'\n---------successfully run builtin crystal for {ty} performance----------\n')
        if bBaseline:
            return res_dict
        
        # load the existing baseline reseult:
        jBaseline = get_perf_baseline(ty=ty)
        # print(f'loaded baseline result: {res_dict}')
        for n, v in res_dict.items():
            if n in jBaseline:
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
                # A run only compares: the baseline changes only with -bl.
                print(f'{ty} ? {n}: ****no baseline perf data compared to current run: {v} '
                      f'(run_perf_test.py -bl {ty} adds it)')



    

