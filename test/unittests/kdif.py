def main():
       from pyemaps import Crystal                 
       from pyemaps import DPList, showDif 
       
       si = Crystal.from_builtin('Silicon')    
       emc, si_dp = si.generateDP()
       dpl = DPList(' ')                 #----create a diffraction pattern list to hold the results
    
       dpl.add(emc, si_dp) 
       showDif(dpl)   

def dpdb():
    import os
    from pyemaps import Crystal as crystal
    from pyemaps import EMC, SIMC  
    
    cr = crystal.from_builtin('Aluminium')
    xa0=(2,0,0)   # x-axis
    res = 200      # resolution
    ret, dbfn = cr.generateDPDB(emc=EMC(zone=(0,0,1),  simc=SIMC(gmax=3.9)), xa = xa0, res = res)
    
    if dbfn is None or not os.path.exists(dbfn):
        print(f'Error finding generated DP or diffraction pattern database file')
        return None
    return dbfn

if __name__ == '__main__':
    dpdb()
