@echo off

set PYPIREPO=%1

if "%PYPIREPO%" == "" (
    echo Usage: local.bat pypi_repo_type
    echo        pypi_repo_type: test or prod
    echo        test: upload package testpypi.org repos
    echo        prod: upload package pypi.org repos for public download
    goto:eof
)

call python -m pip uninstall -y pyemaps

set whl_fname=''
set batch_dir=%~dp0
if "%PYPIREPO%" == "test" (
    
    for /f "tokens=1,2 delims=:" %%i in ('python "%batch_dir%build_pyemaps" -t') do (
        if "%%i"=="wheel file name" set whl_fname=%%j
    )
) else (
    
    for /f "tokens=1,2 delims=:" %%i in ('python "%batch_dir%build_pyemaps"') do (
        if "%%i"=="wheel file name" set whl_fname=%%j
    )
)

echo Captured wheel file name from python: "%batch_dir%%whl_fname%"
call pip install "%batch_dir%%whl_fname%"


@REM if "%PYPIREPO%" == "test" (
echo ###################################################
echo %PYPIREPO% repository package build completed
echo ###################################################
