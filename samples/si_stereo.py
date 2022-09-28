
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

```

Author:     EMLab Solutions, Inc.
Date:       September 26th, 2022    
"""
# try:
#     from pyemaps import DEF_CBED_DSIZE, DEF_MODE
# except ImportError as e:
#     print(f'Importing error: {e}')
#     exit(1)

from pyemaps import EMC, DPError,EMCError

MAX_PROCWORKERS = 4

def getStereo(cr=None, emc = EMC(), ckey='tilt'):
    from pyemaps import Crystal

    if not cr or not isinstance(cr, Crystal):
        raise CrystalClassError
    
    stereo = cr.generateStereo(tilt = emc.tilt) if (ckey == 'tilt') else cr.generateStereo(zone = emc.zone)

    return emc, stereo


def generate_stereo(name = 'Silicon', ckey = 'tilt'):
    '''
    This routine demonstrate how to use pyemaps dif module to generate kinematic diffraction paterns
    : name: crystal name from builtin database
    : dsize: diffracted beams size
    : ckey: emcontrol key name
    : sim_rand: randomized simulation control which is added to EMControl class, these controls
    :           are not changed much (default values if not set). But if changes are needed, then they 
    :           are also set from within EMControl class
    '''
    # from pyemaps import DPList, SIMC
    import concurrent.futures
    from pyemaps import Crystal as cryst

    cr = cryst.from_builtin(name)

    # create an EM control object based on the key input "ckey"
    emclist = []
    for i in range(-3,3): 
        
        if ckey == 'tilt':
            emclist.append(EMC(tilt=(i*0.5, 0.0)))
  
        if ckey == 'zone':
            emclist.append(EMC(zone=(i,-i,1)))

    
    fs = []
    slist=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_PROCWORKERS) as e:
        
        for ec in emclist:
            fs.append(e.submit(getStereo, cr = cr, emc = ec, ckey = ckey))

        for f in concurrent.futures.as_completed(fs):
            try:
                emc, stereo = f.result()               
            except Exception as e:
                msg = str(f'message: {e}')
                print('failed to generate stereodiagram with '+msg)
                exit(1)
            else:
                slist.append((emc, stereo))
                # print(f' successfully generated stereodiagram')        
    
    return slist

if __name__ == '__main__':
    from pyemaps import showStereo
    em_keys = ['tilt', 'zone']
    for k in em_keys:
        stereoList = generate_stereo(ckey=k)
        showStereo(stereoList, name='Silicon', iShow=True, zLimit = 1, bSave=True)
        