"""
This file is part of pyemaps
___________________________

pyemaps is free software for non-comercial use: you can 
redistribute it and/or modify it under the terms of the GNU General 
Public License as published by the Free Software Foundation, either 
version 3 of the License, or (at your option) any later version.

pyemaps is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pyemaps.  If not, see <https://www.gnu.org/licenses/>.

Contact supprort@emlabsoftware.com for any questions and comments.
___________________________

This sample code is to demostrate using pyemaps to generate and render
kinematic diffraction patterns while changing with sample tilt in 
x direction 

Author:     EMLab Solutions, Inc.
Date:       May 07, 2022    

"""
try:
    from pyemaps import DEF_CBED_DSIZE, DEF_MODE
except ImportError as e:
    print(f'Importing error: {e}')
    exit(1)

from pyemaps import EMC, DPError, DPListError, EMCError, BlochError

MAX_PROCWORKERS = 4

def generate_difs(name = 'Silicon', mode = DEF_MODE, ckey = 'tilt'):
    from pyemaps import DPList
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

    for i in range(-3,3): 

        if ckey == 'tilt':
            emclist.append(EMC(tilt=(i*0.5, 0.0)))
        
        if ckey == 'zone':
            emclist.append(EMC(zone=(0, i, 1)))

        if ckey == 'defl':
            emclist.append(EMC(defl=(i*0.5, 0.0)))

        if ckey == 'vt':
            emclist.append(EMC(vt=200 + i*10))

        if ckey == 'cl':
            emclist.append(EMC(cl=1000 + i*50))

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
            except:
                print('failed to generate diffraction patterns with unknow error')
                exit(1)
            
    return difs
                
def generate_bimages(name = 'Silicon', dsize = 0.16, ckey = 'tilt'):
    import concurrent.futures
    from pyemaps import Crystal as cryst

    cr = cryst.from_builtin(name)
    
    fs=[]
   
    emclist =[] 
    imgs = []

    for i in range(-3,3): 

        if ckey == 'tilt':
            emclist.append(EMC(tilt=(i*0.5, 0.0)))
        
        if ckey == 'zone':
            emclist.append(EMC(zone=(0, i, 1)))

        if ckey == 'defl':
            emclist.append(EMC(defl=(i*0.5, 0.0)))

        if ckey == 'vt':
            emclist.append(EMC(vt=200 + i*10))

        if ckey == 'cl':
            emclist.append(EMC(cl=1000 + i*50))

    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_PROCWORKERS) as e:

        for ec in emclist:
            fs.append(e.submit(cr.generateBloch, disk_size=dsize, em_controls = ec))

        for f in concurrent.futures.as_completed(fs):
            try:
               emc, img = f.result()

            except (BlochError, EMCError, DPListError) as e:
                print(f'{f} generated an exception: {e.message}')
            except:
                print('failed to generate diffraction patterns')    
            imgs.append((emc, img))
    return imgs