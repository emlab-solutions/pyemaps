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

build_type = os.getenv('EMAPS_BTYPE')
if build_type is None:
    build_type = 'free'

if os.getenv('PYEMAPS_DEBUG') is not None:
    pyemaps_debug = int(os.getenv('PYEMAPS_DEBUG'))
else:
    pyemaps_debug = 0

mod_name = "emaps"

MKLROOT = os.getenv('MKLROOT')
IFORTROOT = os.getenv('IFORTROOT')

dpgen_cobj = 'write_dpbin.o'

compile_args_debug=['-Qm64',
                    '-Od',
              '-WB',
              '-heap-arrays:1024',
              '-Qopenmp',
              '-Qmkl',
            #   '-Qopenmp-simd',
            #   '-GS:partial', 
              '-fpp',
              '-warn:all',
            #   '-O2', #this option does not work with -fast
            #   '-libs:static',
            #   '-MT',
            #   '-assume:buffered_io',
            #   '-traceback',
            #   '-check:all',
            #   '-align:array32byte',
            #   '-Qparallel',
            #   '-Qopt-report:2',
              '-c']
# --------------- production options--------------
compile_args=['-Qm64',
              '-WB',
              '-heap-arrays:1024',
              '-Qopenmp',
              '-Qmkl',
              '-GS:partial', 
              '-fpp',
              '-warn:all',
              '-O2', #this option does not work with -fast
              '-libs:static',
              '-MT',
              '-assume:buffered_io',
              '-c']

# --------debugging options-----------
# compile_args=['-Qm64',
#               '-WB',
#               '-heap-arrays:1024',
#               '-check:all',
#               'Qfp-stack-check',
#               '-Qopenmp',
#               '-GS:partial', 
#               '-fpp',
#               '-warn:nointerfaces',
#             #   '-O2', #this option does not work with -fast
#             #   '-libs:static',
#               '-MT',
#               '-assume:buffered_io',
#               '-traceback',
#               '-c']
              
compile_args_lin= ['-m64',
                   '-WB', 
                   '-qopenmp', 
                   '-qmkl', 
                   '-heap-arrays', 
	               '-r8', 
                   '-fpp', 
                #    '-warn nointerfaces',
                   '-O3',
                #    'fp-stack-check',
                   '-c']

intel_libs = ['mkl_intel_lp64',
              'mkl_intel_thread',
              'mkl_core', 
              'libiomp5md']

c_compile_args = ["-std=c11", "-stack_size 2000000"]

intel_libs_lin = ['mkl_rt', 
              'iomp5',
              'pthread',
              'm',
              'dl']

lapack_lib = 'mkl_lapack95_lp64'

install_requires_common = [
            'numpy >= 1.21.2',
            'matplotlib >= 3.2.1',
            ]

dif_source = [
            'diff_types.f90', 
            'diffract.f90',
            'scattering.f90', 
            'spgra.f90',
            'diff_memalloc.f90',
            'crystal_mem.f90', 
            'emaps_consts.f90',
            'xtal0.f90', 
            'helper.f90', 
            'asf.f90', 
            'atom.f',
            'metric.f', 
            'readutils.f',
            'sfsub.f90', 
            'spgroup.f90', 
            'lafit.f90'
            ]

bloch_files = ['zg.f90',
               'cbloch.f90',
               'bloch_mem.f90',
               'bloch.f90'
              ]
stereo_files = ['stereo.f90']

mxtal_files = ['mxtal_mem.f90',
               'mxtal.f90']

dpgen_files =['cdpgen.f90',
              'dp_types.f90',
			  'dp_gen.f90'
             ]

csf_files =['csf_types.f90',
			  'csf.f90'
            ]

powder_files =['powder_types.f90',
			  'powder.f90',
              'pkprof.f90'
              ]

spgra_files =['spgra.f90']

c_objs_free_win = ['blochimgs.obj']
c_objs_free_lin = ['blochimgs.o']


sct_files =['scattering_sct.pyf', 'scattering.f90']  

spgra_files =['spg_spgseek.pyf', 'spgseek.f90', 'spgra.f90']    

# ------------- ediom -----------------
ediomSRCFiles = ['imgutil_sub.cpp', 
            'DPIndex.cpp', 
            'nrutil.cpp', 
            'refine.cpp',
            'peak.cpp',
            'StackDP.cpp', 
            'simplxc.cpp',
            'symmetry.cpp',
            # 'ediom_wrap.c',
            'ediom.i']
