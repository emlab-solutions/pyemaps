"""

An example of using pyemaps crystal and diffraction modules to 
1) create a crystal from built-in data for Silicon 
2) generate kinematical diffraction patterns
3) display the diffraction pattern using pyemaps's built-in plot function 

Usage:
a) install pyemaps diffraction and crystal modules:
    pip install pyemaps
b) run  
    python si_diff.py

"""
def run_si_sample():
    #import Crystal class from pyemaps as cryst
    from pyemaps import Crystal as cryst

    # create a crystal class instance and load it with builtin silican data
    si = cryst.from_builtin('silicon')

    # run diffraction on the crystal instance with all default controls
    # parameters
    si_dp = si.gen_diffPattern()

    #plot and show the pattern just generated using pyemaps built-in plot function
    si_dp.plot()