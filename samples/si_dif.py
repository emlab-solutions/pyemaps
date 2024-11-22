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

Contact supprort@emlabsoftware.com for any questions and comments.
___________________________

Author:     EMLab Solutions, Inc.
Date:       May 11, 2022    


This sample code is to render kinematic diffraction patterns generated
by pyemaps by changing zone axis
'''
try:
    from pyemaps import DEF_CBED_DSIZE, DEF_MODE
except ImportError as e:
    print(f'pyEmaps importing error: {e}')
    exit(1)

from pyemaps import EMC, DPError,EMCError

MAX_PROCWORKERS = 4

def generate_difs(name = 'Silicon', mode = DEF_MODE, ckey = 'tilt', sim_rand=False):
    '''
    This routine demonstrate how to use pyemaps dif module to generate kinematic diffraction paterns
    
    : name: crystal name from builtin database
    : dsize: diffracted beams size
    : ckey: emcontrol key name
    : sim_rand: randomized simulation control which is added to EMControl class, these controls
    :           are not changed much (default values if not set). But if changes are needed, then they 
    :           are also set from within EMControl class
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
                exit(1)
            except Exception as e:
                print('failed to generate diffraction patterns with  ' + str(e))
                exit(1)

    # sort the diffraction patern list by controls
    difs.sort()       

    return difs

if __name__ == '__main__':
    
    from pyemaps import showDif

    em_keys = ['tilt', 'zone', 'defl', 'vt', 'cl']
    
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