# ------------- ediom -----------------


def get_ediom_srcdir():

    current_path = Path(os.path.abspath(__file__))

    parent_path = current_path.parent.absolute()

    return os.path.join(parent_path, 'ediom')

def get_ediom_sources():

    ediom_dir = get_ediom_srcdir()
 
    src_list = []
    for sf in ediomSRCFiles:
        src_list.append(os.path.join(ediom_dir, sf))
    print(f'Ediom source file list: {src_list}')
    # exit()
    return src_list   
   
def get_ediom_includes():
    #  for ccompiler cl arguement too long issue
    # see https://github.com/pypa/setuptools/pull/3775/commits/dd03b731045d5bb0b47648554f9a1a7429ef306a
    # temporary fix
    import numpy as np
    from sysconfig import get_paths
    
    includeDirs=[np.get_include()]
    # python's include
    includeDirs.append(get_paths()['include'])
    includeDirs.append(get_ediom_srcdir())

    return includeDirs

def get_ediom_libs():
    from sysconfig import get_paths
    return [os.path.join(get_paths()['data'], 'libs'),]

def get_emaps_srcdir():

    current_path = Path(os.path.abspath(__file__))

    parent_path = current_path.parent.absolute()

    return os.path.join(parent_path, 'emaps')

def get_extra_objects():
    '''
    extra objects such as those from c code
    '''
    import platform, os

    objs = []
    osname = platform.platform().lower()
    print(f'OS name found: {osname}')
    
    
    if  'windows' in osname:
        objs = c_objs_free_win
    elif 'linux' in osname:
        objs = c_objs_free_lin
    else:
        raise Exception('Unsupported OS')

    # if build_type == "all":
    if  'windows' in osname:
        objs.append('write_dpbin.obj') 
    elif 'linux' in osname:
        objs.append('write_dpbin.o')
    else:
        raise Exception('Unsupported OS')

    emaps_dir = get_emaps_srcdir()
    objlist = [os.path.join(emaps_dir, o) for o in objs]
    return objlist

def get_scattering_sources():

    emaps_dir = get_emaps_srcdir()

    src_list = []
    for sf in sct_files:
        src_list.append(os.path.join(emaps_dir, sf))
    
    return src_list        


def get_spg_sources():

    emaps_dir = get_emaps_srcdir()

    src_list = []
    for sf in spgra_files:
        src_list.append(os.path.join(emaps_dir, sf))
    
    return src_list

def get_diffract_sources(comp=None):

    src_list = []
    emaps_dir = get_emaps_srcdir()

    pyfname = mod_name
    # if build_type == 'full':
    # pyfname += '_dpgen'

    pyf = ".".join([pyfname,'pyf'])
    src_list.append(pyf)
    src_list.extend(dif_source)
    src_list.extend(csf_files)
    src_list.extend(powder_files)
    src_list.extend(bloch_files)
    src_list.extend(stereo_files)
    src_list.extend(mxtal_files)
    # if build_type == 'full':
    src_list.extend(dpgen_files)
    
    
    print(f'source code list: {src_list}')
    return [os.path.join(emaps_dir, srcfn) for srcfn in src_list]

def get_cifreader_source():
    current_path = Path(os.path.abspath(__file__))
    pyemaps_parent_path = current_path.parent.absolute()
    cifreader_path = os.path.join(pyemaps_parent_path, 'CifFile')

    print(f'-----------CifReader Source path: {cifreader_path}')

    src_files = ["src/lib/lex.yy.c","src/lib/py_star_scan.c"]
    return [os.path.join(cifreader_path, s) for s in src_files]

def get_comp():
    '''
    Get pyemaps component to be built from comp.json file
    '''
    
    import json, os
    from pathlib import Path

    json_cfg = os.getenv('PYEMAPS_JSON')

    if not json_cfg:
        json_cfg = "comp.json" # default

    emapsdir = get_emaps_srcdir()
    comp = 'dif'

    comp_cfg = os.path.join(emapsdir,json_cfg)
    try:
        with open(comp_cfg, 'r') as jf:
            comp = json.load(jf)['component']

    except IOError as e:
        raise ValueError(f"Error reading component configure file: {e}")
   
    return comp

class build_dp_ext(numpy_build_ext):
    def finalize_options(self):
        numpy_build_ext.finalize_options(self)
        emapsdir = get_emaps_srcdir()
        cobj = os.path.join(emapsdir, dpgen_cobj)
        self.link_objects = [cobj]

