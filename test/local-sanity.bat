
@echo off 
@REM basic usage
@REM ******** running this for github workflow ********

@REM        Must be run under pyemaps directory

@REM --------------  starting time --------------  
set startTime=%time%
echo Script started at %startTime%

@REM call pyemaps -s
call pyemaps -c
call pyemaps -v

echo y | call pyemaps -cp

python .\test\run_samples.py -gr all
echo Done with samples sanity tests 

python .\test\run_features.py -gr all
echo Done with features sanity tests 

python .\test\run_unittests.py -gr all
echo Done with unit tests 

call python .\test\performance\run_perf_test.py -r all
echo Done with performance tests 

@REM set return_code=%ERRORLEVEL%

@REM if %return_code%==1 (
@REM     echo ##############free package testing completed: %return_code%
@REM ) else if %return_code%==2 (
@REM     call python .\pyemaps_samples\al_dpgen.py
@REM     @REM call python .\pyemaps_samples\al_ediom.py
@REM     echo ##############Full package testing completed: %return_code%
@REM ) else if %return_code%==3 (
@REM     call python .\pyemaps_samples\al_dpgen.py
@REM     @REM call python .\pyemaps_samples\al_ediom.py
@REM     echo ##############UIUC package testing completed: %return_code%
@REM ) else (
@REM     echo ##############Unknown package testing error: %return_code%
@REM )
rm -rf pyemaps_samples

rem --------------  Capture end time -----------------
set endTime=%time%
echo Script ended at %endTime%

rem Convert the times to seconds for easier calculation
set /a startSeconds=(%startTime:~0,2%*3600) + (%startTime:~3,2%*60) + (%startTime:~6,2%)
set /a endSeconds=(%endTime:~0,2%*3600) + (%endTime:~3,2%*60) + (%endTime:~6,2%)

rem Calculate the duration in seconds
set /a duration=endSeconds-startSeconds
@REM echo simple duration at %duration%

rem Handle negative duration in case the script ran past midnight
if %duration% lss 0 set /a duration+=86400
@REM echo normalized duration at %duration%

rem Convert seconds back to hours, minutes, and seconds
set /a hours=duration/3600
set /a minutes=(duration%%3600)/60
set /a seconds=duration%%60

echo Script duration: %hours% hours %minutes% minutes %seconds% seconds
