# '''
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
# 
# Author:     EMLab Solutions, Inc.
# Date:       May 07, 2022    
# '''
'''
Kinematic diffraction module is designed to handle kinematic simulation
data. It is composed of Point, Line and Disk class objects.

'''
from . import EMC, SIMC
from . import DPError, PointError, LineError, PIndexError, \
              DiskError, DPListError

# precision digits for comparison purposes
NDIGITS = 1
DIFF_PRECISION = 0.95
MIN_OPACITY = 0.2
MAX_OPACITY = 0.35

from . import XMAX, YMAX
#int: Diffraction simulation output limits

DEF_MODE = 1 
#int: Default diffraction simulation mode, normal

def _double_eq(a,b):
    '''
    For internal testing only
    '''
    return abs(a-b) <= DIFF_PRECISION

class Point:
    '''
    Coordinates of kinematic diffraction pattern object.
    
    '''
    def __init__(self, p=(0.0, 0.0)):

        setattr(self, 'x', p[0])
        setattr(self, 'y', p[1])

    @property
    def x(self):
        '''
        X coordinate
        '''
        return self._x
    
    @property
    def y(self):
        '''
        Y coordinate
        '''
        return self._y

    @x.setter
    def x(self, v):
        
        try:
            self._x=float(v)
        except ValueError as e:
            raise PointError("Point component must be floating point nuberic type")

    @y.setter
    def y(self, v):
        
        try:
            self._y=float(v)
        except ValueError as e:
            raise PointError("Point component must be floating point nuberic type")
    
    def __lt__(self, other):
        if isinstance(other, Point):
            x1 = self._x
            x2 = other.x

            if x1 != x2:
                return x1 < x2

            y1 = self._y
            y2 = other.y

            if y1 != y2:
                return y1 < y2

            return False

        raise PointError("comparison must be of Point objects")

    def __imul__(self, rhs):
        if not isinstance(rhs, int) and not isinstance(rhs, float):
            raise ValueError('right hand side must be numberic')
        
        self._x *= rhs
        self._y *= rhs

        return self
            
    def __iadd__(self, other):
        if isinstance(other, Point):
            self._x += other.x
            self._y += other.y
            return self

        raise PointError("addition of different type other than Point type not supported")
    
            
    def __isub__(self, other):
        if isinstance(other, Point):
            self._x -= other.x
            self._y -= other.y
            return self

        raise PointError("subtraction of different type other than Point type not supported")
    
    def __key__(self):
        return (self._x, self._y)
    
    def __hash__(self):
        return hash(self.__key__())
    
    def __eq__(self, other):
        if isinstance(other, Point):
            return _double_eq(self._x, other.x) and \
                   _double_eq(self._y, other.y)

        raise PointError("comparison must be of Point objects")

    def __repr__(self):
        return str("({}, {})".format(self._x, self._y))

    def __iter__(self):
        return iter((self._x, self._y))

