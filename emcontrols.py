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

.. data:: DEF_OMEGA
    :value: 10

.. data:: DEF_SAMPLING
    :value: 8

.. data:: SAMPLE_THICKNESS
    :value: (200, 200, 100)


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
    
"""
from . import  EMCError


sdefault = ' [**default**]'
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

from pyemaps import (DEF_ZONE, 
                    DEF_DEFL, 
                    DEF_TILT, 
                    DEF_CL, 
                    DEF_KV, 
                    DEF_APERTURE,
                    DEF_OMEGA, 
                    DEF_SAMPLING, 
                    DEF_THICKNESS)

DEF_SIMC = {
    'excitation': DEF_EXCITATION,
    'gmax': DEF_GMAX, 
    'bmin': DEF_BMIN,
    'intensity': DEF_INTENSITY,
    'gctl': DEF_GCTL,
    'zctl': DEF_ZCTL,
    'omega': DEF_OMEGA,
    'sampling': DEF_SAMPLING,
    'sth': DEF_THICKNESS[0]
}           
SIMC_DESC = {
    'excitation': 'Excitation error range in (min, max)',
    'gmax': 'Maximum recipricol vector length', 
    'bmin': 'Beta perturbation cutoff',
    'intensity': 'Kinematic diffraction intensity cutoff level and scale in (level, scale)',
    'gctl': 'Maximum index number for g-list',
    'zctl': 'Maximum zone or Miller index index number',
    'omega': 'Diagnization cutoff value',
    'sampling': 'Number of sampling points',
    'sth': 'Samples thickness'
}

SIM_COMTROLS_KEYS=['excitation', 'gmax', 'bmin', 'intensity', 
                   'gctl', 'zctl', 'omega', 'sampling', 'sth']
class SIMControl:
    '''
    Simulation controls, to be embedded in EMControl

    '''
    def __init__(self, excitation = DEF_SIMC['excitation'], \
                       gmax = DEF_SIMC['gmax'], \
                       bmin = DEF_SIMC['bmin'], \
                       intensity = DEF_SIMC['intensity'], \
                       gctl = DEF_SIMC['gctl'], \
                       zctl = DEF_SIMC['zctl']
                       ):

        setattr(self, 'excitation', excitation)
        setattr(self, 'gmax', gmax)
        setattr(self, 'bmin', bmin)
        setattr(self, 'intensity', intensity)       
        setattr(self, 'gctl', gctl)
        setattr(self, 'zctl', zctl)
        #Setting optional control parameters to defaults if not set 
        setattr(self, 'sampling', DEF_SIMC['sampling'])
        setattr(self, 'omega', DEF_SIMC['omega'])
        setattr(self, 'sth', DEF_SIMC['sth'])

    def __call__(self, **kwargs):
        """
        Adding more simulation control patameters during Bloch 
        or other simulations.

        """
        for k, v in kwargs.items():
            if k not in DEF_SIMC:
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
       '''kinematic diffraction intensity cutoff level and scale in (level, scale)'''
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
        Samples thickness, must be an integer - optional attributes 
        of the emcontrols, set to default if not present
        '''

        return self._sth

    @excitation.setter
    def excitation(self, excit):
        
       if not excit or \
          not isinstance(excit, tuple) or \
          len(excit) != 2 or \
          not isinstance(excit[0], (int, float)) or \
          not isinstance(excit[1], (int, float)) or \
          excit[0] > excit[1]:
            raise EMCError('Excitation values must be a tuple of two numbers in ascending order')
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

    @omega.setter
    def omega(self, ov):
        if ov is None or not isinstance(ov, (int,float)):
            raise EMCError("omega must be a numberal")
            
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
        if sv is None or not isinstance(sv, int):
                raise EMCError("Sample thickness must be an integer")
            
        self._sth = sv

    def __lt__(self, other):
        return self.__key__() < other.__key__()
    
    def __key__(self):
        data = self.__dict__
        return [data[k] for k in data.keys()]

    def __eq__(self, other):

        return self.__dict__== other.__dict__
    
    def _str_prop(self, k) -> str:
        '''internal - out formatted string for k attributes'''

        if k not in SIMC_DESC or not hasattr(self, k):
            return EMCError('internal error!')
        
        v = getattr(self, k)

        return SIMC_DESC[k] + ': ' + str(v) + (sdefault if v== DEF_SIMC[k] else '')
    
    def _check_def(self, k) -> bool:
        '''internal - checking if the attribute k is at default value'''
        if k not in SIMC_DESC or not hasattr(self, k):
            return EMCError('internal error!')
        
        v = getattr(self, k)

        return v == DEF_SIMC[k]
        
    def __str__(self) -> str:

       simulation = ['Simulation Controls:']

       for k in DEF_SIMC:       
            simulation.append(self._str_prop(k))

    #    simulation.append(SIMC_DESC('gmax') + ' ' +
    #         str(self._gmax) + (sdefault if self._gmax == DEF_GMAX else ''))

    #    simulation.append(SIMC_DESC('bmin') + ' ' + 
    #         str(self._bmin) + (sdefault if self._bmin == DEF_BMIN else ''))

    #    simulation.append(SIMC_DESC('intensity') + ' ' + 
    #         str(self._intensity) + (sdefault if self._intensity == DEF_INTENSITY else ''))

    #    simulation.append(SIMC_DESC('gctl') + ' ' + 
    #         str(self._gctl) + (sdefault if self._gctl == DEF_GCTL else ''))

    #    simulation.append(SIMC_DESC('zctl') + ' ' + 
    #         str(self._zctl) + (sdefault if self._zctl == DEF_ZCTL else ''))

    #    simulation.append(SIMC_DESC('omega') + ' ' +
    #         str(self._omega) + (sdefault if self._omega == DEF_OMEGA else ''))
       
    #    simulation.append(SIMC_DESC('sampling') + ' ' + 
    #         str(self._sampling) + (sdefault if self._sampling == DEF_SAMPLING else ''))
       
    #    simulation.append(SIMC_DESC('sth') + ' ' + 
    #         str(self._sth) + (sdefault if self._sth == DEF_THICKNESS[0] else ''))

       return "\n\t".join(simulation)

    # def _isDefExcitation(self):
    #     '''Helper function to minimize trips to backend modules'''
    #     return self._excitation == DEF_EXCITATION

    # def _isDefGmax(self):
    #     '''Helper function to minimize trips to backend modules'''
    #     return self._gmax == DEF_GMAX

    # def _isDefBmin(self):
    #     '''Helper function to minimize trips to backend modules'''
    #     return self._bmin == DEF_BMIN

    # def _isDefIntensity(self):
    #     '''Helper function to minimize trips to backend modules'''
    #     return self._intensity == DEF_INTENSITY

    # def _isDefGctl(self):
    #     '''Helper function to minimize trips to backend modules'''
    #     return self._gctl == DEF_GCTL

    # def _isDefZctl(self):
    #     '''Helper function to minimize trips to backend modules'''
    #     return self._zctl == DEF_ZCTL

    def plot_format(self):
        '''
        Format simulation controls in builtin display functions
        Only plot those parameter that are not defaults

        '''
        simcstrs = []

        for k in DEF_SIMC:
            
            if self._check_def(k):
                continue

            format_str = k + '='
            v = getattr(self, k)

            if k == 'excitation':
                format_str += '({:.2f},{:.2f})'.format(v[0], v[1])
            elif k == 'gmax':
                format_str += '{:.2f}'.format(v)
            elif k == 'bim':
                format_str += '{:.2f}'.format(v)
            elif k == 'intensity':
                format_str += '({:.2f},{:.2f})'.format(self._intensity[0], self._intensity[1])
            elif k == 'gctl':
                format_str += '{:.2f}'.format(v)
            elif k == 'zctl':
                format_str += '{:.2f}'.format(v)
            elif k == 'omega':
                format_str += '{:.2f}'.format(v)
            elif k == 'sampling':
                format_str += '{:.2f}'.format(v)
            elif k == 'sth':
                format_str += '{:d}'.format(v)
            else:
                continue

            simcstrs.append(format_str)

        return ';'.join(simcstrs)

    @classmethod
    def _from_random(cls):

        ''' Design for internal testing purpose only'''

        import random

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
                     intensity = inten, \
                     gmax = gmx, \
                     bmin = bmn, \
                     gctl = gc, \
                     zctl = zc)

        except Exception as e:
            raise EMCError(str(e))
        else:
            return sc


# from pyemaps import (DEF_ZONE, 
#                     DEF_DEFL, 
#                     DEF_TILT, 
#                     DEF_CL, 
#                     DEF_KV, 
#                     DEF_APERTURE,
#                     DEF_OMEGA, 
#                     DEF_SAMPLING, 
#                     DEF_THICKNESS)
                                
DEF_EMC = {
    'mode': {'defval': DEF_MODE, 'desc': 'Simulation mode'},
    'dsize': {'defval': DEF_CBED_DSIZE, 'desc': 'Diffracted beam size, only used for CBED mode'},
    'zone': {'defval': DEF_ZONE, 'desc': 'Starting zone axis'},
    'tilt': {'defval': DEF_TILT, 'desc': 'Tilt in x and y directions (x,y)'},
    'defl': {'defval': DEF_DEFL, 'desc': 'Shifts in x and y directions (x, y)'},
    'cl': {'defval': DEF_CL, 'desc': 'Shifts in x and y directions (x, y)'},
    'vt': {'defval': DEF_KV, 'desc': 'High voltage'},
    'xaxis': {'defval': DEF_XAXIS, 'desc': 'Crystal horizontal axis in reciprical space'},
    'pix_size': {'defval': DEF_PIXSIZE, 'desc': 'Detector pixel size in microns'},
    'det_size': {'defval': DEF_DETSIZE, 'desc': 'Detector size in microns'},
    'aperture': {'defval': DEF_APERTURE, 'desc': 'Objective lense aperture'},
    'simc': {'defval': None, 'desc': 'Simulation Controls'}
}                                           
# DEF_DESC = {
#     'zone': 'Starting zone axis',
#     'tilt': 'Tilt in x and y directions (x,y)', 
#     'defl': 'Shifts in x and y directions (x, y)',
#     'cl': 'Cameral length',
#     'vt': 'High voltage',
#     'xaxis': 'Crystal horizontal axis in reciprical space',
#     'pix_size': 'Detector pixel size in microns',
#     'det_size': 'Detector size in microns',
#     'mode': 'Simulation mode: 1 - normal, 2 - CBED',
#     'dsize': 'Diffracted beam size, only used for CBED mode',
#     'aperture': 'Objective lense aperture',
#     'simc': None
# }                               
# EM_CONTROLS_KEYS = ['zone','tilt','defl', 'cl', 'vt', 
#                      'xaxis', 'pix_size', 'det_size', 
#                      'mode', 'dsize', 'aperture', 'simc']

class EMControl:
    '''
    Microscope and sample property controls class. Its attributes include:

    * **tilt**: sample tilt in x and y directory (x,y)
    * **zone**: starting zone axis
    * **defl**: shifts in x and y direction (x, y)
    * **cl**: cameral length
    * **vt**: hight voltage in kilo-volts
    * **simc*: `SIMControl <pyemaps.emcontrols.html#pyemaps.emcontrols.SIMControl>`_ object

    Other optional emcontrol parameters:

    * **aperture**: Objective len aperture
    * **pix_size**: detector pixel size
    * **det_size**: detector size
    * **xaxis**: crystal horizontal axis in reciprical space
    * **mode**: simulation mode: 1- normal, 2-CBED
    * **dsize**: diffracted beam size

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

        setattr(self, 'mode', DEF_MODE)
        setattr(self, 'aperture', DEF_APERTURE)
        setattr(self, 'dsize', -1) #(not used mode == 1)
        setattr(self, 'pix_size', DEF_PIXSIZE)
        setattr(self, 'det_size', DEF_DETSIZE)
        setattr(self, 'xaxis', DEF_XAXIS)

    def __call__(self, **kwargs):
        """
        Additional class members added as simulation is run.

        """
        
        for k, v in kwargs.items():
            if k not in DEF_EMC:
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
            if k not in DEF_EMC:
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
        '''Starting zone axis'''
        return self._zone
    
    @property
    def tilt(self):
        '''Tilt in x and y directions (x,y)'''
        return self._tilt
    
    @property
    def defl(self):
        '''Shifts in x and y directions (x, y)'''
        return self._defl
    
    @property
    def cl(self):
        '''Cameral length'''
        return self._cl
    
    @property
    def vt(self):
        '''Hight voltage in kilo-volts'''
        return self._vt

    @property
    def simc(self):
        '''
        `SIMControl <modules.html#pyemaps.emcontrols.SIMControl>`_ object
        '''
        return self._simc

    @property
    def xaxis(self):
       '''crystal horizontal axis in reciprical space'''
       return self._xaxis
    
    @property
    def aperture(self):
        '''Objective lense aperture - optional''' 
        return self._aperture

    @property
    def pix_size(self):
       '''Detector pixel size in microns- optional'''

       return self._pix_size

    @property
    def det_size(self):
       '''Detector size in microns- optional'''
       return self._det_size

    @property
    def mode(self):
       '''Simulation mode: 1-normal 2-CBED, optional'''
       return self._mode

    @property
    def dsize(self):
       '''Simulation diffracted beam size, only used for CBED mode- optional '''

       return self._dsize


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

    @xaxis.setter
    def xaxis(self, xv):
       if xv is None:
            self._xaxis = DEF_XAXIS
       else:
        if not isinstance(xv, tuple) or \
            len(xv) != 3 or \
            not isinstance(xv[0], int) or \
            not isinstance(xv[1], int) or \
            not isinstance(xv[2], int):
                raise EMCError('Invalid crystal horizon axis')
        
        self._xaxis = xv
  
    
    @simc.setter
    def simc(self, sc):
        if not isinstance(sc, SIMControl):
           raise EMCError("Simulation control invlid")
        
        self._simc = sc
    
    @aperture.setter
    def aperture(self, av):
        if av is None:
            self._aperture = DEF_APERTURE
        else:
            if not isinstance(av, (int,float)):
                raise EMCError("Voltage must be a numberal")
            
            self._aperture = av

    @pix_size.setter
    def pix_size(self, pv):
       if pv is None:
            self._pix_size = DEF_PIXSIZE
       else:
            if not isinstance(pv, int):
                raise EMCError('Detector pixel size in microns must be an integer')
       
            self._pix_size = pv

    @det_size.setter
    def det_size(self, dv):
       if dv is None:
            self._det_size = DEF_DETSIZE
       else:
            if not isinstance(dv, int):
                    raise EMCError('Detector size must be integer')
            
            self._det_size = dv   

    @mode.setter
    def mode(self, mv):
       if mv is None:
            self._mode = DEF_MODE
       else:
            if not isinstance(mv, int) or \
                (mv != 1 and mv != 2):
                    raise EMCError('mode must be integer of value 1 or 2')
            
            self._mode = mv   

    @dsize.setter
    def dsize(self, dv):
       if dv is None:
            self._dsize = DEF_CBED_DSIZE if self._mode == 2 else -1
       else:     
            if not isinstance(dv, (int,float)):
                    raise EMCError('Detector size must be integer')
            
            self._dsize = dv   
                
    def __lt__(self, other):
        return self.__key__() < other.__key__()

    def __key__(self):
        data = self.__dict__
        
        td = []
        for k in data:
            if 'simc' not in k:
                td.append(data[k])
            else:
                td.append(data[k].__key__())
                
        return td 

    def __eq__(self, other):
        if not isinstance(other, EMControl):
           raise EMCError("Comparison must be done with another EMControl object")
 
        return self.__dict__ == other.__dict__

    def _str_prop(self, k) -> str:
        '''internal'''
        if k not in DEF_EMC or not hasattr(self, k):
            return EMCError('internal error!')
            
        v = getattr(self, k)

        if k == 'mode':
            cstr=[]
            # m = getattr(k)
            if v == DEF_EMC[k]['defval']:
                cstr.append(DEF_EMC['mode']['desc'] + ': Normal ' + sdefault)
                cstr.append(DEF_EMC['dsize']['desc'] + ': Undefined, not used')
            elif v == DEF_EMC[k]['defval'] + 1:
                cstr.append(DEF_EMC['mode']['desc'] + ': CBED')
                try:
                    ds = self._dsize
                except AttributeError as e:
                    raise Exception from e
                else:
                    cstr.append(DEF_EMC['dsize']['desc'] + 
                        str(ds) + (sdefault if ds == DEF_EMC['dsize']['defval'] else ''))
            else:
                cstr.append('Mode: Unknown (Error)')
                cstr.append('Diffraction beam size: Undefined')
            return '\n'.join(cstr)

        if k == 'dsize':
            return '' # do nothing, already taken care of


        return DEF_EMC[k]['desc'] + ': ' + str(v) + \
               (sdefault if v== DEF_EMC[k]['defval'] else '')
        
    def __str__(self):
        '''
        Readable printout of the EMC class object.
        The output will include all class attribute values and annotate
        those with default values with [**default**] string 
        '''
        # from . import SIMC

        cstr = ['Electron Microscope Controls:',]
        
        # if self._mode == 1:
        #     cstr.append('Mode: Normal' + sdefault)
        #     cstr.append('Diffraction beam size: Undefined, not used')
        # elif self._mode == 2:
        #     cstr.append('Mode: CBED')
        #     try:
        #         ds = self._dsize
        #     except AttributeError as e:
        #         raise Exception from e
        #     else:
        #         cstr.append('Diffraction beam size: ' + 
        #             str(ds) + (sdefault if ds == DEF_CBED_DSIZE else ''))
        # else:
        #     cstr.append('Mode: Unknown (Error)')
        #     cstr.append('Diffraction beam size: Undefined')

        # cstr.append('Zone: ' + str(self._zone) + 
        #     (sdefault if self._zone == DEF_ZONE else ''))

        # cstr.append('Tilt: ' + str(self._tilt) + 
        #     (sdefault if self._tilt == DEF_TILT else ''))

        # cstr.append('Deflection: ' + str(self._defl) + 
        #     (sdefault if self._defl == DEF_DEFL else ''))

        # cstr.append('Camera Length: ' + str(self._cl) + 
        #     (sdefault if self._cl == DEF_CL else ''))

        # cstr.append('High Voltage: ' + str(self._vt) + 
        #     (sdefault if self._vt == DEF_KV else ''))

        # cstr.append('Aperture: ' + str(self._aperture) +
        #     (sdefault if self._aperture == DEF_APERTURE else ''))

        # cstr.append('Xaxis: ' + str(self._xaxis) +
        #     (sdefault if self._xaxis == DEF_XAXIS else ''))

        # cstr.append('Detector pixel size: ' + str(self._pix_size) +
        #     (sdefault if self._pix_size == DEF_PIXSIZE else ''))
        
        # cstr.append('Detector size: ' + str(self._det_size) + 
        #     (sdefault if self._det_size == DEF_DETSIZE else ''))

        for k in DEF_EMC:
            if k != 'dsize' and k !='simc': #skip these attributes
                cstr.append(self._str_prop(k))
            
        cstr.append(str(self._simc))

        return '\n'.join(cstr)

    
    def _check_def(self, k) -> bool:
        '''internal - checking if the attribute k is at default value'''
        if k not in DEF_EMC or not hasattr(self, k):
            return EMCError('internal error!')
        
        v = getattr(self, k)

        if k == 'dsize':
            if self._mode == 1:
                return True
            elif self._mode == 2 and v == DEF_EMC[k]['defval']:
                return True
            else:
                return False

        if k == 'simc':
            return v == SIMControl()

        return v == DEF_EMC[k]['defval']

    def plot_format(self):
        '''
        Format simulation controls in builtin display functions
        Only plot those parameter that are not defaults

        '''
        emcstrs = []

        for k in DEF_EMC:
            
            if self._check_def(k):
                continue

            format_str = k + '='
            v = getattr(self, k)

            if k == 'mode':
                format_str += 'CBED'
            elif k == 'dszie':
                format_str += '{:.2f}'.format(v)
            elif k == 'zone' or k == 'xaxis':
                format_str += '({:d},{:d},{:d})'.format(v[0],v[1],v[2])
            elif k == 'tilt' or k == 'defl':
                format_str += '({:.2f},{:.2f})'.format(v[0],v[1])
            elif k == 'cl' or k == 'vt':
                format_str += '{:.2f}'.format(v)
            elif k == 'aperture': 
                format_str += '{:.2f}'.format(v)
            elif k == 'pix_size' or k == 'det_size':
                format_str += '{:d}'.format(v)
            else:
                continue

            emcstrs.append(format_str)

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

        return ';'.join(emcstrs)

    # def plot_format(self):
    #     """
    #     Control string format for built-in display functions
    #     Only non-default controls values are displayed

    #     """
    #     emcstrs = []

    #     smode = 'normal'
    #     if hasattr(self, 'mode') and self._mode == 2:
    #         smode = 'CBED'
        
    #     emcstrs.append('mode=' + smode)

    #     if hasattr(self, 'dsize'): # only print when in CBED mode
    #         if self._mode == 2 and self._dsize != DEF_CBED_DSIZE:
    #             emcstrs.append('dsize=' + '{:.2f}'.format(self._dsize))

    #     if self._zone != DEF_ZONE:
    #         emcstrs.append('zone=' + '({:d},{:d},{:d})'.format(self._zone[0],
    #                                                            self._zone[1],
    #                                                            self._zone[2])
    #                       )

    #     if self._tilt != DEF_TILT:
    #         emcstrs.append('tilt=' + '({:.2f},{:.2f})'.format(self._tilt[0], 
    #                                                           self._tilt[1])
    #                       )

    #     if self._defl != DEF_DEFL:
    #         emcstrs.append('defl=' + '({:.2f},{:.2f})'.format(self._defl[0], 
    #                                                           self._defl[1])
    #                       )

    #     if self._cl != DEF_CL:
    #         emcstrs.append('camlen=' + '{:.2f}'.format(self._cl))

    #     if self._vt != DEF_KV:
    #         emcstrs.append('vt=' + '{:.2f}'.format(self._vt))

    #     if self._xaxis != DEF_XAXIS:
    #         emcstrs.append('xaxis=' + '({:d},{:d},{:d})'.format(self._xaxis[0],
    #                                                             self._xaxis[1],
    #                                                             self._xaxis[2]))

    #     if self._aperture != DEF_APERTURE:
    #         emcstrs.append('aperture=' + '{:.2f}'.format(self._aperture))

    #     if self._pix_size != DEF_PIXSIZE:
    #         emcstrs.append('pix_size=' + '{:d}'.format(self._pix_size))

    #     if self._det_size != DEF_DETSIZE:
    #         emcstrs.append('det_size=' + '{:.2f}'.format(self._det_size))

    #     cstr = ''

    #     if len(emcstrs) != 0:
    #         cstr = cstr + ';'.join(emcstrs)

    #     simstr = self._simc.plot_format()

    #     if len(simstr) != 0 and len(cstr) != 0:
    #         return cstr + '\n' + simstr

    #     if len(simstr) == 0 and len(cstr) != 0:
    #         return cstr

    #     if len(simstr) != 0 and len(cstr) == 0:
    #         return simstr
        
    #     return ''