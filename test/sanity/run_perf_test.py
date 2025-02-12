from perf import run_perf, perf_fname_dict, gen_perf_baseline
if __name__ == '__main__':
    import argparse
    import time
    parser = argparse.ArgumentParser(description="Build and publish script for pyeamps")
    parser.add_argument("-bl", "--baseline", type=str, nargs="?", const="", default="", help="generate baseline", required=False)
    parser.add_argument("-r", "--run", type=str, nargs="?", const="", default="", help="build version input", required=False)
    
    args = parser.parse_args()

    run = args.run
    if run is not None and run in perf_fname_dict:
        # print(f'run is {run}')
        run_perf(ty=run)
        exit(0)
      
    if run is not None and run == 'all':
        for k in perf_fname_dict:
            run_perf(ty=k)
        exit(0)
    
    baseline = args.baseline
    if baseline is not None and baseline in perf_fname_dict:
        gen_perf_baseline(ty=baseline)
        exit(0)
    
    if baseline is not None and baseline == 'all':
        for k in perf_fname_dict:
            gen_perf_baseline(ty=k)
        exit(0)

    print(f'Performance test must have arguements of -bl or -r')