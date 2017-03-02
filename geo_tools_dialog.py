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

import os
import gttracetool

from PyQt4 import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
class GeoToolsDialog(QtGui.QDialog):
    def __init__(self, iface,parent=None):
        """Constructor."""
        super(GeoToolsDialog, self).__init__(parent)
        self.iface = iface
        self.canvas = iface.mapCanvas()
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setup_gui()
    def setup_gui(self):
        self.dialog_layout = QVBoxLayout()
        self.setLayout(self.dialog_layout)
        self.setWindowTitle('qTrace')

        vector_group = QGroupBox('Select Target Layer')
        self.vector_layer_combo_box = QgsMapLayerComboBox()
        self.vector_layer_combo_box.setCurrentIndex(-1)
        self.vector_layer_combo_box.setFilters(QgsMapLayerProxyModel.VectorLayer)
        vector_layout = QVBoxLayout()
        vector_layout.addWidget(self.vector_layer_combo_box)
        vector_group.setLayout(vector_layout)
        create_memory_layer = QPushButton("Create Temporary Target Layer")
        vector_layout.addWidget(create_memory_layer)
        

        cost_group = QGroupBox('Select Cost Layer')
        cost_layout = QVBoxLayout()
        self.cost_layer_combo_box = QgsMapLayerComboBox()
        self.cost_layer_combo_box.setCurrentIndex(-1)
        self.cost_layer_combo_box.setFilters(QgsMapLayerProxyModel.RasterLayer)
        cost_layout.addWidget(self.cost_layer_combo_box)
        cost_group.setLayout(cost_layout)


        trace_group = QGroupBox("Find Trace")
        trace_layout = QFormLayout()
        run_trace_button = QPushButton("Digitize and run")
        clear_points_button = QPushButton("Clear Points")
        run_trace_button.clicked.connect(self.run_trace_tool)
        trace_layout.addWidget(run_trace_button) 
        trace_layout.addWidget(clear_points_button) 
        clear_points_button.clicked.connect(self.delete_control_points)
        trace_group.setLayout(trace_layout)

        cost_calculator_group = QGroupBox("Build Cost Layer")
        cost_calculator_layout = QFormLayout()
        build_cost_layer_button = QPushButton("Calculate Cost Layer")
        cost_calculator_layout.addWidget(build_cost_layer_button) 
        cost_calculator_group.setLayout(cost_calculator_layout)
        raster_layer_combo_box = QgsMapLayerComboBox()
        raster_layer_combo_box.setCurrentIndex(-1)
        raster_layer_combo_box.setFilters(QgsMapLayerProxyModel.RasterLayer)
        cost_calculator_layout.addWidget(raster_layer_combo_box)

        self.dialog_layout.addWidget(vector_group)
        self.dialog_layout.addWidget(cost_group)
        self.dialog_layout.addWidget(trace_group)
        self.dialog_layout.addWidget(cost_calculator_group)
    def run_trace_tool(self):
        target = self.vector_layer_combo_box.currentLayer()
        cost = self.cost_layer_combo_box.currentLayer() 
        self.tracetool = gttracetool.GtTraceTool(self.canvas,self.iface,target,cost)
        self.canvas.setMapTool(self.tracetool)
        #self.dialog_layout.addWidget(self.dlg.)
    def delete_control_points(self):
        if self.tracetool:
            self.tracetool.delete_control_points()
