
from pyemaps import showBloch

def run_bloch_tests():
    from sample_base import generate_bimages
    em_keys = ['tilt', 'zone', 'defl', 'vt', 'cl']
    for k in em_keys:
        imgs = generate_bimages(ckey=k)
        showBloch(imgs)

if __name__ == '__main__':
    
    run_bloch_tests()
