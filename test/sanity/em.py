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
Date:       August 25, 2022   

This class is helper for handling pyemaps microscope controls
"""
from pyemaps import dif, bloch
import pyemaps

from . import EMCError, EMSIMError

# retirve the defaults from backend
DEF_EXCITATION              = (dif.DEF_sgmax, dif.DEF_sgmin)
DEF_GMAX                    = dif.DEF_gmax
DEF_BMIN                    = dif.DEF_bmin
DEF_INTCTL                  = dif.DEF_intctl
DEF_INTZ0                   = dif.DEF.INTZ0
DEF_MODE                    = dif.DEF_MODE
DEF_OMEGA                   = dif.DEF_OMEGA
DEF_SAMPLING                = bloch.DEF_SAMPLING
DEF_PIXSIZE                 = bloch.DEF_PIXSIZE
DEF_DETSIZE                 = bloch.DEF_DET


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
    def __init__(self, excit = DEF_EXCITATION,
                       gmax = DEF_GMAX,
                       bmin = DEF_BMIN,
                       intctl = DEF_INTCTL,
                       intz0 = DEF_INTZ0,
                    #    mode = DEF_MODE,
                       **args):
        
        # excit=gmax=bmin=intclt=intz0=mode=
        # if args.has_key( "extcitation" ):
        #     excit = args["extcitation"]
        # else:
        #     excit = DEF_EXCITATION

        # if args.has_key( "gmax" ):
        #     gmax = args["gmax"]
        # else:
        #     gmax = DEF_GMAX

        # if args.has_key( "bmin" ):
        #     bmin = args["bmin"]
        # else:
        #     bmin = DEF_BMIN

        # if args.has_key( "intctl" ):
        #     intctl = args["intctl"]
        # else:
        #     intctl = DEF_INTCTL

        # if args.has_key( "intz0" ):
        #     intz0 = args["intz0"]
        # else:
        #     intz0 = DEF_INTZ0

        # if args.has_key( "mode" ):
        #     mode = args["intz0"]
        # else:
        #     mode = DEF_MODE

        if args.has_key( "omega" ):
            omega = args["omega"]
        elif args.has_key( "sampling" ):
            omega = DEF_OMEGA
            sampling = args["sampling"]
        elif args.has_key( "pixsize" ):
            sampling = DEF_SAMPLING
            pixsize = args["pixsize"]
        elif args.has_key( "detsize" ):
            pixsize = DEF_PIXSIZE
            detsize = args["detsize"]
        else:
            detsize = DEF_DETSIZE
            if len(args) > 0:
                raise EMSIMError('Unrecognized input')

        setattr(self, 'excitation', excit)
        setattr(self, 'gmax', gmax)
        setattr(self, 'bmin', bmin)
        setattr(self, 'intctl', intctl)
        setattr(self, 'intz0', intz0)
        # setattr(self, 'mode', mode)
        setattr(self, 'omega', omega)
        setattr(self, 'sampling', sampling)
        setattr(self, 'pixsize', pixsize)
        setattr(self, 'detsize', detsize)

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
    def intctl(self):
       return self._intctl

    @property
    def intz0(self):
       return self._intz0

    @property
    def mode(self):
       return self._mode

    @property
    def omega(self):
       return self._omega

    @property
    def sampling(self):
       return self._sampling

    @property
    def pixsize(self):
       return self._pixsize

    @property
    def detsize(self):
       return self._detsize


    @excitation.setter
    def loc(self, excit):
       if not excit or \
          not isinstance(excit, tuple) or \
          len(excit) != 2 or \
          isinstance(excit[0], (int, float)) or \
          isinstance(excit[1], (int, float)):
              raise EMSIMError('Excitation values must be a tuple of tow numbers')
       
       self._excitation = excit

    @gmax.setter
    def loc(self, gm):
       if isinstance(gm, (int, float)):
              raise EMSIMError('gmax values must be a tuple of tow numbers')
       
       self._gmax = gm

    @bmin.setter
    def loc(self, bm):
       if isinstance(bm, (int, float)):
              raise EMSIMError('bmin values must be a tuple of tow numbers')
       
       self._bmin = bm

    @intctl.setter
    def loc(self, intc):
       if isinstance(intc, int):
              raise EMSIMError('kinematic intensity values must be an integer')
       
       self._intctl = intc

    @intz0.setter
    def loc(self, intz):
       if isinstance(intz, float):
              raise EMSIMError('kinematic intensity values must be an integer')
       
       self._intz0 = intz

    # @mode.setter
    # def loc(self, mode):
    #    if isinstance(mode, int):
    #           raise EMSIMError('kinematic mode values must be an integer of 1 or 2')
       
    #    self._mode = mode

    @omega.setter
    def loc(self, om):
       if isinstance(om, int):
              raise EMSIMError('kinematic intensity values must be an integer')
       
       self._omega = om

    @sampling.setter
    def loc(self, sam):
       if isinstance(sam, int):
              raise EMSIMError('dynamic diffraction sampling values must be an integer')
       
       self._sampling = sam

    @pixsize.setter
    def loc(self, ps):
       if isinstance(ps, int):
              raise EMSIMError('bloch simulation parameters must be an integer')
       
       self._pixsize = ps

    @detsize.setter
    def loc(self, dts):
       if isinstance(dts, int):
              raise EMSIMError('dynamic diffraction sampling values must be an integer')
       
       self._detsize = dts
           
    def __eq__(self, other):

       if not isinstance(other, SIMControl):
              return False

       if self._excitation != other.excitation: 
              return False

       if self._gmax != other.gmax:
              return False

       if self._bmin != other.bmin:
              return False

       if self._intctl != other.intctl: 
              return False

       if self._intz0 != other.intz0:
              return False

    #    if self._mode != other.mode:
    #           return False

       if self._omega != other.omega:
              return False

       if self._sampling != other.sampling:
              return False

       if self._pixsize != other.pixsize:
              return False

       if self._detsize != other.detsize:
              return False

       return True
    
    def __str__(self) -> str:
       
       simulation = ['Simulation Controls Parameters:']

    #    simulation.append('Mode: ' + 'Normal' if self._mode == DEF_MODE else 'CBED')
       simulation.append('excitation: ' +  str(self._exciation))
       simulation.append('gmax??: ' + str(self._gmax))
       simulation.append('bmin??: ' + str(self._bmin))
       simulation.append('kinematic intensity limit: ' + str(self._intctl))
       simulation.append('kinematic intensity control limit??: ' + str(self._intz0))
       simulation.append('Omega??: ' + str(self._omega))
       simulation.append('Sampling??: ' + str(self._sampling))
       simulation.append('pixsize??: ' + str(self._pixsize))
       simulation.append('detsize??: ' + str(self._detsize))

       return "\n ".join(simulation)

DEF_TILT             = dif.DEF_TILT
DEF_NORM_DSIZE       = dif.NORM_DISK_SIZE
DEF_CBED_DSIZE       = dif.CBED_DISK_SIZE
DISK_MIN             = 0.01 #??
DISK_MAX             = 4.0  #??
DEF_CL               = dif.DEF_CL
DEF_KV               = dif.DEF_KV
DEF_DEFL             = (DEF_TILT, DEF_TILT, DEF_TILT)
DEF_APERTURE         = bloch.DEF_APER

# DEF_EMCONTROLS = dict(
#                     cl = DEF_CL,
#                     vt = DEF_KV,
#                     defl = DEF_DEFL,
#                     ds = DEF_NORM_DSIZE
#                     )

# class MICControl:
#     '''
#     Microscope Control Parameter:
#         initializing class with a control dictionary of the format:
#         camera length                  cl
#         high voltage                   vt
#         deflection:                    defl
#         beams convergence angle        ds 
#         aperture:                      aper??
#     This is the newer version of EMControl class
#     '''
#     def __init__(self, cl = None, 
#                        vt = None, 
#                        defl = None,
#                        aper = None):
        
#         if not defl:
#             defl = DEF_DEFL

#         if not vt:
#             vt = DEF_KV

#         if not cl:
#             cl = DEF_CL

#         if not ds:
#             ds = DEF_NORM_DSIZE

#         if not aper:
#             aper = DEF_APERTURE

#         emc_dict = dict(defl = defl,
#                        vt = vt,
#                        cl = cl,
#                        ds = ds,
#                        aper =aper)
        
#         for k, v in emc_dict.items():
#             setattr(self, k, v)

#     @classmethod
#     def from_dict(cls, emc_dict):

#         if not isinstance(emc_dict, dict):
#             raise EMCError('invalid data input in constructing EMC from a dictionary')

#         d = vt = c = dk = ap = None 
#         for k, v in emc_dict.items():
#             if k not in DEF_EMCONTROLS:
#                 print(f'Invilid key {k} found in the input, ignored')
#                 continue
            
#             if k == 'defl':
#                 d = v
#             if k == 'vt':
#                 vt = v
#             if k == 'cl':
#                 c = v
#             if k == 'ds':
#                 dk = v
#             if k == 'aper':
#                 ap = v

#         return cls(defl = d, vt = vt,
#                    cl = c, ds = dk, aper=ap)
    
#     @property
#     def defl(self):
#         return self._defl
    
#     @property
#     def cl(self):
#         return self._cl
    
#     @property
#     def vt(self):
#         return self._vt
    
#     @property
#     def ds(self):
#         return self._ds
    
#     @property
#     def aper(self):
#         return self._aper

#     @cl.setter
#     def cl(self, clen):
#         if not isinstance(clen, int) and not isinstance(clen, float):
#            raise ValueError("Camera length must be of number")

#         self._cl = clen
    
#     @vt.setter
#     def vt(self, kv):
#         if not isinstance(kv, int) and not isinstance(kv, float):
#            raise EMCError("Voltage must be of integer")
        
#         self._vt = kv

#     @defl.setter
#     def defl(self, df):
#         if not isinstance(df, tuple) or len(df) != 2:
#            raise EMCError("deflection must be tuple of two numbers")
        
#         typelist = list(map(type, df))

#         for vt in typelist:
#             if vt != float and vt != int:
#                 raise EMCError('Input values for deflection must be numeric')

#         self._defl = df
    
#     @ds.setter
#     def ds(self, dv):
#         if not isinstance(dv, int) and not isinstance(dv, float):
#            raise EMCError("Voltage must be of integer")
        
#         if dv < DISK_MIN or dv > DISK_MAX:
#             raise EMCError("Beam diffraction angle too small")

#         self._ds = dv
    
#     @aper.setter
#     def ds(self, ap):
#         if not isinstance(ap, int) and not isinstance(ap, float):
#            raise EMCError("Aperture must be numberal")
        
#         self._aper = ap

#     def __eq__(self, other):
#         if not isinstance(other, MICControl):
#            raise EMCError("Comparison must be done with EMControl object")

#         if other.defl != self._defl:
#             return False 

#         if other.cl != self._cl:
#             return False 

#         if other.vt != self._vt:
#             return False 

#         if other.ds != self._ds:
#             return False 

#         if other.aper != self._aper:
#             return False 

#         return True


#     def __str__(self):
#         cstr = ['Microscope Control Parameters:']
        
#         cstr.append('Camera Length: ' + str(self._cl))
#         cstr.append('Voltage: ' + str(self._vt))
#         cstr.append('Deflection: ' + str(self._defl))
#         cstr.append('Beam Diffraction Angle: ' + str(self._ds))
#         cstr.append('Aperture: ' + str(self._aper))

#         return '\n'.join(cstr)

# DEF_TILT             = (DEF_TILT, DEF_TILT, DEF_TILT)
# DEF_ZONE             = (0,0,1)
# DEF_XAXIS            = (0,0,0)
# DEF_THICKNESS        = bloch.DEF_THICKNESS

# class SAMControl:
#     '''
#        Sample control parameter class
#        x-axis
#     #    tilt:                (x,y)
#     #    zone                 (0,0,1)
#        thickness            only applied to dynamic diffraction
#     '''
     
#     def __init__(self, #zone = None, 
#                        #tilt = None, 
#                        xaxis = None, 
#                        thickness = None):
       
#     #    if not zone:
#     #           zone = DEF_ZONE
       
#     #    if not tilt:
#     #           tilt = DEF_TILT
       
#        if not xaxis:
#               xaxis = DEF_XAXIS
       
#        if not thickness:
#               xaxis = DEF_THICKNESS

#     #    setattr(self, 'zone', zone)
#     #    setattr(self, 'tilt', tilt)
#        setattr(self, 'xaxis', xaxis)
#        setattr(self, 'thickness', thickness)

#     # @property
#     # def zone(self):
#     #     return self._zone
    
#     # @property
#     # def tilt(self):
#     #     return self._tilt

#     @property
#     def xaxis(self):
#         return self._xaxis
    
#     @property
#     def thickness(self):
#         return self._thickness

#     # @zone.setter
#     # def zone(self, zv):
#     #     if not isinstance(zv, tuple) or len(zv) != 3 or \
#     #        list(map(type, zv)) != [int, int, int]:
#     #        raise EMCError("Zone axis must be tuple of three intergers")
        
#     #     if zv == (0,0,0):
#     #        raise EMCError("Zone axis must not be (0,0,0)")

#     #     self._zone = zv 

#     # @tilt.setter
#     # def tilt(self, tl):
#     #     if not isinstance(tl, tuple) or len(tl) != 2:
#     #        raise EMCError("Tilt must be tuple of two numbers")

#     #     typelist = list(map(type, tl))
        
#     #     for vt in typelist:
#     #         if vt != float and vt != int:
#     #             raise EMCError('Input values for tilt must be nmeric')

#     #     self._tilt = tl

#     @xaxis.setter
#     def zone(self, xv):
#         if not isinstance(xv, tuple) or len(xv) != 3 or \
#            list(map(type, xv)) != [int, int, int]:
#            raise EMCError("Zone axis must be tuple of three intergers")
        
#         if xv == (0,0,0):
#            raise EMCError("Zone axis must not be (0,0,0)")

#         self._xaxis = xv 

#     @thickness.setter
#     def thicknes(self, tv):
#         if not isinstance(tv, (int, float)):
#            raise EMCError("Tilt must be tuple of two numbers")

#         self._thickness = tv

#     def __eq__(self, other):
#         if not isinstance(other, SAMControl):
#            raise EMCError("Comparison must be done with EMControl object")
        
#         # if other.zone != self._zone:
#         #     return False 

#         # if other.tilt != self._tilt:
#         #     return False 

#         if other.xaxis != self._xaxis:
#             return False 

#         if other.thickness != self._thickness:
#             return False 

#         return True


#     def __str__(self):

#         cstr = ['Sample Control Parameters:']

#         # cstr.append('Zone: ' + str(self._zone))
#         # cstr.append('Tilt: ' + str(self._tilt))
#         cstr.append('xaxis: ' + str(self._xaxis))
#         cstr.append('Thickness: ' + str(self._thickness))
        
#         return '\n'.join(cstr)
    
class EM:
    '''
    All diffraction simulations controls
    '''
    def __init__(self, em_ctrl=MICControl(), 
                       sam_ctrl=SAMControl(), 
                       sim_ctrl=SAMControl()):
        pass
           
