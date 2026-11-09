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
import os
from pathlib import Path

# pyemaps is pure Python. The bundled PyCifRW's optional C scanner
# (pyemaps.CifFile.StarScan, sources in CifFile/src/lib) is not built:
# pyemaps reads CIF files with ReadCif's default pure-Python scanner, and
# PyCifRW falls back to it when StarScan is absent. That makes the wheel
# py3-none-any, one wheel for every Python version.
from setuptools import setup
try:
    from setuptools.command.install_data import install_data as _install_data
except ImportError:
    # setuptools has no install_data command of its own (checked up to
    # 84.2.1), so this branch is the one that normally runs. Python 3.12+
    # has no stdlib distutils, but importing setuptools first makes
    # setuptools' bundled copy answer this import.
    from distutils.command.install_data import install_data as _install_data


class install_data_in_package(_install_data):
    '''
    Install data_files inside the installed package, as numpy.distutils did.

    Plain setuptools installs relative data_files under sys.prefix. The
    wheel then puts them in its .data/ section, so __main__.py,
    __version__.py, __config__.py, cdata/ and samples/ would end up outside
    site-packages/pyemaps. Point install_data at install_lib instead, which
    keeps the same wheel layout as earlier pyemaps releases.
    '''
    def finalize_options(self):
        self.set_undefined_options('install',
                                   ('install_lib', 'install_dir'),
                                   ('root', 'root'),
                                   ('force', 'force'),
                                   )


install_requires = [
            'emaps >= 1.1.2',
            'numpy >= 1.21.2',
            'matplotlib >= 3.2.1'
            ]

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
      description                       ="A Python Package for Transmission Electron Diffraction Simulations and Crystallographic Computing",
      long_description_content_type     ='text/markdown',
      long_description                  = get_long_description(),
      py_modules                        = ['pyemaps.crystals',
                                           'pyemaps.kdiffs',
                                           'pyemaps.ddiffs',
                                           'pyemaps.display',
                                           'pyemaps.errors',
                                           'pyemaps.fileutils',
                                           'pyemaps.xtal',
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

      packages                         = ['pyemaps.diffract', 
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
      cmdclass                          = {'install_data': install_data_in_package},

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

