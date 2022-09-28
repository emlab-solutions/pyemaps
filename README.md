# Introducing __pyemaps__
1. <a id="contents"></a>[Overview](#overview)
2. <a id="contents"></a>[Requirements](#requirements)
3. <a id="contents"></a>[Installation](#installation)
4. <a id="contents"></a>[Basic Usage](#basic-usage)
5. <a id="contents"></a>[Getting Started](#getting-started)
6. <a id="contents"></a>[Visualisation](#visualisation)
7. <a id="contents"></a>[Licence](#licence)

## Overview [`↩`](#contents) <a id="overview"></a>
__pyemaps__ package is a collection of python modules and libraries designed for transmission electron diffraction simulations and related crystallographic calculations. Main features include:

>**Kinematic and Dynamic Diffraction Simulations** 

>**Electron Powder Diffraction Simulations**

>**Crystallographic Transformations and Calculations**

>_NEW!_ **Stereodiagram**

>_NEW!_ **Crystal Constructor**

>**Crystal Structure Factors Calculations**
> * X-Ray Structure Factors
> * Electron Structure Factor in V (volts)
> * Electron Structure Factor in 1/&#8491;^2
> * Electron Absorption Structure Factor in 1/&#8491;^2 

__pyemaps__ comes with a set of helper classes with the intent of making accesses to above feature easy for users:

* **Crystal** : crystal data module, classes and methods for loading crystal data from various data sources such _pyemaps_' own builtin data formatted files and (IUCr) Crystallographic Information Framework (CIF); for preparing microscope and sample control parameters for the above simulations.

* **EMC** : electron microscope control module. Its class __EMC__ makes it easy to handle simulation control parameters.  

* **DP** :  kinematic diffraction python class. It encapsulates and models diffraction pattern generated from __Crystal__ class instance.   

* **BlochImgs** : dynamic diffraction images list class. This class is designed for handling multiple slices of bloch images with their associated controls. 

* **Display**: This python helper class provides a builtin visualisation of kinematic diffraction patterns with Kikuchi and HOLZ lines, and diffracted beams or disks and their Miller indices. Its methods also include rendering of dynamic diffraction (Bloch) images. Users can easily replace or extend these methods into their own application.   

* **Errors**: Error handling for __pyemaps__, capturing errors and making actionable and trackable error messages.

__pyemaps__ is based on the proprietary Fortran applications released as backend of [cloudEMAPS2.0](https://emaps.emlabsolutions.com). 

Check [pyemaps release notes](https://emlab-solutions.github.io/pyemaps/#release-notes) for updates and releases. We welcome comments and suggestions from our user community. For reporting any issues and requesting pyemaps improvements, or sharing scripts using __pyemaps__, please go to [our support page](https://www.emlabsolutions.com/contact/). 

If you benefit from __pyemaps__ in your microscopy and crystallography research and education and would like to donate, go to [PayPal](https://www.paypal.com/paypalme/pyemaps22). Your generous donations are greatly appreciated and will keep us in the business of providing free software to the communities.   

## Requirements [`↩`](#contents) <a id="requirements"></a>

* __Operating Systems__: Windows, 64-bit, >= 8GB RAM

* __Python__: Version == 3.7 (other python version support upcoming)
* __numpy__: Version >= 1.21.2
* __matplotlib__: Version >= 3.2.1
* __PyCifRW__ Version == 4.4.3

Linux support planned in future releases, stay tuned.

## Installation [`↩`](#contents) <a id="installation"></a>

```
(.venv) $ pip install pyemaps
 ```
 
where .venv is the python virtual environment

*PYEMAPS_DATA* environment variable is set to a directory where all custom crystal data and output files are located provides central location for organizing your own crystal data, as well as your results from pyemaps runs. __pyemaps__ also searches this directory for your crystal data. If these environment variable is set, all output from __pyemaps__ will be placed.

```
    PYEMAPS_DATA=<local directory>  # pyemaps data home, must have right permisions for pyemaps
    PYEMAPS_DATA/crystals           # hosts all custom crystal data files (.xtl, .cif)
    PYEMAPS_DATA/bloch              # location for all bloch images output files
    PYEMAPS_DATA/mxtal              # place for all crystal constructor output files such as *.xyz

```
Note: the legacy environment variable PYEMAPS_CRYSTALS is still supported if it is set.

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
    from pyemaps import BImgList
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
    bloch_imgs_list = BImgList(c_name)
    emc, img = si.generateBloch(sampling = 20) #with all default parameters
    
    #create a dynamic diffraction pattern list /w assiated controls

    bloch_imgs_list.add(emc, img) 
    
    showBloch(bloch_imgs_list) #grey color map
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
__Kinematic Diffraction Pattern__ for _Silicon_ crystal:
|  |  |
| - | - |
|![](https://github.com/emlab-solutions/imagepypy/raw/main/si_dif1.png) |![](https://github.com/emlab-solutions/imagepypy/raw/main/si_dif2.png) |


__Dynamic Diffraction Pattern__ for _Silicon_ crystal with sampling set at 20: 

|  |  |
| - | - |
|![](https://github.com/emlab-solutions/imagepypy/raw/main/si_bloch1.png) |![](https://github.com/emlab-solutions/imagepypy/raw/main/si_bloch2.png) |

__Stereodiagram__ for _Silicon_ crystal
|  |  |
| - | - |
|![](https://github.com/emlab-solutions/imagepypy/raw/main/Stereo_Silicon4.png) |![](https://github.com/emlab-solutions/imagepypy/raw/main/Stereo_Silicon1.png) |

To see all crystal names with builtin data, call:
```python
from pyemaps import Crystal as cr
cr.list_all_builtin_crystals()
```

To use a crystal data not in built-in database in above format (as xtl format), replace the code in _sample.py_:
```python
from pyemaps import Crystal as cr
si = cr.from_xtl(fn)
```
CIF format has recently been added to crystal data sources where __pyemaps__ can import:
```python
from pyemaps import Crystal as cr
si = cr.from_cif(fn)
```
where _fn_ is a crystal data file name. See release notes for details how pyemaps imports cif data

Note: __pyemaps__ searches for _fn_ if the full path is provided. Otherwise, it will look up the file in current working directory or in the directory set by *PYEMAPS_DATA* environment variable. In latter cases, _fn_ is the file name without path.

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

* __powder.py__: _electron powder diffraction_ generation and intensity plot by __Powder__ pyemaps module. 

* __si_stereo.py__: _stereodiagram_ generation by ____ pyemaps __Stereo__ module. 

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