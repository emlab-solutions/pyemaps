@echo off

@REM CALL C:\Apps\Intel\compiler\2022.1.0\env\vars.bat intel64
@REM cd pyemaps
@REM input arguement of 

set PYPIREPO=%1
@REM set PACKAGE_TYPE=%2
@REM set DEBUG_TYPE=%3

if "%PYPIREPO%" == "" (
    echo Usage: local.bat pypi_repo_type
    echo        pypi_repo_type: test or public
    echo        test: upload package testpypi.org repos
    echo        prod: upload package pypi.org repos for public download
    goto:eof
)

@REM if "%EMAPS_BTYPE%" NEQ "free" (
@REM     if "%1" NEQ "full" (
@REM         if "%1" NEQ "uiuc" (
@REM             echo Error: Build type incorrect, must be one of free or all
@REM             goto:eof
@REM         )
@REM     )
@REM )

@REM if "%PACKAGE_TYPE%" == "" (
@REM     echo Usage: local.bat build_type package_type [debug]
@REM     echo        build_type: free or all
@REM     echo        package_type: test or prod
@REM     goto:eof
@REM )

@REM if "%PACKAGE_TYPE%" NEQ "test" (
@REM     if "%PACKAGE_TYPE%" NEQ "prod" (
@REM         echo Error: Package type incorrect, must be one of test or prod
@REM         goto:eof
@REM     )
@REM )

@REM if "%DEBUG_TYPE%" == "debug" (
@REM     echo debug build set in batch
@REM     set PYEMAPS_DEBUG=1
@REM ) else (
@REM     echo not a build set in batch
@REM     set PYEMAPS_DEBUG=0
@REM )

call python -m pip uninstall -y pyemaps

@REM if "%PYPIREPO%" == "test" (
@REM     call python build_pyemaps -t -v 3.1.3
@REM     call python -m pip install dist\pyemaps-3.1.3-cp37-cp37m-win_amd64.whl
@REM     @REM echo got here after test package build
@REM ) else (
@REM     call python build_pyemaps -v 1.0.7
@REM     call python -m pip install dist\pyemaps-1.0.7-cp37-cp37m-win_amd64.whl
@REM     @REM echo got here after production package build
@REM )

set whl_fname=''
set batch_dir=%~dp0
if "%PYPIREPO%" == "test" (
    @REM capture the wheel file name and path dynamically
    for /f "tokens=1,2 delims=:" %%i in ('python "%batch_dir%build_pyemaps" -t') do (
        if "%%i"=="wheel file name" set whl_fname=%%j
    )
) else (
    @REM capture the wheel file name and path dynamically
    for /f "tokens=1,2 delims=:" %%i in ('python "%batch_dir%build_pyemaps"') do (
        if "%%i"=="wheel file name" set whl_fname=%%j
    )
)

echo Captured wheel file name from python: "%batch_dir%%whl_fname%"
call pip install "%batch_dir%%whl_fname%"

@REM @REM set default as free package
@REM set typename=free   

@REM if "%EMAPS_BTYPE%" == "full" (
@REM     set typename=full
@REM )
@REM if "%EMAPS_BTYPE%" == "uiuc" (
@REM     set typename=uiuc
@REM )

@REM @REM set default package as test package
@REM set packname=test
@REM if "%PYPIREPO%" == "public" (
@REM     set packname=public
@REM )
@REM echo.
@REM echo.


@REM if "%PYPIREPO%" == "test" (
echo ###################################################
echo %PYPIREPO% repository package build completed
echo ###################################################
@REM )else (
@REM     echo ##############################################
@REM     echo %typename% %packname% package build completed
@REM     echo ##############################################
@REM )
@REM echo.
@REM echo.