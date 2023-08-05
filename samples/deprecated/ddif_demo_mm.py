 
if __name__ == "__main__":
    
    from pyemaps import Crystal as cr
    from pyemaps import showBloch

    si = cr.from_builtin('Silicon')
    
    bimgs = si.generateBloch(sampling = 20,
                             sample_thickness=(400,1200,400)
    )
    showBloch(bimgs, bSave=True, bColor = True, layout='table')