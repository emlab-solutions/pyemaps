from ast import keyword
from ensurepip import version
from multiprocessing import AuthenticationError
from nturl2path import url2pathname
from ssl import Options

from numpy.distutils.command.build_ext import build_ext as numpy_build_ext
import os

emaps_fsource = 'emaps'
dpgen_cobj = 'write_dpbin.o'

def get_comp():
    '''
    Get pyemaps component to be built from comp.json file
    '''
    
    import json, os
    from pathlib import Path

    json_cfg = os.getenv('PYEMAPS_JSON')

    if not json_cfg:
        json_cfg = "comp.json" # default

    currdir = Path(os.path.dirname(os.path.realpath(__file__)))/emaps_fsource
    comp = 'dif'

    comp_cfg = os.path.join(currdir,json_cfg)
    try:
        with open(comp_cfg, 'r') as jf:
            comp = json.load(jf)['component']

    except IOError as e:
        raise ValueError(f"Error reading component configure file: {e}")
   
    # delete temp config file comp.json
    # if os.path.exists(comp_cfg):
    #     os.remove(comp_cfg)
    # else:
    #     print(f"The comfiguration file {comp_cfg)} does not exits")

    return comp

class build_dp_ext(numpy_build_ext):
    def finalize_options(self):
        numpy_build_ext.finalize_options(self)
        cobj = os.path.join(emaps_fsource, dpgen_cobj)
        self.link_objects = [cobj]

def configuration(parent_package='',top_path=None):
    from codecs import open
    from os import path
    
    here = path.abspath(path.dirname(__file__))
    
    # Get the long description from the README file
    with open(path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()

    from numpy.distutils.misc_util import Configuration
    
    version = {}
    with open("__version__.py") as fp:
        exec(fp.read(), version)

    config = Configuration(
        'pyemaps',
        parent_package,
        top_path,
        version = version['__version__'],
        description = 'Python Modules for Transmission Electron Diffraction Simulations',
        long_description_content_type='text/markdown',
        long_description = long_description
    )

    config.add_subpackage('diffract',emaps_fsource)
    config.add_data_files('license.txt', 'README.md', 'COPYING')
    config.add_data_dir('test')
    config.add_data_dir('cdata')
    config.add_data_dir('samples')
    config.make_config_py() #generated automatically by distutil based on supplied __config__.py
    return config

if __name__ == '__main__':
    import setuptools 
    from numpy.distutils.core import setup

    config = configuration(top_path='')
    
    comp = get_comp()
    if comp == 'dpgen':
        cmd ={}
        cmd['build_ext'] = build_dp_ext

        setup(**config.todict(), cmdclass = cmd)
    else:
        setup(**config.todict())