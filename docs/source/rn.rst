Release Notes
=============

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


Version 0.6.0 Beta
------------------ 

12-11-2022 
~~~~~~~~~~

Improvements
~~~~~~~~~~~~

- Diffraction simulation result list objects: 
  - `DPList <pyemaps.kdiffs.html#pyemaps.kdiffs.diffPattern>`_ and 
  - `BImgList <pyemaps.ddiffs.html#pyemaps.ddiffs.BlochImgs>`_ 
    can now be sorted by its controls objects in their builtin 
    sorting function shown as following code snippet:

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
