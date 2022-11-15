if __name__ == '__main__':
    
    from pyemaps import Crystal as cr
    from pyemaps import CrystalClassError
    from pyemaps import BlochError
    try:
        si = cr.from_builtin('Silicon')

        bimgs = si.generateBloch(sample_thickness=(200, 1000, 100), bSave=True)

    except (CrystalClassError, BlochError) as e:
        print(f'error: generate and write bloch image data1: {e.message}')
    except Exception as e:
        print(f'error: generate and write bloch image data2: ' + str(e))
   
   