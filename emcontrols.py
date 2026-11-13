"""
.. This file is part of pyEMAPS.

Microscope and simulation controls.

This module defines two control classes: :py:class:`EMControl` for the microscope, sample
and detector, and :py:class:`SIMControl` for the simulation. The simulation controls change
less often, so an EMControl holds a SIMControl.

The main classes are also available from ``pyemaps`` as ``EMC`` and ``SIMC``.

Simulation control defaults
---------------------------

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

.. data:: DEF_THICKNESS
    :value: (200, 200, 100)

Microscope control defaults
---------------------------

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

.. pyEMAPS is free software. You can redistribute it and/or modify
.. it under the terms of the GNU General Public License as published
.. by the Free Software Foundation, either version 3 of the License,
.. or (at your option) any later version.

.. pyEMAPS is distributed in the hope that it will be useful,
.. but WITHOUT ANY WARRANTY; without even the implied warranty of
.. MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
.. GNU General Public License for more details.

.. You should have received a copy of the GNU General Public License
.. along with pyEMAPS.  If not, see `<https://www.gnu.org/licenses/>`_.

.. Contact support@emlabsoftware.com for any questions and comments.

.. ----

.. Author:     EMLab Solutions, Inc.
.. Date:       May 09, 2022
"""

from . import  EMCError
import math
EMC_TOLERANCE = 1.0e-07

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
                    DEF_DSIZE_LIMITS,
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
    'excitation': 'Excitation error range (min, max)',
    'gmax': 'Maximum reciprocal vector length (1/Å)', 
    'bmin': 'Beta perturbation cutoff',
    'intensity': 'Kinematic diffraction intensity cutoff level and scale (level, scale)',
    'gctl': 'Maximum index for the g-list',
    'zctl': 'Maximum zone axis index',
    'omega': 'Diagonalization cutoff',
    'sampling': 'Number of sampling points',
    'sth': 'Sample thickness (Å)'
}

def doc_dec_simc(k):
    def doc_str(obj):
        obj.__doc__ = obj.__doc__.format(SIMC_DESC[k])
        return obj
    return doc_str


# Printing the controls: one aligned line per control, with its unit. A control that differs
# from its default also shows the default.
LABEL_WIDTH = 26


def _num(v):
    """A number as short text, without single-precision noise: 0.30000001192092896 is 0.3."""
    return f'{v:.6g}'


def _pair(v):
    return f'({_num(v[0])}, {_num(v[1])})'


def _indices(v):
    return ' '.join(_num(i) for i in v)


def _line(label, value, default=None):
    """One printed control; *default* is the default's text, shown if it differs from *value*."""
    s = f'  {label:<{LABEL_WIDTH}}{value}'
    if default is not None and default != value:
        s += f'   (default {default})'
    return s


# key: (label, format)
SIMC_PRINT = {
    'excitation': ('Excitation error range', lambda v: f'{_num(v[0])} to {_num(v[1])}'),
    'gmax': ('Max. reciprocal vector', lambda v: f'{_num(v)} 1/Å'),
    'bmin': ('Beta perturbation cutoff', _num),
    'intensity': ('Intensity cutoff, scale', lambda v: f'{_num(v[0])}, {_num(v[1])}'),
    'gctl': ('Max. g-list index', _num),
    'zctl': ('Max. zone axis index', _num),
    'omega': ('Diagonalization cutoff', _num),
    'sampling': ('Sampling points', _num),
    'sth': ('Sample thickness', lambda v: f'{_num(v)} Å'),
}

EMC_PRINT = {
    'zone': ('Zone axis', lambda v: f'[{_indices(v)}]'),
    'tilt': ('Tilt (x, y)', lambda v: f'{_pair(v)} degrees'),
    'defl': ('Shift (x, y)', _pair),
    'cl': ('Camera length', lambda v: f'{_num(v)} mm'),
    'vt': ('High voltage', lambda v: f'{_num(v)} kV'),
    'pix_size': ('Detector pixel size', lambda v: f'{_num(v)} µm'),
    'det_size': ('Detector size', lambda v: f'{_num(v)} pixels'),
    'aperture': ('Objective aperture', _num),
}


