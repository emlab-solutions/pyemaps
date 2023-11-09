import perf 
if __name__ == '__main__':
    for k in perf.perf_fname_dict:
        perf.gen_perf_baseline(ty=k)