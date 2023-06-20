:: This .bat file installs:
::  1) Python 3.8.0 if other Python versions do not found in the system
::  2) Project's dependencies.

:: The installer.bat script needs:
::  1) requirements_installer.py in the same folder
::  2) requirements.txt with required package names
::  3) In dependencies/ folder - "python-3.8.0.exe" and other
::     package dependencies that can be obtained using command: py -m pip download <package name>

@echo off
:: Set working directory
cd %~dp0

:: Check is Python exists or not
for /F "delims= " %%i in ('py -V') do (
    set pyexist=%%i
)
echo %pyexist%

if /I "%pyexist%" neq "Python" (
    :: Behavior if Python does not exist
    echo Python does not found in this system.
    echo Installation of Python 3.8.0
    echo Please wait a few minutes...
    dependencies\python-3.8.0.exe /passive PrependPath=1 Include_test=0
    echo Python 3.8.0 has been successfully installed!
) else (
    :: If Python exists
    echo Python was found in this system.
)

echo Installation of dependencies...
py requirements_installer.py --try-internet

:: Flush variables
set pyexist=
pause