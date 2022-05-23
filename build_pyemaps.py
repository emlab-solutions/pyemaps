from multiprocessing.sharedctypes import Value
import os

MAKE_LOOKUP = dict(
    dif = 'DIFPYF',
    bloch = 'BLOCHPYF',
    dpgen = 'CDPOBJ DPGENPYF',
    csf = 'CSFPYF',
    all = 'CDPOBJ ALLPYF'
)

test_pypi_url = "https://test.pypi.org"
rel_pypi_url = "https://pypi.org"
twine_cfg = 'pypi_twine.cfg'

def remove():
    '''
    remove build and dist directory in the pyemaps root directory
    '''
    import os, shutil
    from pathlib import Path
    
    builddir = Path("build")
    print(f"Build dir: {builddir}")
    if os.path.exists(builddir) and os.path.isdir(builddir):
        shutil.rmtree(builddir)


    distdir = Path('dist')
    print(f"Distribution dir: {distdir}")
    if os.path.exists(distdir) and os.path.isdir(distdir):
        shutil.rmtree(distdir)

def set_cfg(comp):
    import json, os

    json_cfg = os.getenv('PYEMAPS_JSON')

    if not json_cfg:
        json_cfg = "comp.json" # default

    # write a file recording the comp name for setup consumption
    
    json_obj = json.dumps(dict(component = comp))
    try:
        with open(json_cfg, 'w', encoding="utf-8") as f:
            f.write(json_obj)

    except IOError as e:
        raise ValueError(f"Error writing configuration file {json_cfg} for packaging")


def make_pyf(comp):
    '''
    make .pyf file according to comp name
    '''
    # first change working directory to emaps
    pyemapsroot = os.getcwd()
    os.chdir('emaps')
    emapsdir = os.getcwd()

    os.system("make clean")

    pyf_fname = 'emaps_'
    makestr = "make EMAPSALLMODULES"
    if comp in MAKE_LOOKUP:
        makestr += ' '
        makestr += MAKE_LOOKUP[comp]
        pyf_fname += comp
    else:
        os.chdir(pyemapsroot)
        raise ValueError("Error: build pyemaps build type: {comp}")
    
    os.system("make clean")

    os.system(makestr)

    pyf_fn = os.path.join(emapsdir, pyf_fname)
    
    try:
         os.path.exists(pyf_fn)

    except FileNotFoundError as e:
        os.chdir(pyemapsroot)
        raise ValueError("Error: compiling PYF file {pyf_fn} for: {comp}") 

    set_cfg(comp)

    os.chdir(pyemapsroot)

def get_bversion(btest = True):
    '''
    get build version number dynamically from the repo
    using repo APIs and write the version to __verson__ file
    '''
    import requests, re, json
    MAX_VER_DIGIT = 10
    
    repo_url = test_pypi_url if btest else rel_pypi_url
    url = repo_url + '/pypi/pyemaps/json'

    response = requests.get(url)
    
    try:
        jresp = response.json()

    except json.decoder.JSONDecodeError as e:
        print(f"error: getting response from pypi api: {e.msg}")
        raise SystemExit(e)

    except requests.exceptions.RequestException as e:        
        raise SystemExit(e)

    rels = jresp['releases']
    # get the current release
    max_ver = '0.0.1'
    for k in rels.keys():
        # major, minor, sub = int(re.split('.', k))
        # if max_major
        if k > max_ver:
            max_ver = k
    # increment version number by 1
    print(f"releases max: {max_ver}")

    ver = re.split(r"\.", max_ver)
    
    if len(ver) != 3:
        raise ValueError("Error: version number validation error")
    
    major, minor, sub = ver
    
    ver_num = int(major)*MAX_VER_DIGIT**2 + int(minor)*MAX_VER_DIGIT + int(sub)
    # increment the version number
    print(f"releases numer: {ver_num}")
    ver_num += 1

    if ver_num > MAX_VER_DIGIT**3:
        raise ValueError(f"Error: version numbers are full")

    sub = ver_num % MAX_VER_DIGIT
    minor = ver_num // MAX_VER_DIGIT
    major = ver_num // MAX_VER_DIGIT**2

    new_version = '.'.join([str(major), str(minor), str(sub)])
    print(f"new releases: {new_version}")

    with open('__version__.py', 'w') as vf:
        vf.write('__version__ = \"' + new_version + '\"')

    return new_version

def build_package(comp = 'dif', repo_test = True):
    '''
    Build the package
    Conponent configuration via PYEMAPS_JSON env variable
    '''
    print(f"####Begin building pyemaps package for {comp}...")

    #  build the source distribution
    os.system('python -m build -s')

    #  build the wheel distribution (linrary build)
    os.system('python -m build -w')


def upload_package(bRelease = False, ver = None):

    repo_name = 'pypi' if bRelease else 'testpypi'

    ul_cmd = 'python -m twine upload --repository ' + \
            repo_name + ' --config-file ' + twine_cfg + \
            ' dist/*'+ ver + '* --verbose'

    if bRelease:
        q = str(f"About to publish pyemaps v{ver} ") + \
            "to official public repository." + \
            "Are you sure? [Y|n]"
        ans = input(q).lower().strip()[:1]

        if ans == 'n':
            print(f"info: upload to {repo_name} canceled")
            return 0

        if ans == 'y' or ans == '':
            print(f"Uploading package to pypi.org: {ul_cmd}")
            os.system(ul_cmd)
            return 1
        else:
            raise ValueError(str(f"Invalid answer: {ans}"))

    else:
        print(f"Uploading package to test.pypi.org: {ul_cmd}")
        os.system(ul_cmd)
    return 1 #successful

def install_package(btest = True, ver= '0.0.0'):

    repo_url = ''
    if btest:
        repo_url ='-i ' + test_pypi_url + '/simple/'
    
    install_cmd = 'python -m pip install ' + repo_url + ' pyemaps=='+ver
    print(f'installation: {install_cmd}')
    os.system(install_cmd)


if __name__ == "__main__":
    import argparse
    import time
    parser = argparse.ArgumentParser(description="Build and publish script for pyeamps")
    parser.add_argument("-c", "--component", type=str, nargs="?", const="dif", default="dif", help="build pyemaps component, defaults to dif module", required=False)
    parser.add_argument("-u", "--upload", action="store_true", help="upload the build or not", required=False)
    parser.add_argument("-t", "--test-repo", action="store_true", help="upload to the build to test repo test.pypi.org", required=False)
    parser.add_argument("-i", "--install", action="store_true", help="install the package from above repo", required=False)
    # parser.add_argument("-n", "--no-build", action="store_true", help="No build", required=False)
    
    args = parser.parse_args()
    comp = args.component

    if not comp:
        # defaults to dif pyeamps module
        comp = 'dif'
    
    make_pyf(comp)

    ver = get_bversion(btest = args.test_repo)

    remove()
    build_package(comp)

    if not args.upload:
        exit(0)

    # upload the package
    ret = upload_package(bRelease = not args.test_repo , ver = ver)

    if ret ==0:
        # user canceled upload in case of release   
        exit(0)

    if not args.install:
        exit(0)
    
    # wait for the upload is done 
    time.sleep(10)
    install_package(btest = args.test_repo, ver=ver)
    

    
