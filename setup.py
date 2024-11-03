'''
This file is part of pyemaps
___________________________

pyemaps is free software. You can redistribute it and/or modify 
it under the terms of the GNU General Public License as published 
by the Free Software Foundation, either version 3 of the License, 
or (at your option) any later version..

pyemaps is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pyemaps.  If not, see <https://www.gnu.org/licenses/>.

Contact supprort@emlabsoftware.com for any questions and comments.
___________________________


Author:             EMLab Solutions, Inc.
Date Created:       May 07, 2022  

'''
from ast import keyword
from ensurepip import version
from multiprocessing import AuthenticationError
from nturl2path import url2pathname
from random import sample
from ssl import Options

import setuptools
from numpy.distutils.core import Extension, setup

from numpy.distutils.command.build_ext import build_ext as numpy_build_ext

import os
from pathlib import Path

install_requires = [
            'emaps >= 1.0.5',
            'numpy >= 1.21.2',
            'matplotlib >= 3.2.1'
            ]

def get_cifreader_source():
    current_path = Path(os.path.abspath(__file__))
    pyemaps_parent_path = current_path.parent.absolute()
    cifreader_path = os.path.join(pyemaps_parent_path, 'CifFile')

    # print(f'-----------CifReader Source path: {cifreader_path}')

    src_files = ["src/lib/lex.yy.c","src/lib/py_star_scan.c"]
    return [os.path.join(cifreader_path, s) for s in src_files]

def get_samples(sdn = 'samples'):
    '''
    input: sdn = sample directory name under pyemaps
    '''

    import os, glob
    base_dir = os.path.realpath(__file__)
    samples_base_dir = os.path.join(os.path.dirname(base_dir), sdn)
    sbase_files = os.path.join(samples_base_dir, '*.py')
    sfile_list = glob.glob(sbase_files)
    # for full package only
    # sfile_list.append('al_db.bin')
    sfile_list.append('al.img')
    sfile_list.append('mask.im3')
    sfile_list.append('raw.img')


    return [os.path.join(sdn, os.path.basename(name)) for name in sfile_list]

def get_cdata(sdn = 'cdata'):
    '''
    input: sdn = sample directory name under pyemaps
    '''
    import glob


    free_xtl_remove = []
    free_xtl_remove = ['SiAlONa.xtl']

    base_dir = os.path.realpath(__file__)
    samples_base_dir = os.path.join(os.path.dirname(base_dir), sdn)
    sbase_files = os.path.join(samples_base_dir, '*.xtl')
    sfile_list = glob.glob(sbase_files)
    res = [os.path.join(sdn, os.path.basename(name)) for name in sfile_list]
   
    out =[]
    
    for rf in res:
        _, rfn = os.path.split(rf)
        if rfn not in free_xtl_remove:
            out.append(rf)
        
    return out

def get_install_requires():
    import sys
    install_reqs = install_requires.copy()
    return install_reqs


pyemaps_cifreader = Extension("pyemaps.CifFile.StarScan",
        sources                = get_cifreader_source()
)

def get_version(f):
    version = {}
    with open(f + ".py") as fp:
        exec(fp.read(), version)
    
    return version[f]

def get_long_description():
    from codecs import open
    from os import path
        
    here = path.abspath(path.dirname(__file__))
        
    # Get the long description from the README file
    with open(path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
    
    return long_description

setup(name                              ="pyemaps",
      version                           = get_version('__version__'),
      long_description_content_type     ='text/markdown',
      long_description                  = get_long_description(),
      py_modules                        = ['pyemaps.crystals',
                                           'pyemaps.kdiffs',
                                           'pyemaps.ddiffs',
                                           'pyemaps.display',
                                           'pyemaps.errors',
                                           'pyemaps.fileutils',
                                           'pyemaps.emcontrols',
                                           'pyemaps.stackimg',
                                           'pyemaps.CifFile.CifFile_module',
                                           'pyemaps.CifFile.yapps3_compiled_rt',
                                           'pyemaps.CifFile.YappsStarParser_1_1',
                                           'pyemaps.CifFile.YappsStarParser_1_0',
                                           'pyemaps.CifFile.YappsStarParser_STAR2',
                                           'pyemaps.CifFile.YappsStarParser_2_0',
                                           'pyemaps.CifFile.StarFile',
                                           'pyemaps.CifFile.TypeContentsParser'],

      ext_modules                       = [pyemaps_cifreader,],

      packages                          = ['pyemaps.diffract', 
                                           'pyemaps.scattering', 
                                           'pyemaps.spg',
                                           'pyemaps.CifFile',
                                           'pyemaps.CifFile.drel'
                                           ],
      
      package_dir                       = {'pyemaps':'',
                                           'pyemaps.CifFile':'CifFile/src'
                                            },
      entry_points                      = {
                                            'console_scripts': [
                                            'pyemaps=pyemaps.__main__:main',  # This makes 'pyemaps' a command-line executable
                                            ],
                                            },
      install_requires                  = get_install_requires(),
      
      data_files                        = [('pyemaps', 
                                            ['__config__.py',
                                            '__main__.py',
                                            '__version__.py',
                                            'README.md',
                                            'COPYING',
                                            'license.txt']),
                                            ('pyemaps/samples', get_samples()),
                                            ('pyemaps/cdata', get_cdata()),

                                          ],
      exclude_package_data              = {'pyemaps':['*.i', 
                                                '*.cpp', 
                                                '*.f90',
                                                '*.pyd', 
                                                '*.toml', 
                                                '*.in', 
                                                '__pycache__/*.pyc',
                                                '*.egg-info/*'
                                                'setup.py',
                                                'setup_win.cfg',
                                                'setup_lin.cfg',
                                                'README.md',
                                                'CONTRIBUTING.md'
                                                ],
                                            'pyemaps.stem4d':['*.i', 
                                                            '*.cpp',
                                                            '__pycache__/*.pyc'
                                                            ]
                                            }
)

