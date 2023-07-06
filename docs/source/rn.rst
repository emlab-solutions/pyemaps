Release Notes
=============

Version 1.0.7 Stable
------------------ 

07-06-2023 
~~~~~~~~~~

New
~~~

- Anular dark field (ADF) for an experimental diffraction image. This bew feature is only
  available in full and paid package. 

Improvements
~~~~~~~~~~~~

- Bug fixes
- Updated EMC control when x-axis input is the default of (0,0,0) when pyemaps
  will calculate the value. This value is then updated in the output control for
  kinematical and dynamic diffraction simulations, as well as stereodiagram.

Version 1.0.6 Stable
------------------ 

05-27-2023 
~~~~~~~~~~

Improvements
~~~~~~~~~~~~

- Large angle CBED image generation sample code *si_lacbed.py* added.
- Bug fixes

Version 1.0.5 Stable
------------------ 

05-12-2023 
~~~~~~~~~~

New
~~~

- Large angle CBED pattern generation. 
- Calculated diffracted beams for dynamic diffraction simulation or Bloch session.

See `generateBloch <pyemaps.crystals.html#pyemaps.crystals.Crystal.generateBloch>`_
for details.

Improvements
~~~~~~~~~~~~

- Optimization in bloch image generation for multiple sample thickness.


Version 1.0.4 Stable
------------------ 

05-07-2023 
~~~~~~~~~~

Improvements
~~~~~~~~~~~~

- Incremental memory performance improvement in Bloch simulation.
- *getBeams* function folded into  
  `getSCMatrix <pyemaps.crystals.html#pyemaps.crystals.Crystal.getSCMatrix>`_ 
  as one of its return elements. See sample code *si_scm.py* for demonstration of the usage changes.
- Bug fixes.

Version 1.0.3 Stable
------------------ 

04-23-2023 
~~~~~~~~~~

Improvements
~~~~~~~~~~~~

- A major memory improvement in dynamic diffraction simulation(Bloch), 
  resulting a large performance improvement in Bloch simulation.
- Bloch simulation functions related to scattering matrix calculation 
  and its associated computations re-organized as follows:

  - `getSCMatrix <pyemaps.crystals.html#pyemaps.crystals.Crystal.getSCMatrix>`_ 
  - `getBeams <pyemaps.crystals.html#pyemaps.crystals.Crystal.getBeams>`_
  - *getEigen* function is folded into getSCMatrix call starting 
    from Stable verion 1.0.3 

  See documents for details of the changes for each functions. Also, the sample code
  *si_scm.py* shows the usage changes.

- More performance improvement are coming up, stay tuned.

Version 1.0.2 Stable
------------------ 

04-02-2023 
~~~~~~~~~~

New
~~~

In preview:

- Diffraction pattern database builder.
- :ref:`Electron diffraction pattern indexing <usage:experimental diffraction pattern indexing>`

Version 1.0.1 Stable
------------------ 

02-16-2023 
~~~~~~~~~~
Improvements
~~~~~~~~~~~~

- Bug fixes in single simulation display functions and other incremental improvements. 

  Send your suggestions and comments to support@emlabsoftware.com.


Version 1.0.0 Stable
------------------ 

02-07-2023 
~~~~~~~~~~
The first stable version!

Improvements
~~~~~~~~~~~~

- Bug fixes in dynamic diffraction simulations. The temporary file name
  collision issue discovered during some multiprocess executions is now
  fixed. We'd like to thank our users for reporting the issue. 

  Send your suggestions and comments to support@emlabsoftware.com.


Version 0.6.2 Beta
------------------ 

01-15-2023 
~~~~~~~~~~

Improvements
~~~~~~~~~~~~

- Bug fixes.
- Display function parameters naming changes to be more consistent. Specifically,
  *ishow* and *kshow* parameters are now becoming *iShow* and *kShow* as show 
  below:  

  .. code-block:: python
    
    showDif(.., iShow=True, kShow = True)

  In additional each of the display functions 
    * *showDif* 
    * *showBloch*
    * *showStereo*
  gains an optional boolean input parameter *bClose* with default of *False*.
  This input controls whether the display windows close or not after all displays are completed. 
  Default value, if not set, is *False*. In which case, users must close the display windows 
  manuallly for each display, failure to do so may result in too many display windows.  

  .. code-block:: python
    
    showBloch(.., bClose=True,..)

  Setting *bClose* to *True* is useful where the display functions are called to preventing
  too many display windows open. 

- The electronic micropscope control class - EMControl or EMC fills attributes with 
  default values if not set.  


Version 0.6.1 Beta
------------------ 

01-05-2023 
~~~~~~~~~~

Improvements
~~~~~~~~~~~~

- Bug fixes.
- Display will keep the figures windows open for each display. Users are now responsible to close them.



Version 0.6.0 Beta
------------------ 

12-11-2022 
~~~~~~~~~~

Improvements
~~~~~~~~~~~~

