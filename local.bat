@REM # '''
@REM # This file is part of pyemaps
@REM # ___________________________

@REM # pyemaps is free software for non-comercial use: you can 
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

@REM # '''
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
