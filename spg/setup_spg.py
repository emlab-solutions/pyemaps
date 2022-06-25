from ensurepip import version
from nturl2path import url2pathname
from unicodedata import name

mod_name = "spg"
ver = "1.0.0"

spgra_files =['spg_spgseek.pyf', 'spgseek.f95', 'spgra.f95']

compile_args=['-m64',         
            '-Wno-tabs', 
            '-Warray-bounds',
            '-fdefault-double-8',
            '-fdefault-real-8',
            '-fopenmp',
            '-fcheck=all,no-array-temps',
            '-cpp', 
            '-Wall',
            '-O3']

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

    # c, src_files = get_sources()
    
    # if not src_files:
    #     raise ValueError("Error finding extension source!")

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