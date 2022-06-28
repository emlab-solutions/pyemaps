@REM basic usage
call python -m pyemaps -s
call python -m pyemaps -c
call python -m pyemaps -v
call python -m pyemaps -cp


@REM calculation and cif/xtl import tests
python .\import_calc_sanity 

@REM samples sanity tests
call python .\pyemaps_samples\si_csf.py
call python .\pyemaps_samples\powder.py
call python .\pyemaps_samples\si_tilt.py
call python .\pyemaps_samples\si_deflection.py
call python .\pyemaps_samples\si_zone.py
call python .\pyemaps_samples\si_vt.py
call python .\pyemaps_samples\si_cl.py
