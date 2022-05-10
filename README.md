# Introducing __pyemaps__
1. <a id="contents"></a>[Overview](#overview)
2. <a id="contents"></a>[Requirements](#requirements)
3. <a id="contents"></a>[Installation](#installation)
4. <a id="contents"></a>[Basic Usage](#basic-usage)
5. <a id="contents"></a>[Getting Started](#getting-started)
6. <a id="contents"></a>[Visualization](#visualization)
7. <a id="contents"></a>[License](#license)

## Overview [`↩`](#contents) <a id="overview"></a>
__pyemaps__ package is a collection of python modules and libraries designed for transmission electron diffraction simulations and related crystallographic calculations. Main features include:

>**Crystal** : crystal data module, classes and methods loading crystal data from various sources, including diffraction patterns generation based on the crystal data and microscope and sample control parameters

>**DP** :  kinematic diffraction python class. It encapsulates diffraction pattern data generated by the Crystal class instance and diffraction pattern visualization methods such as plotting Kikuchi and HOLZ lines, and diffraction spots or disks and their indices. 

__pyemaps__ is based on the proprietary Fortran applications released as backend of [cloudEMAPS2.0](https://emaps.emlabsolutions.com). 

Future releases planned include:

>*Bloch* : dynamic Bloch wave simulation.

Check [EMlab Solution, Inc.](https://www.emlabsolutions.com) for updates and releases. We welcome comments and suggestions from our user community. For reporting any issues and requesting pyemaps improvements, or sharing scripts using __pyemaps__, please go to [our support page](https://www.emlabsolutions.com/contact/). 

If you benefit from __pyemaps__ in your microscopy and crystallography research and education, go to [PayPal](https://www.paypal.com/paypalme/pyemaps22) to donate. Your generous donations keep us in the business of providing free software to the communities.   

## Requirements [`↩`](#contents) <a id="requirements"></a>

* __Python__: Version >= 3.6
* __Operating Systems__: Windows

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
#import Crystal class from pyemaps as cryst
from pyemaps import Crystal as cryst
# create a crystal class instance and load it with builtin silicon data
si = cryst.from_builtin('silicon')

# generate diffraction on the crystal instance with all default controls
# parameters
si_dp = si.generateDP()
#plot and show the diffraction pattern using pyemaps built-in plot function
si_dp.plot()
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
microscope voltage: 200 kv
sample tilt: (0.0,0.0)
sample offset: (0.0,0.0)
spot size: 0.05 Å
```

![](https://github.com/emlab-solutions/imagepypy/raw/main/kdiff_si.png?raw=True "Kinematic diffraction for silicon")

To see all crystal names with builtin data, call:
```python
cryst.list_all_builtin_crystals()
```
where cryst is imported __pyemaps__ Crystal class

To use a crystal data not in built-in database in above format (as xtl format), replace the code in _sample.py_:
```python
si = cryst.from_builtin('silicon')
```
with:
```python
si = cryst.from_xtl(fn)
```
where _fn_ is a crystal data file name.

Note: __pyemaps__ searches for _fn_ if the full path is provided. Otherwise, it will look up the file in current working directory or in the directory set by *PYEMAPS_CRYSTALS* environment variable. In latter cases, _fn_ is just the file name without path.

Checking __pyemaps__ version and displaying copyright information:
```
python -m pyemaps -c (--copyright)
python -m pyemaps -v (--version)
```

## Visualization [`↩`](#contents) <a id="visualization"></a>
In addition to Python's _matplotlib_ for displaying diffraction patterns generated by __pyemaps__ as shown above, DigitalMicrography (referred as DM here) is another option. The python script support in DM can realize the diffraction patterns from __pyemaps__ with its line and circle annotations as demonstrated below: 

```python
import numpy as np
import DigitalMicrograph as DM
from pyemaps import XMAX, YMAX
#----diffraction patterns generated by these bounds
#   [-XMAX, XMAX, -YMAX, YMAX]
#    screen size multiplier
mult = 4
#simple diffraction mode lookup
DIFF_MODE = ('Normal', 'CBED')
#------Diffraction modes-------
#       1 - normal
#       2 - CBED
def SetCommonProp(comp):
    comp.SetResizable(False)
    comp.SetMovable(False)
    comp.SetDeletable(False)
    
def show_diffract(dp, md=1, name = 'Diamond'):   
    shape = (2*XMAX*mult,2*YMAX*mult)
    dif_raw = np.ones((shape), dtype = np.float32)
    dif_raw[:,:] = 255.0
    dm_dif_img = DM.CreateImage(dif_raw)
    dif_img = dm_dif_img.ShowImage()
    dif_img_disp = dm_dif_img.GetImageDisplay(0)
    
    if md <1 or md > 2:
        print(f'diffraction mode provided {md} not supported')
        return 1
    
    img_title = str(f'Kinematic Diffraction Simulation:  {name} in {DIFF_MODE[md-1]} Mode')
    dm_dif_img.SetName(img_title)    
    #xs,ys = diff_dict['bounds'] # not used
    num_klines = dp.nklines
    if num_klines > 0:
        klines = dp.klines
        for kl in klines:        
            x1, y1, x2, y2 = kl             
            xx1, yy1, = (x1 + XMAX)*mult,(y1 + YMAX)*mult 
            xx2, yy2  = (x2 + XMAX)*mult,(y2 + YMAX)*mult            
            kline = dif_img_disp.AddNewComponent(2, xx1, yy1, xx2, yy2)            
            SetCommonProp(kline)
            kline.SetForegroundColor(0.7, 0.7, 0.7) #grey
            kline.SetBackgroundColor(0.2,0.2,0.5)# dark blue
    num_disks = dp.ndisks
    if num_disks > 0:
        disks = dp.disks
        for d in disks:
            x1, y1, r, i1, i2, i3 = d
            xx, yy, rr = (x1 + XMAX)*mult, (y1 + YMAX)*mult, r*mult                         
            idx = '{:d} {:d} {:d}'.format(i1,i2,i3)            
            disk = dif_img_disp.AddNewComponent(6, xx-rr, yy-rr, xx+rr, yy+rr)
            
            SetCommonProp(disk)
            disk.SetForegroundColor(0.0,0.0,1.0) # blue
            disk.SetBackgroundColor(0.5,0.5,0.75)# dark blue
            if md == 1:
                disk.SetFillMode(1)
            else:
                disk.SetFillMode(2)        
            indxannot0 = DM.NewTextAnnotation(0, 0, idx, 10)            
            t, l, b, r = indxannot0.GetRect()
            w = r-l
            h = b-t            
            nl = xx - ( w / 2)
            nr = xx + ( w / 2)
            nt = yy -rr - h if md ==1 else yy - (h / 2)
            nb = yy + rr + h if md == 1 else yy + (h / 2)            
            indxannot = DM.NewTextAnnotation(nl, nt, idx, 10)            
            dif_img_disp.AddChildAtEnd(indxannot)
            SetCommonProp(indxannot)
            indxannot.SetForegroundColor(0.9,0,0) #light red
            indxannot.SetBackgroundColor(1,1,0.5)
            
    if md == 2:
        num_hlines = dp.nhlines
        if num_hlines > 0 :
            hlines = dp.hlines
            for hl in hlines:
                x1, y1, x2, y2 = hl
                xx1, yy1 = (x1 + XMAX)*mult, (y1 + YMAX)*mult 
                xx2, yy2 = (x2 + XMAX)*mult, (y2 + YMAX)*mult                
                hline = dif_img_disp.AddNewComponent(2, xx1, yy1, xx2, yy2)
                SetCommonProp(hline)
                hline.SetForegroundColor(0,0,0.8)
                hline.SetBackgroundColor(0.2,0.2,0.5)# dark blue                
    del dm_dif_img
    return 0              
      
def run_si_dm_sample():  
    from pyemaps import Crystal as cr
    #-----------load crystal data into a Crystal class object-----------------
    name = 'Silicon'
    si = cr.from_builtin(name)
    #-----------content of the crystal data-----------------------------------
    print(si)
    #-----------generate diffraction pattern in CBED mode---------------------
    si_dp_cbed = si.generateDP(mode = 2, dsize = 0.2)
    #-----------Plot the pattern in DM----------------------------------------
    show_diffract(si_dp_cbed, md = 2, name = name)

    #-----------generate diffraction pattern in normal mode-------------------
    si_dp = si.generateDP()
    #-----------content of the crystal data-----------------------------------
    show_diffract(si_dp, name = name)

run_si_dm_sample()

```
![](https://github.com/emlab-solutions/imagepypy/blob/main/kdiff_si_dm.png?raw=True "Kinematic diffraction for silicon python script dm_diff.py")

Other sample scripts designed for you to explore pyemaps are available in samples directory:
* __si_tilt_normal.py__: spot diffraction patterns generated with silicon crystal data, plotted with _matplotlib pyplot_ module. The code also shows how a list of diffraction patterns are generated and displayed as one of electron microscope and sample control - tilt in x direction changes.

* __si_tilt_cbed.py__: The same as above with the diffraction mode set to CBED.

* __pyplot_dm_si_diff.py__: DM python script which generate and plot diffraction pattern for silicon crystal using _matplotlib pyplot_ module

* __pyplot_dm_si_diff_color.py__: Similar to the above, the plot is done in color.

## License [`↩`](#contents) <a id="license"></a>

 __pyemaps__ is distributed for electron diffraction and microscopy research, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
* __pyemaps__ is for non-commercial use.
* __pyemaps__ is free software under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. You should have received a copy of the GNU General Public License along with __pyemaps__.  If not, see <https://www.gnu.org/licenses/>.

Contact supprort@emlabsoftware.com for any questions regarding the license terms.