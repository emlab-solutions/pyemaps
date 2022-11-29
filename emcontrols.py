# """
# This file is part of pyemaps
# ___________________________

# pyemaps is free software for non-comercial use: you can 
# redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either 
# version 3 of the License, or (at your option) any later version.

# pyemaps is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with pyemaps.  If not, see <https://www.gnu.org/licenses/>.

# Contact supprort@emlabsoftware.com for any questions and comments.
# ___________________________

# Author:     EMLab Solutions, Inc.
# Date:       May 09, 2022   

# This class is helper for handling pyemaps microscope controls
# """

"""
There are two controls classes this module defines: `microscope controls <modules.html#pyemaps.emcontrols.EMControl>`_
and `simulations controls <modules.html#pyemaps.emcontrols.SIMControl>`_. 

Since the latter changes much less frequently than the former, 
simulation control is embedded as a member of a microscope controls class.

Simulation Control Constants and Default Values:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. data:: DEF_EXCITATION
    :value: (0.3, 2.0)

.. data:: DEF_GMAX 
    :value: 3.5

.. data:: DEF_BMIN
    :value: 0.1

.. data:: DEF_INTENSITY
    :value: (0.0, 5)

.. data:: DEF_GCTL
    :value: 6.0

.. data:: DEF_ZCTL
    :value: 5.0

.. data:: DEF_XAXIS
    :value: (0, 0, 0)

.. data:: DEF_PIXSIZE
    :value: 25

.. data:: DEF_DETSIZE
    :value: 512

.. data:: DEF_MODE
    :value: 1

.. data:: DEF_CBED_DSIZE
    :value: 0.16

Microscope Control Constants and Default Values:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. data:: DEF_TILT
    :value: (0.0, 0.0)

.. data:: DEF_ZONE
    :value: (0, 0, 1)

.. data:: DEF_DEFL
    :value: (0.0, 0.0)

.. data:: DEF_KV
    :value: 200.0

.. data:: DEF_CL
    :value: 1000.0

.. data:: DEF_APERTURE
    :value: 1.0

.. data:: DEF_OMEGA
    :value: 10

.. data:: DEF_SAMPLING
    :value: 8

.. data:: SAMPLE_THICKNESS
    :value: (200, 200, 100)


"""
from . import  EMCError

from pyemaps import (
                    DEF_EXCITATION, 
                    DEF_GMAX, 
                    DEF_BMIN, 
                    DEF_INTENSITY, 
                    DEF_GCTL, 
                    DEF_ZCTL, 
                    DEF_XAXIS, 
                    DEF_PIXSIZE, 
                    DEF_DETSIZE,
                    DEF_CBED_DSIZE,
                    DEF_MODE)              

SIM_COMTROLS_KEYS=['excitation', 'gmax', 'bmin', 'intensity', 'gctl', 'zctl',
                    'xaxis', 'pix_size', 'det_size', 'mode', 'dsize']