- Diffraction simulation result list objects `DPList <pyemaps.kdiffs.html#pyemaps.kdiffs.diffPattern>`_ and 
  `BImgList <pyemaps.ddiffs.html#pyemaps.ddiffs.BlochImgs>`_ can now be sorted by its controls objects in their builtin 
  sorting function shown in the following code snippet:

  .. code-block:: python
    
    from pyemaps import DPList

    dpl = DPList(name) 
     ....  # more code here
    # sorting the images by their associated controls
    dpl.sort()

  See sample code *si_dif.py* and *si_bloch.py* for more details on how to
  use the function and display them in the sorting order.

  For stereodiagram results where there is no builtin result objects, users
  can build a python list of control and result pair and apply python style 
  sorting on the list as follows:

  .. code-block:: python
    
    slist.sort(key=lambda x: x[0])

  Refer to *si_stereo.py*.
    
- Enhanced Bloch simulation memory management, bloch simulation exception handling
  and result accuracies.


Version 0.5.0 Beta
------------------ 

11-30-2022 
~~~~~~~~~~

Improvements
~~~~~~~~~~~~

- Documentation impreovements.
- Kinematic diffraction pattern: Kikuchi and HOLZ lines intensities 
  data added and rendered as opacities of the lines.
- More control parameters added to EMControls as optional attributes.
  See :doc:`pyemaps.emcontrols` for more details.


Version 0.4.9 Beta
------------------ 

11-26-2022 
~~~~~~~~~~

Improvements
~~~~~~~~~~~~

- Bug fixes.
- *Display* module enhancements:
    1. Added layout option of *table* format. For example, 
       showDif(dpl, ..., layout='table') will result in rendering of 
       kinematic diffraction pattern *dpl* in a m x n table format 
       where n is less or equal to 3.

       .. note:: 

          If *layout* input is ommitted or set to 'individual', the 
          functions will render each image individually in sequence 
          as before.

    2. *cShow* option is also added to the display functions to show 
       control parameters on the final figure if it is set to `True` 
       which is also the default. Otherwise, no control parameters 
       will be displayed. 

      .. note:: 

        Due to space constraints, control parameters with default values
        will be ommitted from the final rendering, even if cShow is set 
        to `True`.

    
    .. image:: https://github.com/emlab-solutions/imagepypy/raw/main/dif_table.png
        :target: https://github.com/emlab-solutions/imagepypy/raw/main/dif_table.png


Version 0.4.8 Beta
------------------ 

11-19-2022 
~~~~~~~~~~

Improvements
~~~~~~~~~~~~

- Crystal volume limit increased to 1200.
- Dynamic diffraction simulation expanded to handle larger number of 
  diffracted beams up to 5000.

  .. warning::

      The increase can result in much longer simulation time. In some cases
      with large diffracted beams numbers near the limit, it may mean 
      30 minutes or longer. The simulation time varies depending your system. 

- More build-in crystal data added because of the above expansions. Additional
  built-in crystals:

::

    'BiMnO3'
    'CoSb3_Skutterudite'
    'Pentacene'


Version 0.4.7 Beta
------------------ 
11-14-2022
~~~~~~~~~~

New
~~~

Reorganized dynamic diffraction simulation into sessions with:

1. `beginBloch <pyemaps.crystals.html#pyemaps.crystals.Crystal.beginBloch>`_. Starts a Bloch wave dynamic diffraction session.
2. `endBloch <pyemaps.crystals.html#pyemaps.crystals.Crystal.endBloch>`_. Ends a dynamic diffraction session.

These methods enable pyemaps to retain simulation in memory while preventing repeatitive computations, making
pyemaps more efficient. Dynamic simulation data can be retrieved during session include:

- `getBlochImages <pyemaps.crystals.html#pyemaps.crystals.Crystal.getBlochImages>`_. Retrieves bloch images and/or save the images into raw image files.
- `getSCMatrix <pyemaps.crystals.html#pyemaps.crystals.Crystal.getEigen>`_. Gets scattering matrix at a selected sampling point.
- `getEigen <pyemaps.crystals.html#pyemaps.crystals.Crystal.getSCMatrix>`_. Gets eigen values at a selected sampling point.
- `getBeams <pyemaps.crystals.html#pyemaps.crystals.Crystal.getBeams>`_. Retrieves diagnization Miller indexes at each sampling point.
- `printIBDetails <pyemaps.crystals.html#pyemaps.crystals.Crystal.printIBDetails>`_. Prints miscellenous data such as incidental beams and a list of sampling points etc. 

.. note::

      `generateBloch <pyemaps.crystals.html#pyemaps.crystals.Crystal.generateBloch>`_ is kept for backward compatibility purposes.
      This function is now equivalent to calling:
        
      - `beginBloch <pyemaps.crystals.html#pyemaps.crystals.Crystal.beginBloch>`_ 
      - `getBlockImages <pyemaps.crystals.html#pyemaps.crystals.Crystal.getBlockImages>`_
      - `endBloch <pyemaps.crystals.html#pyemaps.crystals.Crystal.endBloch>`_




    