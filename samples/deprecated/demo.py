def gen_kdiff():
       from pyemaps import Crystal as cr
       from pyemaps import DPList, showDif

       si = cr.from_builtin('Silicon')

       emc, si_dp = si.generateDP(mode=2)
       dpl = DPList('Silicon', mode = 2)
       dpl.add(emc, si_dp)
       showDif(dpl)


if __name__ == '__main__':
       gen_kdiff()


