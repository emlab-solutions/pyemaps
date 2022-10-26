def add_csf(target):
    '''
    #####INPUT#######
    -------------kv-----------------------
      Accelaration Voltage in Volts
    --------------------------------------
    -------------smax---------------------
      Limit of Sin(theta)/Wave length
    --------------------------------------
    -------------sftype-------------------
      Structure Factors Type:
      1 - x-ray structure factor (default)
      2 - electron structure factor in volts (V)
      3 - electron structure factor in 1/angstrom^2 in (V)
      4 - electron absorption structure factor in 1/angstrom^2 (V)
    --------------------------------------
    -------------aptype-------------------
      Structure Factor in (Amplitude, Phase) or (Real, Imaginary):
      0 - in (Real, Imaginary) 
      1 - in (Amplitude, Phase) (default)
    --------------------------------------

    ####OUTPUT########
    The function returns an array of structure factors
    Each item in the output array [sfs] is of a dictionary type
    for each element:
      hkl: (h,k,l)    - Miller Indices 
      sw: s           - Sin(theta)/Wave length
      ds: d           - d-spacing
      amp_re          - Structure factor amplitude or rela part
      phase_im        - Structure factor phase or imaginary part
'''
    try:
        from . import csf

    except ImportError as e:               
        print(f"Error: required module pyemaps.csf not found")
        
    sf_type_lookup = ['X-ray Structure Factors',
                  'Electron Strcture Factors in kV',
                  'Electron Structure Factor in 1/\u212B',
                  'Electron Absorption Structure Factor in 1/\u212B^2']

    sf_ap_flag = [('real', 'imaginary'), ('amplitude', 'phase')]

    def printCSF(self, sfs):

        sftype =sfs[0]['sftype']
        aptype =sfs[0]['aptype']
        if sftype < 1 or sftype > 4:
            print(f'Invalid structure factor type input: {sftype}')
            return sfs

        if aptype < 0 or aptype > 1:
            print(f'Invalid structure factor output data flag: {aptype}')
            return sfs

        subj = sf_type_lookup[sftype-1]
        print(f"-----{subj}----- ")
        print(f"     crystal\t\t: {self.name}")

        # print(f"     by EMLab Solutions, Inc.     \n")

        mi = "     h k l \t\t: Miller Index"
        print(mi)
        ssw = str(f"     s-w   \t\t: Sin(\u03F4)/Wavelength <= {sfs[0]['smax']}")
        print(ssw )
        dss = "     d-s   \t\t: D-Spacing"
        print(dss)
        
        if sftype > 1:
            print(f"     high voltage\t: {sfs[0]['kv']} V\n")
        else:
            print(f" ")


        sap1 = sf_ap_flag[aptype][0]
        sap2 = sf_ap_flag[aptype][1]
        
        print(f"{'h':^4}{'k':^4}{'l':^5}{'s-w':^16}{'d-s':^16}{sap1:^16}{sap2:^16}\n")
        
        nb = len(sfs)
        for i in range(1, nb, 1):
            h,k,l = sfs[i]['hkl']
            sw,ds = sfs[i]['sw'], sfs[i]['ds']
            sf1,sf2 = sfs[i]['amp_re'], sfs[i]['phase_im']
            
            sh = '{0: < #04d}'. format(int(h))
            sk = '{0: < #04d}'. format(int(k))
            sl = '{0: < #05d}'. format(int(l))

            ssw = '{0: < #016.10f}'. format(float(sw))
            sds = '{0: < #016.10f}'. format(float(ds))
            ssf1 = '{0: < #016.7g}'. format(float(sf1))

            if aptype == 1:
                ssf2 = '{0: < #016.6f}'. format(float(sf2))
            else:
                ssf2 = '{0: < #016.6g}'. format(float(sf2))

            print(f"{sh}{sk}{sl}{ssw}{sds}{ssf1}{ssf2}")    

        print('\n')          

    def generateCSF(self, kv = 100, smax = 0.5, sftype = 1, aptype = 0):
        
        sfs = [dict(kv = kv, smax = smax, sftype = sftype, aptype = aptype)]

        self.load()

        nb, ret = csf.generate_sf(kv, smax, sftype, aptype)

        if ret != 0 and nb <= 0:
            print(f'Error running generating structure factor for {self.name}')
            return sfs

        for i in range(2, nb+1):
            ret = 0
            ret,h,k,l,s,d,sf1,sf2 = csf.get_sf(i)
            if ret != 0: 
                print(f'Error running generating sructure factor for {self.name}')
                return sfs
            
            sf = dict(hkl = (h,k,l),
                       sw = s,
                       ds = d,
                       amp_re = sf1,
                       phase_im = sf2
                     )
            sfs.append(sf)    

        #release the memory
        csf.delete_sfmem()

        return sfs
    
    target.generateCSF = generateCSF
    target.printCSF = printCSF

    return target