'''
.. This file is part of pyEMAPS
 
.. ----

.. pyEMAPS is free software. You can redistribute it and/or modify 
.. it under the terms of the GNU General Public License as published 
.. by the Free Software Foundation, either version 3 of the License, 
.. or (at your option) any later version..

.. pyEMAPS is distributed in the hope that it will be useful,
.. but WITHOUT ANY WARRANTY; without even the implied warranty of
.. MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
.. GNU General Public License for more details.

.. You should have received a copy of the GNU General Public License
.. along with pyEMAPS.  If not, see `<https://www.gnu.org/licenses/>`_.

.. Contact supprort@emlabsoftware.com for any questions and comments.

.. ----

.. Author:             EMLab Solutions, Inc.
.. Date Created:       May 07, 2022  

'''
def add_csf(target):
    '''
      Generate crystal structure factors. The following types 
      Structure Factors are currently supported:

      * x-ray structure factor (default)
      * electron structure factor in volts (V)
      * electron structure factor in 1/angstrom^2 in (V)
      * electron absorption structure factor in 1/angstrom^2 (V)
      
    '''
    try:
        from . import csf

    except ImportError as e:
        print(f"Error: required module pyemaps.csf not found")

    from .. import CSFError

    # backend csf.generate_sf / csf.get_sf return codes
    _CSF_ERR = {
        1: 'structure factor generation failed',
        2: 'invalid structure factor type (sftype must be 1-4)',
        3: 'too many reflections within smax for the backend beam limit; '
           'reduce smax and retry',
        4: 'backend ran out of memory sizing the reflection set; reduce smax',
        5: 'backend reflection-count estimate was too low (internal error)',
    }
        
    # printCSF titles, by structure factor type (sftype 1-4). The units match the backend's
    # scaling: type 2 is the crystal potential coefficient V_g, in volts; types 3 and 4 are
    # U_g = 2meV_g/h^2 (relativistic) and its absorption counterpart, both in 1/Angstrom^2.
    sf_type_lookup = ['X-ray Structure Factors',
                  'Electron Structure Factors in Volts',
                  'Electron Structure Factors in 1/Angstrom^2',
                  'Electron Absorption Structure Factors in 1/Angstrom^2']

    sf_ap_flag = [('real', 'imaginary'), ('amplitude', 'phase')]

    def printCSF(self, sfs):
        """
        Print structure factors from :py:meth:`~pyemaps.crystals.Crystal.generateCSF` as a table.

        :param sfs: the list returned by :py:meth:`~pyemaps.crystals.Crystal.generateCSF`.
        :type sfs: list of dict, required

        Example output, X-ray structure factors of Silicon as amplitude and phase:

        .. code-block:: console

            -----X-ray Structure Factors-----
                 crystal            : Silicon
                 h k l              : Miller Index
                 s-w                : Sin(theta)/Wavelength <= 0.5
                 d-s                : D-Spacing

             h   k   l        s-w             d-s          amplitude         phase

             1   1   1    0.1594684869    3.1354157925    58.89618        180.000000
             0   0   2    0.1841383278    2.7153499126    1.171896e-06    180.000000
             ...
        """
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

        mi = "     h k l \t\t: Miller Index"
        print(mi)
        # ssw = str(f"     s-w   \t\t: Sin(\u03F4)/Wavelength <= {sfs[0]['smax']}")
        ssw = str(f"     s-w   \t\t: Sin(theta)/Wavelength <= {sfs[0]['smax']}")
        print(ssw )
        dss = "     d-s   \t\t: D-Spacing"
        print(dss)
        
        if sftype > 1:
            print(f"     high voltage\t: {sfs[0]['kv']} kV\n")
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

    def cleanCSF(self):
        """
        Free the memory used by the structure factor calculation, and unload the crystal from the
        simulation backend. :py:meth:`~pyemaps.crystals.Crystal.generateCSF` calls this itself.
        """
        csf.delete_sfmem()
        self.unload()
                
    def generateCSF(self, kv = 100, smax = 0.5, sftype = 1, aptype = 0):
        """
        Calculate the crystal's structure factors.

        :param kv: accelerating voltage, in kV. Used for the electron structure factors.
        :type kv: int or float, optional
        :param smax: largest sin(θ)/λ to include, in 1/Å.
        :type smax: int or float, optional
        :param sftype: the structure factor type:

            1. X-ray (the default)
            2. electron, in volts
            3. electron, in 1/Å²
            4. electron absorption, in 1/Å²

        :type sftype: int, optional
        :param aptype: the output format: 0 for real and imaginary parts (the default), or 1 for
            amplitude and phase (in degrees).
        :type aptype: int, optional
        :return: a list of dictionaries. The first holds the inputs: ``kv``, ``smax``, ``sftype``
            and ``aptype``. Each one after it is one reflection:

            .. code-block:: python

                {
                    'hkl': (h, k, l),     # Miller indices
                    'sw': s,              # sin(theta)/lambda, 1/Å
                    'ds': d,              # d-spacing, Å
                    'amp_re': ar,         # amplitude, or real part
                    'phase_im': ph        # phase in degrees, or imaginary part
                }

        :rtype: list of dict
        :raise ~pyemaps.errors.CSFError: if the calculation fails, *sftype* is invalid, or there are more
            reflections within *smax* than the backend can handle; in that case, lower *smax*.

        To print the result as a table, pass it to :py:meth:`~pyemaps.crystals.Crystal.printCSF`.
        """
        sfs = [dict(kv = kv, smax = smax, sftype = sftype, aptype = aptype)]

        self.load()

        nb, ret = csf.generate_sf(kv, smax, sftype, aptype)

        if ret != 0 or nb <= 0:
            self.cleanCSF()
            detail = _CSF_ERR.get(ret, f'backend returned code {ret}')
            raise CSFError(f'{detail} (crystal {self.name})')

        for i in range(2, nb+1):
            ret = 0
            ret,h,k,l,s,d,sf1,sf2 = csf.get_sf(i)
            if ret != 0:
                self.cleanCSF()
                raise CSFError(f'failed to retrieve reflection {i} of {nb} '
                               f'(crystal {self.name})')
            
            sf = dict(hkl = (h,k,l),
                       sw = s,
                       ds = d,
                       amp_re = sf1,
                       phase_im = sf2
                     )
            sfs.append(sf)    

        #release the memory
        self.cleanCSF()

        return sfs
    
    target.generateCSF = generateCSF
    target.printCSF = printCSF
    target.cleanCSF = cleanCSF

    return target
