
from pathlib import Path
import os

# ------------------pyemaps data file and locations-------------
#             set by PYEMAPS_DATAHOME 
#             -- location to retrieve data and put darta
# 
def auto_fn(cn, ty='diffraction'):
    '''
    Auto-generate file name based on crystal name and time stamp
    '''
    import datetime

    curr_time  = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    return cn + ty + curr_time

def find_pyemaps_datahome(home_type='crystals'):
    '''
    The file name of intended bloch image is constructed:
    1) if environment variavle PYEMAPS_HOME is set then
        the file will be in $PYEMAPS_HOME/"<home_type>" folder
    2) otherwise, the file will be save in current working directory
    '''
    # pyemaps_datahome = ''
    # if home_type='crystals' and 'PYEMAPS_CRYSTALS' in os.environ:
    #     pyemaps_datahome = os.getenv('PYEMAPS_CRYSTALS')

    #
    # defaults to current working directory
    bLegacy = False
    if 'PYEMAPS_CRYSTALS' in os.environ:
        bLegacy = True
    
    env_name = 'PYEMAPS_CRYSTALS' if bLegacy else 'PYEMAPS_DATA'

    # defaults to current working directory
    pyemaps_datahome = os.getcwd()

    # but find pyeamsp home if exists
    if env_name in os.environ:
        pyemaps_home = os.getenv('PYEMAPS_DATA')

        if Path(pyemaps_home).exists(): 
            pyemaps_datahome = pyemaps_home
        else:
            try:
                os.mkdir(pyemaps_home)
            except OSError:
                # can't create the directory, fall back to current directory
                pass
            else:
                pyemaps_datahome = pyemaps_home

    if bLegacy:
        return pyemaps_datahome # done when legacy

    # if the environment home folder does extists
    pyemaps_home = pyemaps_datahome
    pyemaps_home = os.path.join(pyemaps_home, home_type)

    if Path(pyemaps_home).exists():
        return pyemaps_home

    try:
        os.mkdir(pyemaps_home)
    except OSError:
        raise CrystalClassError('Failed to find data home for pyemaps')
    else:    
        pyemaps_home

    return pyemaps_datahome

def fn_path_exists(fn):
    fn_dir = os.path.dirname(fn)
    if fn_dir is not None and Path(fn_dir).exists():
        return True
    return False

def compose_ofn(fn, name, ty='diffraction'):
    '''
    validing user input file and compose output file name
    using pyemaps's environment variable

    '''
    pyemaps_datahome=find_pyemaps_datahome(home_type=ty)

    if fn is None:
        fn = auto_fn(self.name, ty=ty)
        return os.path.join(pyemaps_datahome, fn)
    
    # valid input fn
    fpath, fname = os.path.split(fn)
    
    # can't write any file to a path that does not exist  
    if fpath and not Path(fpath).exists():
        raise MxtalError('Error: file path not found')

    if not fpath: # if no path compose fn 
        if not fname:
            fn = auto_fn(self.name, ty=ty)
        else:
            fn = fname
        return os.path.join(pyemaps_datahome, fn)

    # left with both path not empty and exists, then go with the input
    return fn
# -----------------crystal data loading and saving -----------------
#                  from/to data files on disks
#       
#                   CIF files