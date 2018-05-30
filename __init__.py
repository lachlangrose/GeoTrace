# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoTools
                                 A QGIS plugin
 Collection of tools for geoscience analysis
                             -------------------
        begin                : 2015-09-08
        copyright            : (C) 2015 by Lachlan Grose
        email                : lachlan.grose@monash.edu
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""
import sys, os

#Add tools directory to python path
currentPath = os.path.dirname( __file__ )
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/tools'))

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load GeoTools class from file GeoTools.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #setup matplotlib to use 'agg' backend to avoid import errors related to tkinter (not installed on windows OsGeo4w)
    import matplotlib as mpl
    mpl.use('agg')
    try:
        import matplotlib.pyplot as plt
    except:
        assert(False, "Error - incorrect matplotlib backend. Please use 'Agg'.")
   
    from .geo_trace import GeoTrace
    return GeoTrace(iface)
