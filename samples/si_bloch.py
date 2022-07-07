
from pyemaps import showBloch

def sanity_check_bloch():
    from pyemaps import Crystal as cr

    si = cr.from_builtin('Silicon')
    ec, img = si.generateBloch()
    showBloch([(ec, img)])

def run_bloch_tests():
    from sample_base import generate_bimages
    em_keys = ['tilt', 'zone', 'defl', 'vt', 'cl']
    for k in em_keys:
        imgs = generate_bimages(ckey=k)
        showBloch(imgs)

if __name__ == '__main__':
    sanity_check_bloch()
    run_bloch_tests()
