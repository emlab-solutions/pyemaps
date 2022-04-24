# precision digits
NDIGITS = 1
DIFF_PRECISION = 0.95
XMAX, YMAX = 75, 75

def double_eq(a,b):
    return abs(a-b) <= DIFF_PRECISION

class Point:
    def __init__(self, x0=0.0, y0=0.0):
        self.x=float(x0)
        self.y=float(y0)

    def __lt__(self, other):
        if isinstance(other, Point):
            if self.x != other.x:
                return self.x < other.x
            if self.y != other.y:
                return self.y < other.y
            return False

        return NotImplemented
    
    def __key__(self):
        return (self.x, self.y)
    
    def __hash__(self):
        return hash(self.__key__())
    
    def __eq__(self, other):
        if isinstance(other, Point):
            return double_eq(self.x, other.x) and \
                   double_eq(self.y, other.y)
             
        return NotImplemented

    def __repr__(self):
        return str("({}, {})".format(self.x, self.y))


class Line:
    def __init__(self, pt1, pt2, type=1):
        #type 1 - kline; 2 - hline
        if isinstance(pt1, Point) and isinstance(pt2, Point):
            self.pt1 = pt1
            self.pt2 = pt2
            self.type = type          
    
    # def slope(self):
    #     slope = 0.0
    #     try:
    #         slope = (self.pt2.y - self.pt1.y) / (self.pt2.x - self.pt1.x)
    #     except ZeroDivisionError:
    #         slope = None

    #     return slope
    
    # def middle(self):
    #     return Point((self.pt2.x - self.pt1.x)/2, (self.pt2.y - self.pt1.y)/2) 

    def __lt__(self, other):
        if isinstance(other, Line):
            if self.type == other.type:
                if not (self.pt1 == other.pt1):
                    return self.pt1 < other.pt1

                if not (self.pt2 == other.pt2):
                    return self.pt2 < other.pt2

                return False
            return False
        
        return NotImplemented
    
    def __key__(self):
        return (self.pt1, self.pt2)
    
    def __hash__(self):
        return hash(self.__key__())
    
    def __eq__(self, other):
        if isinstance(other, Line):
            if self.type != other.type:
                return False

            if (self.pt1 == other.pt1) and \
                (self.pt2 == other.pt2):
                return True

            if (self.pt1 == other.pt2) and \
                (self.pt2 == other.pt1):
                return True
            # sl = self.slope()
            # osl = other.slope()
            # c = self.middle()
            # oc = other.middle()

            # # if both are vertical lines
            # if not sl and not osl:
            #     return c == oc

            # if not sl or not osl:
            #     return False

            # return double_eq(sl, osl) and (c == oc)
            
            return False                        

        return NotImplemented

    def __repr__(self):
        return str("[{}, {}]".format(self.pt1.__repr__(), self.pt2.__repr__()))

    # def plot(self, plt):
    #     """
    #     Plotting the line using the python matplotlib.pyplot

    #     """
    #     x = [self.pt1.x, self.pt2.x]
    #     y = [self.pt1.y, self.pt2.y]
    #      # x = [0, 150]
    #     # y = [0, 150]
    #     plt.plot(x, y, 'k')

class Index:
    def __init__(self, I1=0, I2=0, I3=0):
        self.I1=I1
        self.I2=I2
        self.I3=I3
        
    def __lt__(self, other):
        if isinstance(other, Index):
            if self.I1 != other.I1:
                return self.I1 < other.I1
            
            if self.I2 != other.I2:
                return self.I2 < other.I2

            if self.I3 != other.I3:
                return self.I3 < other.I3

            return False

        return NotImplemented
    
    def __key__(self):
        return (self.I1, self.I2, self.I3)
    
    def __hash__(self):
        return hash(self.__key__())
    
    def __str__(self):
        return str("{} {} {}".format(self.I1, self.I2, self.I3))

    def __repr__(self):
        return str("({}, {}, {})".format(self.I1, self.I2, self.I3))
    
    def __eq__(self, other):
        if isinstance(other, Index):
            return self.__key__() == other.__key__()

        return NotImplemented