def get_samples(sdn = 'samples'):
    '''
    input: sdn = sample directory name under pyemaps
    '''

    import os, glob
    base_dir = os.path.realpath(__file__)
    samples_base_dir = os.path.join(os.path.dirname(base_dir), sdn)
    sbase_files = os.path.join(samples_base_dir, '*.py')
    sfile_list = glob.glob(sbase_files)
    sfile_list.append('al_db.bin')
    sfile_list.append('al.img')

    return [os.path.join(sdn, os.path.basename(name)) for name in sfile_list]

def get_cdata(sdn = 'cdata'):
    '''
    input: sdn = sample directory name under pyemaps
    '''
    import glob


    free_xtl_remove = []
    if build_type == 'free':
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

def get_library_dirs():
    
    import platform

    lib_folder = ''
    mkl_folder = 'intel64'

    osname = platform.platform().lower()
    print(f'OS name found: {osname}')
    if  'windows' in osname:
        lib_folder = 'intel64_win'
    elif 'linux' in osname:
        lib_folder = 'intel64'
    else:
        raise Exception('Unsupported OS')

    libdir = []
    libdir.append(os.path.join(IFORTROOT, 'compiler', 'lib', lib_folder)) #intel openmp libdir
    libdir.append(os.path.join(MKLROOT, 'lib', mkl_folder))
    
    return libdir

def get_include_dirs():
    # pass
    incl = []
    incl.append(get_emaps_srcdir())
    incl.append(os.path.join(MKLROOT, 'include'))
    return incl

def get_libraries():
    import sys

    libs = []
    if sys.platform == 'win32': 
        libs = intel_libs.copy()
    elif sys.platform == 'linux':
        libs = intel_libs_lin.copy()
    else:
        raise Exception('The OS is not supported')

    libs.insert(0, lapack_lib)
    return libs

def get_compiler_args():
    import sys
    if sys.platform == 'win32': 
        return compile_args if pyemaps_debug == 0 else compile_args_debug
    elif sys.platform == 'linux':
        return compile_args_lin
    else:
        raise Exception('The OS is not supported')

def get_install_requires():
    import sys
    install_reqs = install_requires_common.copy()

    if sys.platform == 'win32': 
        install_reqs += ['msvc-runtime == 14.29.30133',
                        'intel-fortran-rt == 2022.1.0',
                        'mkl == 2022.1.0']
        return install_reqs
    elif sys.platform == 'linux':
        install_reqs += ['intel-fortran-rt == 2022.1.0',
                         'mkl == 2022.1.0']
        return install_reqs
    else:
        raise Exception('The OS is not supported')
    
def get_emaps_macros():
    
    if build_type != 'uiuc' and build_type != 'full' and build_type != 'free':
        raise ValueError("Error: build type not specified")

    def_list = [('NPY_NO_DEPRECATED_API','NPY_1_7_API_VERSION')]
    
    undef_list = []

    if build_type == 'full':
        # full version
        undef_list.append('__BFREE__')
        undef_list.append('__BUIUC__')

    if build_type == 'free':
        # limited free version
        def_list.append(('__BFREE__', 1))
        undef_list.append('__BUIUC__')

    if build_type == 'uiuc':
        # less limited free version
        def_list.append(('__BUIUC__', 1))
        undef_list.append('__BFREE__')

    if pyemaps_debug != 0:
        # print(f'Build is debug build: {pyemaps_debug}')
        def_list.append(('__BDEBUG__', 1))
    else:
        # print(f'Build is not a debug build: {pyemaps_debug}')
        undef_list.append('__BDEBUG__')
    
    # print(f'defundef list: {def_list}, {undef_list}')
    # exit()
    return [def_list, undef_list]
    
# ------------------- must set this before build -------------------

# from distutils import ccompiler
# cc = ccompiler.new_compiler()
# cc.set_include_dirs([])


pyemaps_build_defs, pyemaps_build_undefs= get_emaps_macros()
pyemaps_dif = Extension("pyemaps.diffract.emaps",
        sources                = get_diffract_sources(),
        extra_f90_compile_args     = get_compiler_args(),
        define_macros          = pyemaps_build_defs,
        undef_macros           = pyemaps_build_undefs,
        extra_link_args        =["-static", ],
        libraries              = get_libraries(),
        library_dirs           = get_library_dirs(),
        include_dirs           = get_include_dirs(),
        extra_objects          = get_extra_objects(),
        f2py_options           = ["--quiet",]
)

