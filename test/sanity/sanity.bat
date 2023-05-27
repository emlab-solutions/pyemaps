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
    call python .\pyemaps_samples\si_lacbed.py
    call python .\pyemaps_samples\si_rawblochimgs.py
    call python .\pyemaps_samples\si_constructor.py
    call python .\pyemaps_samples\si_stereo.py
    call python .\pyemaps_samples\si_scm.py
    call python .\pyemaps_samples\si_dpgen.py
    call python .\pyemaps_samples\al_ediom.py
    python test\sanity\feature_sanity.py
    @REM performance test - all includes all types: dif, bloch and stereo
     python test\sanity\run_perf_test.py -r all
    @REM unit test: EMC SIMC class basic function tests
     python test\unittests\emc\test1.py
     python test\unittests\package_test\type_test.py
     python test\unittests\kdif\sanity_doc.py
     python test\unittests\bloch\si_bloch_docs.py
     python test\unittests\bloch\disk_size.py
    rm -rf pyemaps_samples
)