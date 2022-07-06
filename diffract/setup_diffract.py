from ensurepip import version
from nturl2path import url2pathname
from unicodedata import name

mod_name = "emaps"
ver = "1.0.0"
dp_cobj = "write_dpbin.o"

compile_args=['-m64',         
            '-Wno-tabs', 
            '-Warray-bounds',
            '-fdefault-double-8',
            '-fdefault-real-8',
            '-fopenmp',
            '-fcheck=all,no-array-temps',
            '-cpp', 
            '-Wall',
            '-O3']

dif_source = ['diffract.f95',
            'diff_types.f95', 
            'scattering.f95', 
            'spgra.f95',
            'diff_memalloc.f95',
            'crystal_mem.f95', 
            'emaps_consts.f95',
            'xtal0.f95', 
            'helper.f95', 
            'asf.f95', 
            'atom.f95',
            'metric.f95', 
            'readutils.f95',
            'sfsub.f95', 
            'spgroup.f95', 
            'lafit.f95'
            ]

bloch_files = ['cg.f95',
               'bloch.f95',
               'bloch_mem.f95'
            ]

dpgen_files =['dp_types.f95',
			  'dp_gen.f95'
            ]

csf_files =['csf_types.f95',
			  'csf.f95'
            ]

powder_files =['powder_types.f95',
			  'powder.f95',
              'pkprof.f95'
            ]

spgra_files =['spgra.f95']

        
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
        
    return comp, None

def configuration(parent_package='', top_path=None):
    import os
    from numpy.distutils.misc_util import Configuration

    config = Configuration('diffract', parent_package, top_path)

    src_files = get_sources()
    
    if not src_files:
        raise ValueError("Error finding extension source!")

    print(f'source list for duffract: {src_files}')

    config.add_extension(
                 name                   = mod_name,
                 sources                = src_files,
                 extra_f90_compile_args = compile_args,
    )

    # print(f"####Before building pyemaps package for {c}...")  

    return config

    
if __name__ == "__main__":

    import setuptools
    from numpy.distutils.core import setup

    setup(**configuration(top_path='').todict())