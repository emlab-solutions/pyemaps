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
pyemaps_samples_dir = 'pyemaps_samples'

def copy_samples():
    '''
    Copies sample code from package directory to current diretory 
    for easy access.
    '''
    import os, sys
    import shutil

    curr_dir = os.getcwd()
    
    q = str(f"Copy pyemaps samples into {pyemaps_samples_dir} in current directory?\n ")
    
    inp = input(q +"[Y/n] ")

    if inp and not inp.lower().strip()[:1] == "y":
        print("No sample code is copied!")
        sys.exit(1)

    curr_samples_dir = os.path.join(curr_dir, pyemaps_samples_dir)

    if not os.path.exists(curr_samples_dir):
        os.makedirs(curr_samples_dir)
    
    pyemaps_pkgdir = os.path.dirname(os.path.abspath(__file__))
    pkg_samples_dir = os.path.join(pyemaps_pkgdir, "samples")

    for file_name in os.listdir(pkg_samples_dir):
        
        if file_name == 'si_pyemaps.py':
            continue
        source = os.path.join(pkg_samples_dir, file_name)
        destination = os.path.join(curr_samples_dir, file_name)
        
        if os.path.isfile(source):
            shutil.copy(source, destination)
            print(f'Copied sample code: {file_name} in pyemaps package to {destination}')

    print(f'Run sample code by typing: \"python pyemaps_samples\<sample>\"')

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
        pyemaps -cp (--copysamples)
        pyemaps -v (--version)
        pyemaps -l (--license) <trial|info|license token>

        To get help on all options, use:
        pyemaps -h (--help) 
    """
    
    try:
        from .samples.si_pyemaps import run_si_sample
        
        from emaps import PKG_TYPE, TYPE_FREE, TYPE_FULL, TYPE_UIUC
        
    except ImportError as e:
        print(f"Error: importing built-in sample and pyemaps constants from backend: {e}")
        
    import argparse
    import datetime
    import pkg_resources

    parser = argparse.ArgumentParser(description="pyEMAPS command line tool.",  
                                     formatter_class=argparse.RawTextHelpFormatter)
    
    parser.add_argument("-c", 
                        "--copyright", 
                        default=False, 
                        action='store_true',
                        help="display pyEMAPS copyrights.", 
                        required=False)
    parser.add_argument("-cp", 
                        "--copysamples", 
                        default=False, 
                        action='store_true',
                        help="copy sample code into current working directory.", 
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

    ver = pkg_resources.require("pyemaps")[0].version + str(f" {rel_stage}").lower()
    
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
          
        if args.copysamples:
            copy_samples()
            exit(0)
        
        if args.sample:
            run_si_sample()
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