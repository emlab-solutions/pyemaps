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
    python test\sanity\import_calc_sanity
    rm -rf pyemaps_samples
)