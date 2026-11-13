'''
This file is part of pyemaps
___________________________

pyemaps is free software. You can redistribute it and/or modify 
it under the terms of the GNU General Public License as published 
by the Free Software Foundation, either version 3 of the License, 
or (at your option) any later version.

pyemaps is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pyemaps.  If not, see <https://www.gnu.org/licenses/>.

Contact support@emlabsoftware.com for any questions and comments.
___________________________

Author:     EMLab Solutions, Inc.
Date:       May 11, 2022    


This sample code generates kinematic diffraction patterns for Silicon
while varying one microscope control at a time (tilt, zone axis,
deflection, high voltage or camera length), in parallel processes, and
displays them.
'''
import sys

try:
    from pyemaps import DEF_CBED_DSIZE, DEF_MODE
except ImportError as e:
    print(f'pyEMAPS importing error: {e}')
    sys.exit(1)

from pyemaps import EMC, DPError, EMCError

MAX_PROCWORKERS = 4
em_keys = ['tilt', 'zone', 'defl', 'vt', 'cl']

def generate_difs(name = 'Silicon', mode = DEF_MODE, ckey = 'tilt', sim_rand=False):
    '''
    Generates kinematic diffraction patterns with pyEMAPS' dif module,
    one for each of six values of the microscope control named by ckey.

    : name: crystal name from the built-in database
    : mode: diffraction mode, 1 for normal and 2 for CBED
    : ckey: name of the microscope control to vary: 'tilt', 'zone',
    :       'defl', 'vt' or 'cl'
    : sim_rand: if True, use one set of randomized simulation controls
    :           (SIMC) for all the patterns instead of the defaults
'''
    from pyemaps import DPList, SIMC
    import concurrent.futures
    from pyemaps import Crystal as cryst

    cr = cryst.from_builtin(name)

    if mode == 2:
        dsize = DEF_CBED_DSIZE
    else:
        dsize = None
    
    fs=[]
    # create an empty diffraction pattern list
    difs = DPList(name, mode = mode)

    emclist =[] 

    if sim_rand:
        sc = SIMC._from_random()

    for i in range(-3,3): 
        emc = EMC()
        if ckey == 'tilt':
            emc.tilt = (i*0.5, 0.0)
        
        if ckey == 'zone':
            emc.zone= (0, i, 1)

        if ckey == 'defl':
            emc.defl= (i*0.5, 0.0)

        if ckey == 'vt':
            emc.vt= 200 + i*10

        if ckey == 'cl':
            emc.cl= 1000 + i*50

        if sim_rand:
            emc.simc = sc

        emclist.append(emc)

    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_PROCWORKERS) as e:

        for ec in emclist:
            fs.append(e.submit(cr.generateDP, mode=mode,  dsize=dsize, em_controls = ec))

        for f in concurrent.futures.as_completed(fs):
            try:
                emc, diffP = f.result()
                difs.add(emc, diffP)
                
            except (DPError, EMCError) as e:
                print(f'{f} generated an exception: {e.message}')
                sys.exit(1)
            except Exception as e:
                print('failed to generate diffraction patterns with ' + str(e))
                sys.exit(1)

    # sort the diffraction pattern list by controls
    difs.sort()       

    return difs

def main():
    
    from pyemaps import showDif
    
    for k in em_keys:
        dpl = generate_difs(ckey=k, mode=2)
        showDif(dpl, 
                layout='table' if k == 'tilt' or k == 'zone' else 'individual', 
                kShow=False, 
                iShow=False, 
                bSave=(k=='zone'),
                bClose=True
                )

    for k in em_keys:
        dpl = generate_difs(ckey=k, sim_rand=True)
        showDif(dpl, bClose=True)

if __name__ == '__main__':
    main()
