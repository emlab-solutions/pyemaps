Getting Started
===============

.. _installation:

Installation
------------

To use pyemaps, first install it using pip:

.. code-block:: console

   (.venv) $ pip install pyemaps

where .venv is the python virtual environment.

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
    $(PYEMAPS_DATA)/bloch              # location for all bloch images output files
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


Once a crystal object is created and loaded` it is ready for simulations
and calculations.   

Kinematic Diffraction Simulation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from pyemaps import Crystal as cr        # Crystal class
    from pyemaps import DPList               # Kinematic diffraction patterns class
    from pyemaps import showDif              # Builtin visualization helper class
    
    # create a crystal class object and load it with builtin silicon data
    c_name = 'Silicon'
    si = cr.from_builtin(c_name)

    # Simulate kinematic diffraction with the crystal instance 
    # All controls input are default values
    
    dpl = DPList(c_name)

    emc, si_dp = si.generateDP()
    dpl.add(emc, si_dp)    

    # Plot and show the diffraction pattern using 
    # pyemaps built-in plot function
    showDif(dpl)

    # Show Diffraction patterns by hiding Kikuchi lines
    showDif(dpl, kshow=False) 

    # Show Diffraction patterns by hiding both Kukuchi line and Miller Indexes
    showDif(dpl, kshow=False, ishow=False) 

    # Show Diffraction patterns by hiding Miller Indices
    showDif(dpl, ishow=False)

Here crystal class method *generateDP* produces a 
`kinmatic diffraction pattern <pyemaps.kdiffs.html#pyemaps.kdiffs.diffPattern>`_ (si_dp) 
using all default control parameters . 

Go to `generateDP <pyemaps.crystals.html#pyemaps.crystals.Crystal.generateDP>`_ for a complete
list of control parameters. 

*showDif*, a method in the pyemaps `display module <pyemaps.display.html#module-pyemaps.display>`_  
visualizes the *si_dp* diffraction pattern with options controling whether to show Kikuchi lines or
Miller Indexes.

Dynamic Diffraction Simulation - Bloch
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from pyemaps import Crystal as cr        # Crystal class
    from pyemaps import BImgList             # Dynamic diffraction image list class
    from pyemaps import showBloch            # Builtin visualization helper function

    # create a crystal class object and load it with builtin silicon data
    c_name = 'Silicon'
    si = cr.from_builtin(c_name)

    # Generate dynamic diffraction patterns using pyemaps' bloch module
    # with all other default parameters except sampling

    bloch_imgs_list = BImgList(c_name)
    emc, img = si.generateBloch(sampling = 20) 
    
    # Create a dynamic diffraction image list

    bloch_imgs_list.add(emc, img) 
    
    # Display the image with grey scale color map and #with predefined color map
    showBloch(bloch_imgs_list) 
    showBloch(bloch_imgs_list, bColor=True) 

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
   such as ImageJ (TODO link) and DigitalMicrograph. 

.. note::

   To start a Bloch simultion session and retrieve the scattering matrix 
   and other dynamic diffraction session information, see `getSCMatrix method 
   <pyemaps.crystals.html#pyemaps.crystals.Crystal.getSCMatrix>`_  
   between `beginBloch
   <pyemaps.crystals.html#pyemaps.crystals.Crystal.beginBloch>`_ and 
   `endBloch calls
   <pyemaps.crystals.html#pyemaps.crystals.Crystal.endBloch>`_.

To see all crystal names in the *pyemaps* built-in database, call 
`list_all_builtin_crystals: <pyemaps.crystals.html#pyemaps.crystals.Crystal.list_all_builtin_crystals>`_:

.. code-block:: python

   from pyemaps import Crystal as cr
   cr.list_all_builtin_crystals()


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
   shows how kinematic diffraction patterns is generated and rendered with 
   *matplotlib pyplot* module. The code also shows how a list of diffraction 
   patterns are generated by changing one of electron microscope controls:
   tilt in x direction.

* *si_bloch.py*: 
   demonstrates dynamic diffraction simulations by *bloch* *pyemaps* module.

* *si_csf.py*: 
   calculates and outputs structure factors using *CSF* *pyemaps* module. 

* *powder.py*: 
   calculates and plots electron powder diffraction pattern using 
   *Powder* *pyemaps* module. 

* *si_stereo.py*: 
   plots stereodiagram using *Stereo* *pyemaps* module. 

More samples code will be added as more features and releases are available. 
