'''
Check that simulations stay correct when one process switches between crystals.

The simulation backend holds one crystal at a time. Each Crystal used to remember that it had
been loaded even after another crystal replaced it in the backend, so its next simulation
skipped loading and used the other crystal's data: Silicon simulated after Germanium gave
Germanium's results.

    python run_crystal_switch.py [-bc all]     # the -bc argument is accepted for ci_sanity.py

Each check simulates a crystal, switches to another, and simulates the first again; the
results must match the first run exactly. Exits 1 if any check fails.
'''
import gc
import os
import sys

import numpy as np

os.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')

from pyemaps import EMC, Crystal          # noqa: E402


def pattern(crystal):
    '''The kinematic pattern at [001], as an array of disk centers and indices.'''
    emc, dp = crystal.generateDP(em_controls=EMC())
    return np.array([[d.c.x, d.c.y, *tuple(d)[3:]] for d in dp.disks])


def powder(crystal):
    return crystal.generatePowder()


def stereo(crystal):
    return np.array([[*p['c'], *p['idx']] for p in crystal.generateStereo()])


def supercell(crystal):
    return str(crystal.generateMxtal())


def same(a, b):
    if isinstance(a, str):
        return a == b
    return a.shape == b.shape and np.array_equal(a, b)


def check_switch(simulate):
    '''Silicon, then Germanium, then Silicon and Germanium again.'''
    si, ge = Crystal.from_builtin('Silicon'), Crystal.from_builtin('Germanium')
    si1, ge1 = simulate(si), simulate(ge)
    si2, ge2 = simulate(si), simulate(ge)
    if same(si1, ge1):
        return False, 'Silicon and Germanium give the same result'
    if not same(si1, si2):
        return False, 'Silicon after Germanium differs from Silicon first'
    if not same(ge1, ge2):
        return False, 'Germanium after Silicon differs from Germanium first'
    return True, 'each crystal gives its own result after switching'


def check_delete():
    '''Deleting a crystal whose data was replaced must not remove the current crystal's.'''
    ge_ref = pattern(Crystal.from_builtin('Germanium'))
    si, ge = Crystal.from_builtin('Silicon'), Crystal.from_builtin('Germanium')
    pattern(si)
    pattern(ge)
    del si
    gc.collect()
    if not same(pattern(ge), ge_ref):
        return False, 'Germanium changed after a replaced Silicon was deleted'
    return True, 'deleting a replaced crystal leaves the current one'


def check_constructor():
    '''The constructor loads a crystal differently; a simulation afterwards must reload it.'''
    si = Crystal.from_builtin('Silicon')
    ref = pattern(si)
    supercell(si)
    if not same(pattern(si), ref):
        return False, 'Silicon pattern changed after building a supercell'
    return True, 'simulation after the constructor matches'


def main():
    checks = [(f'switch: {name}', lambda s=simulate: check_switch(s))
              for name, simulate in (('generateDP', pattern), ('generatePowder', powder),
                                     ('generateStereo', stereo),
                                     ('generateMxtal', supercell))]
    checks += [('delete a replaced crystal', check_delete),
               ('constructor, then simulation', check_constructor)]

    failed = 0
    for name, check in checks:
        ok, msg = check()
        print(f'{"PASS" if ok else "FAIL"}  {name}: {msg}')
        failed += not ok

    if failed:
        print(f'++++++ Crystal switching checks FAILED: {failed} of {len(checks)} +++++++')
        return 1
    print(f'++++++ Crystal switching checks SUCCEEDED: {len(checks)} checks +++++++')
    return 0


if __name__ == '__main__':
    sys.exit(main())
