
if __name__ == "__main__":
       from pyemaps import Crystal as cr
       from pyemaps import EMC

       si = cr.from_builtin('Silicon')
       
       ec = EMC(tilt = (0.5,-0.5), zone = (1,0,1))
       sl = si.generateStereo(xa=(2,0,0), 
                            tilt=(0.5,-0.5),
                            zone=(1, 0, 1))
                         
       from pyemaps import showStereo
       showStereo([(ec,sl),], 
               name='Silicon', 
               iShow=True,
               bSave=True,
               zLimit = 1)
