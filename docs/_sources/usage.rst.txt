Getting Started
===============

.. _installation:

Installation
------------

To use pyemaps, first install it using pip:

.. code-block:: console

   (.venv) $ pip install pyemaps

where .venv is the python virtual environment.

.. note::
   
   To prevent conflicts of pyemaps dependencies with your existing python
   libraries, it is recommended that pyemaps install in its own python environment
   such as that with Annaconda or Miniconda.

.. code-block:: console

   conda create -n <env-name> python=3.7
   conda activate <env-name>
   python -m pip install pyemaps

where <env-name> is the name of the new conda environment.

.. _Environment Variables:

Enviroment Variables
--------------------

*PYEMAPS_DATA* environment variable is set to represent pyemaps' data home directory.
It provides a central location for organizing your own crystal data, and it is also used 
for storing your simulation and calculation results.   

**pyemaps** searches crystal files in the following order when only file name is provided:

1. Current working directory. 
2. Data home directory pointed by *PYEMAPS_DATA*.

For output from **pyemaps** simulations and calculations, the placement order is reversed:

1. Data home directory pointed by *PYEMAPS_DATA* if it is set. 
2. Current working directory.

The layout of the pyemaps data home directory is as follows:

.. code-block:: console

    $(PYEMAPS_DATA)=<local directory>  # pyemaps data home, must have read and write permisions
    $(PYEMAPS_DATA)/crystals           # hosts all custom crystal data files (.xtl, .cif)
    $(PYEMAPS_DATA)/dif                # location for all kinematic diffraction simulation output
    $(PYEMAPS_DATA)/bloch              # location for all Bloch dynamic simulations images output files
    $(PYEMAPS_DATA)/stereo             # location for all stereodiagram output files
    $(PYEMAPS_DATA)/mxtal              # place for all crystal constructor output files such as *.xyz

.. note::
   
   The legacy environment variable $(PYEMAPS_CRYSTALS) is still supported if it is set.

Quickstart pyemaps
------------------

After *pyemaps* installation, run the following to check if the package is installed
and setup correctly on your system by verifying the version and other information about
the package: 

.. code-block:: console

   python -m pyemaps --version (-v)
   python -m pyemaps --copyright (-c)

A test for *pyemaps* basic kinematic function is also provided:  

.. code-block:: console

   python -m pyemaps --sample (-s)

All pyemaps simulations and calculations start from its 
`Crystal class <pyemaps.crystals.html#pyemaps.crystals.Crystal>`_. 
To import the class:

.. code-block:: python

   from pyemaps import Crystal

Before starting pyemaps diffraction simulation, the crystal
object must be created and loaded. The following example
creates a *si* crystal object by loading it from pyemaps 
built-in database for Silicon crystal using 
`from_builtin <pyemaps.crystals.html#pyemaps.crystals.Crystal.from_builtin>`_ 

.. code-block:: python
 
    from pyemaps import Crystal as cr  

    si = cr.from_builtin('Silicon')

.. note::
   
   Pyemaps also provides methods for creating crystal objects from other 
   data sources, including imports from CIF, JSON formatted files. Go to 
   `Crystal class <pyemaps.crystals.html#pyemaps.crystals.Crystal>`_
   for more details.


Once a crystal object is created and loaded, it is ready for simulations
and calculations.   

Kinematic Diffraction Simulation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pyemaps import Crystal            #----pyemaps crystal module
   from pyemaps import DPList, showDif    #----Helper modules
   
   si = Crystal.from_builtin('Silicon')   #----loading Silicon crystal from builtin database
   emc, si_dp = si.generateDP()           #----generate kinematic diffraction pattern
                                          #----Output:
                                          #----emc: associated microscope and 
                                          #         simulation control object
                                          #----si_dp: diffraction pattern generated
   print(si_dp)                           #----raw representation of kinematic diffraction pattern 

   dpl = DPList('Silicon')                #----create a diffraction pattern list to hold the results
   dpl.add(emc, si_dp)                    #----can add more if desired

   showDif(dpl, bClose=False)             #----visual representation of diffraction pattern


