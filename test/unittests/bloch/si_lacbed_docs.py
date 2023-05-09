from pyemaps import EMC, DEF_CBED_DSIZE

MAX_PROCWORKERS = 4

def generate_lacbed_images(name = 'Silicon', dsize = DEF_CBED_DSIZE, ckey = 'tilt'):
    
    from pyemaps import Crystal as cryst
    from pyemaps import SIMC
    TY_LACBED = 1 

    cr = cryst.from_builtin(name)
    
    vt = 100
    sth = (500, 1750, 250)
    simc = SIMC(excitation=(0.3,1.0), bmin=0.1)

    try:
        bimgs = cr.generateBloch(sampling = 40,
                                em_controls = EMC(zone=(1,1,1),
                                vt=vt,
                                cl=1000,
                                simc=simc),
                                sample_thickness = sth,
                                nType = TY_LACBED,
                                bSave = True
                                )
    except Exception as e:
            print(f'Generated an exception: {e}') 
            return None
            
    bimgs.sort()
    return bimgs 

if __name__ == '__main__':
    
    from pyemaps import showBloch

    imgs = generate_lacbed_images()
    if imgs is not None:
        showBloch(imgs, cShow=True, layout='table', bSave = True, bClose=True)