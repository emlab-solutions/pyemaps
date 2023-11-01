import numpy as np
import DigitalMicrograph as DM

from pyemaps import Crystal as cr
from pyemaps import XMAX, YMAX
#----diffraction patterns generated by these bounds
#   [-XMAX, XMAX, -YMAX, YMAX]

#    screen size multiplier of diff bounds
mult = 4

#simple diffraction mode lookup
DIFF_MODE = ('Normal', 'CBED')
#------Diffraction modes-------
#       1 - normal
#       2 - CBED
def addline( x1, y1, x2, y2): 
    '''
    reserved for later use
    '''
    xx1, yy1, xx2, yy2 = x1*2, y1*2, x2*2, y2*2
    dmline = DM.NewLineAnnotation(xx1, yy1, xx2, yy2)
    
    dmline.SetResizable(False)
    dmline.SetMovable(False)
    dmline.SetDeletable(False)
    dmline.SetForegroundColor(0,1,0)
    dmline.SetBackgroundColor(0.2,0.2,0.5)
    
    return dmline


def adddisk( x1, y1, r, indx): 
    '''
    reserved for later use
    '''
    xx1, yy1, rr = x1*2, y1*2, r*2
    dmdisk = DM.NewOvalAnnotation()
    dmdisk.SetCircle(xx1-r,yx1-r, xx1+rr,yy1+r)
    dmdisk.SetLabel(indx)

    return dmdisk

    
def SetCommonProp(comp):
    '''
    Setting common attributes of the line and circle annotation components
    '''
    comp.SetResizable(False)
    comp.SetMovable(False)
    comp.SetDeletable(False)
    
def show_diffract(dp, md=1, name = 'Diamond'):
    #transform the plotting area based on pyemaps diffraction dimensions:
    # XMAX
    # YMAX
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
      
      
def run_si_dm_sample():  
    from pyemaps import EMC
    #-----------load crystal data into a Crystal class object-----------------
    name = 'Silicon'
    si = cr.from_builtin(name)

    #-----------content of the crystal data-----------------------------------
    print(si)
    
    #-----------generate diffraction pattern in CBED mode--------------------- 
    emc = EMC(tilt=(-0.2, 0.5), zone=(1,-1,2))
    
    mode = DIFF_MODE.index('CBED')+1
    _, si_dp_cbed = si.generateDP(mode = mode, dsize = 0.2, em_controls=emc)

    #-----------Plot the pattern in DM----------------------------------------
    show_diffract(si_dp_cbed, md = mode, name = name)


    #-----------generate diffraction pattern in normal mode-------------------
    _, si_dp = si.generateDP()
    #print(si_dp)

    #-----------content of the crystal data-----------------------------------
    show_diffract(si_dp, name = name)

      
def run_si_dm_bloch():  
    from pyemaps import EMC
    #-----------load crystal data into a Crystal class object-----------------
    name = 'ErbiumPyrogermanate'
    ep = cr.from_builtin(name)

    #-----------content of the crystal data-----------------------------------
    print(ep)
    
    #-----------generate diffraction pattern in CBED mode--------------------- 
    emc = EMC(tilt=(-0.2, 0.5), zone=(1,-1,2))
    
    try:
        _ = ep.generateBloch()

    except Exception as e:
        print(f'Error running dynamic diffraction simuation for {name}')
    #-----------Plot the pattern in DM----------------------------------------
    import os
    imgpath = os.environ.get('PYEMAPS_DATA')
    imgf = os.path.join(imgpath, 'bloch')

    print(f'Generate image file is located at: {imgf}')
    #-----------content of the crystal data-----------------------------------
    # show_diffract(si_dp, name = name)

if __name__ == '__main__'
    run_si_dm_sample()
    run_si_dm_bloch()