Here crystal class method *generateDP* produces a kinmatic diffraction pattern or
`DPList <pyemaps.kdiffs.html#pyemaps.kdiffs.diffPattern>`_ (si_dp) 
using all default control parameters . 

Go to `generateDP <pyemaps.crystals.html#pyemaps.crystals.Crystal.generateDP>`_ for a complete
list of control parameters. 

*showDif*, a method in the pyemaps `display module <pyemaps.display.html#module-pyemaps.display>`_  
visualizes the *si_dp* diffraction pattern with options controling whether to show Kikuchi lines or
Miller Indexes.

Bloch Wave Dynamic Diffraction Simulation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To simplify, we will call this simulation as Bloch or Bloch simulation throughout this help
document.

.. code-block:: python

    from pyemaps import Crystal as cr        # Crystal class
    from pyemaps import BImgList             # Dynamic diffraction image list class
    from pyemaps import showBloch            # Builtin visualization helper function

    # create a crystal class object and load it with builtin silicon data
    c_name = 'Silicon'
    si = cr.from_builtin(c_name)

    # Generate dynamic diffraction patterns using pyemaps' bloch module
    # with all other default parameters except sampling

    try:
      bloch_imgs_list = si.generateBloch(sampling = 20) 
      
    except Exception as e:
      print(f'Error: {e}')

    else:        
      showBloch(bloch_imgs_list) #grey color map
      showBloch(bloch_imgs_list, bColor=True) #with predefined color map
   
The crystal method *generateBloch* starts a Bloch wave dynamic diffraction simulation with 
the sampling resolution of 20 pixels along the disk radius. 

For a complete set of controls and input parameters for the Bloch simulation, 
go to `generateBloch <pyemaps.crystals.html#pyemaps.crystals.Crystal.generateBloch>`_  

Pyemaps also provides a helper class `BImgList <pyemaps.ddiffs.html#pyemaps.ddiffs.BlochImgs>`_
and an image rendering method *showBloch* in `display module <pyemaps.display.html#module-pyemaps.display>`_ 
visualizing the Bloch simulation results.

.. note::

   To generate multiple images with a specified range of sample thickness 
   and save them in raw image data file. See the description of `generateBloch method 
   <pyemaps.crystals.html#pyemaps.crystals.Crystal.generateBloch>`_. 
   
   The raw image data file can be imprted into third party visualization tools
   such as `ImageJ <https://imagej.nih.gov/ij/>`_ and 
   `DigitalMicrograph <https://www.gatan.com/products/tem-analysis/gatan-microscopy-suite-software>`_. 

.. note::

   To start a Bloch simultion session and retrieve the scattering matrix 
   and other dynamic diffraction session information, see `getSCMatrix method 
   <pyemaps.crystals.html#pyemaps.crystals.Crystal.getSCMatrix>`_  
   between `beginBloch
   <pyemaps.crystals.html#pyemaps.crystals.Crystal.beginBloch>`_ and 
   `endBloch calls
   <pyemaps.crystals.html#pyemaps.crystals.Crystal.endBloch>`_.

To see all crystal names in the *pyemaps* built-in database, call 
`list_all_builtin_crystals <pyemaps.crystals.html#pyemaps.crystals.Crystal.list_all_builtin_crystals>`_:

.. code-block:: python

   from pyemaps import Crystal as cr
   cr.list_all_builtin_crystals()

Current list of built-in crystals in *pyemaps*:

