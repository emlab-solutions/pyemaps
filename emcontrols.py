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

from . import  EMCError, EMSIMError

from pyemaps import DEF_ZONE, \
                    DEF_DEFL, \
                    DEF_TILT, \
                    DEF_CL, \
                    DEF_KV
                    
DEF_CONTROLS_KEYS = ['zone','tilt','defl', 'cl', 'vt']

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
    def __init__(self, *, tilt = DEF_TILT, 
                       zone = DEF_ZONE, 
                       defl = DEF_DEFL, 
                       vt = DEF_KV, 
                       cl = DEF_CL):

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
            if k not in DEF_CONTROLS_KEYS:
                print(f'Invilid key {k} found in the input, ignored')
                continue
            
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


from pyemaps import DEF_EXCITATION, \
                    DEF_GMAX, \
                    DEF_BMIN, \
                    DEF_INTENCITY, \
                    DEF_GCTL, \
                    DEF_ZCTL              

class SIMControl:
    '''
       pyemaps diffraction simulation controls parameter class
       excitation: excit = tuple(sgmax, sgmin)
       gmax: 
       bmin:
       intctl:
       intz0:
       mode: diffraction simulation mode - 1 == mormal; 2 == CBED
       omega: bloch specific parameter
       sampling: bloch specific parameter
       pixsize: pixel size for bloch image
       detsize: detector size for bloch image
    '''
    def __init__(self, excitation = DEF_EXCITATION, \
                       gmax = DEF_GMAX, \
                       bmin = DEF_BMIN, \
                       intencity = DEF_INTENCITY, \
                       gctl = DEF_GCTL, \
                       zctl = DEF_ZCTL
                       ):

        setattr(self, 'excitation', excitation)
        setattr(self, 'gmax', gmax)
        setattr(self, 'bmin', bmin)
        setattr(self, 'intencity', intencity)       
        setattr(self, 'gctl', gctl)
        setattr(self, 'zctl', zctl)

    @property
    def excitation(self):
       return self._excitation

    @property
    def gmax(self):
       return self._gmax

    @property
    def bmin(self):
       return self._bmin

    @property
    def intencity(self):
       return self._intencity

    @property
    def gctl(self):
       return self._gctl

    @property
    def zctl(self):
       return self._zctl

    @excitation.setter
    def excitation(self, excit):
       if not excit or \
          not isinstance(excit, tuple) or \
          len(excit) != 2 or \
          not isinstance(excit[0], (int, float)) or \
          not isinstance(excit[1], (int, float)):
            raise EMSIMError('Excitation values must be a tuple of two numbers')
       
       self._excitation = excit

    @gmax.setter
    def gmax(self, gm):
       if not isinstance(gm, (int, float)):
            raise EMSIMError('gmax values must be a tuple of tow numbers')
       
       self._gmax = gm

    @bmin.setter
    def bmin(self, bm):
       if not isinstance(bm, (int, float)):
            raise EMSIMError('bmin values must be a tuple of tow numbers')
       
       self._bmin = bm

    @intencity.setter
    def intencity(self, intv):
       if not intv or \
          not isinstance(intv[0], int) or \
          not isinstance(intv[1], (int, float)):
            raise EMSIMError('kinematic intensity values must be numberal')
       
       self._intencity = intv

    @gctl.setter
    def gctl(self, gv):
       if not isinstance(gv, (int, float)):
            raise EMSIMError('gctl values must be an integer')
       
       self._gctl = gv

    @zctl.setter
    def zctl(self, zv):
       if not isinstance(zv, (int, float)):
            raise EMSIMError('zctl values must be an integer')
       
       self._zctl = zv
           
    def __eq__(self, other):

       if not isinstance(other, SIMControl):
              return False

       if self._excitation != other.excitation: 
              return False

       if self._gmax != other.gmax:
              return False

       if self._bmin != other.bmin:
              return False

       if self._intencity != other.intencity: 
              return False

       if self._gctl != other.gctl:
              return False

       if self._zctl != other.zctl:
              return False

       return True
    
    def __str__(self) -> str:
       
       simulation = ['Simulation Controls Parameters:']

       simulation.append('excitation: ' +  str(self._excitation))
       simulation.append('gmax??: ' + str(self._gmax))
       simulation.append('bmin??: ' + str(self._bmin))
       simulation.append('intencity: ' + str(self._intencity))
       simulation.append('gctl??: ' + str(self._gctl))
       simulation.append('zctl??: ' + str(self._zctl))

       return "\n ".join(simulation)

    def isDefExcitation(self):
        return self._excitation == DEF_EXCITATION

    def isDefGmax(self):
        return self._gmax == DEF_GMAX

    def isDefBmin(self):
        return self._bmin == DEF_BMIN

    def isDefIntencity(self):
        return self._intencity == DEF_INTENCITY

    def isDefGctl(self):
        return self._gctl == DEF_GCTL

    def isDefZctl(self):
        return self._zctl == DEF_ZCTL