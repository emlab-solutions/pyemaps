
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
Date:       September 26th, 2022

This sample code generates stereodiagrams for Silicon over a series of
tilts and a series of zone axes, in parallel processes, and displays
them with their Miller indices.
"""

import sys
import concurrent.futures
from pyemaps import EMC

MAX_PROCWORKERS = 4

def getStereo(cn, emc, ckey='tilt'):
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
    Generates stereodiagrams with pyEMAPS' stereo module, one for each
    of six values of the microscope control named by ckey.

    : name: crystal name from the built-in database
    : ckey: name of the microscope control to vary: 'tilt' or 'zone'

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
                sys.exit(1)
            else:
                slist.append((emc, stereo))  
                    
    #  sorting the list by controls
    slist.sort(key=lambda x: x[0])

    return slist


def main():
    from pyemaps import showStereo

    # display in table format
    stereoList = generate_stereo(ckey='tilt')
    showStereo(stereoList, 
               name='Silicon', 
               layout='table',
               iShow=True,
               bClose=True, 
               zLimit = 1)

    # display each stereodiagram in its own window
    stereoList = generate_stereo(ckey='zone')
    showStereo(stereoList, 
               name='Silicon',
               iShow=True,
               bClose=True, 
               zLimit = 1)


if __name__ == '__main__':
    main()
