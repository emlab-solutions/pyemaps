
# Table of Contents
1. <a id="contents"></a>[Overview](#overview)
2. <a id="contents"></a>[Installation](#installation)
3. <a id="contents"></a>[Basic Usage](#basic-usage)
4. <a id="contents"></a>[Getting Started](#getting-started)
5. <a id="contents"></a>[Integration with Others Tools](#integration-with-others-tools)
6. <a id="contents"></a>[License](#license)

## Overview [`↩`](#contents) <a id="overview"></a>
__pyemaps__ package is a collection of python modules and libraries designed for transmission electron diffraction simulations and related crystallographic calculations. Main features include:

>**Crystal** : crystal data module, classes and methods loading crystal data from various sources, including diffraction patterns generation based on the crystal data and microscope and sample control parameters

>**DP** :  kinematic diffraction python class. It encapsulates diffraction pattern data generated by the Crystal class instance and diffraction pattern visualization methods such as plotting Kikuchi and HOLZ lines, and diffraction spots or disks and their indices. 

__pyemaps__ is based on the proprietary Fortran applications released as backend of [cloudEMAPS2.0](https://emaps.emlabsolutions.com). 

Future releases planned include:

>*Bloch* : dynamic Bloch wave simulation.

Check [EMlab Solution, Inc.](https://www.emlabsolutions.com) for updates and releases. We welcome comments and suggestions from our user community. For reporting any issues and requesting pyemaps improvements, or sharing scripts using __pyemaps__, please go to [our support page](https://www.emlabsolutions.com/contact/). 

We ask for your support and donation to continue to provide free software packages like this to make impact in research and education in microscopy and crystallography.  

## Installation [`↩`](#contents) <a id="installation"></a>

```
python -m pip pyemaps
```
or
 ```
 pip install pyemaps
 ```

## Basic Usage [`↩`](#contents) <a id="basic-usage"></a>

```
from pyemaps import Crystal
from pyemaps import DP
```

## Getting Started [`↩`](#contents) <a id="getting-started"></a>

Run the following on command line, after above successful installation step:

```
python sample.py
```

where sample.py is as follows:

```python
#import Crystal class from pyemaps as cryst
from pyemaps import Crystal as cryst

# create a crystal class instance and load it with builtin silican data
si = cryst.from_builtin('silicon')

# run diffraction on the crystal instance with all default controls
# parameters
si_dp = si.gen_diffPattern()

#plot and show the pattern just generated using pyemaps built-in plot function
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
spot size: 0.05 angstron
```

![](https://github.com/emlab-solutions/imagepypy/raw/main/kdiff_si.png?raw=True "Kinematic diffraction for silicon")

## Integration with Others Tools [`↩`](#contents) <a id="integration-with-others-tools"></a>
If you have DigitalMicrography (referred as DM) from Gatan with python support installed on your desktop, you can copy _dm_diff.py_ from __pyemaps__ sample installation directory after pemaps installation in the right environment set for your DM. The python script in the script utilizes DM python annotations to plot the diffraction patterns generated on silicon crystal.

```python
import numpy as np
import DigitalMicrograph as DM

from pyemaps import XMAX, YMAX
#----diffraction patterns generated by these bounds
#   [-XMAX, XMAX, -YMAX, YMAX]

#    screen size 
mult = 4

#simple diffraction mode lookup
DIFF_MODE = ('Normal', 'CBED')
#------Diffraction modes-------
#       1 - normal
#       2 - CBED

def addline( x1, y1, x2, y2): #reserved for later use
    xx1, yy1, xx2, yy2 = x1*2, y1*2, x2*2, y2*2
    dmline = DM.NewLineAnnotation(xx1, yy1, xx2, yy2)
    
    dmline.SetResizable(False)
    dmline.SetMovable(False)
    dmline.SetDeletable(False)
    dmline.SetForegroundColor(0,1,0)
    dmline.SetBackgroundColor(0.2,0.2,0.5)
    
    return dmline


def adddisk( x1, y1, r, indx): #reserved for later use
    xx1, yy1, rr = x1*2, y1*2, r*2
    dmdisk = DM.NewOvalAnnotation()
    dmdisk.SetCircle(xx1-r,yx1-r, xx1+rr,yy1+r)
    dmdisk.SetLabel(indx)

    return dmdisk

    
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
    si_dp_cbed = si.gen_diffPattern(mode = 2, dsize = 0.2)
    #print(si_dp_cbed)

    #-----------Plot the pattern in DM----------------------------------------
    show_diffract(si_dp_cbed, md = 2, name = name)



    #-----------generate diffraction pattern in normal mode-------------------
    si_dp = si.gen_diffPattern()
    #print(si_dp)

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

 __pyemaps__ is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

* __pyemaps__ is for non-commercial use.
* __pyemaps__ is free software under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.

Contact supprort@emlabsoftware.com for any questions and requests.
