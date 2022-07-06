from sample_base import test_blochs


def run_bloch():
    from pyemaps import dif, bloch
    from pyemaps import Crystal as cr

    si = cr.from_builtin('Silicon')
    ec, img = si.generateBloch()
    si.plotBloch(img, emc=ec)
    si.plotBloch(img, bColor = True, emc=ec)

def run_blochs():
    from sample_base import test_blochs
    
    test_blochs(ckey='tilt')
    test_blochs(ckey='zone')
    test_blochs(ckey='defl')
    test_blochs(ckey='vt')
    test_blochs(ckey='cl')
    # plotBlochImages(imgs, bColor = True)

if __name__ == '__main__':
    # run_bloch()
    run_blochs()
