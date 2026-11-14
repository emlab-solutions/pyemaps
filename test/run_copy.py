"""
Check pyemaps -cp, which copies the sample scripts and the notebooks into the current folder.

Each case runs the installed pyemaps command in a fresh temporary folder and checks what lands
where:

- pyemaps -cp copies both sets, -cp samples and -cp notebooks one each;
- the notebooks are copied without their outputs;
- copying again doesn't overwrite a file that's already there;
- answering n copies nothing, and an unknown choice is an error.

Run it after installing the pyEMAPS wheel:

    python run_copy.py

Exits with status 1 if any case fails.
"""
import json
import os
import subprocess
import sys
import tempfile

from importlib.util import find_spec

PKG_DIR = os.path.dirname(find_spec('pyemaps').origin)
SAMPLES = sorted(f for f in os.listdir(os.path.join(PKG_DIR, 'samples'))
                 if os.path.isfile(os.path.join(PKG_DIR, 'samples', f)) and f != 'si_pyemaps.py')
NOTEBOOKS = sorted(f for f in os.listdir(os.path.join(PKG_DIR, 'notebooks'))
                   if f.endswith('.ipynb'))

FOLDERS = {'samples': ('pyemaps_samples', SAMPLES),
           'notebooks': ('pyemaps_notebooks', NOTEBOOKS)}


def run_copy(work, args, answer='y'):
    """Run pyemaps -cp *args* in *work*, answering its question; return (status, output)."""
    p = subprocess.run([sys.executable, '-m', 'pyemaps', '-cp', *args], cwd=work,
                       input=answer + '\n', capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def check_copied(work, wanted):
    """Problems with the folders in *work*, when the sets in *wanted* should have been copied."""
    problems = []
    for name, (folder, files) in FOLDERS.items():
        path = os.path.join(work, folder)
        if name not in wanted:
            if os.path.exists(path):
                problems.append(f'{folder} was created')
            continue
        got = sorted(os.listdir(path)) if os.path.isdir(path) else []
        if got != files:
            problems.append(f'{folder} has {got}, expected {files}')
    return problems


def case_copy(args, wanted):
    with tempfile.TemporaryDirectory() as work:
        status, out = run_copy(work, args)
        problems = [f'exit status {status}'] if status else []
        return problems + check_copied(work, wanted), out


def case_no_outputs():
    with tempfile.TemporaryDirectory() as work:
        status, out = run_copy(work, ['notebooks'])
        problems = [f'exit status {status}'] if status else []
        for f in NOTEBOOKS:
            with open(os.path.join(work, 'pyemaps_notebooks', f), encoding='utf-8') as fp:
                nb = json.load(fp)
            if any(c.get('outputs') for c in nb['cells'] if c['cell_type'] == 'code'):
                problems.append(f'{f} has outputs')
        return problems, out


def case_no_overwrite():
    with tempfile.TemporaryDirectory() as work:
        run_copy(work, [])
        edited = [os.path.join(work, 'pyemaps_samples', SAMPLES[0]),
                  os.path.join(work, 'pyemaps_notebooks', NOTEBOOKS[0])]
        for path in edited:
            with open(path, 'a', encoding='utf-8') as fp:
                fp.write('\nedited')
        status, out = run_copy(work, [])
        problems = [f'exit status {status}'] if status else []
        for path in edited:
            with open(path, encoding='utf-8') as fp:
                if not fp.read().endswith('\nedited'):
                    problems.append(f'{os.path.basename(path)} was overwritten')
        if out.count('Skipped') != 2:
            problems.append('the skipped files are not reported')
        return problems, out


def case_declined():
    with tempfile.TemporaryDirectory() as work:
        status, out = run_copy(work, [], answer='n')
        problems = [] if status == 1 else [f'exit status {status}, expected 1']
        return problems + check_copied(work, ()), out


def case_unknown():
    with tempfile.TemporaryDirectory() as work:
        status, out = run_copy(work, ['examples'])
        problems = [] if status == 2 else [f'exit status {status}, expected 2']
        return problems + check_copied(work, ()), out


def case_old_name():
    with tempfile.TemporaryDirectory() as work:
        p = subprocess.run([sys.executable, '-m', 'pyemaps', '--copysamples', 'samples'],
                           cwd=work, input='y\n', capture_output=True, text=True)
        problems = [f'exit status {p.returncode}'] if p.returncode else []
        return problems + check_copied(work, ('samples',)), p.stdout + p.stderr


CASES = [
    ('pyemaps -cp copies both', lambda: case_copy([], ('samples', 'notebooks'))),
    ('pyemaps -cp samples', lambda: case_copy(['samples'], ('samples',))),
    ('pyemaps -cp notebooks', lambda: case_copy(['notebooks'], ('notebooks',))),
    ('notebooks have no outputs', case_no_outputs),
    ('copying again keeps edited files', case_no_overwrite),
    ('answering n copies nothing', case_declined),
    ('an unknown choice is an error', case_unknown),
    ('--copysamples still works', case_old_name),
]


def main():
    if not NOTEBOOKS:
        print('FAILED  the installed pyEMAPS has no notebooks')
        sys.exit(1)

    failed = 0
    for name, case in CASES:
        problems, out = case()
        print(f'{"FAILED" if problems else "PASSED"}  {name}')
        for p in problems:
            print(f'        {p}')
        if problems:
            print('        output:')
            for line in out.splitlines():
                print('          ' + line)
        failed += bool(problems)

    print(f'{len(CASES) - failed} of {len(CASES)} cases passed')
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
