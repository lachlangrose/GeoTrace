# -*- coding: utf-8 -*-
"""
/***************************************************************************
GeoTools
A geosciences toolkit for QGIS.
Copyright (C) 2014  Lachlan Grose

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA. 
***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from geo_tools_dialog import GeoToolsDialog
import os.path,  sys
# Set up current path.
currentPath = os.path.dirname( __file__ )
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/tools'))
import gttools
import gtlinetool
import gtstereo
import gttracetool
class GeoTools:
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
            'GeoTools_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = GeoToolsDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&GeoTools')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'GeoTools')
        self.toolbar.setObjectName(u'GeoTools')
        self.canvas = self.iface.mapCanvas()
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
        return QCoreApplication.translate('GeoTools', message)


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
        base_icon_path = ':/plugins/GeoTools/'
        tile_icon_path = ':/plugins/GeoTools/tile.png'
        stereo_icon_path = ':/plugins/GeoTools/stereo.png'
        digitize_icon_path = ':/plugins/GeoTools/digitize.png'

        icon_path = ':/plugins/GeoTools/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'GeoTools'),
            callback=self.run,
            parent=self.iface.mainWindow())
        self.add_action(
            tile_icon_path,
            text=self.tr(u'Export Tiles within area'),
            callback=self.rectangle,
            parent=self.iface.mainWindow())
        self.add_action(
            digitize_icon_path,
            text=self.tr(u'Digitize Orientation'),
            callback=self.line,
            parent=self.iface.mainWindow())
        self.add_action(
            stereo_icon_path,
            text=self.tr(u'Stereonet'),
            callback=self.stereo,
            parent=self.iface.mainWindow())
        self.add_action(
            icon_path,
            text=self.tr(u'Trace'),
            callback=self.trace,
            parent=self.iface.mainWindow())
        self.recttool = gttools.GtRectangleTool(self.canvas,self.iface)
        self.linetool = gtlinetool.GtLineTool(self.canvas,self.iface)
        self.tracetool = gttracetool.GtTraceTool(self.canvas,self.iface)
    def trace(self):
        self.canvas.setMapTool(self.tracetool)    
    def rectangle(self):
        self.canvas.setMapTool(self.recttool)
    def line(self):
        self.canvas.setMapTool(self.linetool)
    def stereo(self):

        self.stereo = gtstereo.GtStereo(self.canvas,self.iface)
        self.stereo.run()
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&GeoTools'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
