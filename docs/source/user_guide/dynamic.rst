Dynamic diffraction (Bloch wave)
================================

To simplify, we will call this simulation as Bloch or Bloch simulation throughout this help
document.

.. code-block:: python

    from pyemaps import Crystal as cr        # Crystal class
    from pyemaps import BImgList             # Dynamic diffraction image list class
    from pyemaps import showBloch            # Builtin visualization helper function

    if __name__ == '__main__':
        # create a crystal class object and load it with builtin silicon data
        c_name = 'Silicon'
        si = cr.from_builtin(c_name)

        # Generate dynamic diffraction patterns using pyEMAPS' bloch module
        # with all other default parameters except sampling
        try:
            bloch_imgs_list = si.generateBloch(sampling = 20)

        except Exception as e:
            print(f'Error: {e}')

        else:
            showBloch(bloch_imgs_list)               # grey color map
            showBloch(bloch_imgs_list, bColor=True)  # with predefined color map
   
The crystal method *generateBloch* starts a Bloch wave dynamic diffraction simulation with 
the sampling resolution of 20 pixels along the disk radius. 

For a complete set of controls and input parameters for the Bloch simulation, 
go to :py:obj:`generateBloch <pyemaps.crystals.Crystal.generateBloch>`  

Pyemaps also provides a helper class :py:obj:`BImgList <pyemaps.ddiffs.BlochImgs>`
and an image rendering method *showBloch* in :py:mod:`display module <pyemaps.display>` 
visualizing the Bloch simulation results.

.. note::

   To generate multiple images with a specified range of sample thickness 
   and save them in raw image data file. See the description of :py:obj:`generateBloch method <pyemaps.crystals.Crystal.generateBloch>`. 
   
   The raw image data file can be imported into third party visualization tools
   such as `ImageJ <https://imagej.nih.gov/ij/>`_ and 
   `DigitalMicrograph <https://www.gatan.com/products/tem-analysis/gatan-microscopy-suite-software>`_. 

.. note::

   To start a Bloch simulation session and retrieve the scattering matrix 
   and other dynamic diffraction session information, see :py:obj:`getSCMatrix method <pyemaps.crystals.Crystal.getSCMatrix>`  
   between :py:obj:`beginBloch <pyemaps.crystals.Crystal.beginBloch>` and 
   :py:obj:`endBloch calls <pyemaps.crystals.Crystal.endBloch>`.

See :doc:`crystals` for the built-in crystals you can simulate.

Displaying a series of images
-----------------------------

Below is another example of using *pyEMAPS* builtin display functions
to render Bloch simulation images for *silicon* with:

::

    zone=(1,1,1) 
    hight voltage vt=100
    sample thickness = (500, 1750, 250)
    (starting at 500, ending at 1750 with an increment of 250)
    sampling points: 40

.. image:: https://github.com/emlab-solutions/imagepypy/raw/main/bloch_table.png
    :target: https://github.com/emlab-solutions/imagepypy/raw/main/bloch_table.png

.. code-block:: python

    from pyemaps import EMC, DEF_CBED_DSIZE

    MAX_PROCWORKERS = 4

    def generate_bloch_images(name = 'Silicon', dsize = DEF_CBED_DSIZE, ckey = 'tilt'):
        
        from pyemaps import Crystal as cryst
        from pyemaps import SIMC

        cr = cryst.from_builtin(name)
        
        vt = 100
        sth = (500, 1750, 250)
        simc = SIMC(excitation=(0.3,1.0), bmin=0.1)
    
        try:
            bimgs = cr.generateBloch(sampling = 40,
                                    em_controls = EMC(zone=(1,1,1),
                                    vt=vt,
                                    cl=1000,
                                    simc=simc),
                                    sample_thickness = sth
                                    )
        except Exception as e:
                print(f'Generated an exception: {e}') 
                return None
                
        bimgs.sort()
        return bimgs 

    if __name__ == '__main__':
        
        from pyemaps import showBloch

        imgs = generate_bloch_images()
        if imgs is not None:
            showBloch(imgs, cShow=True, layout='table', bSave = True)
