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

set "Ver=1.0.0"

if "%~1"=="" (
    echo Usage: local.bat [version]
    echo        version: N.N.N where N is any numberal, default to 1.0.0
    @REM goto:eof
) else (
    set "Ver=%~1"
    echo got here and value: "%Ver%"
)

echo pyEMAPS version to be built: "%Ver%"

@REM -------------Uninstalling existing pyEMAPS package----------------
call python -m pip uninstall -y pyemaps

set whl_fname=''
set batch_dir=%~dp0

@REM -------------Build without using EMLab Pypi package repsitory for versions--------------
@REM Use this script to build pyEMAPS for your own pyEMAPS package or for testing

for /f "tokens=1,2 delims=:" %%i in ('python "%batch_dir%build_pyemaps" -v "%Ver%"') do (
        if "%%i"=="wheel file name" set whl_fname=%%j
    )

echo Built wheel file directory: "%batch_dir%"
echo Built wheel file directory: "%whl_fname%"
echo Built wheel file name from python: "%batch_dir%%whl_fname%"
@REM call pip install "%batch_dir%%whl_fname%" --user

echo ###################################################
echo %PYPIREPO% repository package build completed
echo ###################################################
