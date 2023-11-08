pyEMAPS is a python interface into electron diffraction simulations and crystallogrphy calculations. Its
main components are designed for electron microscope operations and simulations, including microscpe controls
and crystal python classes. 

pyEMAPS provides opportunities for user to automate simulations and calculations with common json data 
output and images of well known format suited for further processing.

Check our full [pyemaps documentation](https://emlab-solutions.github.io/pyemaps) for details of pyEMAPS 
python classes designs and their interfaces.

Build pyeEMAPS:

Current pyEMAPS only support Windows and python 3.7. We also recommend you to use vscode to develop your code.
Like many python development, virtual python environment is recommended. Below is a list of steps to establish 
pyEMAPS build environment with python 3.7.9:

1) Install python 3.7.9 with PowerPC admin command line in c:\python37 directory:
   Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.7.9/python-3.7.9-amd64.exe" -OutFile "python-3.7.9-amd64.exe"
   Run the "python-3.7.9-amd64.exe", choose the following in install GUI:
     a. Select Customize Installation
     b. Check and select pip
     c. Install for all users/specific users
     
2) Create a virtual environment for the build
    a. Create a dev directory: mkdir pyemaps-dev (or choose your own directory name)
    b. Create pyemaps_build virtual environemnt:
       c:\python37\python.exe -m venv pyemaps_build
3) Activate pyemaps_build vitual environment:
    .\pyemaps_build\Scripts\activate

4) Update pip:
   C:\Python37\python.exe -m pip install pip --upgrade

5) Install other python packages required for building pyemaps:
   setuptool wheel numpy build

6) Install Microsoft Visual Studio 2019 Community with Build
   https://visualstudio.microsoft.com/vs/older-downloads/
   by selecting "Desktop development with C++" in the installer.
   (You may need to have a microsoft account to be able to download)

8) Build pyEMAPS package:
   python build_pyemaps -t -v 1.0.0

9) Install the new pyEMAPS package:
   pip .\dist\pyemaps-1.0.0-cp37-cp37m-win_amd64.whl
   This will install new pyEMAPS just built in current python virtual environment
   along with all of its dependent packages

10) Testing the new pyEMAPS:
    Current pyEMAPS development comes with a set of basic testing suites, including
    sanity checks, unit tests and stress tests. To run these test suites, call:
      .\test\sanity\sanity.bat
    We are looking for your contribution of tests to make the development of quality and
    stability for the community.

11) Process to follow to contribute to pyEMAPS development as a contributor:
    a. Before making changes for bug fix or feature implementation, write an issue in the pyEMAPS
       github repository.
    b. Create your branch from 'main' branch for the changes you desire.
    c. Testing your changes based on the issues you wrote in previous steps with existing test suites
       and add tests cases to existing test suites if possible.
    d. When ready, make a "pull request" in pyEMAPS repository
    e. Request code review from other contributors, please always include "sharonz2006" in your code reviewer.
    f. Document the changes in sphinx tool for any interface changes. To install sphinx, run:
       pip install -U sphinx
       in your virtual environment (pyemaps_build).
       To compile the documentation changes, run:
          sphinx-build -b html source .

We greatly appreciate your contributions to pyEMAPS and look forward to making it a tool for 
the communty to accelaerate microscopy and crystallography education and research.
    

   

