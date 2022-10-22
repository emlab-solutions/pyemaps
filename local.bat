@REM CALL C:\Apps\Intel\compiler\2022.1.0\env\vars.bat intel64
@REM cd pyemaps
python -m pip uninstall -y pyemaps
python build_pyemaps -c all -t
@REM python -m pip uninstall pyemaps
python -m pip install dist\pyemaps-3.1.2-cp37-cp37m-win_amd64.whl
python samples\si_scm.py