class Line:
    '''
    Kikuchi line representation in kinematic diffraction patterns.
    
    '''
    def __init__(self, pt1 = Point(), pt2=Point(), intensity=0, type=1):
        
        setattr(self, 'pt1', pt1)  
        setattr(self, 'pt2', pt2)    
        setattr(self, 'intensity', intensity)    
        setattr(self, 'type', type)

    @property
    def pt1(self):
        '''
        The first end point of a Line

        '''
        return self._pt1

    @property
    def pt2(self):
        '''
        The second end point of a Line

        '''
        return self._pt2
    
    @property
    def type(self):
        '''
        The type of a Line: Kikuchi line or HOLZ line

        '''
        return self._type
    
    @property
    def intensity(self):
        '''
        Line intensity

        '''
        return self._intensity

    @pt1.setter
    def pt1(self, pv):
        if not isinstance(pv, Point):
            raise LineError("end points must be of Point type")

        self._pt1 = pv

    @pt2.setter
    def pt2(self, pv):
        if not isinstance(pv, Point):
            raise LineError("end points must be of Point type")

        self._pt2 = pv  

    @type.setter
    def type(self, ty):
        if not isinstance(ty, int):
            raise LineError("type must be integer")

        self._type = ty 

    @intensity.setter
    def intensity(self, intense):
        if not isinstance(intense, (int, float)):
            raise LineError("intensity must be integer or float")

        self._intensity = intense

    def __lt__(self, other):

        if isinstance(other, Line):
            if self._type == other.type:
                return False

            pt1 = self._pt1
            pt2 = other.pt1
            if not (pt1 == pt2):
                return pt1 < pt2

            pt1 = self._pt2
            pt2 = other.pt2
            if not (pt1 == pt2):
                return pt1 < pt2

            if self._intensity != other.intensity:
                return self._intensity < other.intensity

            return False
        
        raise LineError("comparison must be between Line objects")
    
    def __key__(self):
        return (self._pt1, self._pt2, self._intensity)
    
    def __hash__(self):
        return hash(self.__key__())
    
    def __isub__(self, other):
        '''
        This operator override is for shifting the line by fixed amount 
        by 2D vector

        '''
        if isinstance(other, Point):
            self._pt1 -= other
            self._pt2 -= other
            return self
        
        raise LineError("substraction of Line class from non-Point class type not supported")
    
    def __iadd__(self, other):
        '''
        This operator override is for shifting the line by fixed amount when
        other line object has the same pt1 and ot2
        '''
        if isinstance(other, Point):
            self._pt1 += other
            self._pt2 += other
            return self
        
        raise LineError("addition of different type not supported")

    def __imul__(self, rhs):
        if not isinstance(rhs, int) and not isinstance(rhs, float):
            raise ValueError('right hand side must be numberic')
        
        self._pt1 *= rhs
        self._pt2 *= rhs

        return self

    def __eq__(self, other):
        if isinstance(other, Line):
            if self._type != other.type:
                return False

            if self._intensity != other.intensity:
                return False

            if not (self._pt1 == other.pt1) or \
               not (self._pt2 == other.pt2):
                return False

            return True

        return False 

    def __repr__(self):
        return str("[{}, {}], {}".format(self._pt1.__repr__(), 
                                         self._pt2.__repr__(), 
                                         self._intensity))

    def __iter__(self):
        x1, y1 = self._pt1
        x2, y2 = self._pt2
        return iter((x1,y1,x2,y2,self._intensity))

    def calOpacity(self, l, h):
        """
        Calculate the line opacity based on its intensity value

        0.2 -> lowest intensity
        0.35-> highest intensity

        """
        if h==l:
            return 0.35

        return MIN_OPACITY + ((self._intensity-l)*(MAX_OPACITY-MIN_OPACITY))/(h-l)

    # def calLineWidth(self, l, h):
    #     """
    #     Calculate the line width based on its intensity value

    #     1.0 -> lowest intensity
    #     1.75-> highest intensity

    #     """
    #     if h==l:
    #         return 1.75

    #     return 1.0 + ((self._intensity-l)*3)/(4.0*(h-l))



    def to_dict(self):
        x1, y1 = self._pt1
        x2, y2 = self._pt2
        return {'pt1': (x1,y1),
                'pt2': (x2,y2), 
                'int': self._intensity}

class Index:
    '''
    Miller Indexes of a diffracted beam representation in kinematic
    diffraction pattern.

    '''
    def __init__(self, I0=(0,0,0)):

        setattr(self, 'I1', I0[0])
        setattr(self, 'I2', I0[1])
        setattr(self, 'I3', I0[2])

    @property
    def I1(self):
        '''
        The first element of Miller Index of a diffracted beam

        '''
        return self._I1

    @property
    def I2(self):
        '''
        The second element of Miller Index of a diffracted beam

        '''
        return self._I2

    @property
    def I3(self):
        '''
        The third element of Miller Index of a diffracted beam

        '''
        return self._I3
        
    @I1.setter
    def I1(self, iv):
        if not isinstance(iv, int):
            raise PIndexError('index must be integer')

        self._I1 = iv
        
    @I2.setter
    def I2(self, iv):
        if not isinstance(iv, int):
            raise PIndexError('index must be integer')

        self._I2 = iv
        
    @I3.setter
    def I3(self, iv):
        if not isinstance(iv, int):
            raise PIndexError('index must be integer')

        self._I3 = iv

    def __lt__(self, other):
        if isinstance(other, Index):
            ii1 = self._I1
            ii2 = other.I1
            if ii1 != ii2:
                return ii1 < ii2
            
            ii1 = self._I2
            ii2 = other.I2
            if ii1 != ii2:
                return ii1 < ii2

            ii1 = self._I3
            ii2 = other.I3
            if ii1 != ii2:
                return ii1 < ii2
            return False

        raise PIndexError('cannot compare with non-Index type')
    
    def __key__(self):
        return (self._I1, self._I2, self._I3)
    
    def __hash__(self):
        return hash(self.__key__())
    
    def __str__(self):
        return str("{} {} {}".format(self._I1, self._I2, self._I3))

    def __repr__(self):
        return str("({}, {}, {})".format(self._I1, self._I2, self._I3))
    
    def __eq__(self, other):
        if isinstance(other, Index):
            return self.__key__() == other.__key__()

        raise PIndexError('cannot compare with non-Index type')
    
    def __iter__(self):
        return iter((self._I1, self._I2, self._I3))

