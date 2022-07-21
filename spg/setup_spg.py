from ensurepip import version
from nturl2path import url2pathname
from unicodedata import name

from pathlib import Path
import os
mod_name = "spg"
ver = "1.0.0"

spgra_files =['spg_spgseek.pyf', 'spgseek.f90', 'spgra.f90']


compile_args=['-Qm64',
              '-WB',
              '-heap-arrays:768',
            #   '-double-size:64',
              '-Qopenmp',
              '-GS', 
              '-4R8',
              '-fpp',
              '-warn:nointerfaces',
            #   '-fast', 
              '-O2', #this option does not work with -fast
            #   '-Qfp-stack-check',
              '-c']

def get_sources():
    
    current_path = Path(os.path.abspath(__file__))

    parent_path = current_path.parent.parent.absolute()

    emaps_dir = os.path.join(parent_path, 'emaps')

    src_list = []
    for sf in spgra_files:
        src_list.append(os.path.join(emaps_dir, sf))
    
    return src_list
        
#     return comp, None

def configuration(parent_package='', top_path=None):
    import os
    from numpy.distutils.misc_util import Configuration

    config = Configuration('spg', parent_package, top_path)

    src_list = get_sources()
    
    config.add_extension(
                 name                   = mod_name,
                 sources                = src_list,
                 extra_f90_compile_args = compile_args,
    )

    return config

    
if __name__ == "__main__":

    import setuptools
    from numpy.distutils.core import setup

    setup(**configuration(top_path='').todict())