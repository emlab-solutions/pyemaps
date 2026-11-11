'''
.. This file is part of pyemaps

Kinematic diffraction module is designed to handle kinematic simulation
data. It is composed of Point, Line and Disk class objects.

 .. ----

.. pyEMAPS is free software. You can redistribute it and/or modify 
.. it under the terms of the GNU General Public License as published 
.. by the Free Software Foundation, either version 3 of the License, 
.. or (at your option) any later version..

.. pyEMAPS is distributed in the hope that it will be useful,
.. but WITHOUT ANY WARRANTY; without even the implied warranty of
.. MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
.. GNU General Public License for more details.

.. You should have received a copy of the GNU General Public License
.. along with pyEMAPS.  If not, see `<https://www.gnu.org/licenses/>`_.

.. Contact supprort@emlabsoftware.com for any questions and comments.

.. ----

.. Author:     EMLab Solutions, Inc.
.. Date:       May 07, 2022    

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

    """
    A 2-D point ``(x, y)`` in a kinematic diffraction pattern.
    """
    def __init__(self, p=(0.0, 0.0)):

        """
        :param p: the coordinates ``(x, y)``.
        :type p: tuple of float, optional
        :raise ~pyemaps.errors.PointError: if a coordinate isn't numeric.
        """
        setattr(self, 'x', p[0])
        setattr(self, 'y', p[1])

    @property
    def x(self):

        """
        The x coordinate.
        """
        return self._x
    
    @property
    def y(self):

        """
        The y coordinate.
        """
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
        # Points within DIFF_PRECISION of each other are equal, so the hash
        # can't depend on the coordinates: equal objects must hash equally.
        return hash(Point)

    def __eq__(self, other):
        if isinstance(other, Point):
            return _double_eq(self._x, other.x) and \
                   _double_eq(self._y, other.y)

        return NotImplemented

    def __repr__(self):
        return str("({}, {})".format(self._x, self._y))

    def __iter__(self):
        return iter((self._x, self._y))

class Line:

    """
    A line in a kinematic diffraction pattern: a Kikuchi line or a HOLZ line.
    """
    def __init__(self, pt1 = None, pt2 = None, intensity=0, type=1):
        
        """
        :param pt1: one end point.
        :type pt1: :py:class:`~pyemaps.kdiffs.Point`, optional
        :param pt2: the other end point.
        :type pt2: :py:class:`~pyemaps.kdiffs.Point`, optional
        :param intensity: the line's intensity, stored as an integer.
        :type intensity: int or float, optional
        :param type: 1 for a Kikuchi line, 2 for a HOLZ line.
        :type type: int, optional
        :raise ~pyemaps.errors.LineError: if an end point isn't a Point, or *intensity* or *type*
            is invalid.
        """
        setattr(self, 'pt1', Point() if pt1 is None else pt1)
        setattr(self, 'pt2', Point() if pt2 is None else pt2)    
        setattr(self, 'intensity', intensity)    
        setattr(self, 'type', type)

    @property
    def pt1(self):

        """
        One end point, a :py:class:`~pyemaps.kdiffs.Point`.
        """
        return self._pt1

    @property
    def pt2(self):

        """
        The other end point, a :py:class:`~pyemaps.kdiffs.Point`.
        """
        return self._pt2
    
    @property
    def type(self):

        """
        The line type: 1 for a Kikuchi line, 2 for a HOLZ line.
        """
        return self._type
    
    @property
    def intensity(self):

        """
        The line's intensity, as an integer.
        """
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
        
        self._intensity = 0
        try:
            self._intensity = int(intense)
        except ValueError as e:
            raise LineError("intensity must be integer or float") from e
        
    def __lt__(self, other):

        if isinstance(other, Line):
            if self._type != other.type:
                return self._type < other.type

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

        """
        Shift the line by subtracting a :py:class:`~pyemaps.kdiffs.Point` from both end points.
        """
        if isinstance(other, Point):
            self._pt1 -= other
            self._pt2 -= other
            return self
        
        raise LineError("substraction of Line class from non-Point class type not supported")
    
    def __iadd__(self, other):

        """
        Shift the line by adding a :py:class:`~pyemaps.kdiffs.Point` to both end points.
        """
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
        Calculate the opacity to draw the line with, scaled linearly by its intensity: 0.2 at the
        lowest intensity *l* and 0.35 at the highest *h*.

        :param l: lowest line intensity in the pattern.
        :param h: highest line intensity in the pattern.
        :return: the opacity, from 0.2 to 0.35. If *l* equals *h*, 0.35.
        :rtype: float
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
        """
        Return the line as a dictionary: ``{'pt1': (x1, y1), 'pt2': (x2, y2), 'int': intensity}``.
        """
        x1, y1 = self._pt1
        x2, y2 = self._pt2
        return {'pt1': (x1,y1),
                'pt2': (x2,y2), 
                'int': self._intensity}

class Index:

    """
    The Miller indices ``(h, k, l)`` of a diffracted beam.
    """
    def __init__(self, I0=(0,0,0)):

        """
        :param I0: the three indices.
        :type I0: tuple of int, optional
        :raise ~pyemaps.errors.PIndexError: if an index isn't an integer.
        """
        setattr(self, 'I1', I0[0])
        setattr(self, 'I2', I0[1])
        setattr(self, 'I3', I0[2])

    @property
    def I1(self):

        """
        The first Miller index, *h*.
        """
        return self._I1

    @property
    def I2(self):

        """
        The second Miller index, *k*.
        """
        return self._I2

    @property
    def I3(self):

        """
        The third Miller index, *l*.
        """
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

        return NotImplemented
    
    def __iter__(self):
        return iter((self._I1, self._I2, self._I3))

class Disk:

    """
    A diffracted beam in a kinematic diffraction pattern: its center, radius and Miller
    indices.
    """
    def __init__(self, c=None, r=0.0, i=None):

        """
        :param c: the center.
        :type c: :py:class:`~pyemaps.kdiffs.Point`, optional
        :param r: the radius.
        :type r: float, optional
        :param i: the Miller indices.
        :type i: :py:class:`~pyemaps.kdiffs.Index`, optional
        :raise ~pyemaps.errors.DiskError: if *c*, *r* or *i* is invalid.
        """
        setattr(self, 'c', Point() if c is None else c)
        setattr(self, 'r', r)
        setattr(self, 'idx', Index() if i is None else i)

    @property 
    def c(self):

        """
        The center of the diffracted beam, a :py:class:`~pyemaps.kdiffs.Point`.
        """
        return self._c
    
    @property
    def r(self):

        """
        The radius of the diffracted beam.
        """
        return self._r
    
    @property
    def idx(self):

        """
        The Miller indices of the diffracted beam, an :py:class:`~pyemaps.kdiffs.Index`.
        """
        return self._idx

    @c.setter
    def c(self, cv):
        
        if not isinstance(cv, Point):
            raise DiskError('disk center must be of Point type')
        
        self._c = cv

    @r.setter
    def r(self, rv):
        self._r = 0.0
        try:
            self._r = float(rv)
        except ValueError as e:
            raise DiskError('disk radius must be real number')

    @idx.setter
    def idx(self, iv):
        
        if not isinstance(iv, Index):
            raise DiskError('disk index must be of Index type')
        
        self._idx = iv
        
    def __eq__(self, other):
        if not isinstance(other, Disk):
            return NotImplemented
        
        if not (self._idx == other.idx):
            return False
        
        if abs(self._r - other.r) > 1.0e-06:
            return False

        if not (self._c == other.c):
            return False

        return True
    
    def __iadd__(self, other):

        """
        Shift the disk by adding a :py:class:`~pyemaps.kdiffs.Point` to its center.
        """
        if isinstance(other, Point):
            self._c += other
            return self
        
        raise DiskError('addition cannot be done with non-Disk type')
    
    def __isub__(self, other):
        """
        Shift the disk by subtracting a :py:class:`~pyemaps.kdiffs.Point` from its center.
        """
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
        # the center is compared with a tolerance (see Point), so only the
        # index goes into the hash
        return hash(self._idx)

    def __repr__(self):

        return "index: " + repr(self._idx) + " " + \
               "center: " + repr(self._c) + " " + \
               str("radius: {}".format(self._r))

    def to_dict(self):

        """
        Return the disk as a dictionary: ``{'c': (x, y), 'idx': (h, k, l), 'r': radius}``.
        """
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

    """
    A kinematic diffraction pattern: its Kikuchi lines, HOLZ lines and diffracted beams.

    :py:meth:`~pyemaps.crystals.Crystal.generateDP` returns one, and
    :py:func:`~pyemaps.display.showDif` displays it. Its coordinates are shifted by
    :py:attr:`shift`. For drawing it with other tools, see :doc:`/user_guide/third_party`.
    """
    def __init__(self, diff_dict):

        """
        :param diff_dict: the raw pattern data from a kinematic simulation. Create diffraction
            patterns with :py:meth:`~pyemaps.crystals.Crystal.generateDP` rather than directly.
        :type diff_dict: dict, required
        :raise ~pyemaps.errors.DPError: if *diff_dict* is missing data or has invalid values.
        """
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

        """
        The Kikuchi lines, a list of :py:class:`~pyemaps.kdiffs.Line`.
        """
        return self._klines

    @property
    def hlines(self):

        """
        The HOLZ lines, a list of :py:class:`~pyemaps.kdiffs.Line`. Only CBED patterns have them.
        """
        return self._hlines

    @property
    def disks(self):

        """
        The diffracted beams, a list of :py:class:`~pyemaps.kdiffs.Disk`.
        """
        return self._disks

    @property
    def nklines(self):

        """
        The number of Kikuchi lines.
        """
        return self._nklines

    @property
    def nhlines(self):

        """
        The number of HOLZ lines.
        """
        return self._nhlines

    @property
    def ndisks(self):

        """
        The number of diffracted beams.
        """
        return self._ndisks

    @property
    def shift(self):

        """
        The shift applied to the pattern's coordinates, a :py:class:`~pyemaps.kdiffs.Point`.
        """
        return self._shift

    @property
    def name(self):

        """
        The crystal's name.
        """
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
            
            if not "r" in d:
                raise DPError("disks must have a radius")

            if not "idx" in d or len(d['idx']) != 3:
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
            return NotImplemented
        
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

        for kl in other.klines:
            if not kl in self._klines:
                return False
        
        for hl in other.hlines:
            if not hl in self._hlines:
                return False
            
        for ds in other.disks:
            if not ds in self._disks:
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

        sDiff.append(str(f'\n# of diffracted beams (disk, index = Miller Index): {self._ndisks}'))
        for i, d in enumerate(self._disks):
            sDiff.append(str("disk# {}:".format(i+1)).ljust(10) + repr(d))
        
        sDiff.append(str(f'\n# of HOLZ lines (hline): {self._nhlines}'))
        for i, h in enumerate(self._hlines):
            sDiff.append(str("hline# {}:".format(i+1)).ljust(10) + repr(h))
        
        return "\n".join(sDiff)

    def _difference(self, other):

        """
        For internal testing only.
        """
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
        """
        Return the pattern as a dictionary of lists:
        ``{'klines': [...], 'hlines': [...], 'disks': [...]}``. Each Kikuchi or HOLZ line is a
        dictionary from :py:meth:`Line.to_dict() <pyemaps.kdiffs.Line.to_dict>`, and each disk one
        from :py:meth:`Disk.to_dict() <pyemaps.kdiffs.Disk.to_dict>`.
        """
        retdict = {}
        
        retdict['klines'] = [kl.to_dict() for kl in self._klines]
        retdict['hlines'] = [hl.to_dict() for hl in self._hlines]
        retdict['disks'] = [d.to_dict() for d in self._disks]
        return retdict

class Diffraction:

    """
    A list of kinematic diffraction patterns (available as ``DPList``), each paired with the
    microscope controls it was simulated with. :py:func:`~pyemaps.display.showDif` displays
    one.

    .. code-block:: python

        from pyemaps import Crystal, DPList

        si = Crystal.from_builtin('Silicon')
        dpl = DPList('Silicon')
        emc, dp = si.generateDP()
        dpl.add(emc, dp)

        for emc, dp in dpl:
            print(emc.zone, dp.ndisks)
    """
    def __init__(self, name, mode=DEF_MODE):
        
        """
        :param name: the crystal's name.
        :type name: str, required
        :param mode: 1 for normal patterns, 2 for CBED.
        :type mode: int, optional
        :raise ~pyemaps.errors.DPListError: if *name* is empty or *mode* isn't 1 or 2.
        """
        setattr(self, 'name', name)
        setattr(self, 'mode', mode)
        setattr(self, 'diffList', [])

    @property
    def name(self):
        """
        The crystal's name.
        """
        return self._name

    @property
    def mode(self):
        """
        The diffraction mode: 1 for normal, 2 for CBED.
        """
        return self._mode
    
    @property
    def diffList(self):
        """
        The patterns, as a list of ``(controls, pattern)`` tuples.
        """
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

        """
        Add a diffraction pattern, with the controls it was simulated with.

        :param emc: the controls.
        :type emc: :py:class:`~pyemaps.emcontrols.EMControl`, required
        :param diffP: the diffraction pattern.
        :type diffP: :py:class:`~pyemaps.kdiffs.diffPattern`, required
        :raise ~pyemaps.errors.DPListError: if *diffP* isn't a diffPattern.
        """
        if not isinstance(diffP, diffPattern):
            raise DPListError('failed to add DP')


        self.diffList.append((emc, diffP))
    
    def sort(self):

        """
        Sort the patterns by their controls.
        """
        self._diffList.sort(key=lambda x: x[0])
            
    def __eq__(self, other):

        """
        Return ``True`` if both lists have the same name, mode and patterns.
        """
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

        """
        Return the ``(controls, pattern)`` tuple at *key*.
        """
        return self._diffList[key]
            
    def clear(self):

        """
        Remove all patterns from the list.
        """
        self._diffList.clear()

    def _report_difference(self, other):
        """
        For internal testing only.
        """
        if not isinstance(other, Diffraction):
            raise DPListError('connt report difference between two different type of objects')
        
        rep = []
        if self == other:
            return rep
        
        if self._name != other.name or self._mode != other.mode:
            rep.append(str(f"Diffractions are generated in different mode/name" ))
            return rep


        def _list(label, items):
            if items:
                rep.append(label.format(len(items)))
                rep.extend("   " + str(x) for x in items)

        for c, d in self:
            od = next((od for oc, od in other if oc == c), None)
            if od is None:
                rep.append(str(f"Control parameters: {c}"))
                rep.append("   no pattern with these controls in the baseline")
                continue

            if d == od:
                continue

            dk, dh, dd = d._difference(od)
            dk2, dh2, dd2 = od._difference(d)

            rep.append(str(f"Control parameters: {c}"))
            _list("{} klines in the new run, not in the baseline:", dk)
            _list("{} klines in the baseline, not in the new run:", dk2)
            _list("{} disks in the new run, not in the baseline:", dd)
            _list("{} disks in the baseline, not in the new run:", dd2)
            _list("{} hlines in the new run, not in the baseline:", dh)
            _list("{} hlines in the baseline, not in the new run:", dh2)

        return rep
                
    def __str__(self):
        sdpl=[]
        for c, d in self:
            sdpl.append(str(f"*****EM Contols: {c}"))
            sdpl.append(f"{d}")

        return "\n".join(sdpl)