class Disk:
    '''
    Diffracted beams representation in kinematic diffraction patterns

    '''
    def __init__(self, c=Point(), r=0.0, i=Index()):

        setattr(self, 'c', c)
        setattr(self, 'r', r)
        setattr(self, 'idx', i)

    @property 
    def c(self):
        '''
        The center point of a diffracted beam.

        '''
        return self._c
    
    @property
    def r(self):
        '''
        The radius of a diffracted beam.

        '''
        return self._r
    
    @property
    def idx(self):
        '''
        The Miller index of a diffracted beam.

        '''
        return self._idx

    @c.setter
    def c(self, cv):
        
        if not isinstance(cv, Point):
            raise DiskError('disk center must be of Point type')
        
        self._c = cv

    @r.setter
    def r(self, rv):
        
        if not isinstance(rv, float):
            raise DiskError('disk radius must be of float type')
        
        self._r = rv

    @idx.setter
    def idx(self, iv):
        
        if not isinstance(iv, Index):
            raise DiskError('disk index must be of Index type')
        
        self._idx = iv
        
    def __eq__(self, other):
        if not isinstance(other, Disk):
            raise DiskError('disk object cannot equal to non disk object')
        
        if not (self._idx == other.idx) or self._r != other.r:
            
            return False

        if not (self._c == other.c):
            return False

        return True
    
    def __iadd__(self, other):
        '''
        This operator override is for shifting the line when
        other line object has the same pt1 and ot2
        '''
        if isinstance(other, Point):
            self._c += other
            return self
        
        raise DiskError('addition cannot be done with non-Disk type')
    
    def __isub__(self, other):
        '''
        This operator override is for shifting the line when
        other line object has the same pt1 and ot2
        '''
        if isinstance(other, Point):
            self._c -= other
            return self
        
        raise DiskError('substraction cannot be done with non-Point type')
    
    def __imul__(self, rhs):
        
        if not isinstance(rhs, int) and not isinstance(rhs, float):
            raise ValueError('right hand side must be numberic')

        self._c *= rhs
        self._r *= rhs

        return self

    def __key__(self):
        center = self._c
        r = self._r
        indx = self._idx
        return (indx.I1, indx.I2, indx.I3, center.x, center.y, r)

    def __hash__(self):
        return hash(self.__key__())

    def __repr__(self):
          
        return "index: " + repr(self._idx) + " " + \
               "center: " + repr(self._c) + " " + \
               str("radius: {}".format(self._r))

    def to_dict(self):
        '''
        Creates a diffracted beam object from a dict pyton object

        '''
        dd = {}  
        dd['c'] = self._c.__key__()
        dd['idx'] = self._idx.__key__()
        dd['r'] = self._r
        return dd

    def __lt__(self, other):
        if not isinstance(other, Disk):
            raise DiskError('comparison cannot be done with non-Disk type')

        if not (self._idx == other.idx):
           return self._idx < other.idx

        if not (self._c == other.c):
           return self._c < other.c

        if self._r != other.r:
            return self._r < other.r 

        return False

    def __iter__(self):
        cx, cy = self._c
        i1, i2, i3 = self._idx
        return iter((cx, cy, self._r, i1, i2, i3))

