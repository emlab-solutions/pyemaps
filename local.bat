@echo off

@REM CALL C:\Apps\Intel\compiler\2022.1.0\env\vars.bat intel64
@REM cd pyemaps
@REM input arguement of 
@REM "free"--------builds free package and 
@REM "all"-------- builds builds full package that includes DPGEN component.

set EMAPS_BTYPE=%1
set PACKAGE_TYPE=%2

if "%EMAPS_BTYPE%" == "" (
    echo Usage: local.bat build_type package_type
    echo        build_type: free or all
    echo        package_type: test or prod
    goto:eof
)

if "%EMAPS_BTYPE%" NEQ "free" (
    if "%1" NEQ "all" (
        echo Error: Build type incorrect, must be one of free or all
        goto:eof
    )
)

if "%PACKAGE_TYPE%" == "" (
    echo Usage: local.bat build_type package_type
    echo        build_type: free or all
    echo        package_type: test or prod
    goto:eof
)

if "%PACKAGE_TYPE%" NEQ "test" (
    if "%PACKAGE_TYPE%" NEQ "prod" (
        echo Error: Package type incorrect, must be one of test or prod
        goto:eof
    )
)


call python -m pip uninstall -y pyemaps

if "%PACKAGE_TYPE%" == "test" (
    call python build_pyemaps -t -v 3.1.2
    call python -m pip install dist\pyemaps-3.1.2-cp37-cp37m-win_amd64.whl
    @REM echo got here after test package build
) else (
    call python build_pyemaps -v 1.0.1
    call python -m pip install dist\pyemaps-1.0.1-cp37-cp37m-win_amd64.whl
    @REM echo got here after production package build
)


set typename=%EMAPS_BTYPE%
if "%EMAPS_BTYPE%" == "all" (
    set typename=full
)
set packname=%PACKAGE_TYPE%
if "%PACKAGE_TYPE%" == "prod" (
    set packname=production
)
echo.
echo.
echo ##############################################
echo %typename% %packname% package build completed
echo ##############################################
echo.
echo.