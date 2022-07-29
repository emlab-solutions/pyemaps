from ensurepip import version
from nturl2path import url2pathname
from unicodedata import name
import os

mod_name = "emaps"
ver = "1.0.0"
dp_cobj = "write_dpbin.o"

MKLROOT = os.getenv('MKLROOT')
IFORTROOT = os.getenv('IFORTROOT')

compile_args=['-Qm64',
              '-WB',
              '-heap-arrays:768',
            #   '-double-size:64',
              '-Qopenmp',
              '-GS', 
              '-4R8',
              '-fpp',
              '-warn:nointerfaces',
              '-O2', #this option does not work with -fast
            #   '-fast', 
            #   '-Qfp-stack-check',
              '-c']

intel_libs = ['mkl_intel_lp64',
              'mkl_intel_thread',
              'mkl_core', 
              'libiomp5md']

lapack_lib = 'mkl_lapack95_lp64'

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

f77obj_files = ['atom.o', 'metric.o', 'readutils.o']

def get_library_dirs():
    # pass
    libdir = []
    libdir.append(os.path.join(IFORTROOT, 'lib', 'intel64')) #intel openmp libdir
    libdir.append(os.path.join(MKLROOT, 'lib', 'intel64' ))
    # print(f'libraries dirs: {libdir}')
    # exit(1)
    return libdir

def get_include_dirs():
    # pass
    incl = []
    incl.append(get_emapsdir())
    incl.append(os.path.join(MKLROOT, 'include'))
    return incl


def get_fcompiler_args():
    c_args = compile_args.copy()
    # lp_mod_include = os.path.join(MKLROOT, 'include', 'intel64', 'lp64')
    # c_args.insert(-1, '-module:' + lp_mod_include,)
    return c_args

def get_libraries():
    libs = intel_libs.copy()
    libs.insert(0, lapack_lib)
    return libs

def get_comp():
    '''
    Get pyemaps component to be built from comp.json file
    '''
    
    import json

    json_cfg = os.getenv('PYEMAPS_JSON')

    if not json_cfg:
        json_cfg = "comp.json" # default

    currdir = os.path.dirname(os.path.realpath(__file__))
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

def get_emapsdir():
    from pathlib import Path

    print(f'current file path: {__file__}')
    current_path = Path(os.path.abspath(__file__))
    print(f'current directory: {current_path}')

    parent_path = current_path.parent.parent.absolute()
    print(f'current parent directory: {parent_path}')

    emaps_dir = os.path.join(parent_path, 'emaps')
    print(f'Parent dir found: {emaps_dir}')

    return emaps_dir

def get_objs():
    obj_list = []
    emapsdir = get_emapsdir()
    return [os.path.join(emapsdir, objn) for objn in f77obj_files]

def get_sources():

    comp = get_comp()
    print(f'----------comp: {comp}')

    src_list = []
    if comp == 'dif':
        pyf = ".".join([mod_name+'_dif','pyf'])
        src_list.append(pyf)
        src_list.extend(dif_source)
        # return comp, src_list
    
    # if comp == 'bloch':
    #     pyf = ".".join([mod_name+'_bloch','pyf'])
    #     src_list.append(pyf)
    #     src_list.extend(dif_source)
    #     src_list.extend(bloch_files)
    #     # return comp, src_list

    if comp == 'dpgen':
        pyf = ".".join([mod_name+'_dpgen','pyf'])
        src_list.append(pyf)
        src_list.extend(dif_source)
        src_list.extend(dpgen_files)
        # return comp, src_list

    if comp == 'csf':
        pyf = ".".join([mod_name+'_csf','pyf'])
        src_list.append(pyf)
        src_list.extend(dif_source)
        src_list.extend(csf_files)
        # return comp, src_list

    if comp == 'powder':
        pyf = ".".join([mod_name+'_powder','pyf'])
        src_list.append(pyf)
        src_list.extend(dif_source)
        src_list.extend(csf_files)
        src_list.extend(powder_files)
        # return comp, src_list

    if comp == 'bloch':
        pyf = ".".join([mod_name+'_bloch','pyf'])
        src_list.append(pyf)
        src_list.extend(dif_source)
        src_list.extend(csf_files)
        src_list.extend(powder_files)
        src_list.extend(bloch_files)

    emapsdir = get_emapsdir()
    return [os.path.join(emapsdir, srcfn) for srcfn in src_list]

    # if comp == 'spgra':
    #     pyf = ".".join([mod_name+'_spgra','pyf'])
    #     src_list.append(pyf)
    #     src_list.extend(spgra_files)
    #     return comp, src_list
        
    # return comp, None

def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration
    # from numpy.distutils.fcompiler import get_default_fcompiler

    # compiler = get_default_fcompiler()

    # f90flags = []
    # if compiler == 'intel' or compiler == 'intelvem':
    #     print()
    config = Configuration('diffract', parent_package, top_path)

    src_files = get_sources()
    
    if not src_files:
        raise ValueError("Error finding extension source!")

    print(f'source list for duffract: {src_files}')
    # exit(1)

    # obj_files = get_objs()
    config.add_extension(   
        name                   = mod_name,
        sources                = src_files,
        extra_f90_compile_args = get_fcompiler_args(),
        # define_macros          = [('__BFREE__', 3),('OMP_NUM_THREADS', 4)],
        define_macros          = [('__BFREE__', 3),],
        undef_macros           = ['WOS',],
        libraries              = get_libraries(),
        library_dirs           = get_library_dirs(),
        include_dirs           = get_include_dirs()
    )

    # print(f"####Before building pyemaps package for {c}...")  

    return config

    
if __name__ == "__main__":

    import setuptools
    from numpy.distutils.core import setup

    setup(**configuration(top_path='').todict())