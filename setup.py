from ast import keyword
from ensurepip import version
from multiprocessing import AuthenticationError
from nturl2path import url2pathname
from ssl import Options

emaps_fsource = 'emaps'
dpgen_cobj = 'write_dpbin.o'

# def copy_cobj(cfg):
#     '''
#     moving the object file <dpgen_cobj> to build directory
#     '''
#     import os, sys
#     import shutil

#     pyemaps_rootdir = os.path.dirname(os.path.abspath(__file__))
#     cobj = os.path.join(pyemaps_rootdir, dpgen_cobj)

#     destdir = cfg.get_build_temp_dir()
#     try:
#         shutil.copy(cobj, os.path.join(destdir, dpgen_cobj))
#     except IOError as e:
#         raise ValueError("Error finding c object file") 


def configuration(parent_package='',top_path=None):
    from codecs import open
    from os import path
    
    here = path.abspath(path.dirname(__file__))
    
    # Get the long description from the README file
    with open(path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()

    from numpy.distutils.misc_util import Configuration
    
    config = Configuration(
        'pyemaps',
        parent_package,
        top_path,
        description = 'Python Modules for Transmission Electron Diffraction Simulations',
        long_description_content_type='text/markdown',
        long_description = long_description
    )

    config.add_subpackage('diffract',emaps_fsource)
    config.add_data_files('license.txt', 'README.md')
    config.add_data_dir('test')
    config.add_data_dir('cdata')
    config.add_data_dir('samples')
    config.make_config_py() #generated automatically by distutil based on supplied __config__.py
    return config

if __name__ == '__main__':
    import setuptools 
    from numpy.distutils.core import setup

    config = configuration(top_path='')

    setup(**config.todict())