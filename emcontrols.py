"""
This file is part of pyemaps
___________________________

pyemaps is free software for non-comercial use: you can 
redistribute it and/or modify it under the terms of the GNU General 
Public License as published by the Free Software Foundation, either 
version 3 of the License, or (at your option) any later version.

pyemaps is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pyemaps.  If not, see <https://www.gnu.org/licenses/>.

Contact supprort@emlabsoftware.com for any questions and comments.
___________________________

Author:     EMLab Solutions, Inc.
Date:       May 09, 2022   

This class is helper for handling pyemaps microscope controls
"""


DEF_CBED_DSIZE = 0.16
DEF_CONTROLS = dict(zone = (0,0,1),
                    tilt = (0.0,0.0),
                    defl = (0.0,0.0),
                    cl = 1000,
                    vt = 200
                    )

class EMControl:
    # initializing class with a control dictionary of the format:
    # DEF_CONTROLS = dict(zone = (0,0,1),
    #                 tilt = (0.0,0.0),
    #                 defl = (0.0,0.0),
    #                 cl = 1000,
    #                 vt = 200
    #                 )
    def __init__(self, emc_dict = None):
        
        if not emc_dict:
            emc_dict = DEF_CONTROLS.copy()

        for k, v in emc_dict.items():
            setattr(self, k, v)
        
    def __get_zone(self):
        return self._zone
    
    def __get_tilt(self):
        return self._tilt
    
    def __get_defl(self):
        return self._defl
    
    def __get_cl(self):
        return self._cl
    
    def __get_vt(self):
        return self._vt

    def __set_zone(self, zn):
        tlist = list(map(type, zn))
        # print(f"zone types: {tlist}")
        if not isinstance(zn, tuple) or \
           list(map(type, zn)) != [int, int, int] or \
           len(zn) != 3:
           raise ValueError("Zone axis must be tuple of three intergers")
        
        self._zone = zn 

    def __set_tilt(self, tl):
        if not isinstance(tl, tuple) or \
           list(map(type, tl)) != [float, float] or \
           len(tl) != 2:
           raise ValueError("Tilt must be tuple of two floats")

        self._tilt = tl
    
    def __set_defl(self, df):
        if not isinstance(df, tuple) or \
           list(map(type, df)) != [float, float] or \
           len(df) != 2:
           raise ValueError("deflection must be tuple of two floats")
        
        self._defl = df
        
    def __set_cl(self, clen):
        if not isinstance(clen, int):
           raise ValueError("Camera length must be of integer")

        self._cl = clen

    def __set_vt(self, kv):
        if not isinstance(kv, int):
           raise ValueError("Voltage must be of integer")
        
        self._vt = kv

    def __eq__(self, other):
        if not isinstance(other, EMControl):
           raise ValueError("Comparison must be done with EMControl object")
        
        if getattr(other, 'zone') != self._zone:
            return False 

        if getattr(other, 'tilt') != self._tilt:
            return False 

        if getattr(other, 'defl') != self._defl:
            return False 

        if getattr(other, 'cl') != self._cl:
            return False 

        if getattr(other, 'vt') != self._vt:
            return False 

        return True


    def __str__(self):
        cstr = []
        cstr.append('Zone: ' + str(self._zone))
        cstr.append('Tilt: ' + str(self._tilt))
        cstr.append('Camera Length: ' + str(self._cl))
        cstr.append('Voltage: ' + str(self._vt))
        return '\n'.join(cstr)
    
    zone = property(__get_zone, __set_zone)
    tilt = property(__get_tilt, __set_tilt)
    defl = property(__get_defl, __set_defl)
    cl = property(__get_cl, __set_cl)
    vt = property(__get_vt, __set_vt)