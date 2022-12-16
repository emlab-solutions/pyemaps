from pyemaps import Crystal as cr
si=cr.from_builtin('Silicon')
from pyemaps import EMC, SIMC, showBloch
def test_local():

    emc=EMC(zone=(1,1,1), vt=100, tilt=(20.0,25), simc=SIMC(excitation=(0.3,1.0)))
    _, _=si.beginBloch_new(aperture=1.0,sampling = 40, omega=10,em_controls=emc)
    bimgs = si.getBlochImages(sample_thickness=(500,1750,250))
    si.endBloch()
    showBloch(bimgs)

    emc=EMC(vt=100, 
            # cl=2000,
            tilt=(-0.7,15.0),
            simc=SIMC(excitation=(0.3,1.0)))
    # showBloch(bimgs)
    bimgs = si.generateBloch(sample_thickness=(500,1750,250), 
                            sampling=40, 
                             pix_size=100, 
                            em_controls=emc )

    showBloch(bimgs)

    emc=EMC(vt=100, 
            cl=3000,
            tilt=(30,0.1),
            simc=SIMC(excitation=(0.3,1.0)))
    # showBloch(bimgs)
    bimgs = si.generateBloch(sample_thickness=(500,1750,250), 
                            sampling=40, 
                             pix_size=100, 
                            em_controls=emc )

    showBloch(bimgs)




if __name__ == '__main__':
    test_local()