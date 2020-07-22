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
    proc = subprocess.run(["python3","-m","pip","install","--user",package],stdout=subprocess.PIPE)
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
        
        if importlib.find_loader('mplstereonet') is None:
            out = pip_install('mplstereonet==0.6')
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
            assert False, "An unexpected import error occurred"

