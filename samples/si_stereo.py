
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

import concurrent.futures
from re import S
from pyemaps import EMC, DPError,EMCError

MAX_PROCWORKERS = 4

def getStereo(cn, emc = EMC(), ckey='tilt'):
    from pyemaps import Crystal as cr
    
    if cn is None:
        return None
    
    cc = cr.from_builtin(cn)
    
    if ckey is None:
        stereo = cc.generateStereo()
        return cn, emc, stereo

    if ckey == 'tilt':
        stereo = cc.generateStereo(tilt = emc.tilt) 
        return cn, emc, stereo
    elif (ckey == 'zone'): 
        stereo = cc.generateStereo(zone = emc.zone)
        return cn, emc, stereo
    else:
        return None


def generate_stereo(name = 'Silicon', ckey = 'tilt'):
    '''
    This routine demonstrate how to use pyemaps stereo module 
    to generate stereodiagram
    
    : name: crystal name from builtin database
    : ckey: emcontrol key name to change
    
    '''
    
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
            fs.append(e.submit(getStereo, cn = name, emc = ec, ckey = ckey))

        for f in concurrent.futures.as_completed(fs):
            try:
                _, emc, stereo = f.result()               
            except Exception as e:
                print('failed to generate stereodiagram with ' + str(e))
                exit(1)
            else:
                slist.append((emc, stereo))
                # print(f' successfully generated stereodiagram')    
                    
    #  sorting the list by controls
    slist.sort(key=lambda x: x[0])

    return slist

if __name__ == '__main__':
    from pyemaps import showStereo

    # display in table format
    stereoList = generate_stereo(ckey='tilt')
    showStereo(stereoList, 
               name='Silicon', 
               layout='table',
               iShow=True, 
               zLimit = 1)

    # display in individual syereodiagram
    stereoList = generate_stereo(ckey='zone')
    showStereo(stereoList, 
               name='Silicon',
               iShow=True, 
               zLimit = 1)       