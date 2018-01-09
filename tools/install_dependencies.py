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
#check to see what operating system if being used
class Installer():
    def __init__(self):
        self.name = 'Installer'
    def install(self):
        filepath = inspect.getfile(inspect.currentframe())
        os.chdir(os.path.dirname(filepath))
        os.chdir('../')
        if platform.system() == 'Windows':
            os.chdir('windows_installers')
            process = subprocess.call('cscript windows_sudo.vbs')
            trace_imported  = False
            #vbs script calls bat script so keep checking if install has worked
            count = 0 
            while trace_imported == False:
                try:
                    import gttracetool
                    trace_imported = True
                except ImportError:
                    time.sleep(1)
                    count+=1
                    trace_imported = False
                    #try for three minutes, if not successful quit
                    if count > 180:
                        return False
            #process.wait()
            return True
        if platform.system() == 'Linux':
            #os.chdir('linux_installers')
            #linux is easy because it has c compiler
            subprocess.call('pip install --user scikit_image',shell=True)
            subprocess.call('pip install --user mplstereonet',shell=True)

            trace_imported = False
            count = 0
            while not trace_imported:
                try:
                    trace_imported = True
                except ImportError:
                    time.sleep(1)
                    count+=1
                    trace_imported = False
                    if count > 180:
                        return False
                return True
        return False

