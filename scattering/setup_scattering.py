from ensurepip import version
from nturl2path import url2pathname
from unicodedata import name

mod_name = "scattering"
ver = "1.0.0"

sct_files =['scattering_sct.pyf', 'scattering.f90']

compile_args=['-Qm64',
              '-WB',
              '-double-size:64',
              '-Qopenmp',
              '-GS', 
              '-4R8',
              '-fpp',
              '-warn:nointerfaces',
              '-O3',
              # '-fast' 
              '-Qfp-stack-check',
              '-c']

def get_sources():
    import os
    from pathlib import Path

    current_path = Path(os.path.abspath(__file__))

    parent_path = current_path.parent.parent.absolute()

    emaps_dir = os.path.join(parent_path, 'emaps')

    src_list = []
    for sf in sct_files:
        src_list.append(os.path.join(emaps_dir, sf))
    
    return src_list

def configuration(parent_package='', top_path=None):
    import os
    from numpy.distutils.misc_util import Configuration

    config = Configuration('scattering', parent_package, top_path)

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