class Disk:
    def __init__(self, c, r, i):
        if isinstance(c, Point):
            self.c = Point(c.x, c.y)
        else:
            return NotImplemented

        if isinstance(r, float):
            self.r = r
        else:
            return NotImplemented

        if isinstance(i, Index):
            self.idx = Index(i.I1, i.I2, i.I3)
        else:
            return NotImplemented

    def __eq__(self, other):
        if not isinstance(other, Disk):
            print("Error: compared object is not a disk object!")
            return NotImplemented
        
        if not (self.idx == other.idx) or self.r != other.r:
            # print(f"Error: comarison failed: index not matching: {self.idx}, {other.idx}")
            return False

        if not (self.c == other.c):
            return False

        return True
    
    def __key__(self):
        center = self.c
        r = self.r
        indx = self.idx
        return (indx.I1, indx.I2, indx.I3, center.x, center.y, r)

    def __hash__(self):
        return hash(self.__key__())

    def __repr__(self):
        # return str("index: ({}, {}, {})  center: [{}, {}] radius: {}".format(*self.__key__()))        
        return "index: " + repr(self.idx) + " " + \
               "center: " + repr(self.c) + " " + \
               str("radius: {}".format(self.r))

    def __lt__(self, other):
        if not isinstance(other, Disk):
            return NotImplemented

        if not (self.idx == other.idx):
           return self.idx < other.idx

        if not (self.c == other.c):
           return self.c < other.c

        if self.r != other.r:
            return self.r < other.r 

        return False

class diffPattern:
    def __init__(self, diff_dict):
        self.name = diff_dict["name"]
        self.nklines = diff_dict["nums"]["nklines"]
        self.ndisks = diff_dict["nums"]["ndisks"]
        self.nhlines = diff_dict["nums"]["nhlines"]

        self.klines = []
        for kline in diff_dict["klines"]:
            pt1 = Point(kline[0][0], kline[0][1])
            pt2 = Point(kline[1][0], kline[1][1])
            self.klines.append(Line(pt1,pt2))
        self.klines = sorted(self.klines)

        self.disks = []

        for disk in diff_dict["disks"]:
            ctr = Point(disk["c"][0], disk["c"][1])
            indx = Index(disk["idx"][0], disk["idx"][1], disk["idx"][2])
            self.disks.append(Disk(ctr, disk["r"], indx))
        self.disks = sorted(self.disks)
        
        self.hlines = []
        for hline in diff_dict["hlines"]:
            pt1 = Point(hline[0][0], hline[0][1])
            pt2 = Point(hline[1][0], hline[1][1])
            self.hlines.append(Line(pt1,pt2, 2))
        self.hlines = sorted(self.hlines)
            

    def __eq__(self, other):
        if not isinstance(other, diffPattern):
            return NotImplemented
        
        if self.name != other.name:
            return False

        if self.nklines != other.nklines or \
            self.ndisks != other.ndisks or \
            self.nhlines != other.nhlines:
            return False

        if len(self.klines) != len(other.klines) or \
            len(self.disks) != len(other.disks) or \
            len(self.hlines) != len(other.hlines):
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
            return NotImplemented
        
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
        sDiff=[]
        for i, k in enumerate(self.klines):
            sDiff.append(str("kline# {}:".format(i+1)).ljust(10) + repr(k))

        for i, d in enumerate(self.disks):
            sDiff.append(str("disk# {}:".format(i+1)).ljust(10) + repr(d))
        
        for i, h in enumerate(self.hlines):
            sDiff.append(str("hline# {}:".format(i+1)).ljust(10) + repr(h))
        
        return "\n".join(sDiff)

    def difference(self, other):
        # A - B (self - other)
        if not isinstance(other, diffPattern):
            return NotImplemented
        
        kdiff = []
        for sk in self.klines:
            if not (sk in other):
                kdiff.append(sk)

        hdiff = []
        for sh in self.hlines:
            if not (sh in other):
                hdiff.append(sh)

        ddiff = []
        for d in self.disks:
            if not (d in other):
                ddiff.append(d)
        
        return (kdiff, hdiff, ddiff)

    def plot(self):
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        import matplotlib.transforms as mtransforms
        
        # x, y = self._get_plot_coords()
        
        fig, ax = plt.subplots()
        fig.canvas.set_window_title('Kinematical Diffraction')

        ax.set_title(f"{self.name}")
        ax.set_aspect('equal')
        for kl in self.klines:
            xx = [kl.pt1.x, kl.pt2.x]
            yy = [kl.pt1.y, kl.pt2.y]
            ax.plot(xx, yy, 'k', alpha=0.2)

        for hl in self.hlines:
            xx = [hl.pt1.x, hl.pt2.x]
            yy = [hl.pt1.y, hl.pt2.y]
            ax.plot(xx, yy, 'k', alpha=0.2)

        for d in self.disks:
            centre = (d.c.x, d.c.y)
            # idx = '' + str(d.idx)
            dis = patches.Circle(centre, d.r, alpha=1.0, fc='blue')
            ax.add_patch(dis)
            # ax.annotate(idx,centre,)
            trans_offset = mtransforms.offset_copy(ax.transData, fig=fig,
                                       x=0.0, y=d.r/2, units='points')
            plt.text(centre[0],centre[1], str(d.idx), transform=trans_offset)

        fig.canvas.draw()

        ax.set_axis_off()
        plt.show()

