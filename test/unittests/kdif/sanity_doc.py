def run_kdiffraction():

    from pyemaps import Crystal             #----pyemaps crystal module
    from pyemaps import DPList, showDif     #----Helper modules
    
    si = Crystal.from_builtin('Silicon')    #----loading Silicon crystal from builtin database
    emc, si_dp = si.generateDP()            #----generate kinematic diffraction pattern
                                            #----Output:
                                            #----emc: associated microscope and 
                                            #            simulation control object
                                            #----si_dp: diffraction pattern generated
    print(si_dp)                            #----raw representation of kinematic diffraction pattern 

    dpl = DPList('Silicon')                 #----create a diffraction pattern list to hold the results
    dpl.add(emc, si_dp)                     #----can add more if desired

    showDif(dpl, bClose=False)              #----visual representation of diffraction pattern
    
if __name__ == '__main__':
    run_kdiffraction()