from ensurepip import version
from nturl2path import url2pathname
from unicodedata import name
# import importlib.util as ilu
from pathlib import Path
import os
import importlib.util as ilu

# from ..diffract.setup_diffract import compiler_args
# import sys

# current_path = Path(os.path.abspath(__file__))
# parent_path = current_path.parent.parent.absolute()

# folder = os.path.join(parent_path, 'diffract')
# sys.path.append(folder)

# from setup_diffract import compile_args
# # file = 'setup_diffract'
# # spec = ilu.spec_from_file_location(file, folder)

# # print(f'------parent path found: {spec}')
# # difbuildmod = ilu.module_from_spec(spec)
# # spec.loader.exec_module(difbuildmod)
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
    import os
    from pathlib import Path

    print(f'current file path: {__file__}')
    current_path = Path(os.path.abspath(__file__))
    print(f'current directory: {current_path}')

    parent_path = current_path.parent.parent.absolute()
    print(f'current parent directory: {parent_path}')

    emaps_dir = os.path.join(parent_path, 'emaps')
    print(f'Parent dir found: {emaps_dir}')

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