class SIMControl:
    """
    Simulation controls. An :py:class:`EMControl` holds one as its ``simc``; it's also
    available from ``pyemaps`` as ``SIMC``.

    .. code-block:: python

        from pyemaps import EMC, SIMC

        emc = EMC(zone=(1, 1, 0), simc=SIMC(gmax=1.0, excitation=(0.3, 1.0)))

    The dynamic diffraction methods also record ``omega``, ``sampling`` and ``sth`` (sample
    thickness, Å) here.
    """
    def __init__(self, excitation = DEF_SIMC['excitation'], \
                       gmax = DEF_SIMC['gmax'], \
                       bmin = DEF_SIMC['bmin'], \
                       intensity = DEF_SIMC['intensity'], \
                       gctl = DEF_SIMC['gctl'], \
                       zctl = DEF_SIMC['zctl']
                       ):

        """
        :param excitation: excitation error range ``(min, max)``. Defaults to (0.3, 2.0).
        :type excitation: tuple of float, optional
        :param gmax: maximum reciprocal vector length, in 1/Å. Defaults to 3.5.
        :type gmax: float, optional
        :param bmin: beta perturbation cutoff. Defaults to 0.1.
        :type bmin: float, optional
        :param intensity: kinematic intensity cutoff level and scale, ``(level, scale)``. Defaults
            to (0.0, 5).
        :type intensity: tuple of float, optional
        :param gctl: maximum index for the g-list. Defaults to 6.
        :type gctl: int, optional
        :param zctl: maximum zone axis index. Defaults to 5.
        :type zctl: int, optional
        :raise ~pyemaps.errors.EMCError: if a value is invalid, or a range isn't in ascending order.
        """
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
        Set controls by keyword, e.g. ``simc(omega=12, sampling=10)``. The simulation methods use
        this to record the values they ran with.
        """
        for k, v in kwargs.items():
            if k not in DEF_SIMC:
                print(f'Key {k} does not belong to supported pyemaps simulation controls, ignored')
                continue

            setattr(self, k, v)
        
    @property
    @doc_dec_simc('excitation')
    def excitation(self):
       '''{0}'''
       return self._excitation

    @property
    @doc_dec_simc('gmax')
    def gmax(self):
       '''{0}'''
       return self._gmax

    @property
    @doc_dec_simc('bmin')
    def bmin(self):
       '''{0}'''
       return self._bmin

    @property
    @doc_dec_simc('intensity')
    def intensity(self):
       '''{0}'''
       return self._intensity

    @property
    @doc_dec_simc('gctl')
    def gctl(self):
       '''{0}'''
       
       return self._gctl

    @property
    @doc_dec_simc('zctl')
    def zctl(self):
       '''{0}'''
       return self._zctl
    
    @property
    @doc_dec_simc('omega')
    def omega(self):
       '''{0}'''
       return self._omega
       
    @property
    @doc_dec_simc('sampling')
    def sampling(self):
       '''{0}'''
       return self._sampling

    @property
    @doc_dec_simc('sth')
    def sth(self):
       '''{0}'''
        # '''
        # Samples thickness, must be an integer - optional attributes 
        # of the emcontrols, set to default if not present
        # '''

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
            raise EMCError('gmax must be a number')
       
       self._gmax = gm

    @bmin.setter
    def bmin(self, bm):

       if not isinstance(bm, (int, float)):
            raise EMCError('bmin must be a number')
       
       self._bmin = bm

    @intensity.setter
    def intensity(self, intv):

       if intv is None or \
          not isinstance(intv, tuple) or \
          len(intv) != 2 or \
          not isinstance(intv[0], (int, float)) or \
          not isinstance(intv[1], (int, float)) or \
          intv[0] > intv[1]:
            raise EMCError('Kinematic intensity must be a tuple of two numbers in ascending order')
       
       self._intensity = intv

    @gctl.setter
    def gctl(self, gv):

       if not isinstance(gv, (int, float)):
            raise EMCError('gctl values must be a numeral')
       
       self._gctl = int(gv)

    @zctl.setter
    def zctl(self, zv):
       if not isinstance(zv, (int, float)):
            raise EMCError('zctl values must be a numeral')
        
       self._zctl = int(zv)

    @omega.setter
    def omega(self, ov):
        if ov is None or not isinstance(ov, (int,float)):
            raise EMCError("omega must be a number")
            
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
        if sv is None or not isinstance(sv, (int, float)):
                raise EMCError("Sample thickness must be a number")
            
        self._sth = sv

    def __lt__(self, other):
        return self.__key__() < other.__key__()
    
    def __key__(self):
        data = self.__dict__
        return [data[k] for k in data.keys()]

    def __eq__(self, other):

        if not isinstance(other, SIMControl):
            return NotImplemented

        if self._intensity != other.intensity or \
            self._zctl != other.zctl or \
            self._gctl != other.gctl or \
            self._sth != other.sth or \
            self._sampling != other.sampling:
            # print(f'intensity, zctl, gctl sampling and slice numer does not match:')
            return False

        for a, b in zip(self._excitation, other.excitation):
            if not math.isclose(a, b, abs_tol=EMC_TOLERANCE):
                # print(f'excitation does not match: {self._excitation} != {other.excitation}')
                return False

        if not math.isclose(self._gmax, other.gmax, abs_tol=EMC_TOLERANCE):
            # print(f'gmax does not match: {self._gmax} != {other.gmax}')
            return False

        if not math.isclose(self._bmin, other.bmin, abs_tol=EMC_TOLERANCE):
            # print(f'bmin does not match: {self._bmin} != {other.bmin}')
            return False
        
        if not math.isclose(self._omega, other.omega, abs_tol=EMC_TOLERANCE):
            # print(f'omega does not match: {self._omega} != {other.omega}')
            return False
        
        return True
    
    def _check_def(self, k) -> bool:
        '''internal - checking if the attribute k is at default value'''
        if k not in SIMC_DESC or not hasattr(self, k):
            # return EMCError('internal error!')
            print(f'Warning: simulation class does not have {k} attribute')
            return False

        v = getattr(self, k)

        return v == DEF_SIMC[k]
        
    def __str__(self) -> str:
        """
        Return the controls as readable text, one per line, showing the default of any that
        differ from it.
        """
        lines = ['Simulation controls']
        for k, (label, fmt) in SIMC_PRINT.items():
            lines.append(_line(label, fmt(getattr(self, k)), fmt(DEF_SIMC[k])))

        return '\n'.join(lines)

    def __repr__(self):
        """Show the controls as ``print`` does: in the console, in Jupyter and in lists."""
        return str(self)

    def plot_format(self):
        """
        Format the controls that aren't at their defaults, for the captions of the built-in
        displays.

        :return: the controls, as ``name=value`` pairs separated by semicolons.
        :rtype: str
        """
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
            elif k == 'bmin':
                format_str += '{:.2f}'.format(v)
            elif k == 'intensity':
                format_str += '({:.2f},{:.2f})'.format(self._intensity[0], self._intensity[1])
            elif k == 'gctl':
                format_str += '{:f}'.format(v)
            elif k == 'zctl':
                format_str += '{:f}'.format(v)
            elif k == 'omega':
                format_str += '{:.2f}'.format(v)
            elif k == 'sampling':
                format_str += '{:d}'.format(v)
            elif k == 'sth':
                format_str += '{:.2f}'.format(v)
            else:
                continue

            simcstrs.append(format_str)

        return ';'.join(simcstrs)

    @classmethod
    def from_random(cls):

        """
        Create controls with random values. Kept for backward compatibility; for testing.
        """
        return cls._from_random()

    @classmethod
    def _from_random(cls):

        """
        Create controls with random values. For internal testing.
        """

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
                                
DEF_EMC = {
    'mode': {'defval': DEF_MODE, 'desc': 'Simulation mode'},
    'dsize': {'defval': DEF_CBED_DSIZE, 'desc': 'Diffracted beam size'},
    'zone': {'defval': DEF_ZONE, 'desc': 'Starting zone axis'},
    'tilt': {'defval': DEF_TILT, 'desc': 'Tilt in x and y directions (x, y)'},
    'defl': {'defval': DEF_DEFL, 'desc': 'Shift in x and y directions (x, y)'},
    'cl': {'defval': DEF_CL, 'desc': 'Camera length (mm)'},
    'vt': {'defval': DEF_KV, 'desc': 'High voltage (kV)'},
    'xaxis': {'defval': DEF_XAXIS, 'desc': 'Crystal horizontal axis in reciprocal space'},
    'pix_size': {'defval': DEF_PIXSIZE, 'desc': 'Detector pixel size (microns)'},
    'det_size': {'defval': DEF_DETSIZE, 'desc': 'Detector size (pixels)'},
    'aperture': {'defval': DEF_APERTURE, 'desc': 'Objective lens aperture'},
    'simc': {'defval': None, 'desc': 'Simulation controls'}
} 

# can we use the above lookup for the property docstring?
def doc_dec(k):
    def doc_str(obj):
        obj.__doc__ = obj.__doc__.format(DEF_EMC[k]['desc'])
        return obj
    return doc_str

class EMControl:
    """
    Microscope, sample and detector controls for a simulation, holding the simulation controls
    too. Also available from ``pyemaps`` as ``EMC``.

    * **zone**: starting zone axis
    * **tilt**: sample tilt in x and y, ``(x, y)``
    * **defl**: shift in x and y, ``(x, y)``
    * **cl**: camera length, in mm
    * **vt**: high voltage, in kV
    * **simc**: simulation controls, a :py:class:`SIMControl`

    The simulation methods also record these in it:

    * **mode**: 1 for normal diffraction, 2 for CBED
    * **dsize**: diffracted beam (disk) size, used in CBED mode
    * **aperture**: objective lens aperture
    * **pix_size**: detector pixel size, in µm
    * **det_size**: detector size, in pixels
    * **xaxis**: the crystal's horizontal axis in reciprocal space

    .. code-block:: python

        from pyemaps import Crystal, EMC

        si = Crystal.from_builtin('Silicon')
        emc, dp = si.generateDP(em_controls=EMC(zone=(1, 1, 0), cl=1500))
    """

    def __init__(self, tilt = DEF_TILT, 
                       zone = DEF_ZONE, 
                       defl = DEF_DEFL, 
                       vt = DEF_KV, 
                       cl = DEF_CL,
                       simc = None):
        
        """
        :param tilt: sample tilt ``(x, y)``. Defaults to (0.0, 0.0).
        :type tilt: tuple of float, optional
        :param zone: starting zone axis, three integers, not (0, 0, 0). Defaults to (0, 0, 1).
        :type zone: tuple of int, optional
        :param defl: shift ``(x, y)``. Defaults to (0.0, 0.0).
        :type defl: tuple of float, optional
        :param vt: high voltage, in kV. Defaults to 200.
        :type vt: float, optional
        :param cl: camera length, in mm. Defaults to 1000.
        :type cl: float, optional
        :param simc: simulation controls. Defaults to the default :py:class:`SIMControl`.
        :type simc: :py:class:`SIMControl`, optional
        :raise ~pyemaps.errors.EMCError: if a value is invalid.
        """
        emc_dict = dict(tilt = tilt, 
                       zone = zone, 
                       defl = defl,
                       vt = vt,
                       cl = cl)     
        for k, v in emc_dict.items():
            setattr(self, k, v)
        
        setattr(self, 'simc', SIMControl() if simc is None else simc)

        setattr(self, 'mode', DEF_MODE)
        setattr(self, 'aperture', DEF_APERTURE)
        setattr(self, 'dsize', DEF_CBED_DSIZE) #(not used mode == 1)
        setattr(self, 'pix_size', DEF_PIXSIZE)
        setattr(self, 'det_size', DEF_DETSIZE)
        setattr(self, 'xaxis', DEF_XAXIS)

    def __call__(self, **kwargs):
        """
        Set controls by keyword, e.g. ``emc(mode=2, dsize=0.2)``. Keys that aren't controls are
        ignored, with a message. The simulation methods use this to record the values they ran
        with.
        """
        
        for k, v in kwargs.items():
            if k not in DEF_EMC:
                print(f'key {k} is not in pyemaps microscope control keys, ignored')
                continue    
            setattr(self, k, v)
            
    @classmethod
    def from_dict(cls, emc_dict):

        """
        Create controls from a dictionary.

        :param emc_dict: the controls, with the keys ``tilt``, ``zone``, ``defl``, ``vt`` and
            ``cl``. Other keys are ignored, and the simulation controls are set to their defaults.
        :type emc_dict: dict, required
        :return: the controls.
        :rtype: :py:class:`EMControl`
        :raise ~pyemaps.errors.EMCError: if *emc_dict* isn't a dictionary, or a value is missing or
            invalid.
        """
        if not isinstance(emc_dict, dict):
            raise EMCError('invalid data input in constructing EMC from a dictionary')

        ctor_keys = ('tilt', 'zone', 'defl', 'vt', 'cl')
        kwargs = {}
        sc = None
        for k, v in emc_dict.items():
            if k not in DEF_EMC:
                print(f'Invalid key {k} found in the input, ignored')
                continue

            if k in ctor_keys:
                kwargs[k] = v

            if k == 'simc':
                if isinstance(v, SIMControl):
                    sc = v
                elif isinstance(v, dict):
                    sc = SIMControl()
                    sc(**v)
                elif v is not None:
                    raise EMCError('simc must be a SIMControl object or a dictionary')

        return cls(simc = sc, **kwargs)
  
    @property
    @doc_dec('zone')  
    def zone(self):
        """{0}"""
        return self._zone
    
    @property
    @doc_dec('tilt')  
    def tilt(self):
        '''{0}'''
        return self._tilt
    
    @property
    @doc_dec('defl')  
    def defl(self):
        '''{0}'''
        return self._defl
    
    @property
    @doc_dec('cl')
    def cl(self):
        '''{0}'''
        return self._cl
    
    @property
    @doc_dec('vt')
    def vt(self):
        '''{0}'''
        return self._vt

    @property
    @doc_dec('simc')
    def simc(self):
        '''{0}'''
        return self._simc

    @property
    @doc_dec('xaxis')
    def xaxis(self):
        '''{0}'''
        return self._xaxis
    
    @property
    @doc_dec('aperture')
    def aperture(self):
        '''{0}'''
        return self._aperture

    @property
    @doc_dec('pix_size')
    def pix_size(self):
        '''{0}'''
        return self._pix_size

    @property
    @doc_dec('det_size')
    def det_size(self):
       '''{0}'''
       return self._det_size

    @property
    @doc_dec('mode')
    def mode(self):
        '''{0}'''
        return self._mode

    @property
    @doc_dec('dsize')
    def dsize(self):
       '''{0}'''
       return self._dsize


    @zone.setter
    def zone(self, zv):
        if not isinstance(zv, tuple) or len(zv) != 3 or \
           list(map(type, zv)) != [int, int, int]:
           raise EMCError("Zone axis must be a tuple of three integers")
        
        if zv == (0,0,0):
           raise EMCError("Zone axis must not be (0,0,0)")
  
        self._zone = zv 

    @tilt.setter
    def tilt(self, tl):
        if not isinstance(tl, tuple) or len(tl) != 2:
           raise EMCError("Tilt must be a tuple of two numbers")

        typelist = list(map(type, tl))
        
        for vt in typelist:
            if vt != float and vt != int:
                raise EMCError('Tilt values must be numbers')

        self._tilt = tl

    @defl.setter
    def defl(self, df):
        if not isinstance(df, tuple) or len(df) != 2:
           raise EMCError("Deflection must be a tuple of two numbers")
        
        typelist = list(map(type, df))

        for vt in typelist:
            if vt != float and vt != int:
                raise EMCError('Deflection values must be numbers')

        self._defl = df

    @cl.setter
    def cl(self, clen):
        if not isinstance(clen, (int, float)):
           raise EMCError("Camera length must be a number")
        
        self._cl = clen
    
    @vt.setter
    def vt(self, kv):
        if not isinstance(kv, (int,float)):
           raise EMCError("Voltage must be a number")
        
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
           raise EMCError("Simulation controls must be a SIMControl object")
        
        self._simc = sc
    
    @aperture.setter
    def aperture(self, av):
        if av is None:
            self._aperture = DEF_APERTURE
        else:
            if not isinstance(av, (int,float)):
                raise EMCError("Aperture must be a number")
            
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
            # in case of disk size is set, validate, warn
            if hasattr(self, 'dsize') and mv == 2:
                ds = self._dsize
                ds_min, ds_max = DEF_DSIZE_LIMITS
                
                if ds < ds_min or ds > ds_max:
                    print(f'Warning: beam size is out of range {DEF_DSIZE_LIMITS}')
                    print(f'Please reset the value of beam size before continuing')

            self._mode = mv   

    @dsize.setter
    def dsize(self, dv):
       if dv is None:
            self._dsize = DEF_CBED_DSIZE
       else:     
            if not isinstance(dv, (int,float)):
                    raise EMCError('Diffracted beam size must be a number')

            # in case of CBED mode, the disk size must be in DEF_DSIZE_LIMITS range
            if self._mode == 2:
                ds_min, ds_max = DEF_DSIZE_LIMITS

                if dv < ds_min or dv > ds_max:
                    raise EMCError(f'Beam size is out of range {DEF_DSIZE_LIMITS}')
                
    
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
           return NotImplemented
           
        if self.mode != other.mode or \
           self._pix_size != other.pix_size or \
           self._det_size != other.det_size or \
           self._zone != other.zone or \
           self._xaxis !=other.xaxis:
            # print(f'integer controls: mode pix_size det_size zone or xaxis do not match:')
            return False
        
        if not math.isclose(self._aperture, other.aperture, abs_tol=EMC_TOLERANCE):
            # print(f'aperture controls: does not match: {self._aperture} != {other.aperture}')
            return False
        
        if not math.isclose(self._dsize, other.dsize, abs_tol=EMC_TOLERANCE):
            # print(f'dsize controls: does not match: {self._dsize} != {other.dsize}')
            return False
        
        if not math.isclose(self._vt, other.vt, abs_tol=EMC_TOLERANCE):
            # print(f'vt controls: does not match: {self._vt} != {other.vt}')
            return False
        
        if not math.isclose(self._cl, other.cl, abs_tol=EMC_TOLERANCE):
            # print(f'cl controls: does not match: {self._cl} != {other.cl}')
            return False
        
        for d1, d2 in zip(self._defl, other.defl):
            if not math.isclose(d1, d2, abs_tol=EMC_TOLERANCE):
                # print(f'defl controls: does not match: {self._defl} != {other.defl}')
                return False
            
        for t1, t2 in zip(self._tilt, other.tilt):
            if not math.isclose(t1, t2, abs_tol=EMC_TOLERANCE):
                # print(f'tilt controls: does not match: {self._tilt} != {other.tilt}')
                return False
            
        if not self._simc == other.simc:
            return False
        
        return True

    def __str__(self):
        """
        Return the controls as readable text, one per line, showing the default of any that
        differ from it. The simulation controls follow.
        """
        lines = ['Electron microscope controls']
        for k in DEF_EMC:
            if k in ('dsize', 'simc'):
                continue
            v = getattr(self, k)
            if k == 'mode':
                # The disk size applies only in CBED mode.
                modes = {1: 'Normal', 2: f'CBED, disk size {_num(self._dsize)}'}
                lines.append(_line('Mode', modes.get(v, f'Unknown ({v})'), modes[DEF_MODE]))
            elif k == 'xaxis':
                # (0, 0, 0) lets the simulation choose; it records the axis it chose.
                chosen = any(v)
                lines.append(_line('Horizontal axis', f'({_indices(v)})' +
                                   ('' if chosen else ', chosen by pyEMAPS')))
            else:
                label, fmt = EMC_PRINT[k]
                lines.append(_line(label, fmt(v), fmt(DEF_EMC[k]['defval'])))

        lines.append(str(self._simc))

        return '\n'.join(lines)

    def __repr__(self):
        """Show the controls as ``print`` does: in the console, in Jupyter and in lists."""
        return str(self)

    
    def _check_def(self, k) -> bool:
        '''internal - checking if the attribute k is at default value'''
        if k not in DEF_EMC or not hasattr(self, k):
            
            print(f'Warning: EMControl class does not have {k} attribute')
            return False
        
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
        """
        Format the controls, including the simulation controls, that aren't at their defaults,
        for the captions of the built-in displays.

        :return: the controls, as ``name=value`` pairs separated by semicolons.
        :rtype: str
        """
        emcstrs = []

        for k in DEF_EMC:
            
            if self._check_def(k):
                continue

            format_str = k + '='
            v = getattr(self, k)

            if k == 'mode':
                format_str += 'CBED'
            elif k == 'dsize':
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
                format_str += '{:f}'.format(v)
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
    
    @staticmethod
    def def_dict(): 
        """
        Return the default value of every microscope and simulation control.

        :rtype: dict
        """
        retdict={}
        for k in DEF_EMC:

            if k == 'simc':
                for sk, sv in DEF_SIMC.items():
                    retdict[sk] = sv
                continue

            retdict[k] = DEF_EMC[k]['defval']


        return retdict