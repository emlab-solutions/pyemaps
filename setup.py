# This file is part of pyEMAPS.
# Copyright (C) 2021-2026 EMLab Solutions, Inc.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Additional permission under GPLv3 Section 7:
# See license-exception.txt for the exception permitting
# combination with the separately licensed backend, emaps.

'''
Author:             EMLab Solutions, Inc.
Date Created:       May 07, 2022  
'''
import os
from pathlib import Path

# pyemaps is pure Python, so the wheel is py3-none-any: one wheel for every
# Python version. It reads CIF files with its own reader (cifreader.py).
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
            'emaps >= 2.5.0',
            'numpy >= 2.0',
            'matplotlib >= 3.8.4'
            ]

# pip install "pyemaps[emd]": h5py (BSD), to read EMD files (Thermo Fisher Velox and Berkeley
# EMD) with pyemaps.read_image and StackImage.from_file. h5py has no Windows wheels for
# Python 3.15 yet, so the extra installs nothing there, and reading EMD files says so.
extras_require = {
    'emd': ['h5py >= 3.10; python_version < "3.15"'],
}

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
    # crystal structures from the Crystallography Open Database, for the samples
    sfile_list += glob.glob(os.path.join(samples_base_dir, '*.cif'))


    return [os.path.join(sdn, os.path.basename(name)) for name in sfile_list]

def get_notebooks(sdn='notebooks'):
    '''
    The Jupyter notebooks to install, without their outputs. Students see the results by running
    them, and the copies with figures, about twenty times larger, stay on GitHub. Writes the
    stripped copies under build/ and returns their paths.
    '''
    import glob
    import json

    here = os.path.dirname(os.path.realpath(__file__))
    out_dir = os.path.join('build', sdn)
    os.makedirs(os.path.join(here, out_dir), exist_ok=True)

    files = []
    for src in sorted(glob.glob(os.path.join(here, sdn, '*.ipynb'))):
        with open(src, encoding='utf-8') as f:
            nb = json.load(f)
        for cell in nb['cells']:
            if cell['cell_type'] == 'code':
                cell['outputs'] = []
                cell['execution_count'] = None
        dest = os.path.join(out_dir, os.path.basename(src))
        with open(os.path.join(here, dest), 'w', encoding='utf-8', newline='\n') as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
            f.write('\n')
        files.append(dest)

    return files

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
                                           'pyemaps.expimage',
                                           'pyemaps.tiffreader',
                                           'pyemaps.emdreader',
                                           'pyemaps.dmreader',
                                           'pyemaps.readerbase',
                                           'pyemaps.mrcreader',
                                           'pyemaps.mibreader',
                                           'pyemaps.picreader',
                                           'pyemaps.cifreader',
                                           'pyemaps.orientmap',
                                           'pyemaps.probe'],

      packages                         = ['pyemaps.diffract', 
                                           'pyemaps.scattering', 
                                           'pyemaps.spg',
                                           ],
      
      package_dir                       = {'pyemaps':'',
                                            },
      entry_points                      = {
                                            'console_scripts': [
                                            'pyemaps=pyemaps.__main__:main',  # This makes 'pyemaps' a command-line executable
                                            ],
                                            },
      project_urls                      = {
                                            'Documentation': 'https://emlab-solutions.github.io/pyemaps/',
                                            'Source': 'https://github.com/emlab-solutions/pyemaps',
                                            'Issues': 'https://github.com/emlab-solutions/pyemaps/issues',
                                            'Changelog': 'https://emlab-solutions.github.io/pyemaps/rn.html',
                                            },
      install_requires                  = get_install_requires(),
      extras_require                    = extras_require,
      cmdclass                          = {'install_data': install_data_in_package},

      data_files                        = [('pyemaps', 
                                            ['__config__.py',
                                            '__main__.py',
                                            '__version__.py',
                                            'README.md',
                                            'COPYING',
                                            'license.txt',
                                            'license-exception.txt']),
                                            ('pyemaps/samples', get_samples()),
                                            ('pyemaps/notebooks', get_notebooks()),
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

