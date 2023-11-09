#  Open Source __pyEMAPS__ Development Guidelines

1. <a id="contents"></a>[What's pyEMAPS](#overview)
2. <a id="contents"></a>[Build pyEMAPS](#build)
3. <a id="contents"></a>[Installation](#installation)
4. <a id="contents"></a>[Testing](#test)
5. <a id="contents"></a>[Development Process](#process)
5. <a id="contents"></a>[pyEMAPS Contributor License Agreement](#CLA)
5. <a id="contents"></a>[Code of Conduct](#COC)

## What's pyEMAPS [`↩`](#contents) <a id="overview"></a>
__pyEMAPS__ is a python package providing interfaces into electron diffraction simulations and crystallogrphy calculations engines. Its
main components are designed for electron microscope operations and simulations, including microscpe controls and crystal python classes. 
__pyEMAPS__ provides opportunities for users to automate simulations and calculations with common json data output and images of well known 
format suited for further processing.

Check our full [pyemaps documentation](https://emlab-solutions.github.io/pyemaps) for details of __pyEMAPS__ 
python classes designs and their interfaces.

We greatly appreciate your contributions to pyEMAPS and look forward to making it a tool for 
the communty to accelaerate microscopy and crystallography education and research. If you benefit from __pyEMAPS__ in your microscopy 
and crystallography research and education, go to 
[PayPal](https://www.paypal.com/paypalme/pyemaps22) to donate. Your generous donations keep us in the business of providing free software 
to the education and research communities.   

## Build pyEMAPS [`↩`](#content) <a id="build"></a>

Requirements and recommendations:
* __Python__: Version == 3.7
* __Operating Systems__: Windows
* __VSCode__: code editing (recommended)
* __Microsoft Visual Studio 2019 Community__: with build tools

Current __pyEMAPS__ only support Windows and python 3.7. We also recommend you to use vscode to develop your code.
Like many python development, a virtual python environment is recommended to isolate your pyEMAPS development 
environment from your other python development projects. We are also looking for contributors to help us to port __pyEMAPS__
to linux platform.

Below are steps to establish __pyEMAPS__ build environment with python 3.7.9 for example:

* Install python 3.7.9 with Windows PowerShell command line in Administrator mode in c:\python37 directory:
```   
   Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.7.9/python-3.7.9-amd64.exe" -OutFile "python-3.7.9-amd64.exe"
```
* Run the "python-3.7.9-amd64.exe", choose the following in installer GUI:
  
     * Select Customize Installation
     * Check and select pip
     * Install for all users/specific users   
* Create a virtual environment called "pyemaps_build" for the build
     * Create a dev directory:
       ```
       mkdir pyemaps-dev
       ``` 
       (or choose your own directory name)
     * Create pyemaps_build virtual environemnt:
       ```
       c:\python37\python.exe -m venv pyemaps_build
       ```
* Activate pyemaps_build vitual environment:
     ```
    .\pyemaps_build\Scripts\activate
     ```
* Update pip:
  ```
   C:\Python37\python.exe -m pip install pip --upgrade
  ```
* Install other python packages required for building pyemaps:
  ``` 
  pip install setuptool wheel numpy build
  ```
* Install Microsoft Visual Studio 2019 Community with build tools 
   https://visualstudio.microsoft.com/vs/older-downloads/
   by selecting "Desktop development with C++" in the installer.
   (You may need to have a microsoft account to be able to download)
* Build pyEMAPS package, run:
  ```
   python build_pyemaps -t -v 1.0.0
  ```
## Installation [`↩`](#contents) <a id="installation"></a>

* Install the new pyEMAPS package:
  ```
   pip .\dist\pyemaps-1.0.0-cp37-cp37m-win_amd64.whl
  ```
  This will install new pyEMAPS just built in current python virtual environment
  along with all of its dependent packages

## Testing [`↩`](#contents) <a id="test"></a>

  Current pyEMAPS development comes with a set of basic testing suites, including 
   * sanity checks
   * unit tests
   * stress tests.

   To run these test suites, call:
   ```
      .\test\sanity\sanity.bat
   ```
   We are looking for your contributions to make the development tomake __pyEMAPS__ quality and stable 
   tool for the community.

## Development Process [`↩`](#contents) <a id="process"></a>

As any open source development, we strongly recommend the following process to follow for all contributors:

* __Issues creation__. Before making changes for bug fix or feature implementation, create an issue in the pyEMAPS
   github repository be communicating what you intend to change or fix to your fellow contributors.

* __Development Branch__. Create your own branch from 'main' branch for the changes you desire.
  
* __Backwards Compatibilities Tests__. Existing test suites designed for testing most of the features
   are strongly recommended.

* __New Tests Additions__. New test cases for the changes introduced into the package are desired to keep the quality 
   of __pyEMAPS__
  
* __Pull Requests__. Before merging your changes into production branch "main", a pull request is required. The request created
  should be verbose enough to convey the summary of the changes and any issues the changes are to address. 
  
* __Code Review__. Requesting code review from fellow contributors in your pull requests is also required, please always
  include "sharonz2006" in your code reviewer list.
  
* __Documentation__. You are the author of the changes, so please take the pride by documenting them.  
   We use sphinx tool for documentation generation. To install sphinx, run:
   ```
    pip install -U sphinx
   ```
   in your python build virtual environment (pyemaps_build in our example).
 
   Most of the documentations files are in "docs" directory. After making documentation changes to record your changes, compile
   them with sphinx:
   ```
    sphinx-build -b html source .
   ```

## pyEMAPS Contributor License Agreement [`↩`](#contents) <a id="CLA"></a>

Please read and agree to our [Contributor License Agreement](CONTRIBUTING.md) before contributing to this project.

## Code of Conduct [`↩`](#contents) <a id="COC"></a>

pyEMAPS is committed to providing a welcoming and inclusive environment for all contributors. We follow the [Contributor Covenant](https://www.contributor-covenant.org/version/2/0/code_of_conduct/) as our code of conduct. Please make sure to review it before contributing.

**[Read the Contributor Covenant](https://www.contributor-covenant.org/version/2/0/code_of_conduct/)**

Any instances of unacceptable behavior can be reported to support@emlabsoftware.com.


