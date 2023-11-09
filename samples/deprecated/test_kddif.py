
from pyemaps import EMC, DEF_CBED_DSIZE, DEF_MODE

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
    else:
        sc = SIMC()

    for i in [-1,1]: 
        emc=EMC(cl=200)
        if ckey == 'tilt':
           emc.tilt=(i*0.5, 0.0)
        
        if ckey == 'zone':
            emc.zone=(0, i, 1)

        if sim_rand:
            emc.simc = sc

        emc(simc=sc)
        emclist.append(emc)
        

    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_PROCWORKERS) as e:

        for ec in emclist:
            print(f"emcontrol: {ec}")
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
    

def generate_difs(name = 'Silicon', mode = DEF_MODE, ckey = 'tilt', sim_rand=False):
    '''
    This routine demonstrate how to use pyemaps dif module to generate kinematic diffraction paterns
    
    : name: crystal name from builtin database
    : dsize: diffracted beams size
    : ckey: emcontrol key name
    : sim_rand: randomized simulation control which is added to EMControl class, these controls
    :           are not changed much (default values if not set). But if changes are needed, then they 
    :           are also set from within EMControl class
    '''
    from pyemaps import DPList, SIMC
    import concurrent.futures
    from pyemaps import Crystal as cryst
    from pyemaps import EMC, DPError,EMCError


    cr = cryst.from_builtin(name)

    if mode == 2:
        dsize = DEF_CBED_DSIZE
    else:
        dsize = None
    
    fs=[]
    # create an empty diffraction pattern list
    difs = DPList(name, mode = mode)

    emclist =[] 

    if sim_rand:
        sc = SIMC._from_random()

    for i in [-1,1]: 
        emc = EMC()
        if ckey == 'tilt':
            emc.tilt = (i*0.5, 0.0)
        
        if ckey == 'zone':
            emc.zone= (0, i, 1)

        if ckey == 'defl':
            emc.defl= (i*0.5, 0.0)

        if ckey == 'vt':
            emc.vt= 200 + i*10

        if ckey == 'cl':
            emc.cl= 1000 + i*50

        if sim_rand:
            emc.simc = sc

        emclist.append(emc)

    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_PROCWORKERS) as e:

        for ec in emclist:
            print(f"controls: {ec}")
            fs.append(e.submit(cr.generateDP, mode=mode,  dsize=dsize, em_controls = ec))

        for f in concurrent.futures.as_completed(fs):
            try:
                emc, diffP = f.result()
                difs.add(emc, diffP)
                
            except (DPError, EMCError) as e:
                print(f'{f} generated an exception: {e.message}')
                exit(1)
            except Exception as e:
                print('failed to generate diffraction patterns with  ' + str(e))
                exit(1)

    # sort the diffraction patern list by controls
    difs.sort()       

    return difs

from pyemaps import showBloch
from pyemaps import showDif

if __name__ == '__main__':
    
    em_keys = ['zone']
    
#     for k in em_keys:
#         imgs = generate_bloch_images(ckey=k)
#         if imgs is not None:
#             showBloch(imgs, bSave=True, bClose=True)
#         else:
#             exit(1)

    for k in em_keys:
        dpl = generate_difs(ckey=k, mode=2)
        showDif(dpl, 
                layout='table' if k == 'tilt' or k == 'zone' else 'individual', 
                kShow=False, 
                iShow=True,
                bClose=False
                )

#     for k in em_keys:
#         imgs = generate_bloch_images(ckey=k, sim_rand=True)
#         if imgs is not None:
#             showBloch(imgs, bClose=True)
#         else:
#             exit(1)
        
