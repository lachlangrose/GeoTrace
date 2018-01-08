@echo off

REM get the QGIS directory
REM move into the QGIS directory
if EXIST %ProgramFiles%\QGIS*\ ( 
    set QGIS=%ProgramFiles%\QGIS*\
    set platform=1
	echo %platform%
    goto install )
if EXIST %ProgramFiles(x86)% (
    set QGIS=%ProgramFiles(x86)%\QGIS*\
    set platform=0
    goto install )


echo "Error: Could not find an installed copy of QGIS"

exit

:install
REM move into the QGIS directory to load OSGEO4W and install dependencies
cd %QGIS%

REM load OSGEO4W environment (including the QGIS python)
call "bin\o4w_env.bat"
dir
echo exist "bin\o4w_env.bat"


REM update pip
call python -m pip install --upgrade setuptools

REM install mplstereo using python
call python -m pip install mplstereonet

REM change back to the directory with the python wheels
cd /D %UserProfile%
cd .qgis2\python\plugins\GeoTrace\windows_installers

echo %platform%

IF %platform% == 0 (
call python -m pip install Cython-0.27.2-cp27-cp27m-win32.whl
call python -m pip install scikit_image-0.13.1-cp27-cp27m-win32.whl
)

IF %platform% == 1 (

call python -m pip install Cython-0.27.2-cp27-cp27m-win_amd64.whl
call python -m pip install scikit_image-0.13.1-cp27-cp27m-win_amd64.whl 

)

echo GeoTrace dependencies were succesfully installed.
