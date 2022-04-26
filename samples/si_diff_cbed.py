
def run_si_sample_cbed():
    #import Crystal class from pyemaps as cryst
    from pyemaps import Crystal as cryst

    # create a crystal class instance and load it with builtin silican data
    si = cryst.from_builtin('silicon')
    # print(si)

    # run diffraction on the crystal instance with all default controls
    # parameters
    si_dp2 = si.gen_diffPattern(mode=2, dsize=0.16)
    # print(si_dp2)

    #plot and show the pattern just generated using pyemaps built-in plot function
    si_dp2.plot(mode = 2)

if __name__ == '__main__':
    run_si_sample_cbed()