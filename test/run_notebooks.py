"""
Execute the pyEMAPS notebooks and check them.

Each notebook in ../notebooks (or the ones named on the command line) runs from start to finish
in a fresh kernel. A notebook fails if a cell raises an error, or if a cell that calls one of
pyEMAPS' plotting functions shows no figure, which would mean plots no longer draw in notebooks.
The notebooks on disk aren't changed.

Needs nbclient and ipykernel in this Python environment, with pyEMAPS installed:

    python run_notebooks.py [--kernel NAME] [--data FOLDER] [notebook.ipynb ...]

--data names a folder of data files to put in each notebook's data folder, so a notebook finds
them instead of downloading them: adf.ipynb downloads adftest900.im3, 472 MB, otherwise. The
4D-STEM notebooks need an activated license.

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

# Calls that must produce a figure in a notebook: pyEMAPS' displays, and matplotlib's own.
PLOT_CALL = re.compile(r'\b(showDif|showBloch|showStereo|plot2Powder|showMatchedDBDP|'
                       r'viewExpImage|indexImage)\(|\bplt\.show\(')


def add_data_files(data, work):
    """Link (or, across drives, copy) each file in the folder *data* into *work*."""
    for name in os.listdir(data):
        source = os.path.join(data, name)
        if os.path.isfile(source):
            try:
                os.link(source, os.path.join(work, name))
            except OSError:
                shutil.copy2(source, work)


def check_notebook(path, kernel, data=None):
    """Run one notebook in a temporary folder; return a list of problems (empty if it passed)."""
    nb = nbformat.read(path, as_version=4)
    with tempfile.TemporaryDirectory() as work:
        # Saved figures go to the temporary folder, not the user's data folder.
        os.environ['PYEMAPS_DATA'] = work
        if data:
            add_data_files(data, work)
        client = nbclient.NotebookClient(nb, timeout=1800, kernel_name=kernel,
                                         resources={'metadata': {'path': work}})
        try:
            client.execute()
        except nbclient.exceptions.CellExecutionError as e:
            return [str(e).splitlines()[-1]]

    problems = []
    for i, cell in enumerate(nb.cells):
        if cell.cell_type != 'code' or not PLOT_CALL.search(cell.source):
            continue
        if not any('image/png' in out.get('data', {}) for out in cell.outputs):
            problems.append(f'cell {i} plots but shows no figure')
    return problems


def main():
    parser = argparse.ArgumentParser(description='Execute and check the pyEMAPS notebooks.')
    parser.add_argument('notebooks', nargs='*', help='notebooks to run (default: all)')
    parser.add_argument('--kernel', default='python3', help='Jupyter kernel to run them with')
    parser.add_argument('--data', help='folder of data files to give the notebooks, such as '
                                       'adftest900.im3, so they are not downloaded again')
    args = parser.parse_args()

    paths = args.notebooks or sorted(
        os.path.join(NOTEBOOKS_DIR, f) for f in os.listdir(NOTEBOOKS_DIR) if f.endswith('.ipynb'))

    failed = 0
    for path in paths:
        start = time.time()
        problems = check_notebook(path, args.kernel, args.data)
        status = 'FAILED' if problems else 'PASSED'
        print(f'{status}  {os.path.basename(path)}  ({time.time() - start:.0f} s)')
        for p in problems:
            print(f'        {p}')
        failed += bool(problems)

    print(f'{len(paths) - failed} of {len(paths)} notebooks passed')
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
