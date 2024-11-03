
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

def stereo_run_thru_builtin():
    from pyemaps import Crystal as cr
    from pyemaps import showStereo

    lcrystals = cr.list_all_builtin_crystals()

    fs = []
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_PROCWORKERS) as e:
        
        for c in lcrystals:
            fs.append(e.submit(getStereo, cn = c, emc = EMC(), ckey = None))

        for f in concurrent.futures.as_completed(fs):
            try:
                name, ec, stereo = f.result()               
            except Exception as e:
                print('failed to generate stereodiagram with ' + str(e))
            else:
                showStereo([(ec,stereo)], name=name, iShow=True, zLimit = 1)
         

if __name__ == '__main__':
    from pyemaps import showStereo

    stereo_run_thru_builtin()
    