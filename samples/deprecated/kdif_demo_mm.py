
if __name__ == "__main__":
       from pyemaps import Crystal as cr
       si = cr.from_builtin('Silicon')

       from pyemaps import DPList
       emc, si_dp = si.generateDP(mode=2)
       dpl = DPList('Silicon', mode = 2)
       dpl.add(emc, si_dp)

       from pyemaps import showDif
       showDif(dpl)
