Data folder and license
=======================

.. _Environment Variables:

Environment Variables
---------------------

*PYEMAPS_DATA* environment variable is set to represent pyEMAPS' data home directory.
It provides a central location for organizing your own crystal data, and it is also used 
for storing your simulation and calculation results.   

**pyEMAPS** searches crystal files in the following order when only file name is provided:

1. Current working directory. 
2. Data home directory pointed by *PYEMAPS_DATA*.

For output from **pyEMAPS** simulations and calculations, the placement order is reversed:

1. Data home directory pointed by *PYEMAPS_DATA* if it is set. 
2. Current working directory.

The layout of the pyEMAPS data home directory is as follows:

.. code-block:: console

    $(PYEMAPS_DATA)=<local directory>  # pyemaps data home, must have read and write permissions
    $(PYEMAPS_DATA)/crystals           # hosts all custom crystal data files (.xtl, .cif)
    $(PYEMAPS_DATA)/dif                # location for all kinematic diffraction simulation output
    $(PYEMAPS_DATA)/bloch              # location for all Bloch dynamic simulations images output files
    $(PYEMAPS_DATA)/stereo             # location for all stereodiagram output files
    $(PYEMAPS_DATA)/mxtal              # place for all crystal constructor output files such as *.xyz

.. note::
   
   The legacy environment variable $(PYEMAPS_CRYSTALS) is still supported if it is set.


.. _License Activation:

License Activation
------------------

There is no license requirement for many of **pyEMAPS**' base features. However, to access 
its extended features like 4DSTEM, a license activation is required. The activations in pyEMAPS can 
also be done without internet connection if isolation is desired. Finally, once license is activated,
all license checks are offline without requirement for internet connections. 

To obtain a **pyEMAPS** license:

* **Trial license**: **pyEMAPS** has a 7-days trial license that allows users to check out 
  the features without committing to a purchase. This license can also be converted or upgraded 
  to production license.

  Use the following command to get the trial license when internet connection is available:

  .. code-block:: console

   pyemaps --license trial (-l)

* **License activation token**: contact support@emlabsoftware.com for the 19 character license
  activation token. This way of activation can be used for both trial and product license
  activation online or offline.  

  .. code-block:: console

   pyemaps --license <license token> (-l)

  where <license token> is of format: XXXX-XXXX-XXXX-XXXX here X is an alphanumeric character.

  Contact support@emlabsoftware.com for obtaining a license activation token.

* **License information**: use the following command to find out if a license exists and valid.
  If so, the license information is displayed.

  .. code-block:: console

   pyemaps --license info (-l)
