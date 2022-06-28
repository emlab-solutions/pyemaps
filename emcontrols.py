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

from . import EMCError

DEF_CBED_DSIZE = 0.16
DEF_CONTROLS = dict(zone = (0,0,1),
                    tilt = (0.0,0.0),
                    defl = (0.0,0.0),
                    cl = 1000,
                    vt = 200
                    )

class EMControl:
    '''
    initializing class with a control dictionary of the format:
    DEF_CONTROLS = dict(zone = (0,0,1),
                    tilt = (0.0,0.0),
                    defl = (0.0,0.0),
                    cl = 1000,
                    vt = 200
                    )
    '''
    def __init__(self, emc_dict = DEF_CONTROLS):
        
        if not isinstance(emc_dict, dict) or len(emc_dict) != 5:
            raise EMCError('invalid data')

        if 'tilt' not in emc_dict or \
           'zone' not in emc_dict or \
           'defl' not in emc_dict or \
           'cl' not in emc_dict or \
           'vt' not in emc_dict:
           raise EMCError('missing key(s) in EMC data')
        
        for k, v in emc_dict.items():
            setattr(self, k, v)
    
    @property
    def zone(self):
        return self._zone
    
    @property
    def tilt(self):
        return self._tilt
    
    @property
    def defl(self):
        return self._defl
    
    @property
    def cl(self):
        return self._cl
    
    @property
    def vt(self):
        return self._vt
    
    @property
    def zone(self):
        return self._zone

    @zone.setter
    def zone(self, zv):
        if not isinstance(zv, tuple) or \
           list(map(type, zv)) != [int, int, int] or \
           len(zv) != 3:
           raise EMCError("Zone axis must be tuple of three intergers")
        
        self._zone = zv 

    @tilt.setter
    def tilt(self, tl):
        if not isinstance(tl, tuple) or \
           list(map(type, tl)) != [float, float] or \
           len(tl) != 2:
           raise EMCError("Tilt must be tuple of two floats")

        self._tilt = tl

    @defl.setter
    def defl(self, df):
        if not isinstance(df, tuple) or \
           list(map(type, df)) != [float, float]:
           raise EMCError("deflection must be tuple of two floats")
        
        self._defl = df

    @cl.setter
    def cl(self, clen):
        if not isinstance(clen, int) and not isinstance(clen, float):
           raise ValueError("Camera length must be of number")

        self._cl = clen
    
    @vt.setter
    def vt(self, kv):
        if not isinstance(kv, int) and not isinstance(kv, float):
           raise EMCError("Voltage must be of integer")
        
        self._vt = kv

    def __eq__(self, other):
        if not isinstance(other, EMControl):
           raise EMCError("Comparison must be done with EMControl object")
        
        if other.zone != self._zone:
            return False 

        if other.tilt != self._tilt:
            return False 

        if other.defl != self._defl:
            return False 

        if other.cl != self._cl:
            return False 

        if other.vt != self._vt:
            return False 

        return True


    def __str__(self):
        cstr = []
        cstr.append('Zone: ' + str(self._zone))
        cstr.append('Tilt: ' + str(self._tilt))
        cstr.append('Deflection: ' + str(self._defl))
        cstr.append('Camera Length: ' + str(self._cl))
        cstr.append('Voltage: ' + str(self._vt))
        return '\n'.join(cstr)
