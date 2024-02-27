cd %~dp0

IF NOT EXIST .local_version (
  echo.>.local_version
)
set /p local_version=<.local_version
set /p current_version=<VERSION

IF NOT "%local_version%"=="%current_version%" (
  call setup.bat true
)

call venv\Scripts\activate.bat

python launch.py

deactivate