class SIMControl:
    '''
    Simulation controls, to be embedded in EMControl

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


    def __call__(self, **kwargs):
        """
        Adding more simulation control patameters during Bloch simulation
        runtime.

        """
        for k, v in kwargs.items():
            if k not in SIM_COMTROLS_KEYS:
                print(f'Key {k} does not belong to supported pyemaps simulation controls, ingored')

            setattr(self, k, v)
        
    @property
    def excitation(self):
       '''excitation error range in (min, max)'''
       return self._excitation

    @property
    def gmax(self):
       '''maximum recipricol vector length'''
       return self._gmax

    @property
    def bmin(self):
       '''beta perturbation cutoff'''
       return self._bmin

    @property
    def intensity(self):
       ''' 
       kinematic diffraction intensity cutoff 
       level and scale in (level, scale)
       '''
       return self._intensity

    @property
    def gctl(self):
       '''maximum index number for g-list'''
       return self._gctl

    @property
    def zctl(self):
       '''maximum zone or Miller index index number'''
       return self._zctl

    @property
    def xaxis(self):
       '''crystal horizontal axis in reciprical space'''
       return self._xaxis

    @property
    def pix_size(self):
       '''Detector pixel size in microns'''
       return self._pix_size

    @property
    def det_size(self):
       '''crystal horizontal axis in reciprical space'''
       return self._det_size

    @property
    def mode(self):
       '''Simulation mode: 1-normal 2-CBED'''
       return self._mode

    @property
    def dsize(self):
       '''Simulation diffracted beam size, only used for CBED mode'''
       return self._dsize

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
  
    @pix_size.setter
    def pix_size(self, pv):

       if not isinstance(pv, int):
            raise EMCError('Detector pixel size in microns must be an integer')
       
       self._pix_size = pv

    @det_size.setter
    def det_size(self, dv):

       if not isinstance(dv, int):
            raise EMCError('Detector size must be integer')
       
       self._det_size = dv   

    @mode.setter
    def mode(self, mv):
       if not isinstance(mv, int) or \
          (mv != 1 and mv != 2):
            raise EMCError('mode must be integer of value 1 or 2')
       
       self._mode = mv   

    @dsize.setter
    def dsize(self, dv):

       if not isinstance(dv, (int,float)):
            raise EMCError('Detector size must be integer')
       
       self._dsize = dv   

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

       if self._pix_size != other.pix_size:
              return False

       if self._det_size != other.det_size:
              return False

       if self._mode != other.mode:
              return False

       if self._dsize != other.dsize:
              return False

       return True
    
    def __str__(self) -> str:
       
       simulation = ['Simulation Controls Parameters:']


       if hasattr(self, 'mode'):
            smode = 'unknown'
            if self._mode == 1:
                smode = 'normal'
            
            if self._mode == 2:
                smode = 'CBED'
            simulation.append('Simulation mode: ' + smode)

       if hasattr(self, 'dsize'):
            simulation.append('Diffarcted beam size: ' + str(self._dsize))

       simulation.append('excitation error range: ' +  str(self._excitation))
       simulation.append('maximum recipricol vector length: ' + str(self._gmax))
       simulation.append('beta perturbation cutoff: ' + str(self._bmin))
       simulation.append('kinematic diffraction intensity cutoff level and scale: '+ str(self._intensity))
       simulation.append('crystal horizontal axis in reciprical space: ' + str(self._xaxis))
       simulation.append('maximum index number for g-list: ' + str(self._gctl))
       simulation.append('maximum zone index number: ' + str(self._zctl))

       if hasattr(self, 'pix_size'):
            simulation.append('Detector pixel size: ' + str(self._pix_size))

       if hasattr(self, 'det_size'):
            simulation.append('Detector size: ' + str(self._det_size))

       return "\n ".join(simulation)

    def _isDefExcitation(self):
        '''Helper function to minimize trips to backend modules'''
        return self._excitation == DEF_EXCITATION

    def _isDefGmax(self):
        '''Helper function to minimize trips to backend modules'''
        return self._gmax == DEF_GMAX

    def _isDefBmin(self):
        '''Helper function to minimize trips to backend modules'''
        return self._bmin == DEF_BMIN

    def _isDefIntensity(self):
        '''Helper function to minimize trips to backend modules'''
        return self._intensity == DEF_INTENSITY

    def _isDefXaxis(self):
        '''Helper function to minimize trips to backend modules'''
        return self._xaxis == DEF_XAXIS

    def _isDefGctl(self):
        '''Helper function to minimize trips to backend modules'''
        return self._gctl == DEF_GCTL

    def _isDefZctl(self):
        '''Helper function to minimize trips to backend modules'''
        return self._zctl == DEF_ZCTL

    def plot_format(self):
        '''
        Format simulation controls in builtin display functions
        Only plot those parameter that are not defaults

        '''
        simcstrs = []

        if hasattr(self, 'mode') and self._mode and self._mode != DEF_MODE:
            smode = 'unknown'
            if self._mode == 1:
                smode = 'normal'
            
            if self._mode == 2:
                smode = 'CBED'
            
            simcstrs.append('mode=' + smode)

        if hasattr(self, 'dsize') and self._dsize and self._dsize != DEF_CBED_DSIZE:
            simcstrs.append('dsize=' + '{:.2f}'.format(self._dsize))

        if not self._isDefExcitation():
            simcstrs.append('excitation=' + '({:.2f},{:.2f})'.format(self._excitation[0], self._excitation[1]))

        if not self._isDefGmax():
            simcstrs.append('gmax=' + '{:.2f}'.format(self._gmax))

        if not self._isDefBmin():
            simcstrs.append('bmin=' + '{:.2f}'.format(self._bmin))

        if not self._isDefIntensity():
            simcstrs.append('intensity=' + '({:.2f},{:.2f})'.format(self._intensity[0], self._intensity[1]))

        if not self._isDefXaxis():
            simcstrs.append('xaxis=' + '({:d},{:d},{:d})'.format(self._xaxis[0],self._xaxis[1],self._xaxis[2]))

        if not self._isDefGctl():
            simcstrs.append('gctl=' + '{:.2f}'.format(self._gctl))

        if not self._isDefZctl():
            simcstrs.append('zctl=' + '{:.2f}'.format(self._zctl))

        if hasattr(self, 'pix_size') and self._pix_size != DEF_PIXSIZE:
            simcstrs.append('pix_size=' + '{:d}'.format(self._pix_size))

        if hasattr(self, 'det_size') and self._det_size != DEF_DETSIZE:
            simcstrs.append('det_size=' + '{:.2f}'.format(self._det_size))
        
        return ';'.join(simcstrs)

    @classmethod
    def _from_random(cls):

        ''' Design for internal testing purpose only'''

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

from pyemaps import (DEF_ZONE, 
                    DEF_DEFL, 
                    DEF_TILT, 
                    DEF_CL, 
                    DEF_KV, 
                    DEF_APERTURE,
                    DEF_OMEGA, 
                    DEF_SAMPLING, 
                    DEF_THICKNESS)
                    
EM_CONTROLS_KEYS = ['zone','tilt','defl', 'cl', 'vt', 
                     'aperture', 'omega', 'sampling', 
                     'sth']

class EMControl:
    '''
    Microscope and sample property controls class. Its attributes include:

    * **tilt**: sample tilt in x and y directory (x,y)
    * **zone**: starting zone axis
    * **defl**: shifts in x and y direction (x, y)
    * **cl**: cameral length
    * **vt**: hight voltage in kilo-volts
    * **simc*: `SIMControl <pyemaps.emcontrols.html#pyemaps.emcontrols.SIMControl>`_ object

    Other control parameters:

    * **aperture**: Objective len aperture
    * **omega**: Diagnization cutoff value
    * **sampling**: Number of sampling points
    * **sth**: Sample thickness. 

    '''

    def __init__(self, tilt = DEF_TILT, 
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

    def __call__(self, **kwargs):
        """
        Additional class members added as simulation is run.

        """
        
        for k, v in kwargs.items():
            if k not in EM_CONTROLS_KEYS:
                print(f'key {k} is not in pyemaps microscope control keys, ignored')
                continue    
            setattr(self, k, v)
            
    @classmethod
    def from_dict(cls, emc_dict):

        '''
        Create an EMControl object from a python dict object

        :param emc_dict: Microscope control dict object
        :type emc_dict: dict, required
        :raises: EMCError, if validation fails

        '''
        if not isinstance(emc_dict, dict):
            raise EMCError('invalid data input in constructing EMC from a dictionary')

        t = z = d = vt = c = None 
        for k, v in emc_dict.items():
            if k not in EM_CONTROLS_KEYS:
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
        '''starting zone axis'''
        return self._zone
    
    @property
    def tilt(self):
        '''tilt in x and y directions (x,y)'''
        return self._tilt
    
    @property
    def defl(self):
        '''shifts in x and y directions (x, y)'''
        return self._defl
    
    @property
    def cl(self):
        '''cameral length'''
        return self._cl
    
    @property
    def vt(self):
        '''hight voltage in kilo-volts'''
        return self._vt
    
    @property
    def simc(self):
        '''
        `SIMControl <modules.html#pyemaps.emcontrols.SIMControl>`_ object
        '''
        return self._simc
    
    @property
    def aperture(self):
        '''Objective len aperture'''
        return self._aperture
    
    @property
    def omega(self):
        '''Diagnization cutoff value'''
        return self._omega
       
    @property
    def sampling(self):
        '''Number of sampling points'''
        return self._sampling

    @property
    def sth(self):
        '''
        Samples thickness setting in tuple of three integers: (start, end, step)

        '''
        return self._sth

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
    
    @aperture.setter
    def aperture(self, av):
        if not isinstance(av, (int,float)):
           raise EMCError("Voltage must be a numberal")
        
        self._aperture = av
    
    @omega.setter
    def omega(self, ov):
        if not isinstance(ov, (int,float)):
           raise EMCError("Voltage must be a numberal")
        
        self._omega = ov
    
    @sampling.setter
    def sampling(self, sv):
        try:
            v = int(sv)
        except ValueError:
            raise EMCError("Invalid number of sampling points input")
        
        self._sampling = v
    
    @sth.setter
    def sth(self, sv):
        if not isinstance(sv, int):
           raise EMCError("Sample thickness must be an integer")
        
        self._sth = sv
    
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

        if other.aperture != self._aperture:
            return False 

        if other.omega != self._omega:
            return False 

        if other.sampling != self._sampling:
            return False 

        if other.sth != self._sth:
            return False 

        return True


    def __str__(self):
        from . import SIMC

        cstr = []
        cstr.append('Zone: ' + str(self._zone))
        cstr.append('Tilt: ' + str(self._tilt))
        cstr.append('Deflection: ' + str(self._defl))
        cstr.append('Camera Length: ' + str(self._cl))
        cstr.append('Voltage: ' + str(self._vt))

        if hasattr(self, 'aperture'):
            cstr.append('Aperture: ' + str(self._aperture))

        if hasattr(self, 'omega'):
            cstr.append('Omega: ' + str(self._omega))

        if hasattr(self, 'sampling'):
            cstr.append('Sampling: ' + str(self._sampling))

        if hasattr(self, 'sth'):
            cstr.append('Thickness: ' + str(self._sth))

        if not self._simc == SIMC():
            cstr.append('Simulation parameters: ' + str(self._simc))

        return '\n'.join(cstr)

    def plot_format(self):
        """
        Control string format for built-in display functions
        Only non-default controls values are displayed

        """
        emcstrs = []
        if self._zone != DEF_ZONE:
            emcstrs.append('zone=' + '({:d},{:d},{:d})'.format(self._zone[0],
                                                               self._zone[1],
                                                               self._zone[2])
                          )

        if self._tilt != DEF_TILT:
            emcstrs.append('tilt=' + '({:.2f},{:.2f})'.format(self._tilt[0], 
                                                              self._tilt[1])
                          )

        if self._defl != DEF_DEFL:
            emcstrs.append('defl=' + '({:.2f},{:.2f})'.format(self._defl[0], 
                                                              self._defl[1])
                          )

        if self._cl != DEF_CL:
            emcstrs.append('camlen=' + '{:.2f}'.format(self._cl))

        if self._vt != DEF_KV:
            emcstrs.append('vt=' + '{:.2f}'.format(self._vt))

        if hasattr(self, 'aperture') and self._aperture != DEF_APERTURE:
            emcstrs.append('aperture=' + '{:.2f}'.format(self._aperture))

        if hasattr(self, 'omega') and self._omega != DEF_OMEGA:
            emcstrs.append('omega=' + '{:.2f}'.format(self._omega))

        if hasattr(self, 'sampling') and self._sampling != DEF_SAMPLING:
            emcstrs.append('sampling=' + '{:.2f}'.format(self._sampling))

        if hasattr(self, 'sth') and self._sth != DEF_THICKNESS[0]:
            emcstrs.append('thickness=' + 
                            '{:d}'.format(self._sth)
                          )

        cstr = ''

        if len(emcstrs) != 0:
            cstr = cstr + ';'.join(emcstrs)

        simstr = self._simc.plot_format()

        if len(simstr) != 0 and len(cstr) != 0:
            return cstr + '\n' + simstr

        if len(simstr) == 0 and len(cstr) != 0:
            return cstr

        if len(simstr) != 0 and len(cstr) == 0:
            return simstr
        
        return ''