class diffPattern:
    '''
    Create a kinematic diffraction pattern based on the pyemaps
    kinematic simulation output in python dict object.

    See :doc:Visualization for how to visualize 
    kinematic diffraction patterns using this object.

    '''
    def __init__(self, diff_dict):
        '''
        :param diff_dict: Only accepts output from pyemaps kinematic diffraction run.
        :type diff_dict: dict, required

        '''
        if not diff_dict or not isinstance(diff_dict, dict):
            raise DPError("failed to construct diffraction pattern object")


        if 'nums' not in diff_dict or \
           'name' not in diff_dict or \
           'klines' not in diff_dict or \
           'hlines' not in diff_dict or \
           'disks' not in diff_dict:
            raise DPError("Invalid diffraction data")

        ndiffs = diff_dict['nums']
        if not isinstance(ndiffs, dict) or \
           'nklines' not in ndiffs or \
           'nhlines' not in ndiffs or \
           'ndisks' not in ndiffs:
            raise DPError("Invaild diffraction data")

        if 'bounds' not in diff_dict:
            setattr(self, 'shift', [0.0,0.0])
        else:
        # set the shifts first
            setattr(self, 'shift', diff_dict['bounds'])


        for k, v in diff_dict.items():
            if k != 'nums' and k != 'bounds':
                setattr(self, k, v)

            elif k == 'nums':
                
                for k1, v1 in v.items():
                    setattr(self, k1, v1)

    @property
    def klines(self):
        ''' Kikuchi lines array '''
        return self._klines

    @property
    def hlines(self):
        ''' Holz lines array '''
        return self._hlines

    @property
    def disks(self):
        ''' Disks array '''
        return self._disks

    @property
    def nklines(self):
        ''' Number of Kikuchi lines '''
        return self._nklines

    @property
    def nhlines(self):
        ''' Number of HOLZ lines '''
        return self._nhlines

    @property
    def ndisks(self):
        ''' Number of Disks '''
        return self._ndisks

    @property
    def shift(self):
        ''' Shifts of the diffraction pattern '''
        return self._shift

    @property
    def name(self):
        ''' Crystal name '''
        return self._name

    @klines.setter
    def klines(self, kls):
        
        if not hasattr(kls, "__len__"):
            raise DPError("klines data invalid")
        
        self._klines = []
        for k in kls:
            try:
                x1,y1,x2,y2,intensity = k

            except Exception as e:
                raise DPError(f'kline data invalid: {e}')

            else:
                pt1 = Point(p=(x1,y1))
                pt2 = Point(p=(x2,y2))

                pt1 -= self._shift
                pt2 -= self._shift

                ln = Line(pt1 = pt1, 
                          pt2 = pt2, 
                          intensity=intensity)

                self._klines.append(ln)

    @hlines.setter
    def hlines(self, hls):
        
        if not hasattr(hls, "__len__"):
            raise DPError("hlines data invalid")
        
        self._hlines = []
        for h in hls:
            try:
                x1,y1,x2,y2,intensity = h

            except Exception as e:
                raise DPError(f'hlines data invalid: {e}')
                
            else:
                pt1 = Point(p=(x1,y1))
                pt2 = Point(p=(x2,y2))


                pt1 -= self._shift
                pt2 -= self._shift

                ln = Line(pt1 = pt1, 
                          pt2 = pt2, 
                          type = 2,
                          intensity=intensity)

                self._hlines.append(ln)

    @disks.setter
    def disks(self, dks):
        
        if not hasattr(dks, "__len__"):
            raise DPError("disks must be an array of Disk objects")
        
        self._disks =[]
        for d in dks:
            if not "c" in d or len(d['c']) != 2:
                raise DPError("disks must have a center of Point type")
            
            if not "r" in d or not isinstance(d['r'], float):
                raise DPError("disks must have a radius")

            if not "idx" in d or len(d['idx']) != 3 or \
                list(map(type, d['idx'])) != [int, int, int]:
                raise DPError("disks must be an index of three integers")

            ctr = Point(d['c'])
            ctr -= self._shift
            
            r = d['r']
            indx = Index(d['idx'])
            dk = Disk(ctr, r, indx)

            self._disks.append(dk)

    @name.setter
    def name(self, name):
        
        if not isinstance(name, str):
            raise DPError("name must be of string type")

        self._name = name

    @shift.setter
    def shift(self, sft):
        
        if isinstance(sft, tuple) and \
            list(map(type, sft)) != [float, float]:
            raise DPError("diffraction pattern shift must be a tuple of two floats")

        self._shift = Point(sft)

    @nklines.setter
    def nklines(self, nk):
        
        if not isinstance(nk, int):
            raise DPError("input must be integer")

        self._nklines = nk

    @nhlines.setter
    def nhlines(self, nh):
        
        if not isinstance(nh, int):
            raise DPError("input must be integer")
            
        self._nhlines = nh

    @ndisks.setter
    def ndisks(self, nd):
        
        if not isinstance(nd, int):
            raise DPError("input must be integer")
            
        self._ndisks = nd

    def __eq__(self, other):

        if not isinstance(other, diffPattern):
            raise DPError("DP object does not compare with objects of rother types")
        
        if self._name != other.name:
            return False

        if self._nklines != other.nklines or \
            self._ndisks != other.ndisks or \
            self._nhlines != other.nhlines:
            return False

        if len(self._klines) != len(other.klines) or \
            len(self._disks) != len(other.disks) or \
            len(self._hlines) != len(other.hlines):
            return False

        dk, dh, dd = self.difference(other)
        if len(dk) != 0 or len(dh) != 0 or len(dd) != 0:
            return False

        dk, dh, dd = other.difference(self)
        if len(dk) != 0 or len(dh) != 0 or len(dd) != 0:
            return False

        return True
            
    def __contains__(self, lc):

        if (not isinstance(lc, Line)) and (not isinstance(lc, Disk)):
            raise DPError("DP object does not contain other types other than defined lines, disks")
        
        dlist = []
        if isinstance(lc, Line) and lc.type == 1:
            dlist = self.klines

        elif isinstance(lc, Line) and lc.type == 2:
            dlist = self.hlines

        else:
            dlist = self.disks

        for l in dlist:
            if l == lc:
                return True 

        return False

    def __str__(self):

        sDiff=[str(f'# of Kikuchi lines (kline): {self._nklines}')]
        for i, k in enumerate(self._klines):
            sDiff.append(str("kline# {}:".format(i+1)).ljust(10) + repr(k))

        sDiff.append(str(f'\n# of diffracted beams (disk, index = Miller Index): {self._nklines}'))
        for i, d in enumerate(self._disks):
            sDiff.append(str("disk# {}:".format(i+1)).ljust(10) + repr(d))
        
        sDiff.append(str(f'\n# of HOLZ lines (hline): {self._nhlines}'))
        for i, h in enumerate(self._hlines):
            sDiff.append(str("hline# {}:".format(i+1)).ljust(10) + repr(h))
        
        return "\n".join(sDiff)

    def _difference(self, other):
        '''Internal testing use only'''
        # A - B (self - other)
        if not isinstance(other, diffPattern):
            raise DPError("DP object does not compare with objects of DP types")
        
        kdiff = []
        for sk in self._klines:
            if not (sk in other):
                kdiff.append(sk)

        hdiff = []
        for sh in self._hlines:
            if not (sh in other):
                hdiff.append(sh)

        ddiff = []
        for d in self._disks:
            if not (d in other):
                ddiff.append(d)
        
        return (kdiff, hdiff, ddiff)

    def to_dict(self):
        retdict = {}
        
        retdict['klines'] = [kl.to_dict() for kl in self._klines]
        retdict['hlines'] = [hl.to_dict() for hl in self._hlines]
        retdict['disks'] = [d.to_dict() for d in self._disks]
        return retdict

