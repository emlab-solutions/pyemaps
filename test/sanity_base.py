"""
This file is part of pyemaps
___________________________

pyemaps is free software. You can redistribute it and/or modify 
it under the terms of the GNU General Public License as published 
by the Free Software Foundation, either version 3 of the License, 
or (at your option) any later version.

pyemaps is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pyemaps.  If not, see <https://www.gnu.org/licenses/>.

Contact supprort@emlabsoftware.com for any questions and comments.
___________________________

```

Author:     EMLab Solutions, Inc.
Date:       Jan. 5th, 2025    
"""
import os
from pathlib import Path
import pickle


feat_list=[
            'diff', 
           'bloch', 
           'stereo', 
           'mxtal'
           ]
sample_feat_list = [{'diff': 'si_dif'},
                   {'bloch': 'si_block'},
                    {'lacbed': 'si_lacbed'},
                    {'scm': 'si_scm'},
                    {'stereo': 'si_stereo'},
                    {'powder': 'powder'},
                    {'csf': 'si_csf'},
                    {'mxtal': 'si_constructor'},
                    # {'dpgen': 'si_dpgen'}, TODO later
                    ]
unittest_feat_list = [
    {'diff': 'si_dif_docs'},
    {'bloch': 'si_block_docs'},
    {'lacbed': 'si_lacbed_docs'},
]
BL_GENERATION = 1
BL_COMPARISON = 2
BL_NONE = 3

TY_BUILTIN=1
TY_CIF=2
def get_cifdata_dir():

    current_path = Path(os.path.abspath(__file__))

    test_path = current_path.parent.absolute()

    return os.path.join(test_path, 'cifdata')


def get_builtin_dir():
    import pyemaps
    from pathlib import Path

    return(Path(pyemaps.__file__).parent.absolute())

def get_crystal_filename(fp):
    file_name = os.path.splitext(os.path.basename(fp))[0]
    return file_name

def get_current_folder():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return current_dir

def get_baseline_feature_filename(feature=feat_list[0], cdata_ty=TY_BUILTIN, bCreate=True):
    bdir = os.path.join(get_current_folder(), 'baseline', 'features', feature)
    if bCreate and not os.path.exists(bdir):
        os.makedirs(bdir, exist_ok=True)
    return os.path.join(bdir, 'builtin.pkl' if cdata_ty == TY_BUILTIN else 'cif.pkl')

def get_baseline_sample_filename(feature='diff', bCreate=True):
    bFound = False
    retfn = ''
    for fl in sample_feat_list:
        if feature in fl:
            if feature == 'scm' or feature == 'lacbed':
                bdir = os.path.join(get_current_folder(), 'baseline', 'samples', 'bloch')
            else:
                bdir = os.path.join(get_current_folder(), 'baseline', 'samples', feature) 

            if bCreate and not os.path.exists(bdir):
                os.makedirs(bdir, exist_ok=True)

            retfn = os.path.join(bdir, fl[feature] + '.pkl' if feature != 'dpgen' else fl[feature] + '.bin')
            bFound = True
            break
    if not bFound:
        print(f'Feature provided is not supported: {feature}')
        raise FileExistsError("Feature provided is not supported")
    
    return retfn

def get_baseline_unittest_filename(feature='diff', bCreate=True):
    bFound = False
    retfn = ''
    for fl in unittest_feat_list:
        if feature in fl:
            if feature == 'lacbed':
                bdir = os.path.join(get_current_folder(), 'baseline', 'unittest', 'bloch')
            else:
                bdir = os.path.join(get_current_folder(), 'baseline', 'unittest', feature) 

            if bCreate and not os.path.exists(bdir):
                os.makedirs(bdir, exist_ok=True)

            retfn = os.path.join(bdir, fl[feature] + '.pkl')
            bFound = True
            break
    if not bFound:
        print(f'Feature provided is not supported: {feature}')
        raise FileExistsError("Feature provided is not supported")
    
    return retfn

# def featureInSampleList(f):
#     fl = [list(d.keys())[0] for d in sample_feat_list]           
#     return f in fl

def featureInUnittestList(f):
    fl = [list(d.keys())[0] for d in unittest_feat_list]           
    return (f in fl)

def get_test_cases(cdata_ty=TY_BUILTIN, feature = feat_list[0]):
    
    if cdata_ty ==1:
        data_dir = os.path.join(get_builtin_dir(), "cdata")
        data_ext = '.xtl'
    else:
        data_dir = get_cifdata_dir()
        data_ext = '.cif'
 
    test_cases = []
    
    failed_cif_cases_list = ['1010115.cif', '1010195.cif', '1010197.cif', '1010198.cif']
    for f in os.listdir(data_dir):
        if f not in failed_cif_cases_list and f.endswith(data_ext):
            if feature == 'bloch' and cdata_ty !=TY_BUILTIN and int(os.path.splitext(f)[0]) < 1010150:
                continue
            else:
                test_cases.append(os.path.join(data_dir, f))
    
    return test_cases