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
dynamic diffraction patterns while controls. 

Author:     EMLab Solutions, Inc.
Date:       July 07, 2022    

"""

from pyemaps import EMC, EMCError, BlochError, DEF_CBED_DSIZE

MAX_PROCWORKERS = 4

def generate_bloch_images(name = 'Silicon', dsize = DEF_CBED_DSIZE, ckey = 'tilt', sim_rand=False):
    '''
    This routine demonstrate how to use pyemaps bloch module to generate dynamic diffraction paterns
    : name: crystal name from builtin database
    : dsize: diffracted beams size
    : ckey: emcontrol key name
    : sim_rand: randomized simulation control which is added to EMControl class, these controls
    :           are not changed much (default values if not set). But if changes are needed, then they 
    :           are also set from within EMControl class
    '''
    import concurrent.futures
    from pyemaps import Crystal as cryst
    from pyemaps import BImgList, SIMC

    cr = cryst.from_builtin(name)
    
    fs=[]
   
    emclist =[] 

    if sim_rand:
        sc = SIMC._from_random()

    for i in range(-3,3): 
        emc=EMC()
        if ckey == 'tilt':
           emc.tilt=(i*0.5, 0.0)
        
        if ckey == 'zone':
            emc.zone=(0, i, 1)

        if sim_rand:
            emc.simc = sc

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
               emc, img = f.result()[0]

            except (BlochError, EMCError) as e:
                print(f'{f} generated an exception: {e.message}, {emc}') 
                return bimgs
            except Exception as e:
                print(f'failed to generate diffraction patterns: {e}') 
                return bimgs
            else: 
                bimgs.add(emc, img) 
    # sorting the images by theri associated controls
    bimgs.sort()   
    return bimgs

from pyemaps import showBloch

if __name__ == '__main__':
    
    # from sample_base import generate_bimages
    em_keys = ['tilt', 'zone']
    
    for k in em_keys:
        imgs = generate_bloch_images(ckey=k)
        showBloch(imgs, layout='table')

    for k in em_keys:
        imgs = generate_bloch_images(ckey=k, sim_rand=True)
        showBloch(imgs)