class Diffraction:

    def __init__(self, name, mode=1):
        self.name = name
        self.mode = mode
        self.diffList = [] 
    # Adding new diffraction patterns
    def add(self, params_dict, diffP):
        if not isinstance(diffP, diffPattern):
            return

        self.diffList.append((params_dict, diffP))
            
    def __eq__(self, other):

        if not isinstance(other, Diffraction):
            return NotImplemented
        
        if self.name != other.name or self.mode != other.mode:
            return False

        if len(self.diffList) != len(other.diffList):
            return False

        found = False
        for c, d in self.diffList:
            found = False
            cl = list(c.values())
            for oc, od in other.diffList:
                ocl = list(oc.values())
                # print(f"controls compare: {cl} and {ocl}")
                if cl == ocl:
                    found = (d==od)
                    if not found:
                        break
            if found:
                continue
            else:
                break
        
        return found
            
    def report_difference(self, other):

        if not isinstance(other, Diffraction):
            return NotImplemented
        
        rep = []
        if self == other:
            return rep
        
        if self.name != other.name or self.mode != other.mode:
            rep.append(str(f"Diffractions are generated in different mode/name" ))
            return rep

        # if len(self.diffList) != len(other.diffList):
        #     return False

        for c, d in self.diffList:
            cl = list(c.values())
            for oc, od in other.diffList:
                ocl = list(oc.values())
                # print(f"controls compare: {cl} and {ocl}")
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

    def savebin(self, fn=""):
        import pickle
        import os

        # difffn = os.path.join(spath, self.name)
        # # print(f"output file name : {difffn}")
        # smode = "_normal" if self.mode == 1 else "_CBED"
        # difffn = difffn + smode
        # difffn = difffn + ".bin"
        # # print(f"output file name : {difffn}")

        with open(fn, "wb") as f:
            pickle.dump(self.name,f, pickle.HIGHEST_PROTOCOL)
            pickle.dump(self.mode,f, pickle.HIGHEST_PROTOCOL)
            for d in self.diffList:
                pickle.dump(d, f, pickle.HIGHEST_PROTOCOL)

        return fn

    def readbin(self, dfn="", bPrint = False):
        import pickle

        self.diffList=[]
        with open(dfn, "rb") as f:
            self.name = pickle.load(f)
            self.mode = pickle.load(f)
            while True:
                try:
                    self.diffList.append(pickle.load(f))
                except EOFError:
                    break
        
        if bPrint:
            print(f"-----------------Diffraction Patterns for {self.name}-----------------------\n\n")
            smode = "_normal" if self.mode == 1 else "_CBED"
            print(f"Diffraction Mode: {smode}")
            for c, d in self.diffList:
                # print(f"****Success****: generated diffraction patterns for tilt: {d[0]}\n")
                print(f"\nDiffraction Patterns generated with controls:\n{c}\n")
                print(repr(d))
                
    def __str__(self):
        for c, d in self.diffList:
            print(f"*****EM Contols: {c}")
            print(f"{d}")
        return " "