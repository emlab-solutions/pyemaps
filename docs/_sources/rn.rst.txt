Release Notes
=============

Version 1.1.1 Stable
-------------------- 

11-02-2024 
~~~~~~~~~~

What's New?
~~~~~~~~~~~~

**License activation** of 4DSTEM features added. While many features remained free without license.
See the section on license activation :ref:`License Activation` for more details. 

New **4DSTEM** module and its sub-modules. Importing the new 4DSTEM module as follows:
   
.. code-block:: console

  from pyemaps import stem4d

where stem4d functions are organized into two submodules called *ediom* and *send*:

* *ediom*: electron diffraction indexing and oriention mapping. currently,
  this module contains the diffraction indexing. 
  
  * `Experimental diffraction pattern indexing <modules.html#pyemaps.stackimg.StackImage.indexImage>`_

  Orientan mapping will be added to ediom later.
  
* *send*: scanning electronic nano-diffraction. This module now has the following functions:

  * `Annular bright or darkfield <modules.html#pyemaps.stackimg.StackImage.generateBDF>`_.
  * `Masked images <modules.html#pyemaps.stackimg.StackImage.generateMaskedImage>`_.

To import these two modules, use the follwoing code:

.. code-block:: console

  from pyemaps import ediom
  from pyemaps import send

Both modules will share some common values in its parent module *stem4d*.

Improvements
~~~~~~~~~~~~

* Simplified pyEMAPS command line from:

.. code-block:: console

  pyemaps -m pyemaps [options]

to:

.. code-block:: console

  pyemaps [options]

Version 1.0.9 Stable
-------------------- 

05-29-2024 
~~~~~~~~~~

Improvements
~~~~~~~~~~~~

* Bug fixes for image display. Now all displays are utilizing Matplotlib's Tkinter backend.
* Expanded pyemaps build guide.

Version 1.0.8 Stable
-------------------- 

11-07-2023 
~~~~~~~~~~

New
~~~

- Separated pyemaps simulations backend into standalone python package.
- pyemaps package installation automatically installs backend python package. 
  as one of its depedencies. 
- Made pyemaps source code ready for open source and community contribution. 
  We invite you to become pyemaps contributor, contact support@emlabsoftware.com
  for further information.

Improvements
~~~~~~~~~~~~

- Bug fixes related to DigitalMicrograph (DM) integration and added DM python 
  script sample code, as shown in :ref:`Rendering by Third Party Tools <thirdparty>`




    