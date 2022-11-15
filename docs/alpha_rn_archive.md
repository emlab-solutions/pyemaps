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
    aperture = 1.0,                 #  Objective aperture
    omega = 10,                     #  Diagnization cutoff                            
    sampling = 8,                   #  Number of sampling points
    pix_size = 25,                  #  Detector pixel size in microns
    thickness = 200,                #  Sample thickness
    det_size = 512,                 #  Detector size (it's also resulting bloch image array dimension)
    disk_size = 0.16,               #  Diffraction disk rdius in 1/A
    em_controls = EMC(cl=200)       #  Electron Microscope controls
```
Additional helper classes and method are also added to assist multiple bloch calcaluation and image handling. See _si_bloch.py_ for more details of the usage.

* __BImgList__: similar to DPList class, _BImgList_ is designed to hold and handle multiple bloch images and their associated controls.

* __generateBlochImgs__: This is Crystal method that generate a BImgList objects for input of sample thickness range and step tuple: 
    sample_thickness=(thickness_start, thickness_end, thickness_step)
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

* __generateDif(...) Method Added__: This method in _Crystal_ class generates a list of DPs and their associated electron microscopy controls, or _diffraction_ object. It is in contrast to the existing generateDP(...) method that generate a single diffarction pattern (DP).

### __0.4.2 Alpha__ July 28th, 2022

#### IMPROVEMENTS

* __Dynamic Diffraction Performance and Computation Accuracy Improvements__: Switching to LAPACK libraries in eigen calculations has resulted in great improvements in matrix computations employed in Bloch module. An average of over 100% performance improvements. More performance improvements are planned with OpenMP implementations in compute intense Bloch module. Stay tuned...  

* __Bug Fixes__: Fixed runtime error in display functions on some system. 

### __0.4.3 Alpha__ August 19th, 2022

#### IMPROVEMENTS

* __Installation Dependencies Removed__: CIF reader support for python 3.7 is now added. As result, __pyemaps__ installation no longer requires of MSVC build tool to build it from the source package and additional runtime installation requirement also removed. 

### __0.4.4 Alpha__ September 2nd, 2022

#### NEW

* __More Control Paraameter Added__: A selection of simulation parameters are now added to user input defined in SIMControl class:
```python
class SIMControl:
    def __init__(self, excitation = DEF_EXCITATION, \   #excitation error range (min, max)
                       gmax = DEF_GMAX, \               #maximum recipricol vector length
                       bmin = DEF_BMIN, \               #beta perturbation cutoff
                       intensity = DEF_INTENSITY, \     #kinematic diffraction intensity cutoff level and scale (level, scale)
                       xaxis = DEF_XAXIS, \             #crystal horizontal axis in reciprical space
                       gctl = DEF_GCTL, \               #maximum index number for g-list
                       zctl = DEF_ZCTL                  #maximum zone index number
                       ):
```
For the sake of backward compatibility, these parameters are embedded in SIMControls class object in existing EMControl class. Default values retrieved from dif and bloch modules are assumed if not specified. See detailed definition of SIMControl class in _emcontrols.py_.

Examples of how to use this control class along with previous controls are in sample code _si_dif.py_ and _si_bloch.py_.

#### IMPROVEMENTS

* __Runtime Libraries Installation Requirements__: Runtime libraries are now included in pyemaps installation. pyemaps should now work out of box after its installation. 


### __0.4.5 Alpha__ September 30th, 2022

#### NEW

* __Stereodiagram__: this feature is demonstrated by the sample script __si_stereo.py__. The basic usage:
```python
    from pyemaps import Crystal as cr
    si = cr.from_builtin('Silicon')
    stereolist = si.generateStereo(xa, tilt, zone)
    showStereo(stereolist, iShow=True, zLimit = 1, bSave=True)
    # zLimit for filtering for hkl index
    # iShow for weather to display hkl index
    # bSave for saving images to .png files
``` 
* __Crystal Constructor__: will allow users to transform and manipulate crystal structure. Users will be able to generate .xyz formatted files for visualization in Jmol or other atomic structure visualization tools:
```python
    from pyemaps import Crystal as cr
    si = cr.from_builtin('Silicon')
    mx = si.generateMxtal(**kargs)
    write_xyz(mx, fn)  
    
    # fn is the output .xyz file to be placed in PYEMAPS_DATA/mxtal fodler
``` 
More to come for this module.

* __Bloch Raw Image Output__: Multi-slices and raw images of bloch image generate from generateBlochImgs can now be saved into .im3 files that can be imported to ImageJ, Gatan's Digital Micrograph for viewing.
```python
    si.generateBlochImgs(..., bSave=True)
```
If successful, the file will be located in PYEMAPS_DATA/bloch folder if PYEMAPS_DATA is set, or in current working directory, with auto generated file name of the format:

    <crystal_name>bloch<yyyymmddhhmmss>.im3