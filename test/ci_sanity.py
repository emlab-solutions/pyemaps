'''
Sanity tests for CI: run the samples, features and unit test suites with -bc (compare
with the stored baselines) and fail if any of them fails.

    python test/ci_sanity.py          # from the pyemaps folder, with pyemaps installed

The suites report a baseline mismatch by printing, not by their exit code, so this
script checks their output too. A suite passes when it exits 0, prints none of the
failure messages, and prints the expected number of success lines. Each suite's
output is saved to sanity-logs/<suite>.log.

The performance test isn't run: its timings depend on the machine, so it means
nothing on a shared CI runner. Run it locally (performance/run_perf_test.py -r all).
The stem4d checks (run_stem4d.py) need an activated license, so they aren't run here.
'''
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOGS = Path.cwd() / 'sanity-logs'

# suite name, script, success-line pattern, number of success lines a full pass prints
SUITES = [
    ('samples', 'run_samples.py', r'Baseline match SUCCEEDED', 8),
    ('features', 'run_features.py', r'Baseline comparison SUCCEEDED \+\+\+', 8),
    ('unittests', 'run_unittests.py', r'Unit tests SUCCEEDED', 1),
    ('switching', 'run_crystal_switch.py', r'Crystal switching checks SUCCEEDED', 1),
]
FAILURE = re.compile(r'FAILED|There are failures|does not compare with baseline|'
                     r'Failed to load|test failed|Traceback', re.IGNORECASE)


def run_suite(name, script, ok_pattern, expected):
    print(f'::group::{name}', flush=True)
    proc = subprocess.run([sys.executable, str(HERE / script), '-bc', 'all'],
                          capture_output=True, text=True, encoding='utf-8', errors='replace')
    out = proc.stdout + proc.stderr
    (LOGS / f'{name}.log').write_text(out, encoding='utf-8')
    print(out, flush=True)
    print('::endgroup::', flush=True)

    problems = []
    if proc.returncode != 0:
        problems.append(f'exited with status {proc.returncode}')
    failures = [l.strip() for l in out.splitlines() if FAILURE.search(l)]
    if failures:
        problems.append(f'{len(failures)} failure line(s), first: {failures[0][:160]}')
    found = len(re.findall(ok_pattern, out))
    if found != expected:
        problems.append(f'{found} of {expected} expected success lines')
    return problems


def main():
    os.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')
    os.environ.setdefault('MPLBACKEND', 'Agg')
    LOGS.mkdir(exist_ok=True)

    results = [(name, run_suite(name, script, ok, n)) for name, script, ok, n in SUITES]

    print('\n------------------ sanity test summary ------------------')
    for name, problems in results:
        print(f'{name:10s} {"PASS" if not problems else "FAIL: " + "; ".join(problems)}')
    failed = [name for name, problems in results if problems]
    if failed:
        for name in failed:
            print(f'::error title=Sanity tests::{name} failed, see sanity-logs/{name}.log')
        return 1
    print('All sanity suites passed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
