import numpy as np
# import DigitalMicrograph as DM

from pyemaps import Crystal as cr
      
def run_si_dm_bloch():  
    from pyemaps import EMC
    #-----------load crystal data into a Crystal class object-----------------
    name = 'ErbiumPyrogermanate'
    ep = cr.from_builtin(name)

    #-----------content of the crystal data-----------------------------------
    print(ep)
    
    #-----------generate diffraction pattern in CBED mode--------------------- 
    emc = EMC(tilt=(-0.2, 0.5))
    
    try:
        _ = ep.generateBloch(em_controls=emc, bSave=True)

    except Exception as e:
        print(f'Error running dynamic diffraction simuation for {name}')
    #-----------Plot the pattern in DM----------------------------------------
    import os
    imgpath = os.environ.get('PYEMAPS_DATA')
    imgf = os.path.join(imgpath, 'bloch')

    print(f'Generate image file is located at: {imgf}')
    #-----------content of the crystal data-----------------------------------
    # show_diffract(si_dp, name = name)

if __name__ == '__main__':
    run_si_dm_bloch()
