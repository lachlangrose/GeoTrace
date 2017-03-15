# -*- coding: utf-8 -*-
"""
/***************************************************************************
 File Name: geo_tools_dialog.py
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


import os
import gttracetool
from gtstereo import *
from PyQt4 import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
_plugin_name_ = "GeoTools"

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
    def closeEvent(self,event):
        return
    def setup_gui(self):
        self.dialog_layout = QVBoxLayout()
        self.setLayout(self.dialog_layout)
        self.setWindowTitle('GeoTools')
        tab_layout = QTabWidget()
        tab_layout.addTab(self.setup_trace(),"Trace")
        tab_layout.addTab(self.setup_stereonet(),"Steronet")
        tab_layout.addTab(self.setup_rose(),"Rose")

        self.dialog_layout.addWidget(tab_layout)
    def setup_histogram(self):
        histogram_widget = QWidget()
        histogram_layout = QVBoxLayout()
        histogram_group = QGroupBox("GeoTools Histogram")
        histogram_layout.addWidget(histogram_group)
        histogram_widget.setLayout(histogram_layout)
        return histogram_widget
            
    def setup_stereonet(self):
        stereo_main = Window(self.canvas,self.iface)    
        stereo_widget = QWidget()
        stereo_layout = QVBoxLayout()
        stereo_group = QGroupBox("GeoTools Stereonet")
        stereo_layout.addWidget(stereo_group)
        stereo_layout.addWidget(stereo_main)
        stereo_widget.setLayout(stereo_layout)
        return stereo_widget
    def setup_rose(self):
        stereo_widget = QWidget()
        stereo_layout = QVBoxLayout()
        stereo_group = QGroupBox("GeoTools Rose Diagram")
        stereo_layout.addWidget(stereo_group)
        stereo_widget.setLayout(stereo_layout)
        return stereo_widget
    def setup_alignments(self):
        alignments_widget = QWidget()
        alignments_layout = QVBoxLayout()
        alignments_group = QGroupBox("GeoTools Alignments Tools")
        alignments_layout.addWidget(alignments_group)
        alignments_widget.setLayout(alignments_layout)
        return stereo_widget
        
    def setup_trace(self):
        trace_widget = QWidget()
        trace_main_layout = QVBoxLayout()
        vector_group = QGroupBox('Output Layer')
        self.vector_layer_combo_box = QgsMapLayerComboBox()
        self.vector_layer_combo_box.setCurrentIndex(-1)
        self.vector_layer_combo_box.setFilters(QgsMapLayerProxyModel.VectorLayer)
        vector_layout = QVBoxLayout()
        vector_layout.addWidget(self.vector_layer_combo_box)
        vector_group.setLayout(vector_layout)
        create_memory_layer = QPushButton("Create Temporary Target Layer")
        self.save_control_points = QRadioButton("Store Control Points") 
        self.save_control_points.toggled.connect(self.show_control_point_combo_box)
        self.controlpoint_layer_combo_box = QgsMapLayerComboBox()
        self.controlpoint_layer_combo_box.setCurrentIndex(-1)
        self.controlpoint_layer_combo_box.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.controlpoint_layer_combo_box.setEnabled(False)
        vector_layout.addWidget(self.save_control_points)
        vector_layout.addWidget(self.controlpoint_layer_combo_box)
        #vector_layout.addWidget(create_memory_layer)
        

        cost_group = QGroupBox('Cost Layer')
        raster_calculator_button = QPushButton('Raster Calculator')
        self.invert_cost = QCheckBox('Invert Cost')
        cost_layout = QVBoxLayout()
        self.cost_layer_combo_box = QgsMapLayerComboBox()
        self.cost_layer_combo_box.setCurrentIndex(-1)
        self.cost_layer_combo_box.setFilters(QgsMapLayerProxyModel.RasterLayer)
        cost_layout.addWidget(self.cost_layer_combo_box)
        cost_layout.addWidget(self.invert_cost)
        #cost_layout.addWidget(raster_calculator_button)
        cost_group.setLayout(cost_layout)
        self.fit_plane = QCheckBox("Fit planes")
        dem_label = QLabel("Find fracture orientation using DEM")
        #TODO filter list to only show single band rasters
        cost_layout.addWidget(dem_label)
        cost_layout.addWidget(self.fit_plane)
        self.dem_layer_combo_box = QgsMapLayerComboBox()
        self.dem_layer_combo_box.setCurrentIndex(-1)
        self.dem_layer_combo_box.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.dem_layer_combo_box.setEnabled(False)
        cost_layout.addWidget(self.dem_layer_combo_box)
        self.fit_plane.toggled.connect(self.show_plane_combo_box)

        trace_group = QGroupBox("Find Trace")
        trace_layout = QFormLayout()
        run_trace_button = QPushButton("Start Digitizing")
        clear_points_button = QPushButton("Finish Line")
        undo_button = QPushButton("Undo")

        run_trace_button.clicked.connect(self.run_trace_tool)
        trace_layout.addWidget(run_trace_button) 
        #trace_layout.addWidget(clear_points_button) 
        clear_points_button.clicked.connect(self.delete_control_points)
        trace_group.setLayout(trace_layout)
        
        cost_calculator_group = QGroupBox("Cost Calculator")
        cost_calculator_layout = QFormLayout()
        build_cost_layer_button = QPushButton("Calculate Cost Layer")
        cost_calculator_layout.addWidget(build_cost_layer_button) 
        cost_calculator_group.setLayout(cost_calculator_layout)
        raster_layer_combo_box = QgsMapLayerComboBox()
        raster_layer_combo_box.setCurrentIndex(-1)
        raster_layer_combo_box.setFilters(QgsMapLayerProxyModel.RasterLayer)
        cost_calculator_layout.addWidget(raster_layer_combo_box)
        trace_main_layout.addWidget(vector_group)
        trace_main_layout.addWidget(cost_group)
        #trace_main_layout.addWidget(cost_calculator_group)
        trace_main_layout.addWidget(trace_group)
        trace_widget.setLayout(trace_main_layout)
        return trace_widget
    def run_trace_tool(self):
        target = self.vector_layer_combo_box.currentLayer()
        cost = self.cost_layer_combo_box.currentLayer() 
        if cost.bandCount() != 1:
            self.error("Cost Raster has too many bands")
            return
        if target.geometryType() != QGis.Line:
            self.error("Target has wrong geometry type")
            return 
        self.tracetool = gttracetool.GtTraceTool(self.canvas,self.iface,target,cost)
        if self.save_control_points.isChecked():
            ctrl_pt = self.controlpoint_layer_combo_box.currentLayer()
            if ctrl_pt.geometryType() != QGis.Point:
                self.error("Control points are not points!")
                return
            self.tracetool.setControlPoints(self.controlpoint_layer_combo_box.currentLayer())
        if self.fit_plane.isChecked():
            dem = self.dem_layer_combo_box.currentLayer()
            if dem.bandCount() != 1:
                self.error("DEM must be single band")
                return
            self.tracetool.setDem(dem)
            #self.info("Using DEM for planes")
        self.tracetool.invertCost(self.invert_cost.isChecked())
        self.canvas.setMapTool(self.tracetool)
        #self.dialog_layout.addWidget(self.dlg.)
    def delete_control_points(self):
        if self.tracetool:
            self.tracetool.delete_control_points()
    def show_control_point_combo_box(self):
        if self.controlpoint_layer_combo_box:
            if self.save_control_points.isChecked():
                self.controlpoint_layer_combo_box.setEnabled(True)
            if not self.save_control_points.isChecked():
                self.controlpoint_layer_combo_box.setEnabled(False)
    def show_plane_combo_box(self):
         if self.dem_layer_combo_box:
            if self.fit_plane.isChecked():
                self.dem_layer_combo_box.setEnabled(True)
            if not self.fit_plane.isChecked():
                self.dem_layer_combo_box.setEnabled(False)
    def info(self, msg):
        print "Info: "+ msg
        QMessageBox.information(self, _plugin_name_, msg)

    def warn(self, msg):
        print "Warning: "+ msg
        QMessageBox.warning(self, _plugin_name_, msg)

    def error(self, msg):
        print "Error: "+ msg
        QMessageBox.critical(self, _plugin_name_, msg)