class Diffraction:
    '''
    List of DP objects and its associated EMControl objects.

    '''
    def __init__(self, name, mode=DEF_MODE):
        
        setattr(self, 'name', name)
        setattr(self, 'mode', mode)
        setattr(self, 'diffList', [])

    @property
    def name(self):
        return self._name

    @property
    def mode(self):
        return self._mode
    
    @property
    def diffList(self):
        return self._diffList

    @name.setter
    def name(self, n):
        if not isinstance(n, str) or len(n) == 0:
            raise DPListError('crystal name invalid')
        
        self._name = n

    @mode.setter
    def mode(self, md):
        
        if not isinstance(md, int) or (md != 1 and md != 2):
            raise DPListError('DP mode can only be 1 - normal and 2 - CBED')
        
        self._mode = md

    @diffList.setter
    def diffList(self, dpl):
        if not isinstance(dpl, list):
            raise DPListError('invalid input DP list')

        for emc, dp in dpl:
            if not isinstance(dp, diffPattern) or \
               not isinstance(emc, EMC):
                raise DPListError('invalid data found in DP list')

        self._diffList = dpl

    # Adding new diffraction patterns
    def add(self, emc, diffP):
        '''
        Append a new kenematic diffraction pattern with its associated 
        controls
        '''
        if not isinstance(diffP, diffPattern):
            raise DPListError('failed to add DP')


        self.diffList.append((emc, diffP))
    
    def sort(self):
        ''' Sorting diffraction list by controls'''
        self._diffList.sort(key=lambda x: x[0])
            
    def __eq__(self, other):
        '''Test if two diffraction list is the same'''
        if not isinstance(other, Diffraction):
            return False
        
        if self._name != other.name or self._mode != other.mode:
            return False

        if len(self._diffList) != len(other.diffList):
            return False

        found = False
        for c, d in self:
            found = False
            
            for oc, od in other.diffList:
                if c == oc:
                    found = (d==od)
                    if not found:
                        break
            if found:
                continue
            else:
                break
        
        return found
            
    def __getitem__(self, key):
        '''
        Array like method for retrieving DP
        '''
        return self._diffList[key]

    def _report_difference(self, other):
        """ internal testing call"""
        if not isinstance(other, Diffraction):
            raise DPListError('connt report difference between two different type of objects')
        
        rep = []
        if self == other:
            return rep
        
        if self._name != other.name or self._mode != other.mode:
            rep.append(str(f"Diffractions are generated in different mode/name" ))
            return rep


        for c, d in self:
            cl = list(c.values())
            for oc, od in other:
                ocl = list(oc.values())
                
                if cl == ocl:
                    if not (d == od):
                        dk,dh,dd = d.difference(od)
                        dk2,dh2,dd2 = od.difference(d)

                        details =[]
                        details.append(str(f"Control parameters: {c}"))
                        klen, hlen, dlen = len(dk), len(dh), len(dd)
                        klen2, hlen2, dlen2 = len(dk2), len(dh2), len(dd2)

                        if klen > 0:
                            details.append(str(f"{klen} klines in the new run, not in the baseline:"))
                            # save.writelines(str(f"{klen} klines in the new run, not in the baseline:"))
                            for k in dk:
                                details.append("   " + str(k))
                        if klen2 > 0:
                            details.append(str(f"{klen2} klines in the baseline, not in the new run:"))
                            # save.writelines(str(f"{klen} klines in the new run, not in the baseline:"))
                            for k in dk2:
                                details.append("   " + str(k))
                                
                        if dlen > 0:
                            details.append(str(f"{dlen} disks in the new run, not in the baseline:"))
                            # save.writelines(str(f"{klen} klines in the new run, not in the baseline:"))
                            for d in dd:
                                details.append("   " + str(d))
                        if dlen2 > 0:
                            details.append(str(f"{dlen2} disks in the baseline, not in the new run:"))
                            # save.writelines(str(f"{klen} klines in the new run, not in the baseline:"))
                            for d in dd2:
                                details.append("   " + str(d))
                        
                        if hlen > 0:
                            details.append(str(f"{hlen} hlines in the new run, not in the baseline:"))
                            # save.writelines(str(f"{klen} klines in the new run, not in the baseline:"))
                            for h in dh:
                                details.append("   " + str(h))
                        if hlen2 > 0:
                            details.append(str(f"{hlen2} hlines in the baseline, not in the new run:"))
                            # save.writelines(str(f"{klen} klines in the new run, not in the baseline:"))
                            for h in dh2:
                                details.append("   " + str(h))

                        #  for debugging - dont delete!!!!
                        # details.append(str(f"entire new DP:"))
                        # details.append("   " + str(d))
                        
                        # details.append(str(f"entire baseline DP:"))
                        # details.append("   " + str(od))
        rep.extend(details)
        return rep
                
    def __str__(self):
        sdpl=[]
        for c, d in self:
            sdpl.append(str(f"*****EM Contols: {c}"))
            sdpl.append(f"{d}")

        return "\n".join(sdpl)