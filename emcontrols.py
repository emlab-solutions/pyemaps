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
    def __init__(self, *, tilt = None, 
                       zone = None, 
                       defl = None, 
                       vt = None, 
                       cl = None):

        if not tilt:
            tilt = DEF_CONTROLS['tilt']
        
        if not zone:
            zone = DEF_CONTROLS['zone']
        
        if not defl:
            defl = DEF_CONTROLS['defl']

        if not vt:
            vt = DEF_CONTROLS['vt']

        if not cl:
            cl = DEF_CONTROLS['cl']

        emc_dict = dict(tilt = tilt, 
                       zone = zone, 
                       defl = defl,
                       vt = vt,
                       cl = cl)
        
        for k, v in emc_dict.items():
            setattr(self, k, v)

    @classmethod
    def from_dict(cls, emc_dict):

        if not isinstance(emc_dict, dict):
            raise EMCError('invalid data input in constructing EMC from a dictionary')

        t = z = d = vt = c = None 
        for k, v in emc_dict.items():
            if k not in DEF_CONTROLS:
                err_msg = str(f'Invilid key {k} found in the input')
                raise EMCError(err_msg)

            if k == 'tilt':
                t = v
            if k == 'zone':
                z = v
            if k == 'defl':
                d = v
            if k == 'vt':
                vt = v
            if k == 'cl':
                c = v

        return cls(tilt = t, zone = z,
                    defl = d, vt = vt,
                    cl = c)
        
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
        if not isinstance(zv, tuple) or len(zv) != 3 or \
           list(map(type, zv)) != [int, int, int]:
           raise EMCError("Zone axis must be tuple of three intergers")
        
        if zv == (0,0,0):
           raise EMCError("Zone axis must not be (0,0,0)")

        self._zone = zv 

    @tilt.setter
    def tilt(self, tl):
        if not isinstance(tl, tuple) or len(tl) != 2:
           raise EMCError("Tilt must be tuple of two numbers")

        typelist = list(map(type, tl))
        
        for vt in typelist:
            if vt != float and vt != int:
                raise EMCError('Input values for tilt must be nmeric')

        self._tilt = tl

    @defl.setter
    def defl(self, df):
        if not isinstance(df, tuple) or len(df) != 2:
           raise EMCError("deflection must be tuple of two numbers")
        
        typelist = list(map(type, df))

        for vt in typelist:
            if vt != float and vt != int:
                raise EMCError('Input values for deflection must be nmeric')

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
