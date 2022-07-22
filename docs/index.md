# Introducing __pyemaps__
1. <a id="contents"></a>[Overview](#overview)
2. <a id="contents"></a>[Requirements](#requirements)
3. <a id="contents"></a>[Installation](#installation)
4. <a id="contents"></a>[Basic Usage](#basic-usage)
5. <a id="contents"></a>[Getting Started](#getting-started)
6. <a id="contents"></a>[Visualisation](#visualisation)
7. <a id="contents"></a>[Licence](#licence)
8. <a id="contents"></a>[Frequently Asked Questions](#faq)
9. <a id="contents"></a>[Release Notes](#release-notes)

## Overview [`↩`](#contents) <a id="overview"></a>
__pyemaps__ package is a collection of python modules and libraries designed for transmission electron diffraction simulations and related crystallographic calculations. Main features include:

>**Kinematic and Dynamic Diffraction Simulations** 

>**Electron Powder Diffraction Simulations**

>**Crystallographic Transformations and Calculations**

>**Crystal Structure Factors Calculations**
> * X-Ray Structure Factors
> * Electron Structure Factor in V (volts)
> * Electron Structure Factor in 1/&#8491;^2
> * Electron Absorption Structure Factor in 1/&#8491;^2 

__pyemaps__ comes with a set of helper classes with the intent of making accesses to above feature easy for users:

* **Crystal** : crystal data module, classes and methods for loading crystal data from various data sources such _pyemaps_' own builtin data formatted files and (IUCr) Crystallographic Information Framework (CIF); for preparing microscope and sample control parameters for the above simulations.

* **EMC** : electron microscope control module. Its class __EMC__ makes it easy to handle simulation control parameters.  

* **DP** :  kinematic diffraction python class. It encapsulates and models diffraction pattern generated from __Crystal__ class instance.   

* **BlochImgs** : dynamic diffraction images list class. This class is design for handling multiple slices of bloch images with their associated controls. 

* **Display**: This python helper class provides a builtin visualisation of kinematic diffraction patterns with Kikuchi and HOLZ lines, and diffracted beams or disks and their Miller indices. Its methods also include rendering of dynamic diffraction (Bloch) images. Users can easily replace or extend these methods into their own application.   

* **Errors**: Error handling for __pyemaps__, capturing errors and making actionable and trackable error messages.

See sample code and latest [release notes](https://emlab-solutions.github.io/pyemaps/#release-notes) for details.

__pyemaps__ is based on the proprietary Fortran applications released as backend of [cloudEMAPS2.0](https://emaps.emlabsolutions.com). 


Check [EMlab Solution, Inc.](https://www.emlabsolutions.com) for updates and releases. We welcome comments and suggestions from our user community. For reporting any issues and requesting pyemaps improvements, or sharing scripts using __pyemaps__, please go to [our support page](https://www.emlabsolutions.com/contact/). 

If you benefit from __pyemaps__ in your microscopy and crystallography research and education and would like to donate, go to [PayPal](https://www.paypal.com/paypalme/pyemaps22). Your generous donations are greatly appreciated and will keep us in the business of providing free software to the communities.   

## Requirements [`↩`](#contents) <a id="requirements"></a>

* __Python__: Version >= 3.6
* __numpy__: Version >= 1.21.2
* __matplotlib__: Version >= 3.2.1
* __PyCifRW__ Version == 4.4.3
* __Operating Systems__: Windows, 64-bit, >= 8GB RAM

Linux support planned in future releases, stay tuned.

## Installation [`↩`](#contents) <a id="installation"></a>

```
(.venv) $ pip install pyemaps
 ```
 
where .venv is the python virtual environment

*PYEMAPS_CRYSTALS* environment variable is optional. But setting it to a directory where all custom 
crystal data files are located provides central location for organizing your own crystal data. __pyemaps__ also searches this directory for your crystal data.

```
    PYEMAPS_CRYSTALS=<local directory>
```

See [FAQ](https://emlab-solutions.github.io/pyemaps/#faq) for solutions to possible installation issues.

## Basic Usage [`↩`](#contents) <a id="basic-usage"></a>

```
from pyemaps import Crystal
from pyemaps import DP
```

## Getting Started [`↩`](#contents) <a id="getting-started"></a>

Run the following on command line, after above successful installation:

```
python sample.py
```

where sample.py is as follows:

```python
    from pyemaps import Crystal as cr
    from pyemaps import showDif, showBloch
    from pyemaps import DPList
    # create a crystal class instance and load it with builtin silicon data
    c_name = 'Silicon'
    si = cr.from_builtin(c_name)

    # generate diffraction on the crystal instance with all default controls
    # parameters, default controls returned as the first output ignored
    
    dpl = DPList(c_name)

    emc, si_dp = si.generateDP()
    dpl.add(emc, si_dp)    

    #plot and show the diffraction pattern using pyemaps built-in plot function
    showDif(dpl)

    #hide Kikuchi lines
    showDif(dpl, kshow=False) 

    #hide both Kukuchi line and Miller Indices
    showDif(dpl, kshow=False, ishow=False) 

    #hide Miller Indices
    showDif(dpl, ishow=False)

    #Generate dynamic diffraction patterns using pyemaps' bloch module 
    bloch_imgs_list = []
    emc, img = si.generateBloch() #with all default parameters
    
    #create a dynamic diffraction pattern list /w assiated controls
    bloch_imgs_list.append((emc, img)) 
    
    showBloch(bloch_imgs_list, name = c_name) #grey color map
    showBloch(bloch_imgs_list, bColor=True) #with predefined color map
```

The alternative to run the above without creating sample.py:
```
python -m pyemaps --sample (-s)
```

The diffraction plot is generated with silicon crystal data built in the package:

```
crystal Silicon: dw = iso
cell 5.4307 5.4307 5.4307 90 90 90
atom si 0.125 0.125 0.125 0.4668 1.00
spg 227 2
```

and default electron microscope and sample control parameters:

```
zone axis: (0,0,1)
microscope mode: normal
microscope camera length : 1000 mm
microscope voltage: 200 V
sample tilt: (0.0,0.0)
sample offset: (0.0,0.0)
spot size: 0.05 Å
```

![](https://github.com/emlab-solutions/imagepypy/raw/main/kdiff_si.png?raw=True "Kinematic diffraction for silicon")

The following is the dynamic diffraction pattern for _Silicon_ builtin crystal with sampling set at 20. The left is the image in gray scale and the righ in a predefined color map


![](https://github.com/emlab-solutions/imagepypy/raw/main/si_bloch.png?raw=True "Dynamic diffraction for silicon")

To see all crystal names with builtin data, call:
```python
from pyemaps import Crystal as cr
cr.list_all_builtin_crystals()
```

To use a crystal data not in built-in database in above format (as xtl format), replace the code in _sample.py_:
```python
from pyemaps import Crystal as cr
si = cr.from_builtin('Silicon')
```
with:
```python
from pyemaps import Crystal as cr
si = cr.from_xtl(fn)
```
CIF format has recently been added to crystal data sources where __pyemaps__ can import:
```python
from pyemaps import Crystal as cr
si = cr.from_cif(fn)
```
where _fn_ is a crystal data file name. See release notes for details how pyemaps imports .cif data

Note: __pyemaps__ searches for _fn_ if the full path is provided. Otherwise, it will look up the file in current working directory or in the directory set by *PYEMAPS_CRYSTALS* environment variable. In latter cases, _fn_ is the file name without path.

Checking __pyemaps__ version and displaying copyright information:
```
python -m pyemaps -c (--copyright)
python -m pyemaps -v (--version)
```

## Visualisation [`↩`](#contents) <a id="visualisation"></a>
Accessing diffraction patterns data is easy for pyemaps users to visualize the diffraction patterns in any programs other than pyemaps' builtin plot with python's _matplotlib_ library:

* Raw kinematic diffraction data (DP) in python dictionary:
```python
    dp.__dict__ #dp is a pyemaps DP class object generated from calling generateDP by a crystal object 
``` 
* Individual components (such as Kikuchi lines, Diffracted beams or HOLZ lines) as python lists:
```python
    dp.klines #Kikuchi lines list
    dp.nklines #number of Kikuchi lines, same as len(dp.klines)
    dp.disks #diffracted beams list
    dp.ndisks #number of diffracted beams, same as len(dp.disks)
    dp.hlines #HOLZ lines list
    dp.nklines #number of HOLZ lines, same as len(dp.hlines)
    dp.shift #deflection shifts of all of the above
    ...
```
* Raw dynamic diffraction data (Bloch) is an _numpy_ array of floats with dimension of NxN where N is the detector size input for _generateBloch(...)_ function. Each point in the array represent the image intensity. Pyemaps uses Python _matplotlib_ in its builtin display function _showBloch()_. See its usage in sample code _si_bloch.py_ 

<!-- 
In addition to the above and and pyemaps' built-in _matplotlib_ rendering of diffraction pattern, DigitalMicrography (referred as DM here) is another option with its line and circle annotations objects. Simply open and execute the python script in DM __dm_diff.py__ in _samples_ directory for example.


![](https://github.com/emlab-solutions/imagepypy/blob/main/kdiff_si_dm.png?raw=True "Kinematic diffraction for silicon python script dm_diff.py") -->

Sample scripts designed for you to explore pyemaps features are available in pyemaps' samples directory:
* __si_dif.py__: spot diffraction patterns generated with silicon crystal data, plotted with _matplotlib pyplot_ module. The code also shows how a list of diffraction patterns are generated and changed with one of electron microscope and sample controls - tilt in x direction.

* __si_bloch.py__: demonstrates dynamic diffraction generation with similar control changes.
<!-- 
* __pyplot_dm_si_diff.py__: DM python script which generate and plot diffraction pattern for silicon crystal using _matplotlib pyplot_ module. The rendering of diffracttion patterns are in black for normal mode and CBED in color. -->

* __si_csf.py__: _structure factors_ generation and output by __CSF__ pyemaps module. 

* __powder.py__: _electron powder diffraction_ generation and intensity plot by ____ pyemaps module. 

More samples code will be added as more features and releases are available. 

To copy all of the samples from __pyemaps__ package to the current working directory, following pyemaps installation. Run:
```
python -m pyemaps -cp (--copysamples)
```
all of the samples will be copied from __pyemaps__ install directory to a folder named _pyemaps_samples_ in your current working directory.

## Licence [`↩`](#contents) <a id="licence"></a>

 __pyemaps__ is distributed for electron diffraction and microscopy research, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public Licence for more details.
* __pyemaps__ is for non-commercial use.
* __pyemaps__ is free software under the terms of the GNU General Public Licence as published by the Free Software Foundation, either version 3 of the Licence, or (at your option) any later version. You should have received a copy of the GNU General Public Licence along with __pyemaps__.  If not, see <https://www.gnu.org/licenses/>.

Additional copyright notices and license terms applicable to portions of pyemaps are set forth in the COPYING file.

Contact supprort@emlabsoftware.com for any questions regarding the licence terms.

## Release Notes [`↩`](#contents) <a id="release-notes"></a>

### __0.3.3 Alpha__ May 4th, 2022 

#### NEW

* Kinematical diffraction simulations.
* Diffraction patterns handling and visualizations helper classes
* Sample code demontsrating __pyeamps__ integration in other tools

### __0.3.4 Alpha__ May 7th, 2022  

#### NEW

* An environment variable _PYEMAPS_CRSYTALS_ added enabling custom crystal data file location and lookup

#### IMPROVED

* Requirements section added for __payemaps__ python and OS specifications.

### __0.3.5 Alpha__ May 11th, 2022  

#### NEW

* An electron microscope controls module __EMControls__ added to __pyemaps__ for better handling of controls parameters in __pyemaps__. Its usage:

```
    from pyemaps import EMC
```
this class mirror the following dictionary of controls parameters:
```
    DEF_CONTROLS = dict(zone = (0,0,1),
                    tilt = (0.0,0.0),
                    defl = (0.0,0.0),
                    cl = 1000,
                    vt = 200
                    )
```
#### IMPROVED

* Diffraction pattern generation function parameter is simplified using EMC class:
```
gen_diffPattern(...)
```
to:
```
generateDP(mode = None, dsize = None, em_controls = None)
```
where em_controls is an EMC instance. For backward compatibility, the former function is still in use.

See new sample code in the package for details how to use the new function. 

### __0.3.6 Alpha__ May 24th, 2022  

#### NEW

* __Crystal Structure Factors (CSF)__ module added to __pyemaps__ package for four types crystal structure factors calculations listed in [Overview](#overview).

The basic usage of __CSF__ to generate and output CSF data is embedded in __Crystal__ class method:

```
    generateCSF(kv = 100,               <= High Voltage
                smax = 0.5,             <= Limit for Scattering Angle θ / Wavelength 
                sftype = 1,             <= Structure Factor Types (1-4 as listed in Overview section)
                aptype = 0)             <= With Absorption or Not
    printCSF(SFS)                       <= SFS: Output Structure Factor Data from generateCSF() call           
```
An excerpt of output from the sample code _si_csf.py_ run for electron absorption structure factors:

```
-----Electron Absorption Structure Factor in 1/Å^2-----
    crystal            : Silicon
    h k l              : Miller Index
    s-w                : Sin(ϴ)/Wavelength <= 1.0
    d-s                : D-Spacing
    high voltage       : 100 V

    SF output format   : (amplitude, phase)

h   k    l        s-w             d-s          amplitude         phase

1   1   1    0.1594684670    3.1354161069    0.0005996839    0.000000
0   0   2    0.1841383247    2.7153500000    1.655526e-35    180.000000
0   2   2    0.2604109162    1.9200423983    0.0007835663    0.000000
1   1   3    0.3053588663    1.6374176590    0.0005298455    0.000000
2   2   2    0.3189369340    1.5677080534    9.850372e-19    0.000000
0   0   4    0.3682766494    1.3576750000    0.0007046324    0.000000
...
```
See sample code _si_csf.py_ for detailed guide on using these methods.


### __0.3.7 Alpha__ May 31st, 2022  

#### NEW

* __Electron Powder Diffraction__ (__POWDER__) module added to __pyemaps__ package. Powder diffraction data generation methods are embedded in __Crystal__ class as:

```
    generatePowder(kv = 100,                <= High Voltage
                  t2max = 0.05,             <= Scattering Angle 2θ Limit
                  smax = 1.0,               <= Scattering Angle θ/ Wavelength Limit
                  eta = 1.0,                <= Mixing Coefficient Between Gaussian And Lorentzian
                  gamma = 0.001...)         <= Gamma Is the Fwhm
    plotPowder(PW)                          <= PW: Output powder Data from generatePowder()         
```
The first methods takes user input of high voltage and scattering angle 2ϴ, along with many others to generate the electron powder diffraction in intensity array. __plotPowder__ plots single powder diffraction, while _powder.py_ sample code included in the package also demonstates the electron pwoder diffarction of two crystals: Silicon and Diamond. The latter is with absorption. See sample code _powder.py__ for details on using these mothods.


![](https://github.com/emlab-solutions/imagepypy/blob/main/powder.png?raw=True "Electron powder diffraction for silicon python script powder.py")

### __0.3.8 Alpha__ June 15th, 2022  

#### IMPROVED

* Bug fixes on built-in scattering and space group data.


### __0.3.9 Alpha__ June 28th, 2022  

#### NEW

* __CIF format crystal import__: (IUCr) Crystallographic Information Framework (CIF) files are now being imported into pyemaps crystal class. The basic usage:
```python
    from pyemaps import Crystal
    Crystal.from_cif(fn)
```

The function tries to extract crystal information for cell parameters, unit cells from defined field keys and does its best to match space group data from information provided with what is in pyemaps. We welcome your contributions to the parsing and compiling of CIF in __pyemaps__ in order to improve this feature. More document on this feature along with others are forthcoming.

* __Crystallographic Transformations and Calculations__: 
1) Real to reciprocal space transformation and vice versa; 
2) Angles between two vectors in real and reciprical spaces; 
3) Vector length in real and reciprocal spaces;
4) Wavelength;

```python
    from pyemaps import Crystal as cr
    si = cr.from_builtin('Silicon')
    
    vd = si.d2r()
    print(f'\nDefault real space to reciprocal space transform: \n{vd}')
    vd = si.r2d()
    print(f'\nDefault reciprocal space to real space transform: \n{vd}')

    # real to reciprocal transformation
    v = (1.0, 1.0, 2.0)
    v_recip = si.d2r(v) 
    print(f'\nReal space to reciprocal space transform for {v}:\n{v_recip}')
  
    
    #reciprocal to real transformation
    v_ = si.r2d(v_recip) # v_ ~= v
    print(f'\nReciprocal space to real space transform for {v_recip}:\n{v_}')

    #angle in real space
    v1 = (1.0, 1.0, 2.0)
    v2 = (1.0, 1.0, 1.0)
    real_a = si.angle(v1, v2)
    print(f'\nAngle in real space by vectors {v1} and {v2}: \n{real_a} \u00B0')

    #angle in reciprocal space
    recip_a = si.angle(v1, v2, type = 1)
    print(f'\nAngle in reciprocal space by vectors {v1} and {v2}: \n{recip_a} \u00B0')

    #vector length in real space
    r_vlen = si.vlen(v)
    print(f'\nLength in real space for vector {v}:\n{r_vlen} in \u212B')

    #vector length in reciprocal space
    recip_vlen = si.vlen(v, type = 1)
    print(f'\nLength in reciprocal space for vector {v}:\n{recip_vlen} in 1/\u212B')

    #wave length with high voltage of 200 V
    print(f'\nWave length with high voltage of 200 V:\n{si.wavelength(200)} \u212B')

```

#### IMPROVEMENTS

* __Better error handling__: Many exceptions classes are now added to better handle the failures in pyemaps operations. For example, _CIFError_ for catching CIF import failures and errors. _CrytsalClassError_ can be used to catch most of errors during importing cif files 
* __Raw kinemtic diffraction output__: Modifications in diffraction pattern class __DP__ provides easy access to its data. 

Examples of the above improvements shown as follows:

```python
    from pyemaps import Crystal as cr
    from pyemaps import CrystalClassError, DPError
    try:
        cf = cr.from_cif(cif_fn)
        _, cf_dp = cf.generateDP()
    except (CrystalClassError, DPError) as v:   #<---- Notice the new error handling
        print(f'Loading {cif_fn} failed with message: {v}')
    except:
        print('Other unknown failures, exiting...')
        exit(1)
        
    cf_dp.plot()
    # print the diffraction pattern using the builtin format
    print(f'Diffraction Pattern:\n{cf_dp}\n\n')

    # get the raw diffraction pattern in python dictionary 
    # in case you want to import DP into your own program
    dp_dict = cf_dp.__dict__
    print(f'Raw diffraction pattern in python dictionary:\n{dp_dict}\n\n')
    
    # or the raw data of each components of kinematic diffraction pattern 
    # into your program and/or print them out
    print(f'# of Kikuchi lines: {cf_dp.nklines}\nKikuchi lines list:\n{cf_dp.klines}\n\n')
    print(f'# of diffracted beams (a.k.a Disks): {cf_dp.ndisks}\ndiffracted beams list:\n{cf_dp.disks}\n\n')
    print(f'# of HOLZ lines: {cf_dp.nhlines}\nHOLZ lines list:\n{cf_dp.hlines}')
```
See _errors.py_ for all exception classes.
* __Regression fixed__: _all_builtin_crystals()_ added back to __pyemaps__

### __0.4.0 Alpha__ July 4th, 2022  

#### IMPROVEMENTS

* __Selective Plotting of Diffraction Patterns__: DP plotting function now has two selective parameters: _kshow_ and _ishow_ both of value _True_ or _False_ and  defaults of _True_. _kshow_ is for whether the plot shows __Kikuchi__ lines, while _ishow_ for __Miller Index__ of diffracted beams:
```python  
    from pyemaps import Crystal as cr
    si = cr.from_builtin('Silicon')
    _, si_dp = si.generateDP()
    si_dp.plot() # show all components of DP object: Kikuchi lines, diffracted beams etc.
    si_dp.plot(kshow=False) #hide Kikuchi lines only
    si_dp.plot(kshow=False, ishow=False) #hide both Kikuchi lines and Miller Indices
    si_dp.plot(ishow=False) #hide Miller indices only
```
See sample code _si_diff.py_ for more details.

* __EMC class creation enhancement__: EMC is now created by each control key(s) - tilt, zone, defl, vt and cl (sample tilting, zone, deflection, high voltage and camera lenght respectively) and their values for more efficient construction, instead of by a python dictionary in previous versions. If any one of the parameters is missing, default values assumed:
```python
    from pyemaps import EMC
    emc = EMC(tilt=(0.5,0.0)) 
    # EMC object created with given tilt value and the rest assumed 
    # defaults: zone=(0,0,1); defl=(0.0, 0.0); vt=200;cl=1000 
    # (tilt=(0.0,0.0) if not specified)
```
If a dictionary is desired, from_dict() function is an alternative for such construction:
```python
    from pyemaps import EMC
    emc = EMC.from_dict(emc_dict) 
```

* __Structure Factor Plotting__: The built-in display function of structure factors by a crystal object is now simplified:
```python
    from pyemaps import Crystal as cr
    si = cr.from_builtin('Silicon')
    sfs = si.generateCSF(kv, smax, sftype, aptype)  
    #sftype is x-ray and others aptype=1 indicating SF in amplitue and phase
    si.printCSF(sfs) 
    #other parameters in previous versions no longer needed and are written into sfs header
    ...
``` 
See _si_csf.py_ sample code for more details.

### __0.4.1 Alpha__ July 22th, 2022  

#### NEW

* __Dynamic Diffraction Generation__: __bloch__ module is now added in __pyemaps__ which generate dynamic diffraction patterns. The sample code in the above basic usage demostrates the usage of the new addition to pyemaps' Crystal object in _generateBloch_(...). In addition to pyemaps EMC microscope control input, the method also takes many other control parameter as listed below with their default values:
```python
    aperture = 1.0,                 #  Camera aperture
    omega = 10,                     #  Camera parameter                            
    sampling = 8,                   #  Number of sampling points
    pix_size = 25,                  #  Detector pixel size in microns
    thickness = 200,                #  Sample thickness
    det_size = 512,                 #  Detector size (it's also resulting bloch image array dimension)
    disk_size = 0.16,               #  Diffracted Beams Size
    em_controls = EMC(cl=200)       #  Electron Microscope controls
```
Additional helper classes and method are also added to assist multiple bloch calcaluation and image handling. See _si_bloch.py_ for more details of the usage.

* __BImgList__: similar to DPList class, _BImgList_ is designed to hold and handle multiple bloch images and their associated controls.

* __generateBlochImgs__: This is Crystal method that generate a BImgList objects for input of sample thickness range and step tuple: 
    sample_thickness=(thickness_start, thickness_start, thickness_step)
where thichness_step must be positive number. The usage of this method can be very slow due to the fact that it causes pyemaps to calculate multiple slices of bloch images. The advantage is that it saves computation time when such calculation is needed compared to such computation for each sample thickness with _generateBloch_ call.

* __Limitations__: This free version of Bloch image generation has a limitations on crystals and the number of sampling points due to extensive resource requirements for matrix computation during bloch image generations. These limit generally requires less complexity on input crystals and sampling point of 30 or less. Contact support@emlabsoftware.com for a quote for purchasing a full and accelerated version of pyemaps with no limits.   

#### IMPROVEMENTS

* __Plotting Functions for DP and Bloch Images Isolated__: The display of the diffraction patterns are now moved outside of __pyemaps__ Crystal class to a display module, for better code maintenance, modularity. For kinematic diffraction patterns, a couple of selective parameters are also added to the plotting functions for better control on the pattern displays and for decluttering the view. 

```python
    showDif(dpl)   # dpl is a list of DP and their associated control parameters. 

    #hide Kikuchi lines
    showDif(dpl, kshow=False) 

    #hide both Kukuchi line and Miller Indices
    showDif(dpl, kshow=False, ishow=False) 

    #hide Miller Indices
    showDif(dpl, ishow=False)

    #save images as <crystal.name>.PNG in current directory
    showDif(dpl, bSave=True) # bSave default is False
    showBloch(dpl, bSave=True)
```
Detailed plotting function implementations are lised in _display.py_.

*__generateDif(...) Method Added__: This method in _Crystal_ class generates a list of DPs and their associated electron microscopy controls, or _diffraction_ object. It is in contrast to the existing generateDP(...) method that generate a single diffarction pattern (DP).

