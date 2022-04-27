## Overview
This python package contains python modules and libraries that simulate
diffraction with selected crystal. It contains the following main features:

>**pyemaps** : top level python module, containing many submodules designed for electron microscope simulations

>**Crystal** : crystal data module, classes and methods loading crystal data from various sources. 

>**DP** : kinematic diffraction python class, its methods including diffraction patterns generation based on the crystal data and microscope and sample control parameters.  

The above python modules and libraries are based on the propietory Fortran applications released as backend of [cloudEMAPS2.0](https://emaps.emlabsolutions.com). 

Future releases planned include:

>*Bloch* : dynamic bloch diffraction simulation (proprietory, license needed)

Check [EMlab Solution, Inc.](https://www.emlabsolutions.com) for updates on releases. We welcome your comments and suggestions from our user community. For reporting any issues and requesting pyemaps improvements, even sharing your scripts using pyemaps, please go to [our support page](https://www.emlabsolutions.com/contact/). 

If you feel that __pyemaps__ make a big impact in your research and education in microscopy and crystallography, we ask for your support and donation to continue to provide you with free software packages like this.   

## Installation

```
python -m pip pyemaps
```
or
 ```
 pip install pyemaps
 ```

## Basic Usage

```
from pyemaps import Crystal
from pyemaps import DP
```

## Example

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
microcope camera length : 1000 nm
microscope voltage: 200
sample tilt: (0.0,0.0)
sample offset: (0.0,0.0)
spot size: 0.05 nm
```



![](https://github.com/emlab-solutions/imagepypy/raw/main/kdiff_si.png?raw=True "Kinematic diffraction for silicon")

## Integrating With DigitalMicrogrph (DM)
If you have DigitalMicrography from Gatan with python support installed on your desktop, you can copy dm_diff.py from pyemaps sample installation directory after pemaps has been installed in the right environment for your DM. The python script utilizes DM annotations to plot the diffraction patterns generated on silicon crystal.


![](https://github.com/emlab-solutions/imagepypy/blob/main/kdiff_si_dm.png?raw=True "Kinematic diffraction for silicon python script dm_diff.py")

Other sample scripts designed for you to explore pyemaps and available in samples directory:
* __si_diff_normal.py__: spot diffraction patterns generated with silicon crystal data, plotted with _matplotlib pyplot_ module. The code also shows how a list of diffraction patterns are generated and displayed as one of electron microscope and sample control - tilt in x direction changes.

* __si_diff_cbed.py__: The same as above with exception of diffraction mode changed to CBED.

* __pyplot_dm_si_diff.py__: DM python script which generate and plot diffraction pattern for silicon crystal using _matplotlib pyplot_ module

* __pyplot_dm_si_diff_color.py__: Similar to the above, the plot is done in color.

