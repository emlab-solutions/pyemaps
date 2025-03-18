def run_kdiffraction(bShow=True, bSave=True, bPrint=True):

    from pyemaps import Crystal             #----pyemaps crystal module
    from pyemaps import DPList, showDif     #----Helper modules
    
    si = Crystal.from_builtin('Silicon')    #----loading Silicon crystal from builtin database
    emc, si_dp = si.generateDP()            #----generate kinematic diffraction pattern
                                            #----Output:
                                            #----emc: associated microscope and 
                                            #            simulation control object
                                            #----si_dp: diffraction pattern generated
    if bPrint: print(si_dp)                            #----raw representation of kinematic diffraction pattern 

    dpl = DPList('Silcon')                 #----create a diffraction pattern list to hold the results
    dpl.add(emc, si_dp)                     #----can add more if desired

    if bShow:
        showDif(dpl, bClose=True, bSave=bSave)   
        
    return dpl           #----visual representation of diffraction pattern

def run_kdiff(name = 'Silicon', bShow=True, bSave=False, bPrint=False):

    from pyemaps import Crystal, EMC, SIMC              #----pyemaps crystal module
    from pyemaps import DPList, showDif                 #----Helper modules                    #----can add more if desired
    
    vt = 100
    simc = SIMC(excitation=(0.3,1.0), bmin=0.1)
    em_controls = EMC(zone=(1,1,1),
                      vt=vt,
                      cl=1000,
                      simc=simc)   
    cr = Crystal.from_builtin(name)                     #----loading Silicon crystal from builtin database
    if bPrint: print(cr)

    try:
        print(f'debug: got')
        emc, cr_dp = cr.generateDP(em_controls=em_controls) #----generate kinematic diffraction pattern
                                                            #----Output:
                                                            #----emc: associated microscope and 
                                                            #            simulation control object
                                                            #----si_dp: diffraction pattern generated
                                                            #----raw representation of kinematic diffraction pattern 

        dpl = DPList(name)                                  #----create a diffraction pattern list to hold the results
        dpl.add(emc, cr_dp) 
    except Exception as e:
        print(f'Failed to simulate kinematical diffractions: {e}')
    if bShow:
        showDif(dpl)

if __name__ == '__main__':
    # run_kdiffraction()
    run_kdiff(name='SiAlONa', bPrint=True)
    # SiAlONa, BiMnO3