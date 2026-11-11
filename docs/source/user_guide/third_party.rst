.. _thirdparty:

Using results in other tools
============================


pyEMAPS kinematic diffraction simulation results are captured by 
:py:obj:`DP or diffPattern <pyemaps.kdiffs.diffPattern>` class:

.. code-block:: python
    
    from pyemaps import Crystal as cr
    
    si = cr.from_builtin('Silicon')

    _, dp = si.generateDP()

    dp.klines   # Kikuchi lines list
    dp.nklines  # number of Kikuchi lines, same as len(dp.klines)
    dp.disks    # diffracted beams list
    dp.ndisks   # number of diffracted beams, same as len(dp.disks)
    dp.hlines   # HOLZ lines list
    dp.nklines  # number of HOLZ lines, same as len(dp.hlines)

where dp.klines is a python list of :py:obj:`Line class <pyemaps.kdiffs.Line>` 
objects and dp.disks of :py:obj:`Disk class <pyemaps.kdiffs.Disk>` objects 
and so on. Each of the objects is accessible for its own data such as points when plotting.

Below is an example of rendering a diffraction pattern generated for *Diamond* builtin crystal
in DigitalMicrograph:

.. note::
    For complete python script integrating pyEMAPS into DM, see *si_stereo.py* in samples directory.

.. code-block:: python

    def show_diffract(dp, md=1, name = 'Diamond'):
        from pyemaps import XMAX, YMAX
        import DigitalMicrograph as DM

        shape = (2*XMAX*mult,2*YMAX*mult)

        #A new image from numpy array and initilize it to black background
        dif_raw = np.ones((shape), dtype = np.float32)
        dif_raw[:,:] = 255.0

        #DM create the image
        dm_dif_img = DM.CreateImage(dif_raw)
        dif_img = dm_dif_img.ShowImage()
        dif_img_disp = dm_dif_img.GetImageDisplay(0)
        
        #validate diffraction mode
        if md <1 or md > 2:
            print(f'diffraction mode provided {md} not supported')
            return 1
        
        #set image title
        img_title = str(f'Kinematic Diffraction Simulation:  {name} in {DIFF_MODE[md-1]} Mode')
        dm_dif_img.SetName(img_title)

        #plotting Kikuchi and HOLZ lines and spots as DM components
        num_klines = dp.nklines
        
        if num_klines > 0:
            klines = dp.klines
            for kl in klines:        
                x1,y1,x2,y2, inten = kl #inten: intensity
                
                xx1, yy1, = (x1+ XMAX)*mult,(y1 + YMAX)*mult 
                xx2, yy2  = (x2 + XMAX)*mult,(y2 + YMAX)*mult
                
                kline = dif_img_disp.AddNewComponent(2, xx1, yy1, xx2, yy2)
                
                SetCommonProp(kline)
                
                if inten/5 > 0.8:
                    kline.SetForegroundColor(0.3, 0.3, 0.3) # dark grey
                elif inten/5 > 0.6:
                    kline.SetForegroundColor(0.6, 0.6, 0.6)
                elif inten/5 > 0.4:
                    kline.SetForegroundColor(0.8, 0.8, 0.8)
                else:
                    kline.SetForegroundColor(0.9, 0.9, 0.9) # light grey
                kline.SetBackgroundColor(0.2,0.2,0.5)# dark blue

        num_disks = dp.ndisks
        
        if num_disks > 0:
            disks = dp.disks
            for d in disks:
                x1, y1, r, i1, i2, i3 = d
                xx, yy, rr = (x1 + XMAX)*mult, (y1 + YMAX)*mult, r*mult
                            
                idx = '{:d} {:d} {:d}'.format(i1,i2,i3)
                
                disk = dif_img_disp.AddNewComponent(6, xx-rr, yy-rr, xx+rr, yy+rr)
                
                SetCommonProp(disk)
                disk.SetForegroundColor(0.0,0.0,1.0) # blue
                disk.SetBackgroundColor(0.5,0.5,0.75)# dark blue
                if md == 1:
                    disk.SetFillMode(1)
                else:
                    disk.SetFillMode(2)
            
                # a bit tricky to figure out the index location, has to use
                # the proxy component indxannot0 first. 
                indxannot0 = DM.NewTextAnnotation(0, 0, idx, 10)
                
                t, l, b, r = indxannot0.GetRect()
                w = r-l
                h = b-t
                
                nl = xx - ( w / 2)
                # nr = xx + ( w / 2)
                nt = yy -rr - h if md ==1 else yy - (h / 2)
                # nb = yy + rr + h if md == 1 else yy + (h / 2)
                
                indxannot = DM.NewTextAnnotation(nl, nt, idx, 10)
                
                dif_img_disp.AddChildAtEnd(indxannot)
                SetCommonProp(indxannot)
                indxannot.SetForegroundColor(0.9,0,0) #light red
                indxannot.SetBackgroundColor(1,1,0.5)
                
        if md == 2:
            num_hlines = dp.nhlines
            
            if num_hlines > 0 :
            
                hlines = dp.hlines
                for hl in hlines:
                
                    x1, y1, x2, y2, inten = hl
                    xx1, yy1 = (x1 + XMAX)*mult, (y1 + YMAX)*mult 
                    xx2, yy2 = (x2 + XMAX)*mult, (y2 + YMAX)*mult
                    
                    hline = dif_img_disp.AddNewComponent(2, xx1, yy1, xx2, yy2)
                    SetCommonProp(hline)
                    
                    if inten/5 > 0.8:
                        hline.SetForegroundColor(0.1,0.7,0.3) # dark grey
                    elif inten/5 > 0.6:
                        hline.SetForegroundColor(0.1,0.7,0.6)
                    elif inten/5 > 0.4:
                        hline.SetForegroundColor(0.1,0.7,0.8)
                    else:
                        hline.SetForegroundColor(0.1,0.7,0.9) # light grey
                    
        del dm_dif_img
        return 0        

where *dp* is the kinematic diffraction pattern generated from generateDP call.

.. note:: 

    To get the above display work in *DM*, *pyEMAPS* must be installed in *DM*'s 
    python environment.

Dynamic Diffraction Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The output from bloch dynamic diffraction simulation is an array of 2 or 3 dimensional floating
numbers representing image intensities, depending on whether one or multiple slices of 
dynamic diffraction images are generated. 

**pyEMAPS** provides an option for users to save the images as raw image files that
can be imported into ImageJ or DigitalMicrograph. Refer to 
:py:obj:`generateBloch <pyemaps.crystals.Crystal.generateBloch>` or
:py:obj:`getBlochImages <pyemaps.crystals.Crystal.getBlochImages>` for
details.

Below is a visualization of a raw bloch images files saved from a pyEMAPS dynamic simulation
run in Digita;Micrograph. The raw image contains 10 images each at a sample thickness 
range betwwen 0 and 1000.

.. image:: /_static/images/bloch_3d_dm.png
