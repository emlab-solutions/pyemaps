@REM basic usage
call python -m pyemaps -s
call python -m pyemaps -c
call python -m pyemaps -v

python .\import_calc_sanity 

if "%1"=="local" (
    echo n | call python -m pyemaps -cp
    call python .\si_csf.py
    call python .\powder.py
    call python .\si_tilt.py
    call python .\si_deflection.py
    call python .\si_zone.py
    call python .\si_vt.py
    call python .\si_cl.py
    goto:eof
) else (
    echo y | call python -m pyemaps -cp
    call python .\pyemaps_samples\si_csf.py
    call python .\pyemaps_samples\powder.py
    call python .\pyemaps_samples\si_tilt.py
    call python .\pyemaps_samples\si_deflection.py
    call python .\pyemaps_samples\si_zone.py
    call python .\pyemaps_samples\si_vt.py
    call python .\pyemaps_samples\si_cl.py
    rm -rf pyemaps_samples
)