::

   'Aluminium', 'AluminiumOxide', 'Aluminium_FCC', 'BariumTitanate_180k', 'BariumTitanate_270k', 
   'BariumTitanate_Tetra', 'Boron_Tetra', 'CadmiumSelenide_Hex', 'CadmiumSulfide_Cubic', 
   'CadmiumSulfide_Hex', 'Chromium_BCC', 'CopperOxide', 'Copper_FCC', 'Cu2O_Cuprite', 'Diamond', 
   'ErbiumPyrogermanate', 'FePd_Tetra', 'FeS2_Pyrite', 'GalliumAntimonide', 'GalliumArsenide', 
   'GalliumNitride', 'Germanium', 'Gold_FCC', 'IndiumArsenide', 'LaMnO3', 'LeadZirconateTitanate', 
   'Li2MnO3', 'limno2', 'NaFeO2', 'Nb3Sn', 'Silicon', 'StrontiumTitanate', 'TelluriumDioxide', 
   'TinDioxide_RT', 'TitaniumDioxide_Anatase', 'TitaniumDioxide_Rutile', 'TungstenDiselenide', 
   'VanadiumDioxide_RT', 'ZincOxide', 'Zinc_HCP', 'ZirconiumNitride'


Experimental Diffraction Pattern Indexing 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Electron diffraction patterns (DP) indexing is based on the template matching algorithm to 
compare the acquired DPs to pre-built ones - A DP database generated by pyemaps DPGEN module.

In this feature, the crystal orietations and phases are determined from the best match or fit
to one of the DP in the pre-generated DP database:

.. code-block:: python

      from pyemaps import Crystal as cr
      al = cr.from_builtin('Aluminium')
      ret, dbfn = al.generateDPDB(emc=EMC(), res, xa, vertices)

will generate a DP datbase for Aluminium crystal. Here *vertices* is an array of 3 or 4 zone axis 
indexes that form an enclosed orientation surface area within which the diffraction patterns are generated. 
The database will be saved in *dbfn*. 

For details of this function go to:
`generateDPDB <pyemaps.crystals.html#pyemaps.crystals.Crystal.generateDPDB>`_

.. code-block:: python

   ret, mr, mc =al.loadDPDB(dbfn = dbfn, bShowDBMap=True)
    
will be loading the database into pyemaps' EDIOM module and ready for DP indexing.

.. code-block:: python

  al.importSHExpImage(xifn, bShow=True)

loads the experimental DP file for indexing.

.. code-block:: python

   al.indexExpDP(cc                 = 29.0,                  
                 sigma              = 3.0,
                 img_center         = (99.923, 99.919),
                 rmin               = 10,
                 search_box         = 10.0,
                 scaling_option     = (1,2),
                 filter_threshold   = 0.0,
                 peak_threshold     = 0.8)

indexes the loaded DP image file above. See more details of the usage in 
`indexExpDP <pyemaps.crystals.html#pyemaps.crystals.Crystal.indexExpDP>`_

.. note:: 

   Diffraction pattern indexing feature is now in preview. Current limitaion of the preview
   feature in this free package:

   1. Crystals that are in cubic space group with space numbers of 225, 227 and 229.
   2. The experimental DP image sizes are limited 100 up to 512 pixels.
   3. Diffraction database resolution is restricted in range 100 and 300 sampling points.
   
   Again, we appreciate any comments and suggestions for us to improve this feature. Contact us
   at support@emlabsoftware.com to send us your thoughts or inquiries for full packages 
   without above restrictions. 

Samples code
------------

Sample scripts for exploring *pyemaps* features are available in 
pyemaps' *samples* directory.

To copy all sample scripts from *pyemaps* package installation directory
to the current working directory, run:

.. code-block:: console

   python -m pyemaps -cp

Below is a partial list of sample code:

* *si_dif.py*: 
   shows how kinematic diffraction patterns are generated and rendered with 
   *matplotlib pyplot* module.

* *si_bloch.py*, *si_lacbed.py*: 
   demonstrates dynamic diffraction simulations by *bloch* *pyemaps* module in two
   modes: normal and large angle CBED.

* *si_csf.py*: 
   calculates and outputs structure factors using *CSF* *pyemaps* module. 

* *powder.py*: 
   calculates and plots electron powder diffraction pattern using 
   *Powder* *pyemaps* module. 

* *si_stereo.py*: 
   plots stereodiagram using *Stereo* *pyemaps* module. 

* *si_dpgen.py*: 
   generates a proprietory diffraction database file for silicon crystal. 

* *al_ediom.py*: 
   indexes an experimental diffraction image for aluminium crystal. 


More samples code will be added as more features and releases are available. 
