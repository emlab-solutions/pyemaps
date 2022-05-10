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
from pickle import EMPTY_DICT
from pyemaps import DEF_CBED_DSIZE, DEF_MODE
from pyemaps import EMC

# import copy

MAX_PROCWORKERS = 4
def genDP(cr=None, dsize = None, mode = DEF_MODE, em_dict=EMPTY_DICT):

    if not isinstance(em_dict, dict) and len(em_dict) != 1: 
        raise ValueError("Control arguement incorrect")
        # return None, None

    emc = EMC()
    
    for k, v in em_dict.items():
        if k == 'tilt':
            emc.tilt = v

        if k == 'zone':
            emc.zone = v

        if k == 'defl':
            emc.defl = v
        
        if k == 'cl':
            emc.cl = v
            
        if k == 'vt':
            emc.vt = v

    return cr.generateDP(mode=mode, dsize=dsize, em_controls = emc)


def generate_difs(name = 'silicon', mode = DEF_MODE):
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

    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_PROCWORKERS) as e:
        for i in range(-3,3):
            third = dict(tilt = (i*0.5, 0.0))
            fs.append(e.submit(genDP, cr=cr, dsize=dsize, mode=mode, em_dict=third))

        for f in concurrent.futures.as_completed(fs):
            try:
                emc, diffP = f.result()
            except Exception as e:
                print('%r generated an exception: %s' % (f, e))
            else:
                difs.add(emc, diffP) 

    return difs

def generate_difs_defl(name = 'silicon', mode = DEF_MODE):
    from pyemaps import DPList
    from pyemaps import Crystal as cryst
    # from pyemaps import dif 
    
    import concurrent.futures

    cr = cryst.from_builtin(name)

    if mode == 2:
        dsize = DEF_CBED_DSIZE
    else:
        dsize = None

    
    fs=[]
    difs = DPList(cr.name, mode = mode)

    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_PROCWORKERS) as e:
        for i in range(-10,10):
            third = dict(defl = (i*0.5, 0.0))
            fs.append(e.submit(genDP, cr=cr, dsize=dsize, mode=mode, em_dict=third))

        for f in concurrent.futures.as_completed(fs):
            try:
                emc, diffP = f.result()
            except Exception as e:
                print('%r generated an exception: %s' % (f, e))
            else:
                difs.add(emc, diffP) 
    return difs

def generate_difs_zone(name = 'silicon', mode = DEF_MODE):
    from pyemaps import DPList
    from pyemaps import Crystal as cryst
    # from pyemaps import dif 
    
    import concurrent.futures

    cr = cryst.from_builtin(name)

    if mode == 2:
        dsize = DEF_CBED_DSIZE
    else:
        dsize = None

    
    fs=[]
    difs = DPList(cr.name, mode = mode)

    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_PROCWORKERS) as e:
        for i in range(-3,3):
            third = dict(zone = (0, i, 1))
            fs.append(e.submit(genDP, cr=cr, dsize=dsize, mode=mode, em_dict=third))

        for f in concurrent.futures.as_completed(fs):
            try:
                emc, diffP = f.result()
            except Exception as e:
                print('%r generated an exception: %s' % (f, e))
            else:
                difs.add(emc, diffP) 

    return difs

def generate_difs_cl(name = 'silicon', mode = DEF_MODE):
    from pyemaps import DPList
    from pyemaps import Crystal as cryst
    # from pyemaps import dif 
    
    import concurrent.futures

    cr = cryst.from_builtin(name)

    if mode == 2:
        dsize = DEF_CBED_DSIZE
    else:
        dsize = None

    
    fs=[]
    difs = DPList(cr.name, mode = mode)

    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_PROCWORKERS) as e:
        for i in range(-3,3):
            third = dict(cl = 1000 + i*50)
            fs.append(e.submit(genDP, cr=cr, dsize=dsize, mode=mode, em_dict=third))

        for f in concurrent.futures.as_completed(fs):
            try:
                emc, diffP = f.result()
            except Exception as e:
                print('%r generated an exception: %s' % (f, e))
            else:
                difs.add(emc, diffP) 
    return difs

def generate_difs_vt(name = 'silicon', mode = DEF_MODE):
    from pyemaps import DPList
    from pyemaps import Crystal as cryst
    # from pyemaps import dif 
    
    import concurrent.futures

    cr = cryst.from_builtin(name)

    if mode == 2:
        dsize = DEF_CBED_DSIZE
    else:
        dsize = None

    
    fs=[]
    difs = DPList(cr.name, mode = mode)
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_PROCWORKERS) as e:
        for i in range(-3,3):
            third = dict(vt = 200 + i*10)
            fs.append(e.submit(genDP, cr=cr, dsize=dsize, mode=mode, em_dict=third))

        for f in concurrent.futures.as_completed(fs):
            try:
                emc, diffP = f.result()
            except Exception as e:
                print('%r generated an exception: %s' % (f, e))
            else:
                difs.add(emc, diffP) 
    return difs