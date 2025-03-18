from pyemaps import EMC, DEF_CBED_DSIZE

MAX_PROCWORKERS = 4

def generate_bloch_images(name = 'Silicon', dsize = DEF_CBED_DSIZE, ckey = 'tilt', bSave=True):
    
    from pyemaps import Crystal as cryst
    from pyemaps import SIMC
    import time
    tic = time.time()

    cr = cryst.from_builtin(name)
    
    vt = 100
    sth = (500, 1750, 250)
    simc = SIMC(excitation=(0.3,1.0), bmin=0.1)

    try:
        bimgs = cr.generateBloch(sampling = 10,
                                em_controls = EMC(zone=(1,1,1),
                                vt=vt,
                                cl=1000,
                                simc=simc),
                                sample_thickness = sth,
                                bSave = bSave
                                )
    except Exception as e:
            print(f'Generated an exception: {e}') 
            return None
            
    bimgs.sort()
    # imgs = generate_bloch_images(name = 'SiAlONa')

    toc = time.time()
    
    print(f"Bloch simulation on {cr.name} takes: {toc-tic} seconds")
    return bimgs 
def main():
     
    from pyemaps import showBloch
    
    imgs = generate_bloch_images(name = 'BiMnO3')
    if imgs is not None:
        showBloch(imgs, cShow=True, layout='table', bSave = False, bClose=False)
    else:
        print('Invalid image!')

if __name__ == '__main__':
    
    main()