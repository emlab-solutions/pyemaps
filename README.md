## Overview
This python package contains python modules and libraries that simulate
diffraction with selected crystal. It contains the following features:

>**pyemaps** : top level python module, containing many submodules designed for electron microscope simulations

>**crystal** : crystal data module, classes and methods loading crystal data from various sources

>**dif** : kinematic Diffraction module and libraries, generating diffraction patterns based on the crystal data and microscope and sample control parameters.  

The above python modules and libraries are based on propietory Fortran applications released as backend of [cloudEMAPS2.0](https://emaps.emlabsolutions.com).

Future releases planned include:

>*Bloch* : dynamic bloch diffraction simulation (proprietory, license needed)

Check [EMlab Solution, Inc.](https://www.emlabsolutions.com) for updates and new features.

## Basic Usage

```
from pyemaps import Crystal as cryst
from pyemaps import dif
```

## Installation
```
python -m pip pyemaps
```

## Example Run

Run the following on command line, after installation step above

```
python -m pyemaps -s [--sample] 
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