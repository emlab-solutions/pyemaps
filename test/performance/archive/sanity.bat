
@echo off 
@REM basic usage
@REM --------------  starting time --------------  
set startTime=%time%
echo Script started at %startTime%

call python -m pyemaps -s
call python -m pyemaps -c
call python -m pyemaps -v

echo y | call python -m pyemaps -cp
call python .\pyemaps_samples\si_csf.py
call python .\pyemaps_samples\si_dif.py
call python .\pyemaps_samples\si_bloch.py
call python .\pyemaps_samples\si_lacbed.py
@REM call python .\pyemaps_samples\si_rawblochimgs.py
call python .\pyemaps_samples\si_constructor.py
call python .\pyemaps_samples\si_stereo.py
call python .\pyemaps_samples\si_scm.py
python test\sanity\feature_sanity.py

@REM performance test - all includes all types: dif, bloch and stereo
call python test\sanity\run_perf_test.py -r all
@REM unit test: EMC SIMC class basic function tests
call python test\unittests\emc\test1.py
call python test\unittests\kdif\sanity_doc.py
call python test\unittests\bloch\si_bloch_docs.py
call python test\unittests\bloch\disk_size.py

call python .\pyemaps_samples\powder.py
@REM echo before wrror level: %ERRORLEVEL%
call python test\unittests\package_test\type_test.py
@REM echo after wrror level: %ERRORLEVEL%
set return_code=%ERRORLEVEL%

if %return_code%==1 (
    echo ##############free package testing completed: %return_code%
) else if %return_code%==2 (
    call python .\pyemaps_samples\al_dpgen.py
    call python .\pyemaps_samples\al_ediom.py
    echo ##############Full package testing completed: %return_code%
) else if %return_code%==3 (
    call python .\pyemaps_samples\al_dpgen.py
    call python .\pyemaps_samples\al_ediom.py
    echo ##############UIUC package testing completed: %return_code%
) else (
    echo ##############Unknown package testing error: %return_code%
)
rm -rf pyemaps_samples

rem --------------  Capture end time -----------------
set endTime=%time%
echo Script ended at %endTime%

rem Convert the times to seconds for easier calculation
set /a startSeconds=(%startTime:~0,2%*3600) + (%startTime:~3,2%*60) + (%startTime:~6,2%)
set /a endSeconds=(%endTime:~0,2%*3600) + (%endTime:~3,2%*60) + (%endTime:~6,2%)

rem Calculate the duration in seconds
set /a duration=endSeconds-startSeconds

rem Handle negative duration in case the script ran past midnight
if %duration% lss 0 set /a duration+=86400

rem Convert seconds back to hours, minutes, and seconds
set /a hours=duration/3600
set /a minutes=(duration%%3600)/60
set /a seconds=duration%%60

echo Script duration: %hours% hours %minutes% minutes %seconds% seconds