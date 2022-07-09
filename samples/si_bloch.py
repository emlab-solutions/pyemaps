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
Date:       July 07, 2022    

"""

from pyemaps import EMC, EMCError, BlochError

MAX_PROCWORKERS = 4

def generate_bloch_images(name = 'Silicon', dsize = 0.16, ckey = 'tilt'):
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
            fs.append(e.submit(cr.generateBloch, disk_size=dsize, sampling = 20, em_controls = ec))

        for f in concurrent.futures.as_completed(fs):
            try:
               emc, img = f.result()

            except (BlochError, EMCError) as e:
                print(f'{f} generated an exception: {e.message}')
            except:
                print('failed to generate diffraction patterns')    
            imgs.append((emc, img))
    return imgs

from pyemaps import showBloch

def run_bloch_tests():
    # from sample_base import generate_bimages
    em_keys = ['tilt', 'zone', 'defl', 'vt', 'cl']
    for k in em_keys:
        imgs = generate_bloch_images(ckey=k)
        showBloch(imgs)

if __name__ == '__main__':
    
    run_bloch_tests()
