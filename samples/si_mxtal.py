def test_xyz():
    
    from pyemaps import Crystal as cr
    from pyemaps import CrystalClassError
    from pyemaps import MxtalError
    try:
        si = cr.from_builtin('Silicon')
        if si:
            print(f'crytsal data to generate mxtal: {si}')
            mx = si.generateMxtal(bound=0.1)
    except (CrystalClassError, MxtalError) as e:
        print(f'error: generating mxtal data1: {e.message}')
    except Exception as e:
        print(f'error: generating mxtal data2: cause unknown {e}')
    else:
        # print(f'successfully generated mxtal: {mx}')
        ret = si.write_xyz(mx)

        if ret != 0:
            print(f'failed to write data: {mx} to file')

if __name__ == "__main__":
    test_xyz()
