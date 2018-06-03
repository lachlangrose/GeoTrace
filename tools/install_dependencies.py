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
import importlib

#check to see what operating system if being used
def pip_install(package):
    proc = subprocess.run(["python3","-m","pip","install",package],stdout=subprocess.PIPE)
    return proc.stdout #return output (n.b. return codes from pip don't seem to change for success/failure... hence we don't check...)
class Installer():
    def __init__(self):
        self.name = 'Installer'
    def install(self):
        #get directory plugin is installed in 
        filepath = inspect.getfile(inspect.currentframe())
        os.chdir(os.path.dirname(filepath))
        os.chdir('../')
        success = True
        
        #are we running windows (things get difficult here...)
        if platform.system() == 'Windows':
            #create directory to download installers into
            if os.path.isdir('windows_installers') == False:
                os.mkdir('windows_installers')
            os.chdir('windows_installers') #move into this dir

            if importlib.find_loader('mplstereonet') is None:
                out = pip_install('mplstereonet')
                assert not importlib.find_loader('mplstereonet') is None, "Could not install mplstereonet. Pip output is as follows:\n%s" % out
                
            #try downloading cython and scikit-image binaries from github
            if struct.calcsize("P")*8 == 64: #64-bit OS
                urllib.request.urlretrieve('https://github.com/lachlangrose/GeoTrace/raw/downloads/windows_installers/wheels/Cython-0.28.3-cp36-cp36m-win_amd64.whl',
                'Cython-0.28.3-cp36-cp36m-win_amd64.whl')
                urllib.request.urlretrieve('https://github.com/lachlangrose/GeoTrace/raw/downloads/windows_installers/wheels/scikit_image-0.14.0-cp36-cp36m-win_amd64.whl',
                'scikit_image-0.14.0-cp36-cp36m-win_amd64.whl')
                
                #install cython
                if importlib.find_loader('cython') is None:
                    out = pip_install('Cython-0.28.3-cp36-cp36m-win_amd64.whl')
                    assert not importlib.find_loader('cython') is None, "Could not install cython. Pip output is as follows:\n%s" % out

                #install scikit image
                if importlib.find_loader('skimage') is None:
                    pip_install('scikit_image-0.14.0-cp36-cp36m-win_amd64.whl')
                    assert not importlib.find_loader('skimage') is None, "Could not install scikit-image. Pip output is as follows:\n%s" % out
                    
                    
            if struct.calcsize("P")*8==32: #as above, but 32-bit
                urllib.request.urlretrieve('https://github.com/lachlangrose/GeoTrace/raw/downloads/windows_installers/wheels/Cython-0.28.3-cp36-cp36m-win32.whl','Cython-0.28.3-cp36-cp36m-win32.whl')
                urllib.request.urlretrieve('https://github.com/lachlangrose/GeoTrace/raw/downloads/windows_installers/wheels/scikit_image-0.14.0-cp36-cp36m-win32.whl','scikit_image-0.14.0-cp36-cp36m-win32.whl')
                
                #install cython
                if importlib.find_loader('cython') is None:
                    out = pip_install('Cython-0.28.3-cp36-cp36m-win32.whl')
                    assert not importlib.find_loader('cython') is None, "Could not install cython. Pip output is as follows:\n%s" % out

                #install scikit image
                if importlib.find_loader('skimage') is None:
                    pip_install('scikit_image-0.14.0-cp36-cp36m-win32.whl')
                    assert not importlib.find_loader('skimage') is None, "Could not install scikit-image. Pip output is as follows:\n%s" % out
                    
            #not sure what this does?
            #home_folder = os.path.expanduser("~")
            #user_site_packages_folder = "{}\AppData\\Roaming\\Python\\Python36\\site-packages".format(home_folder)
            #if user_site_packages_folder not in sys.path:
            #     sys.path.append(user_site_packages_folder)
                 
        if platform.system() == 'Linux': #linux is easy because it has c compiler
            #install mplstereonet
            if importlib.find_loader('mplstereonet') is None:
                out = pip_install('mplstereonet')
                assert not importlib.find_loader('mplstereonet') is None, "Could not install mplstereonet. Pip output is as follows:\n%s" % out

            #install scikit image
            if importlib.find_loader('skimage') is None:
                pip_install('scikit_image')
                assert not importlib.find_loader('skimage') is None, "Could not install scikit-image. Pip output is as follows:\n%s" % out

        #finally, check that import works for gttracetool
        try:
            import gttracetool
            return True
        except ImportError:
            assert False, "An unexpected import error occurred... shit's fucked?"

