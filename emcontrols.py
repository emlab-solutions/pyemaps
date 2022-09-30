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

from . import  EMCError

from pyemaps import DEF_EXCITATION, \
                    DEF_GMAX, \
                    DEF_BMIN, \
                    DEF_INTENSITY, \
                    DEF_GCTL, \
                    DEF_ZCTL, \
                    DEF_XAXIS              

class SIMControl:
    '''
    Simulation control parameters, to be embedded in EMControl, including:
    excitation:     excitation error range in (min, max)
    gmax:           maximum recipricol vector length
    bmin:           beta perturbation cutoff
    intensity:      kinematic diffraction intensity cutoff level and scale in (level, scale)
    xaxis:          crystal horizontal axis in reciprical space
    gctl:           maximum index number for g-list
    zctl:           maximum zone index number
    '''
    def __init__(self, excitation = DEF_EXCITATION, \
                       gmax = DEF_GMAX, \
                       bmin = DEF_BMIN, \
                       intensity = DEF_INTENSITY, \
                       xaxis = DEF_XAXIS, \
                       gctl = DEF_GCTL, \
                       zctl = DEF_ZCTL
                       ):

        setattr(self, 'excitation', excitation)
        setattr(self, 'gmax', gmax)
        setattr(self, 'bmin', bmin)
        setattr(self, 'intensity', intensity)       
        setattr(self, 'gctl', gctl)
        setattr(self, 'zctl', zctl)
        setattr(self, 'xaxis', xaxis)

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
    def intensity(self):
       return self._intensity

    @property
    def gctl(self):
       return self._gctl

    @property
    def zctl(self):
       return self._zctl

    @property
    def xaxis(self):
       return self._xaxis

    @excitation.setter
    def excitation(self, excit):
        
       if not excit or \
          not isinstance(excit, tuple) or \
          len(excit) != 2 or \
          not isinstance(excit[0], (int, float)) or \
          not isinstance(excit[1], (int, float)) or \
          excit[0] > excit[1]:
            raise EMCError('Excitation values must be a tuple of two ordered numbers')
       
       self._excitation = excit

    @gmax.setter
    def gmax(self, gm):

       if not isinstance(gm, (int, float)):
            raise EMCError('gmax values must be a tuple of tow numbers')
       
       self._gmax = gm

    @bmin.setter
    def bmin(self, bm):

       if not isinstance(bm, (int, float)):
            raise EMCError('bmin values must be a tuple of tow numbers')
       
       self._bmin = bm

    @intensity.setter
    def intensity(self, intv):

       if intv is None or \
          not isinstance(intv, tuple) or \
          len(intv) != 2 or \
          not isinstance(intv[0], (int, float)) or \
          not isinstance(intv[1], (int, float)) or \
          intv[0] > intv[1]:
            raise EMCError('kinematic intensity values must be ordered numberals')
       
       self._intensity = intv

    @gctl.setter
    def gctl(self, gv):

       if not isinstance(gv, (int, float)):
            raise EMCError('gctl values must be a numeral')
       
       self._gctl = gv

    @zctl.setter
    def zctl(self, zv):
       if not isinstance(zv, (int, float)):
            raise EMCError('zctl values must be a numeral')
        
       self._zctl = zv

    @xaxis.setter
    def xaxis(self, xv):

       if xv is None or \
          not isinstance(xv, tuple) or \
          len(xv) != 3 or \
          not isinstance(xv[0], int) or \
          not isinstance(xv[1], int) or \
          not isinstance(xv[2], int):
            raise EMCError('Invalid crystal horizon axis')
       
       self._xaxis = xv
           
    def __eq__(self, other):

       if not isinstance(other, SIMControl):
              return False

       if self._excitation != other.excitation: 
              return False

       if self._gmax != other.gmax:
              return False

       if self._bmin != other.bmin:
              return False

       if self._intensity != other.intensity: 
              return False

       if self._xaxis != other.xaxis: 
              return False

       if self._gctl != other.gctl:
              return False

       if self._zctl != other.zctl:
              return False

       return True
    
    def __str__(self) -> str:
       
       simulation = ['Simulation Controls Parameters:']

       simulation.append('excitation error range: ' +  str(self._excitation))
       simulation.append('maximum recipricol vector length: ' + str(self._gmax))
       simulation.append('beta perturbation cutoff: ' + str(self._bmin))
       simulation.append('kinematic diffraction intensity cutoff level and scale: ')
       simulation.append('crystal horizontal axis in reciprical space: ' + str(self._xaxis))
       simulation.append('maximum index number for g-list: ' + str(self._gctl))
       simulation.append('maximum zone index number: ' + str(self._zctl))

       return "\n ".join(simulation)

    def isDefExcitation(self):
        return self._excitation == DEF_EXCITATION

    def isDefGmax(self):
        return self._gmax == DEF_GMAX

    def isDefBmin(self):
        return self._bmin == DEF_BMIN

    def isDefIntensity(self):
        return self._intensity == DEF_INTENSITY

    def isDefXaxis(self):
        return self._xaxis == DEF_XAXIS

    def isDefGctl(self):
        return self._gctl == DEF_GCTL

    def isDefZctl(self):
        return self._zctl == DEF_ZCTL

    @classmethod
    def from_random(cls):
        import random
        # random xaxis:
        ax = tuple(random.sample(range(4), k = 3))

        # random excitation
        excit = (random.uniform(0.2, 0.4), random.uniform(1.0, 3.0))

        # random gcuttoffs
        bmn = random.uniform(0.05, 0.15)
        gmx = random.uniform(2.0, 5.0)

        # random intensity
        inten = (0.0, random.randint(4,7))

        # random zone and gcutoffs
        gc = random.uniform(5.0, 7.0)
        zc = random.uniform(4.0, 6.0)
        try:
            sc = cls(excitation = excit, \
                     xaxis = ax, \
                     intensity = inten, \
                     gmax = gmx, \
                     bmin = bmn, \
                     gctl = gc, \
                     zctl = zc)

        except Exception as e:
            raise EMCError(str(e))
        else:
            return sc

from pyemaps import DEF_ZONE, \
                    DEF_DEFL, \
                    DEF_TILT, \
                    DEF_CL, \
                    DEF_KV
                    
DEF_CONTROLS_KEYS = ['zone','tilt','defl', 'cl', 'vt']

class EMControl:
    '''
    initializing class include the following controls:
    
    '''
    def __init__(self, *, tilt = DEF_TILT, 
                       zone = DEF_ZONE, 
                       defl = DEF_DEFL, 
                       vt = DEF_KV, 
                       cl = DEF_CL,
                       simc = SIMControl()):

        emc_dict = dict(tilt = tilt, 
                       zone = zone, 
                       defl = defl,
                       vt = vt,
                       cl = cl)
        
        for k, v in emc_dict.items():
            setattr(self, k, v)
        
        setattr(self, 'simc', simc)

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
            sc = SIMControl()

        return cls(tilt = t, zone = z, defl = d, vt = vt, cl = c, simc = sc)
        
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
    
    @property
    def simc(self):
        return self._simc

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
    
    @simc.setter
    def simc(self, sc):
        if not isinstance(sc, SIMControl):
           raise EMCError("Simulation control invlid")
        
        self._simc = sc

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

        if other.simc != self._simc:
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

