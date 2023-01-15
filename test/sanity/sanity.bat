@REM basic usage
call python -m pyemaps -s
call python -m pyemaps -c
call python -m pyemaps -v

if "%1"=="local" (
    echo n | call python -m pyemaps -cp
    call python .\si_csf.py
    call python .\powder.py
    call python .\si_dif.py
    call python .\si_bloch.py
    python .\import_calc_sanity 
) else (
    echo y | call python -m pyemaps -cp
    call python .\pyemaps_samples\si_csf.py
    call python .\pyemaps_samples\powder.py
    call python .\pyemaps_samples\si_dif.py
    call python .\pyemaps_samples\si_bloch.py
    call python .\pyemaps_samples\si_rawblochimgs.py
    call python .\pyemaps_samples\si_constructor.py
    call python .\pyemaps_samples\si_stereo.py
    call python .\pyemaps_samples\si_scm.py
    python test\sanity\feature_sanity.py
    @REM EMC SIMC class basic function tests
     python test\unittests\emc\test1.py
    rm -rf pyemaps_samples
)