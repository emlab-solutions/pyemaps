'''
.. This file is part of pyEMAPS
 
.. ----

.. pyEMAPS is free software. You can redistribute it and/or modify 
.. it under the terms of the GNU General Public License as published 
.. by the Free Software Foundation, either version 3 of the License, 
.. or (at your option) any later version..

.. pyEMAPS is distributed in the hope that it will be useful,
.. but WITHOUT ANY WARRANTY; without even the implied warranty of
.. MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
.. GNU General Public License for more details.

.. You should have received a copy of the GNU General Public License
.. along with pyEMAPS.  If not, see `<https://www.gnu.org/licenses/>`_.

.. Contact supprort@emlabsoftware.com for any questions and comments.

.. ----

.. Author:     EMLab Solutions, Inc.
.. Date:       May 07, 2022    

'''

rel_stage = 'Stable'

# What pyemaps -cp copies: (description, folder in the package, folder it copies into).
COPY_SETS = {
    'samples': ('sample scripts', 'samples', 'pyemaps_samples'),
    'notebooks': ('notebooks', 'notebooks', 'pyemaps_notebooks'),
}

# The sample that pyemaps -s runs; it isn't copied.
COPY_SKIP = {'si_pyemaps.py'}


def copy_examples(what):
    '''
    Copy the sample scripts, the notebooks, or both into folders in the current directory,
    after asking to confirm. *what* is 'samples', 'notebooks' or 'all'. Files that already exist
    there are left alone, so copying again doesn't overwrite your changes.
    '''
    import os
    import shutil
    import sys

    names = list(COPY_SETS) if what == 'all' else [what]
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    curr_dir = os.getcwd()

    plan = ' and '.join(f'the {COPY_SETS[n][0]} into {COPY_SETS[n][2]}' for n in names)
    inp = input(f'Copy {plan}, in the current directory? [Y/n] ')
    if inp and not inp.lower().strip()[:1] == 'y':
        print('Nothing copied.')
        sys.exit(1)

    for n in names:
        desc, pkg_sub, dest_sub = COPY_SETS[n]
        source_dir = os.path.join(pkg_dir, pkg_sub)
        if not os.path.isdir(source_dir):
            print(f'This pyEMAPS installation has no {desc}.')
            continue

        dest_dir = os.path.join(curr_dir, dest_sub)
        os.makedirs(dest_dir, exist_ok=True)

        copied, skipped = 0, []
        for file_name in sorted(os.listdir(source_dir)):
            source = os.path.join(source_dir, file_name)
            if not os.path.isfile(source) or file_name in COPY_SKIP:
                continue
            destination = os.path.join(dest_dir, file_name)
            if os.path.exists(destination):
                skipped.append(file_name)
                continue
            shutil.copy(source, destination)
            copied += 1
            print(f'Copied {file_name} to {destination}')

        print(f'Copied {copied} file{"" if copied == 1 else "s"} into {dest_dir}.')
        if len(skipped) == 1:
            print(f'Skipped {skipped[0]}, which already exists there. To get a fresh copy, '
                  'rename or delete it and copy again.')
        elif skipped:
            print(f'Skipped {len(skipped)} files that already exist there: '
                  f'{", ".join(skipped)}. To get fresh copies, rename or delete them and copy '
                  'again.')

        if n == 'samples':
            print(f'Run a sample with: python {os.path.join(dest_sub, "<sample>.py")}')
        else:
            print(f'Open the notebooks with Jupyter (pip install jupyter): '
                  f'jupyter notebook {dest_sub}')


def is_alphanumeric_with_dash(s, slen):
    """
    For paid package with full version of simulation backend module with 4DSTEM features, 
    license token validation done here. More validation in the backend as well.

    """
    import re
    
    pattern = r'^[A-Za-z0-9-]+$'
    return bool(re.match(pattern, s) and len(s) == slen)