pyemaps_scattering = Extension("pyemaps.scattering.scattering",
        sources                     = get_scattering_sources(),
        extra_f90_compile_args      = get_compiler_args(),
        extra_link_args             =["-static", ],
        define_macros               = [('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION'),
                                      ],
        f2py_options           = ["--quiet",]
)

pyemaps_spg = Extension("pyemaps.spg.spg",
        sources                     = get_spg_sources(),
        extra_f90_compile_args      = get_compiler_args(),
        extra_link_args        =["-static", ],
        define_macros          = [('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')
                                 ],
        f2py_options           = ["--quiet",]
)


pyemaps_cifreader = Extension("pyemaps.CifFile.StarScan",
        sources                = get_cifreader_source()
)


pyemaps_ediom =  Extension(
            'pyemaps.ediom._ediom',
            sources                 =get_ediom_sources(),
            extra_objects           =[],
            include_dirs            =get_ediom_includes(),
            library_dirs            =get_ediom_libs(),
            libraries               =[],
            define_macros           = pyemaps_build_defs,
            undef_macros            = pyemaps_build_undefs,
            extra_link_args         =[],
            swig_opts               =['-python']
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
                                           'pyemaps.CifFile.CifFile_module',
                                           'pyemaps.CifFile.yapps3_compiled_rt',
                                           'pyemaps.CifFile.YappsStarParser_1_1',
                                           'pyemaps.CifFile.YappsStarParser_1_0',
                                           'pyemaps.CifFile.YappsStarParser_STAR2',
                                           'pyemaps.CifFile.YappsStarParser_2_0',
                                           'pyemaps.CifFile.StarFile',
                                           'pyemaps.CifFile.TypeContentsParser'],

      ext_modules                       = [pyemaps_dif, 
                                           pyemaps_scattering, 
                                           pyemaps_spg,
                                           pyemaps_ediom,
                                           pyemaps_cifreader],

      packages                          = ['pyemaps.diffract', 
                                           'pyemaps.scattering', 
                                           'pyemaps.spg',
                                           'pyemaps.ediom',
                                           'pyemaps.CifFile',
                                           'pyemaps.CifFile.drel'
                                           ],
      
      package_dir                       = {'pyemaps':'',
                                           'pyemaps.CifFile':'CifFile/src'
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
                                                ],
                                            'pyemaps.ediom':['*.i', 
                                                            '*.cpp',
                                                            '__pycache__/*.pyc'
                                                            ]
                                            }
)

if pyemaps_debug:
    print(f'#######################Build is a debug build')
else:
    print(f'#######################Build is not a debug build')
# ------------- using intel compiler------------------------- 
# from setuptools import setup, Extension
# import os

# # Set the path to the Intel C Compiler executable
# os.environ['CC'] = 'C:\\Program Files (x86)\\Intel\\oneAPI\\compiler\\latest\\windows\\bin\\intel64\\icl.exe'

# # Set the necessary environment variables for the Intel C Compiler
# os.environ['INTEL_LICENSE_FILE'] = 'C:\\Program Files (x86)\\Intel\\Licenses\\use.lic'
# os.environ['INTEL_DEV_REDIST'] = 'C:\\Program Files (x86)\\Intel\\oneAPI\\redist\\intel64\\compiler'
# os.environ['LIB'] = 'C:\\Program Files (x86)\\Intel\\oneAPI\\compiler\\latest\\windows\\compiler\\lib\\intel64;C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Community\\VC\\Tools\\MSVC\\14.28.29333\\ATLMFC\\lib\\x64;C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Community\\VC\\Tools\\MSVC\\14.28.29333\\lib\\x64;C:\\Windows\\System32;C:\\Windows\\SysWOW64'
# os.environ['INCLUDE'] = 'C:\\Program Files (x86)\\Intel\\oneAPI\\compiler\\latest\\windows\\compiler\\include;C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Community\\VC\\Tools\\MSVC\\14.28.29333\\ATLMFC\\include;C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Community\\VC\\Tools\\MSVC\\14.28.29333\\include'

# example_module = Extension('_example',
#                            sources=['example.i', 'example.c'],
#                            extra_compile_args=['/Qstd=c11', '/Wall', '/Wextra', '/QxHost', '/Qmarch=native', '/Qopenmp'],
#                            swig_opts=['-py3'],
#                            )
