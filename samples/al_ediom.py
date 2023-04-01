
import os
from pathlib import Path
from pyemaps import Crystal as cr
from pyemaps import EMC

current_file = Path(os.path.abspath(__file__))
samples_path = current_file.parent.absolute()

def getDBFile():
    return os.path.join(samples_path, "al_db.bin")

def getDPImageFn():
    return os.path.join(samples_path, 'al.img')

def test_dp_indexing(cname = 'Aluminium'):
    from pyemaps import Crystal as cr
    from pyemaps import ediom
    import numpy as np
   
    cryst = cr.from_builtin(cname)

    # ------------load existing DP database from file-----------------
    # dbfn = getDBFile()

    # or 
        # ------------generate a new DP database file --------------

        #  first generate a DP database file
    xa0=(2,0,0)
    res = 200
    ret, dbfn = cryst.generateDPDB(emc=EMC(zone=(0,0,1)), res = res, xa = xa0)

    if ret != 0:
        print(f'failed to generate a dp databaes')
        return -1


    ret, mr, mc =cryst.loadDPDB(dbfn = dbfn, bShowDBMap=True)
    
    if ret != 0 or mr <= 0 or mc <=0:
        print(f"Error loading DP database from file {dbfn} into ediom module")
        cryst.release_ediom()
        exit(1)

    xifn = getDPImageFn()
    try:
       cryst.importSHExpImage(xifn, bShow=True)
    except Exception as e:
        cryst.release_ediom()
        raise ValueError from e

    # DPs or peaks search and indexing parameters 
    
    cryst.indexExpDP(cc                 = 29.0,                 # Camera constant
                     sigma              = 3.0,                  # Peak width measurement
                     img_center         = (99.923, 99.919),     # Image or DP image center location
                     rmin               = 10,                   
                     search_box         = 10.0,
                     scaling_option     = (1,2), 
                     filter_threshold   = 0.0,
                     peak_threshold     = 0.8)
    
    # display diffractiom pattern in the database that best match the image pattern
    cryst.showMatchedDBDP()

    # show stereo projection location that corresponds to the matched diffraction pattern
    cryst.showHeatMap(mr, mc)

    # print match diffraction details
    cryst.printDetails()

    # release edio module memory.
    cryst.release_ediom()


if __name__ == '__main__':
    
    test_dp_indexing()
    