def main():
    """
    Liveness test and other information of pemaps package run on command line.

    Usage:
        pyemaps -s (--sample)
        pyemaps -c (--copyright)
        pyemaps -cp (--copy) [samples|notebooks]
        pyemaps -v (--version)
        pyemaps -l (--license) <trial|info|license token>

        To get help on all options, use:
        pyemaps -h (--help) 
    """
    
    try:
        from .samples.si_pyemaps import run_sample
        
        from emaps import PKG_TYPE, TYPE_FREE, TYPE_FULL, TYPE_UIUC
        
    except ImportError as e:
        print(f"Error: importing built-in sample and pyemaps constants from backend: {e}")
        
    import argparse
    import datetime
    from importlib.metadata import version as dist_version

    parser = argparse.ArgumentParser(description="pyEMAPS command line tool.",  
                                     formatter_class=argparse.RawTextHelpFormatter)
    
    parser.add_argument("-c", 
                        "--copyright", 
                        default=False, 
                        action='store_true',
                        help="display pyEMAPS copyrights.", 
                        required=False)
    parser.add_argument("-cp",
                        "--copy",
                        "--copysamples",
                        nargs='?',
                        const='all',
                        default=None,
                        metavar='samples|notebooks',
                        help="copy the sample scripts into pyemaps_samples, the Jupyter\n"
                             "notebooks into pyemaps_notebooks, or, with neither, both.\n"
                             "Files that already exist there aren't overwritten.",
                        required=False)
    
    if PKG_TYPE != TYPE_FREE:
        parser.add_argument("-l", 
                            "--license", 
                            nargs='?', 
                            const='info',   
                            default=None,   
                            metavar='trial|info|<LICENSE_ACTIVATION_TOKEN>',
                            help="""activate license for full package with 4D STEM features. Options are:
- trial: to activate a trial license, this option requires internet connection.
- info: to display current license details, no internet connection is needed.
- <LICENSE_ACTIVATION_TOKEN>: to activate license with license token with or without internet**.
The token is obtained from EMLab Solutions, Inc. by writing to support@emlabsoftware.com.
**No internet is required after license is activated, as all functions including license check are local.""", 
                            required=False
                            )
    parser.add_argument("-s", 
                        "--sample",
                        default=False, 
                        action='store_true',
                        help="run basic pyEMAPS sample code, serving as pyEMAPS liveness test.", 
                        required=False)
    parser.add_argument("-v", 
                        "--version", 
                        default=False, 
                        help="display pyEMAPS version.", 
                        action='store_true',
                        required=False)
   
    try:
        args = parser.parse_args()
    except argparse.ArgumentTypeError as e:
        parser.print_help()
        exit(1)

    if args.copy not in (None, 'all', *COPY_SETS):
        parser.error(f"argument -cp/--copy: expected 'samples' or 'notebooks', not '{args.copy}'")

    ver = dist_version("pyemaps") + str(f" {rel_stage}").lower()
    
    copyrit = ['PyEMAPS - Transmission Electron Diffraction Simulations In Python']
    copy1 = '© 2021-' + datetime.date.today().strftime('%Y') + ' EMLab Solutions, Inc. All rights reserved.'
    
    vers = 'Version ' + ver
    if PKG_TYPE == TYPE_UIUC:
        vers = "Version " + ver +" for use exclusively at University of Illinois at Urbana Champaign." 
    
    if PKG_TYPE == TYPE_FULL:
        vers = "Version " + ver +" with 4DSTEM." 

    copyrit.append(copy1)
    scopyrit = '\n'.join(copyrit)

    if args.version:
        print(f'pyEMAPS {vers.lower()}')
        exit(0)
    elif args.copyright: 
        print(scopyrit)
        exit(0)  
    else:
        copyrit.append(vers)
        copyrit.append('--------------------------------')
        print('\n'.join(copyrit)) 
          
        if args.copy:
            copy_examples(args.copy)
            exit(0)
        
        if args.sample:
            run_sample()
            exit(0)
        
        if args.license is not None and PKG_TYPE != TYPE_FREE:
            
            from emaps import stem4d
            
            lic_option = args.license
            if lic_option is not None:
                lic_option_new = lic_option.lower()
                if lic_option_new == 'info':
                    ret = stem4d.getLicenseInfo()
                elif lic_option_new == 'trial': 
                    ret = stem4d.activate_license_once()
                
                elif is_alphanumeric_with_dash(lic_option, stem4d.LICENSE_TOKEN_LENGTH): 
                    ret = stem4d.activate_license_bytoken_once(lic_option)
                else:
                    print(f'Error: license activation token: {lic_option} is invalid!')
                    exit(1)
            else:
                print(f'Error: license activation token: {lic_option} is invalid!')
                exit(1)
            
            if ret != 0:
                exit(1)

        exit(0)

if __name__ == '__main__':
    main()  