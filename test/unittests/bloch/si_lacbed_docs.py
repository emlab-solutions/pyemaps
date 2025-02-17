from pyemaps import EMC, DEF_CBED_DSIZE

MAX_PROCWORKERS = 4

def generate_lacbed_images(name = 'Silicon', bSave=True):
    
    from pyemaps import Crystal as cryst
    from pyemaps import SIMC
    from pyemaps import TY_LACBED

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
                                det_size = 218,
                                sample_thickness = sth,
                                nType = TY_LACBED,
                                bSave = bSave
                                )
    except Exception as e:
            print(f'Generated an exception: {e}') 
            return None
            
    bimgs.sort()
    return bimgs 

def main():
    from pyemaps import showBloch
    imgs = generate_lacbed_images()
    showBloch(imgs, bClose=True)

if __name__ == '__main__':
    
    main()