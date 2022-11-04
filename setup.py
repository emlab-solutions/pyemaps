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
mod_name = "emaps"

MKLROOT = os.getenv('MKLROOT')
IFORTROOT = os.getenv('IFORTROOT')
# BUILT_TYPE=None #default build type - free, 'uiuc' for uiuc, None, full version

dpgen_cobj = 'write_dpbin.o'


compile_args=['-Qm64',
              '-WB',
              '-heap-arrays',
              '-Qopenmp',
              '-GS', 
              '-4R8',
              '-fpp',
              '-warn:nointerfaces',
              '-O2', #this option does not work with -fast
              '-libs:static',
              '-MT',
              '-c']
              
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
            # 'intel-fortran-rt == 2022.1.0',
            # 'mkl-service == 2.4.0'
            ]

dif_source = ['diffract.f90',
            'diff_types.f90', 
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
               'bloch.f90',
               'bloch_mem.f90'
              ]
stereo_files = ['stereo.f90']

mxtal_files = ['mxtal_mem.f90',
               'mxtal.f90']

dpgen_files =['dp_types.f90',
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

# c_objs = ['blochimgs.o', 'write_dpbin.o']
c_objs_win = ['blochimgs.obj']
c_objs_lin = ['blochimgs.o']


sct_files =['scattering_sct.pyf', 'scattering.f90']  

spgra_files =['spg_spgseek.pyf', 'spgseek.f90', 'spgra.f90']            

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
        objs = c_objs_win
    elif 'linux' in osname:
        objs = c_objs_lin
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

def get_diffract_sources():

    # comp = get_comp()
    # print(f'----------building component: {comp}')

    src_list = []
    # if comp == 'dif':
    #     pyf = ".".join([mod_name+'_dif','pyf'])
    #     src_list.append(pyf)
    #     src_list.extend(dif_source)

    # if comp == 'dpgen':
    #     pyf = ".".join([mod_name+'_dpgen','pyf'])
    #     src_list.append(pyf)
    #     src_list.extend(dif_source)
    #     src_list.extend(dpgen_files)
    #     # return comp, src_list

    # if comp == 'csf':
    #     pyf = ".".join([mod_name+'_csf','pyf'])
    #     src_list.append(pyf)
    #     src_list.extend(dif_source)
    #     src_list.extend(csf_files)
    #     # return comp, src_list

    # if comp == 'powder':
    #     pyf = ".".join([mod_name+'_powder','pyf'])
    #     src_list.append(pyf)
    #     src_list.extend(dif_source)
    #     src_list.extend(csf_files)
    #     src_list.extend(powder_files)
    #     # return comp, src_list

    # if comp == 'bloch':
    #     pyf = ".".join([mod_name+'_bloch','pyf'])
    #     src_list.append(pyf)
    #     src_list.extend(dif_source)
    #     src_list.extend(csf_files)
    #     src_list.extend(powder_files)
    #     src_list.extend(bloch_files)

    # if comp == 'stereo':
    #     pyf = ".".join([mod_name+'_stereo','pyf'])
    #     src_list.append(pyf)
    #     src_list.extend(dif_source)
    #     src_list.extend(csf_files)
    #     src_list.extend(powder_files)
    #     src_list.extend(bloch_files)
    #     src_list.extend(stereo_files)

    pyf = ".".join([mod_name,'pyf'])
    src_list.append(pyf)
    src_list.extend(dif_source)
    src_list.extend(csf_files)
    src_list.extend(powder_files)
    src_list.extend(bloch_files)
    # src_list.extend(dpgen_files)
    
    src_list.extend(stereo_files)
    src_list.extend(mxtal_files)
    print(f'source code list: {src_list}')
    emaps_dir = get_emaps_srcdir()
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

    return [os.path.join(sdn, os.path.basename(name)) for name in sfile_list]

def get_cdata(sdn = 'cdata'):
    '''
    input: sdn = sample directory name under pyemaps
    '''
    import glob

    free_xtl_remove = ['BiMnO3.xtl', 
                       'CoSb3_Skutterudite.xtl', 
                       'Pentacene.xtl', 
                       'SiAlONa.xtl']

    base_dir = os.path.realpath(__file__)
    samples_base_dir = os.path.join(os.path.dirname(base_dir), sdn)
    sbase_files = os.path.join(samples_base_dir, '*.xtl')
    sfile_list = glob.glob(sbase_files)
    res = [os.path.join(sdn, os.path.basename(name)) for name in sfile_list]
    print(f'******build type {build_type}')
    if build_type != 'free':
        return res

    # if it is free package remove some crystals
    out =[]
    
    for rf in res:
        _, rfn = os.path.split(rf)
        if rfn not in free_xtl_remove:
            out.append(rf)
        
    return out

# def get_intel_redist():
#     import os, glob
#     intel_redistdir = os.path.join(os.getenv('IFORTROOT'), 'redist', 'intel64_win', 'compiler')
#     sbase_files = os.path.join(intel_redistdir, '*.dll')
#     ifile_list = glob.glob(sbase_files)
    
#     return ifile_list

def get_library_dirs():
    
    import platform

    lib_folder = ''

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
    libdir.append(os.path.join(MKLROOT, 'lib', lib_folder))
    
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
        return compile_args
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

    if build_type == 'full':
        # full version
        return ([('NPY_NO_DEPRECATED_API', 
                    'NPY_1_7_API_VERSION')
                ], 
                ['__BFREE__', '__BUIUC__' ])

    if build_type == 'free':
        # limited free version
        return ([('__BFREE__', 1),
                ('NPY_NO_DEPRECATED_API', 
                'NPY_1_7_API_VERSION')
                ], 
                ['__BUIUC__'])

    if build_type == 'uiuc':
        # less limited free version
        return ([('__BUIUC__', 1),
                ('NPY_NO_DEPRECATED_API', 
                'NPY_1_7_API_VERSION')
                ], 
                ['__BFREE__'])
    
    raise ValueError("Error: build type not specified")

# ------------------- must set this before build -------------------
pyemaps_build_defs, pyemaps_build_undefs= get_emaps_macros()
# print(f'Defines for the build: {pyemaps_build_defs}')
# print(f'Undefines for the build: {pyemaps_build_undefs}')

pyemaps_dif = Extension("pyemaps.diffract.emaps",
        sources                = get_diffract_sources(),
        extra_f90_compile_args     = get_compiler_args(),
        define_macros          = pyemaps_build_defs,
        undef_macros           = pyemaps_build_undefs,
        # extra_c_compile_args   = c_compile_args,
        # language               = 'c11',
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
        # extra_compile_args         = extra_compile_args,
        # language               = 'c11',
        extra_link_args             =["-static", ],
        define_macros               = [('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION'),
                                #   ('Py_LIMITED_API', '0x03070000'),
                                      ],
        f2py_options           = ["--quiet",]
)

pyemaps_spg = Extension("pyemaps.spg.spg",
        sources                     = get_spg_sources(),
        extra_f90_compile_args      = get_compiler_args(),
        # extra_compile_args         = extra_compile_args,
        # language               = 'c11',
        extra_link_args        =["-static", ],
        define_macros          = [('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')
                                 ],
        f2py_options           = ["--quiet",]
)


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
                                           pyemaps_cifreader],

      packages                          = [ 'pyemaps.diffract', 
                                           'pyemaps.scattering', 
                                           'pyemaps.spg',
                                           'pyemaps.CifFile',
                                           'pyemaps.CifFile.drel'
                                           ],
      
      package_dir                       = {'pyemaps':'',
                                            'pyemaps.CifFile':'CifFile/src'
                                            },
      install_requires              = get_install_requires(),
      
      data_files                    = [('pyemaps', 
                                        ['__config__.py',
                                        '__main__.py',
                                        '__version__.py',
                                        'README.md',
                                        'COPYING',
                                        'license.txt']),
                                        ('pyemaps/samples', get_samples()),
                                        ('pyemaps/cdata', get_cdata()),
                                        # ('pyemaps/diffract', get_intel_redist()),
                                      ]
)