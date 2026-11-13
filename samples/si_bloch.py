"""
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
Date:       July 07, 2022  

This sample code generates dynamic (Bloch wave) CBED patterns for
Silicon over a series of tilts and a series of zone axes, in parallel
processes, and displays them.

"""

import sys
from pyemaps import EMC, DEF_CBED_DSIZE

MAX_PROCWORKERS = 4
em_keys = ['tilt', 'zone']

def generate_bloch_images(name = 'Silicon', dsize = DEF_CBED_DSIZE, ckey = 'tilt', sim_rand=False):
    '''
    Generates dynamic diffraction patterns with pyEMAPS' bloch module,
    one for each of six values of the microscope control named by ckey.

    : name: crystal name from the built-in database
    : dsize: diffracted beam (disk) size
    : ckey: name of the microscope control to vary: 'tilt' or 'zone'
    : sim_rand: if True, use one set of randomized simulation controls
    :           (SIMC) for all the patterns instead of the defaults
'''
    import concurrent.futures
    from pyemaps import Crystal as cryst
    from pyemaps import BImgList, SIMC

    cr = cryst.from_builtin(name)
    
    fs=[]
   
    emclist =[] 

    if sim_rand:
        sc = SIMC._from_random()
    else:
        sc = SIMC()

    for i in range(-3,3): 
        emc = EMC(cl=200, simc=sc)
        if ckey == 'tilt':
            emc.tilt = (i*0.5, 0.0)

        if ckey == 'zone':
            emc.zone = (0, i, 1)

        emclist.append(emc)

    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_PROCWORKERS) as e:

        for ec in emclist:
            fs.append(e.submit(cr.generateBloch, 
                               disk_size=dsize, 
                               sampling = 20, 
                               sample_thickness=(1750,1750,100),
                               em_controls = ec))
        
        bimgs = BImgList(name) 
        for f in concurrent.futures.as_completed(fs):
            try:
                imgs = f.result()

            except Exception as e:
                print(f'Unable to obtain bloch image(s): {e}') 
                return None
            else: 
                emc, img = imgs[0]
                bimgs.add(emc, img)
   
        # sorting the images by their associated controls
        bimgs.sort()   
        return bimgs

from pyemaps import showBloch

def main():
    for k in em_keys:
        imgs = generate_bloch_images(ckey=k)
        if imgs is not None:
            showBloch(imgs, layout='table', bSave=True, bClose=True)
        else:
            sys.exit(1)

    for k in em_keys:
        imgs = generate_bloch_images(ckey=k, sim_rand=True)
        if imgs is not None:
            showBloch(imgs, bClose=True)
        else:
            sys.exit(1)

if __name__ == '__main__':
    main()
        
