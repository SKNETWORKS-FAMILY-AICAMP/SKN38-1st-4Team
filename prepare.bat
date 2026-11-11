@echo off
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
set "UV_CACHE_DIR=%CD%\.uv-cache"
set "UV_PYTHON_INSTALL_DIR=%CD%\.python"
echo [1/3] Checking Python environment...
if not exist ".venv\Scripts\python.exe" goto findpython
".venv\Scripts\python.exe" -c "import sys; assert sys.version_info >= (3, 10)" >nul 2>nul
if not errorlevel 1 goto packages
:findpython
echo Repairing project Python environment...
where py >nul 2>nul
if errorlevel 1 goto knownpython
py -3 -m venv .venv
if not errorlevel 1 goto packages
:knownpython
for %%V in (314 313 312 311 310) do (
    if exist "%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe" (
        "%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe" -m venv .venv
        if not errorlevel 1 goto packages
    )
)
where python >nul 2>nul
if errorlevel 1 goto useuv
python -m venv .venv
if not errorlevel 1 goto packages
:useuv
set "CHIMCHAK_UV=uv"
where uv >nul 2>nul
if not errorlevel 1 goto uvcreate
set "CHIMCHAK_UV=%USERPROFILE%\.local\bin\uv.exe"
if not exist "%CHIMCHAK_UV%" goto failed
:uvcreate
"%CHIMCHAK_UV%" venv --allow-existing --python 3.12 .venv
if errorlevel 1 goto failed
:packages
echo [2/3] Checking Streamlit dependencies...
".venv\Scripts\python.exe" -c "import streamlit, pandas, pydeck, altair, streamlit_js_eval" >nul 2>nul
if not errorlevel 1 goto validate
".venv\Scripts\python.exe" -m ensurepip --upgrade
if errorlevel 1 goto uvpackages
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if not errorlevel 1 goto validate
:uvpackages
set "CHIMCHAK_UV=uv"
where uv >nul 2>nul
if not errorlevel 1 goto installuv
set "CHIMCHAK_UV=%USERPROFILE%\.local\bin\uv.exe"
if not exist "%CHIMCHAK_UV%" goto failed
:installuv
"%CHIMCHAK_UV%" pip install --python .venv\Scripts\python.exe -r requirements.txt
if errorlevel 1 goto failed
:validate
echo [3/3] Validating application...
".venv\Scripts\python.exe" -m compileall -q app.py pages services
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -c "from services.parking_marker import marker_icon, risk_band; assert risk_band(80)[1]; assert marker_icon(50)['url'].startswith('data:image/svg+xml')"
if errorlevel 1 goto failed
echo Ready to start Streamlit.
exit /b 0
:failed
echo ERROR: Python setup failed. See the error message above.
echo Check Python installation and internet access.
exit /b 1
