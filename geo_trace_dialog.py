# -*- coding: utf-8 -*-
"""
/***************************************************************************
 File Name: geo_tools_dialog.py
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


import os
#from PyQt4 import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
_plugin_name_ = "GeoTrace"
trace_imported  = True
try:
    import gttracetool
    trace_imported  = True
except ImportError:
    trace_imported = False
class GeoTraceDialog(QDialog):
    def __init__(self, iface,parent=None):
        """Constructor."""
        super(GeoTraceDialog, self).__init__(parent)
        self.iface = iface
        self.canvas = iface.mapCanvas()
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setup_gui()
    def closeEvent(self,event):
        self.deactivateTrace()
        return
    def setup_gui(self):
        self.dialog_layout = QVBoxLayout()
        self.setLayout(self.dialog_layout)
        self.setWindowTitle('GeoTrace')
        tab_layout = QTabWidget()
        if trace_imported:
            tab_layout.addTab(self.setup_trace(),"Trace")
            tab_layout.addTab(self.setup_advanced_trace(),"Advanced Trace")
            tab_layout.addTab(self.setup_cost_calculator(),"Cost Calculator")

        else:
            tab_layout.addTab(self.setup_error(),"Trace")
            tab_layout.addTab(self.setup_error(),"Advanced Trace")
            tab_layout.addTab(self.setup_error(),"Cost Calculator")
        try:
            tab_layout.addTab(self.setup_stereonet(),"Steronet")
        except ImportError:
            tab_layout.addTab(self.setup_error(),"Steronet")
        try:
            tab_layout.addTab(self.setup_rose(),"Rose")
        except ImportError:
            tab_layout.addTab(self.setup_error(),"Rose")
        tab_layout.addTab(self.setup_about(),"About")
        self.dialog_layout.addWidget(tab_layout)
    def setup_error(self):
        error_widget= QWidget()
        main_layout = QGridLayout()
        missing = QGroupBox("Missing Dependencies")
        error = QTextBrowser()
        info = QFile(":/plugins/GeoTrace/instructions.html")
        info.open(QFile.ReadOnly)
        text = QTextStream(info)
        error.setHtml(text.readAll())
        main_layout.addWidget(missing)
        error.setOpenExternalLinks(True)
        main_layout.addWidget(error)
        error_widget.setLayout(main_layout)
        return error_widget
    def setup_histogram(self):
        histogram_widget = QWidget()
        histogram_layout = QVBoxLayout()
        histogram_group = QGroupBox("GeoTrace Histogram")
        histogram_layout.addWidget(histogram_group)
        histogram_widget.setLayout(histogram_layout)
        return histogram_widget
    def setup_about(self):
        about_widget = QWidget()
        main_layout = QGridLayout()
        text_box = QTextBrowser()
        about = QFile(":/plugins/GeoTrace/about.html")
        about.open(QFile.ReadOnly)
        text = QTextStream(about)
        text_box.setHtml(text.readAll())
        text_box.setOpenExternalLinks(True)
        main_layout.addWidget(text_box)
        about_widget.setLayout(main_layout)

        return  about_widget
    def setup_stereonet(self):
        import gtstereo 
        stereo_main = gtstereo.GtStereo(self.canvas,self.iface)    
        stereo_widget = QWidget()
        stereo_layout = QVBoxLayout()
        stereo_group = QGroupBox("GeoTrace Stereonet")
        stereo_layout.addWidget(stereo_group)
        stereo_layout.addWidget(stereo_main)
        stereo_widget.setLayout(stereo_layout)
        return stereo_widget
    def setup_rose(self):
        import gtrose 
        rose_main = gtrose.GtRose(self.canvas,self.iface)
        rose_widget = QWidget()
        rose_layout = QVBoxLayout()
        rose_group = QGroupBox("GeoTrace Rose Diagram")
        rose_layout.addWidget(rose_group)
        rose_layout.addWidget(rose_main)
        rose_widget.setLayout(rose_layout)
        return rose_widget 
    def setup_advanced_trace(self):
        trace_widget = QWidget()
        trace_main_layout = QVBoxLayout()
        vector_group = QGroupBox()
        self.at_vector_layer_combo_box = QgsMapLayerComboBox()
        self.at_vector_layer_combo_box.setCurrentIndex(-1)
        self.at_vector_layer_combo_box.setFilters(QgsMapLayerProxyModel.LineLayer)
        vector_layout = QFormLayout()
        vector_layout.addRow('Output Layer',self.at_vector_layer_combo_box)
        vector_group.setLayout(vector_layout)
        self.at_controlpoint_layer_combo_box = QgsMapLayerComboBox()
        self.at_controlpoint_layer_combo_box.setCurrentIndex(-1)
        self.at_controlpoint_layer_combo_box.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.unique_field = QgsFieldComboBox()
        vector_layout.addRow('Control Points',self.at_controlpoint_layer_combo_box)
        vector_layout.addRow('Unique ID field',self.unique_field)
        self.at_controlpoint_layer_combo_box.layerChanged.connect(self.unique_field.setLayer)
        self.at_cost_layer_combo_box = QgsMapLayerComboBox()
        self.at_cost_layer_combo_box.setCurrentIndex(-1)
        self.at_cost_layer_combo_box.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.at_invert_cost = QCheckBox()

        vector_layout.addRow('Cost layer',self.at_cost_layer_combo_box)
        vector_layout.addRow('Invert Cost',self.at_invert_cost )

        #self.at_fit_plane = QCheckBox()
        #self.at_dem_layer_combo_box = QgsMapLayerComboBox()
        #self.at_dem_layer_combo_box.setCurrentIndex(-1)
        #self.at_dem_layer_combo_box.setFilters(QgsMapLayerProxyModel.RasterLayer)
        #self.at_dem_layer_combo_box.setEnabled(False)
        #self.at_fit_plane.toggled.connect(self.show_plane_combo_box)
        #vector_layout.addRow("Find orientation using DEM",self.fit_plane)
        #vector_layout.addRow('DEM',self.dem_layer_combo_box)

        self.run_advanced_trace_button = QPushButton("Run")
        vector_layout.addRow(self.run_advanced_trace_button)
        #vector_layout.addWidget(create_memory_layer)
        trace_main_layout.addWidget(vector_group)
        trace_widget.setLayout(trace_main_layout)
        self.run_advanced_trace_button.clicked.connect(self.run_advanced_trace_tool)


        return trace_widget        
    def setup_cost_calculator(self):
        cost_calc_widget = QWidget()
        self.cost_calc_layout = QFormLayout()
        self.raster_layer_combo_box = QgsMapLayerComboBox()
        self.raster_layer_combo_box.setCurrentIndex(-1)
        self.raster_layer_combo_box.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.raster_layer_combo_box.currentIndexChanged.connect(self.updateCostName)
        self.costs = []
        self.cost_calc_layout.addRow("Reference Raster: ", self.raster_layer_combo_box) 
    
        #self.addCost('_lightness','Lightness')
        self.addCost('_darkness','Darkness')
        self.addCost('_sobel','Sobel')
        self.addCost('_sobv','Sobel Vertical Transform')
        self.addCost('_sobh','Sobel Horizontal Transform')
        self.addCost('_roberts','Roberts\' cross opperator')
        self.addCost('_prewitt','Prewitt Transform')
        self.addCost('_scharr','Scharr transform')
        #self.addCost('_phase','Phase Congruency')
        self.cost_name = QLineEdit()
        self.cost_calc_layout.addRow("Cost Layer Name",self.cost_name)
        cost_calculator_run = QPushButton("Run")
        self.cost_calc_layout.addRow(cost_calculator_run)
        cost_calc_widget.setLayout(self.cost_calc_layout)
        cost_calculator_run.clicked.connect(self.run_costcalculator)

        return cost_calc_widget
    def addCost(self,shortname,longname):
        radio = QRadioButton()
        self.costs.append([shortname,radio])
        self.cost_calc_layout.addRow(longname,radio)
        radio.clicked.connect(self.updateCostName)
    def setup_trace(self):
        trace_widget = QWidget()
        trace_main_layout = QVBoxLayout()
        vector_group = QGroupBox('Output Layer')
        self.vector_layer_combo_box = QgsMapLayerComboBox()
        self.vector_layer_combo_box.setCurrentIndex(-1)
        self.vector_layer_combo_box.setFilters(QgsMapLayerProxyModel.LineLayer)
        vector_layout = QVBoxLayout()
        vector_layout.addWidget(self.vector_layer_combo_box)
        vector_group.setLayout(vector_layout)
        create_memory_layer = QPushButton("Create Temporary Target Layer")
        self.save_control_points = QRadioButton("Store Control Points") 
        self.save_control_points.toggled.connect(self.show_control_point_combo_box)
        self.controlpoint_layer_combo_box = QgsMapLayerComboBox()
        self.controlpoint_layer_combo_box.setCurrentIndex(-1)
        self.controlpoint_layer_combo_box.setFilters(QgsMapLayerProxyModel.PointLayer)
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
        self.traceToolActive = False
        self.run_trace_button = QPushButton("Start Digitizing")
        clear_points_button = QPushButton("Finish Line")
        undo_button = QPushButton("Undo")
        
        self.run_trace_button.clicked.connect(self.toggle_trace_tool)
        trace_layout.addWidget(self.run_trace_button) 
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
    def deactivateTrace(self):
        if self.traceToolActive == False:
            return
        self.tracetool.rubberBandLine.reset(QGis.Line)
        self.tracetool.rubberBand.reset(QGis.Point)
        self.tracetool.deactivate()
        self.traceToolActive = False
        self.canvas.setMapTool(QgsMapToolPan(self.canvas))
        self.run_trace_button.setText("Start Digitizing")
        return
    def updateCostName(self,string=None):
        name = self.raster_layer_combo_box.currentLayer().name()
        for c in self.costs:
            if c[1].isChecked():
                name+=c[0]
        #name+=''
        self.cost_name.setText(name)
        return
    def run_costcalculator(self):
        layer = self.raster_layer_combo_box.currentLayer()
        if layer:
            calc = gttracetool.CostCalculator(layer)
            for c in self.costs:
                if c[1].isChecked():
                    calc.run_calculator(c[0],self.cost_name.text())
                
        return 

    def run_advanced_trace_tool(self):
        target = self.at_vector_layer_combo_box.currentLayer()
        cost = self.at_cost_layer_combo_box.currentLayer() 
        ctrl_pt = self.at_controlpoint_layer_combo_box.currentLayer()
        field= self.unique_field.currentField()
        if not target:
            self.error("No target layer selected")
            return
        if not cost:
            self.error("No cost layer selected")
            return
        if not ctrl_pt:
            self.error("No control points layer selected")
            return
        if not field:
            self.error("No unique field iD selected")
            return
        if cost.bandCount() != 1:
            self.error("Cost Raster has too many bands")
            return
        if target.geometryType() != QGis.Line:
            self.error("Target has wrong geometry type")
            return 
        if ctrl_pt.geometryType() != QGis.Point:
            self.error("Target has wrong geometry type")


        batch_trace = gttracetool.GtBatchTrace(self.canvas,target,self.iface,cost,ctrl_pt,field)
        if batch_trace.runBatchTrace() == False:
            self.error("Failed to run batch trace, check your input data")
        return
    def toggle_trace_tool(self):
        
        if self.traceToolActive == True:
            self.deactivateTrace()
            return
        target = self.vector_layer_combo_box.currentLayer()
        cost = self.cost_layer_combo_box.currentLayer() 
        if not target:
            self.error("No target layer selected")
            return
        if not cost:
            self.error("No cost layer selected")
            return

        if cost.bandCount() != 1:
            self.error("Cost Raster has too many bands")
            return
        if target.geometryType() != QGis.Line:
            self.error("Target has wrong geometry type")
            return 
        self.tracetool = gttracetool.GtTraceTool(self.canvas,self.iface,target,cost)
        if not self.tracetool:
            self.error("Failed to create TraceTool.")
        #self.tracetool.deactivatedt.connect(self.deactivateTrace)
        if self.save_control_points.isChecked():
            ctrl_pt = self.controlpoint_layer_combo_box.currentLayer()
            if not ctrl_pt:
                self.error("No control point layer selected")
                return
            if ctrl_pt.geometryType() != QGis.Point:
                self.error("Control points are not points!")
                return
            self.tracetool.setControlPoints(self.controlpoint_layer_combo_box.currentLayer())
        if self.fit_plane.isChecked():
            dem = self.dem_layer_combo_box.currentLayer()
            if not dem:
                self.error("DEM layer not selected")
                return
            if dem.bandCount() != 1:
                self.error("DEM must be single band")
                return
            self.tracetool.setDem(dem)
            #self.info("Using DEM for planes")
        self.tracetool.invertCost(self.invert_cost.isChecked())
        self.run_trace_button.setText("Stop Digitizing")
        self.traceToolActive = True
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
