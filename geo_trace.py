# -*- coding: utf-8 -*-
"""
/***************************************************************************
 File Name: geo_trace.py
 Last Change: 
/*************************************************************************** 
 ---------------
 GeoTrace
 ---------------
 A QGIS plugin
 Collection of tools for geoscience application. Some tools can be found in 
 qCompass plugin for CloudCompare. 
 If you are publishing any work associated with this plugin please cite
 #TODO add citatioN!
                             -------------------
        begin                : 2015-01-1
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

from PyQt5.QtCore import *#QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import *#QAction, QIcon
from PyQt5.QtWidgets import *#QAction, QIcon
# Initialize Qt resources from file resources.py
from .resources import *


# Import the code for the dialog
from .geo_trace_dialog import GeoTraceDialog
import os.path,  sys
import gtlinetool

class GeoTrace:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GeoTrace_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&GeoTrace')
        self.toolbar = self.iface.addToolBar(u'GeoTrace')
        self.toolbar.setObjectName(u'GeoTrace')
        self.canvas = self.iface.mapCanvas()
        #self.dlg = GeoTraceDialog(self.iface)
        self.linetool= gtlinetool.GtLineTool(self.canvas,self.iface)
        self.trace_dockWidget = None
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GeoTrace', message)

    def line(self):
        self.canvas.setMapTool(self.linetool)
    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = ':/plugins/GeoTrace/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'GeoTrace'),
            callback=self.open_trace,
            parent=self.iface.mainWindow())
        #self.add_action(
        #    icon_path,
        #    text=self.tr(u'Digitize'),
        #    callback=self.line,
        #    parent=self.iface.mainWindow())
    def open_trace(self):
        self.dlg = GeoTraceDialog(self.iface)
        self.trace_dockWidget = QDockWidget('GeoTrace', self.iface.mainWindow())
        #for some reason dockwidget wasn't given a name and then the main qgis
        #save state was throwing an error - causing minidump??
        self.trace_dockWidget.setObjectName("GeoTraceDock")
        self.trace_dockWidget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        #self.qProf_QWidget = qprof_QWidget(self.canvas)
        self.trace_dockWidget.setWidget(self.dlg)
        self.trace_dockWidget.destroyed.connect(self.dlg.closeEvent)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.trace_dockWidget)

        self.trace_dockWidget.visibilityChanged.connect(self.dlg.close)
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&GeoTrace'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
