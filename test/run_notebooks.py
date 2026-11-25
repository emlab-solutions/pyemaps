r"""
Execute the pyEMAPS notebooks and check them.

Each notebook in ../notebooks (or the ones named on the command line) runs from start to finish
in a fresh kernel. A notebook fails if a cell raises an error, or if a cell that calls one of
pyEMAPS' plotting functions shows no figure, which would mean plots no longer draw in notebooks.
The notebooks on disk aren't changed, unless --save is given.

Needs nbclient and ipykernel in this Python environment, with pyEMAPS installed:

    python run_notebooks.py [--kernel NAME] [--data FOLDER] [--save [--save-dir FOLDER]]
                            [notebook.ipynb ...]

--data names a folder of data files to put in each notebook's data folder, so a notebook finds
them instead of downloading them: adf.ipynb downloads adftest900.im3, 472 MB, otherwise. The
4D-STEM notebooks need an activated license.

--save writes each notebook that passes back to its file, with its new outputs, so the
repository and the docs show results from the installed pyEMAPS: after a release, run it with the
released packages. The notebooks run from the --save-dir folder (default C:\pyemaps_data), so
the file names they print show that folder and nothing of the user's own; a notebook whose
outputs mention the home folder isn't saved. The folder is removed afterwards if it didn't exist
before. The notebooks' kernel settings are kept.

Exits with status 1 if any notebook fails.
"""
import argparse
import os
import re
import shutil
import sys
import tempfile
import time

import nbclient
import nbformat

NOTEBOOKS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'notebooks')

# Calls that must produce a figure in a notebook: pyEMAPS' displays, including
# OrientationMap.show, and matplotlib's own plt.show.
PLOT_CALL = re.compile(r'\b(showDif|showBloch|showStereo|plot2Powder|showMatchedDBDP|'
                       r'viewExpImage|indexImage)\(|\.show\(')


def add_data_files(data, work):
    """Link (or, across drives, copy) each file in the folder *data* into *work*. With --save,
    every notebook runs in the same folder, so a file linked for an earlier one is kept."""
    for name in os.listdir(data):
        source, target = os.path.join(data, name), os.path.join(work, name)
        if not os.path.isfile(source):
            continue
        if os.path.exists(target) and os.path.samefile(source, target):
            continue
        try:
            os.link(source, target)
        except OSError:
            shutil.copy2(source, target)


def execute(nb, kernel, work, data=None):
    """Run *nb* with *work* as its data and working folder; return a problem, or None."""
    # Saved figures go to that folder, not the user's data folder.
    os.environ['PYEMAPS_DATA'] = work
    if data:
        add_data_files(data, work)
    client = nbclient.NotebookClient(nb, timeout=1800, kernel_name=kernel,
                                     resources={'metadata': {'path': work}})
    try:
        client.execute()
    except nbclient.exceptions.CellExecutionError as e:
        return str(e).splitlines()[-1]
    return None


def mentions_home(nb):
    """Whether any output of *nb* mentions the user's home folder."""
    home = os.path.expanduser('~')
    # as Windows writes it, with forward slashes, and escaped as in a Python string's repr
    forms = {home, home.replace('\\', '/'), home.replace('\\', '\\\\')}
    for cell in nb.cells:
        for out in cell.get('outputs', []):
            text = ''.join(out.get('text', '')) + str(out.get('data', {}).get('text/plain', ''))
            if any(f in text for f in forms):
                return True
    return False


def check_notebook(path, kernel, data=None, save_dir=None):
    """Run one notebook; return a list of problems (empty if it passed). With *save_dir*, it
    runs there and, if it passed, is written back to *path*."""
    nb = nbformat.read(path, as_version=4)
    metadata = dict(nb.metadata)
    if save_dir:
        problem = execute(nb, kernel, save_dir, data)
    else:
        with tempfile.TemporaryDirectory() as work:
            problem = execute(nb, kernel, work, data)
    if problem:
        return [problem]

    problems = []
    for i, cell in enumerate(nb.cells):
        if cell.cell_type != 'code' or not PLOT_CALL.search(cell.source):
            continue
        if not any('image/png' in out.get('data', {}) for out in cell.outputs):
            problems.append(f'cell {i} plots but shows no figure')
    if save_dir and not problems:
        if mentions_home(nb):
            problems.append('an output mentions the home folder; not saved')
        else:
            nb.metadata = metadata
            nbformat.write(nb, path)
    return problems


def main():
    parser = argparse.ArgumentParser(description='Execute and check the pyEMAPS notebooks.')
    parser.add_argument('notebooks', nargs='*', help='notebooks to run (default: all)')
    parser.add_argument('--kernel', default='python3', help='Jupyter kernel to run them with')
    parser.add_argument('--data', help='folder of data files to give the notebooks, such as '
                                       'adftest900.im3, so they are not downloaded again')
    parser.add_argument('--save', action='store_true',
                        help='save the notebooks that pass, with their new outputs')
    parser.add_argument('--save-dir', default=r'C:\pyemaps_data', metavar='FOLDER',
                        help='with --save, the folder the notebooks run from '
                             '(default C:\\pyemaps_data)')
    args = parser.parse_args()

    save_dir, made = None, False
    if args.save:
        save_dir = os.path.abspath(args.save_dir)
        made = not os.path.exists(save_dir)
        os.makedirs(save_dir, exist_ok=True)

    paths = args.notebooks or sorted(
        os.path.join(NOTEBOOKS_DIR, f) for f in os.listdir(NOTEBOOKS_DIR) if f.endswith('.ipynb'))

    failed = 0
    try:
        for path in paths:
            start = time.time()
            problems = check_notebook(path, args.kernel, args.data, save_dir)
            status = 'FAILED' if problems else ('SAVED ' if save_dir else 'PASSED')
            print(f'{status}  {os.path.basename(path)}  ({time.time() - start:.0f} s)')
            for p in problems:
                print(f'        {p}')
            failed += bool(problems)
    finally:
        # also after an error, so a folder this run made isn't left behind
        if made:
            shutil.rmtree(save_dir, ignore_errors=True)

    print(f'{len(paths) - failed} of {len(paths)} notebooks passed'
          + (' and were saved' if save_dir else ''))
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
