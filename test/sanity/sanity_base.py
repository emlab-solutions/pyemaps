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
                    ]

def get_cifdata_dir():

    current_path = Path(os.path.abspath(__file__))

    test_path = current_path.parent.parent.absolute()

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

def get_baseline_filename(feature=feat_list[0], ttype=1):
    bdir = os.path.join(get_current_folder(), 'baseline', feature)
    return os.path.join(bdir, 'builtin.pkl' if ttype == 1 else 'cif.pkl')

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

            retfn = os.path.join(bdir, fl[feature] + '.pkl')
            bFound = True
            break
    if not bFound:
        print(f'Feature provided is not supported: {feature}')
        raise FileExistsError("Feature provided is not supported")
    
    return retfn

def featureInSampleList(f):
    fl = [list(d.keys())[0] for d in sample_feat_list]           
    return (f in fl)