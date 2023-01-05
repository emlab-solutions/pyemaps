python -m pip uninstall -y pyemaps
python build_pyemaps -nb -u
@REM python -m pip uninstall pyemaps
python -m pip install dist\pyemaps-3.1.2-cp37-cp37m-win_amd64.whl
@REM python samples\si_scm.py