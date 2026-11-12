@REM # '''
@REM # This file is part of pyemaps
@REM # ___________________________

@REM # pyemaps is free software: you can 
@REM # redistribute it and/or modify it under the terms of the GNU General 
@REM # Public License as published by the Free Software Foundation, either 
@REM # version 3 of the License, or (at your option) any later version.

@REM # pyemaps is distributed in the hope that it will be useful,
@REM # but WITHOUT ANY WARRANTY; without even the implied warranty of
@REM # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
@REM # GNU General Public License for more details.

@REM # You should have received a copy of the GNU General Public License
@REM # along with pyemaps.  If not, see <https://www.gnu.org/licenses/>.

@REM # Contact supprort@emlabsoftware.com for any questions and comments.
@REM # ___________________________


@REM # Author:             EMLab Solutions, Inc.
@REM # Date Created:       May 07, 2022  


@REM -------------Build using EMLab Pypi package repsitory for versions--------------
@REM For EMLab Solutions build for publishing in pypi repository 
@REM if you are making a local build, please use build.bat instead 

@REM # '''
@echo off
setlocal enabledelayedexpansion

@REM local.bat pypi_repo_type [version]
@REM   pypi_repo_type: test (test.pypi.org numbering) or prod (pypi.org numbering)
@REM   version       : optional explicit version, e.g. 2.0.0. Without it, build_pyemaps
@REM                   takes the newest version on that PyPI and adds one.

set "PYPIREPO=%~1"
set "BUILD_VERSION=%~2"

if "%PYPIREPO%" NEQ "test" if "%PYPIREPO%" NEQ "prod" goto usage

set "BUILD_ARGS="
if "%PYPIREPO%" == "test" set "BUILD_ARGS=-t"
if "%BUILD_VERSION%" NEQ "" (
    echo %BUILD_VERSION%| findstr /r "^[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*$" >nul
    if errorlevel 1 (
        echo Error: the version must look like 2.0.0: %BUILD_VERSION%
        exit /b 1
    )
    set "BUILD_ARGS=!BUILD_ARGS! -v %BUILD_VERSION%"
)

call python -m pip uninstall -y pyemaps

set "whl_fname="
set "batch_dir=%~dp0"
for /f "tokens=1,2 delims=:" %%i in ('python "%batch_dir%build_pyemaps" %BUILD_ARGS%') do (
    if "%%i"=="wheel file name" set "whl_fname=%%j"
)

if not defined whl_fname (
    echo Error: pyemaps build FAILED, see the errors above
    exit /b 1
)
if not exist "%batch_dir%%whl_fname%" (
    echo Error: the wheel "%batch_dir%%whl_fname%" does not exist
    exit /b 1
)

echo Captured wheel file name from python: "%batch_dir%%whl_fname%"
call python -m pip install "%batch_dir%%whl_fname%"
if errorlevel 1 (
    echo pyemaps install FAILED
    exit /b 1
)

echo ###################################################
echo %PYPIREPO% repository package build completed: %whl_fname%
echo ###################################################
exit /b 0

:usage
echo Usage: local.bat pypi_repo_type [version]
echo        pypi_repo_type: test or prod
echo        test: version numbering from test.pypi.org
echo        prod: version numbering from pypi.org
echo        version: explicit version, e.g. 2.0.0
exit /b 1
