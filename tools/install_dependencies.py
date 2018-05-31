"""
/***************************************************************************
 File Name: tools/install_dependencies.py
 Last Change: 
/*************************************************************************** 
 ---------------
 GeoTools
 ---------------
 A QGIS plugin
 Collection of tools for geoscience application. Some tools can be found in 
 qCompass plugin for CloudCompare. 
 If you are publishing any work associated with this plugin please cite
 #TODO add citatioN!
                             -------------------
        begin                : 2017-27-12
        copyright          : (C) 2015 by Lachlan Grose
        email                : lachlan.grose@monash.edu
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import urllib
import subprocess
import os
import platform
import inspect
import struct
import time
import sys
import pip
#check to see what operating system if being used
def pip_install(package):
    #pip.main(['install','--user',package])
    return subprocess.call(["python3","-m","pip","install",package])
class Installer():
    def __init__(self):
        self.name = 'Installer'
    def install(self):
        filepath = inspect.getfile(inspect.currentframe())
        os.chdir(os.path.dirname(filepath))
        os.chdir('../')
        success = True
        if platform.system() == 'Windows':
            if os.path.isdir('windows_installers') == False:
                os.mkdir('windows_installers')
            os.chdir('windows_installers')
            success &= pip_install('mplstereonet')
            if not success:
                return False
            if struct.calcsize("P")*8 == 64:
                urllib.request.urlretrieve('https://github.com/lachlangrose/GeoTrace/raw/downloads/windows_installers/wheels/Cython-0.28.3-cp36-cp36m-win_amd64.whl',
                'Cython-0.28.3-cp36-cp36m-win_amd64.whl')
                urllib.request.urlretrieve('https://github.com/lachlangrose/GeoTrace/raw/downloads/windows_installers/wheels/scikit_image-0.14.0-cp36-cp36m-win_amd64.whl',
                'scikit_image-0.14.0-cp36-cp36m-win_amd64.whl')
                success &= pip_install('Cython-0.28.3-cp36-cp36m-win_amd64.whl')
                if not success:
                    return False
                success &= pip_install('scikit_image-0.14.0-cp36-cp36m-win_amd64.whl')
                if not success:
                    return False
            if struct.calcsize("P")*8==32:
                urllib.request.urlretrieve('https://github.com/lachlangrose/GeoTrace/raw/downloads/windows_installers/wheels/Cython-0.28.3-cp36-cp36m-win32.whl','Cython-0.28.3-cp36-cp36m-win32.whl')
                urllib.request.urlretrieve('https://github.com/lachlangrose/GeoTrace/raw/downloads/windows_installers/wheels/scikit_image-0.14.0-cp36-cp36m-win32.whl','scikit_image-0.14.0-cp36-cp36m-win32.whl')
                success &=  pip_install('Cython-0.28.3-cp36-cp36m-win32.whl')
                if not success:
                    return False
                success &=  pip_install('scikit_image-0.14.0-cp36-cp36m-win32.whl')
                if not success:
                    return False                
            home_folder = os.path.expanduser("~")
            user_site_packages_folder = "{}\AppData\\Roaming\\Python\\Python36\\site-packages".format(home_folder)
            if user_site_packages_folder not in sys.path:
                 sys.path.append(user_site_packages_folder)
        if platform.system() == 'Linux':
            #os.chdir('linux_installers')
            #linux is easy because it has c compiler
            success &= pip_install('scikit_image')
            if not success:
                return false
            success &= pip_install('mplstereonet')
            if not success:
                return false

        try:
            import gttracetool
            return True
        except ImportError:
            return False

