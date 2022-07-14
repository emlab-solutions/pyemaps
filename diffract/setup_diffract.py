from ensurepip import version
from nturl2path import url2pathname
from unicodedata import name

mod_name = "emaps"
ver = "1.0.0"
dp_cobj = "write_dpbin.o"

compile_args=['-Qm64',
              '-WB',
            #   '-double-size:64',
              '-'
              '-Qopenmp',
              '-GS', 
              '-fast',
              '-4R8',
              '-check:all',
            #   '-check:nostack',
              '-fpp',
            #   '-nogen-interfaces',
              '-Qipo',
            #   '-warn:all',
              '-warn:nointerfaces',
              '-O3', 
              '-Qfp-stack-check',
              '-c']

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

bloch_files = ['cg.f90',
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
        
def get_comp():
    '''
    Get pyemaps component to be built from comp.json file
    '''
    
    import json, os

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
    import os
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
    import os
    obj_list = []
    emapsdir = get_emapsdir()
    return [os.path.join(emapsdir, objn) for objn in f77obj_files]

def get_sources():
    import os

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
        # print(f'----------srclist0: {src_list}')
        pyf = ".".join([mod_name+'_bloch','pyf'])
        src_list.append(pyf)
        # print(f'----------srclist1: {src_list}')
        src_list.extend(dif_source)
        # print(f'----------srclist2: {src_list}')
        src_list.extend(csf_files)
        # print(f'----------srclist3: {src_list}')
        src_list.extend(powder_files)
        # print(f'----------srclist4: {src_list}')
        src_list.extend(bloch_files)
        # print(f'----------srclist5: {src_list}')

    emapsdir = get_emapsdir()
    return [os.path.join(emapsdir, srcfn) for srcfn in src_list]

    # if comp == 'spgra':
    #     pyf = ".".join([mod_name+'_spgra','pyf'])
    #     src_list.append(pyf)
    #     src_list.extend(spgra_files)
    #     return comp, src_list
        
    # return comp, None

def configuration(parent_package='', top_path=None):
    import os
    from numpy.distutils.misc_util import Configuration

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
                 extra_f90_compile_args = compile_args,
                 define_macros          = [('__BFREE__', 5),]
                #  extra_objects          = obj_files
    )

    # print(f"####Before building pyemaps package for {c}...")  

    return config

    
if __name__ == "__main__":

    import setuptools
    from numpy.distutils.core import setup

    setup(**configuration(top_path='').todict())