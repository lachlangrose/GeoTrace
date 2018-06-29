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
import inspect
import importlib
#try importing gttracetool and associated dependencies, if an import error occurs trace_imported becomes false and we fail-friendly.
trace_imported  = True 
try:
    import gttracetool
except ImportError:
    trace_imported = False
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from qgis.core import *
from qgis.gui import *

_plugin_name_ = "GeoTrace"


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
        
        
        #try and get access to gttrace tool, installing the necessary (bundled) libraries if need be
        global trace_imported
        if not trace_imported:
            import install_dependencies as installer
            QMessageBox.information(self, _plugin_name_, 'Installing dependencies. \
                \nPlease ensure you are connected to the internet\
                \nThis may take a few minutes')
            #self.iface.messageBar().pushMessage(
            #    "Warning", "Installing dependencies, this may take a few minutes.",
            #     level=QgsMessageBar.WARNING)

            #install dependencies. This will throw an assertion error if anything fails. 
            installer.Installer().install() #lol
            global gttracetool
            import gttracetool
            trace_imported = True
            
        #trace imported succesfully - install either succesfull or not needed
        if trace_imported:
            tab_layout.addTab(self.setup_trace(),"Trace")
            tab_layout.addTab(self.setup_advanced_trace(),"Advanced Trace")
            tab_layout.addTab(self.setup_cost_calculator(),"Cost Calculator")
            tab_layout.addTab(self.setup_stereonet(),"Steronet")
            tab_layout.addTab(self.setup_rose(),"Rose")
            
        #create tabs that don't have dependencies
        tab_layout.addTab(self.setup_about(),"About")
        self.dialog_layout.addWidget(tab_layout)
        
    def setup_error(self):
        error_widget= QWidget()
        main_layout = QGridLayout()
        #missing = QGroupBox("Install Missing Dependencies")
        install_button = QPushButton('Install')
        main_layout.addWidget(install_button)
        install_button.clicked.connect(lambda: self.install_deps())#lambda: install.install())
        error_widget.setLayout(main_layout)
        return error_widget
    def install_deps(self):
        import install_dependencies as installer
        install = installer.Installer()
        success = install.install()
        self.setup_gui()
		
        if success:
            QMessageBox.information(self, _plugin_name_, 'Dependencies installed')
            import gttracetool
            self.setup_gui()
            trace_imported = True
        if not success:
            QMessageBox.warning(self, _plugin_name_, 'Installing dependencies failed')

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
        
        #load html file - N.B. - this should really be in the qrc file?
        filepath = inspect.getfile(inspect.currentframe())
        os.chdir(os.path.dirname(filepath))
        about = QFile("about.html")
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
        vector_group = QGroupBox("Batch Trace Mode")
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

        self.run_advanced_trace_button = QPushButton("Run")
        vector_layout.addRow(self.run_advanced_trace_button)
        #vector_layout.addWidget(create_memory_layer)

        batch_line = QGroupBox("Batch Line Tools")
        batch_line_form = QFormLayout()
        self.linetools_vector_layer_combo_box = QgsMapLayerComboBox()
        self.linetools_vector_layer_combo_box.setCurrentIndex(-1)
        self.linetools_vector_layer_combo_box.setFilters(QgsMapLayerProxyModel.LineLayer)
        self.linetools_dem_layer_combo_box = QgsMapLayerComboBox()
        self.linetools_dem_layer_combo_box.setCurrentIndex(-1)
        self.linetools_dem_layer_combo_box.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.run_line_tools = QPushButton("Calculate Plane for Trace using DEM")
        
        batch_line_form.addRow("Lines",self.linetools_vector_layer_combo_box)
        batch_line_form.addRow("DEM",self.linetools_dem_layer_combo_box)
        batch_line_form.addRow(self.run_line_tools)

        batch_line.setLayout(batch_line_form)

        self.run_line_tools.clicked.connect(self.run_batch_line)

        trace_main_layout.addWidget(vector_group)
        trace_main_layout.addWidget(batch_line)
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
        self.addCost('_phase','Phase Congruency')
        if importlib.find_loader('phasepack') is None:
            self.costs[-1][1].setEnabled(False)
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
        main_group = QGroupBox()
        main_layout = QFormLayout()

        #get current polylines in project
        self.vector_layer_combo_box = QgsMapLayerComboBox()
        self.vector_layer_combo_box.setCurrentIndex(-1)
        self.vector_layer_combo_box.setFilters(QgsMapLayerProxyModel.LineLayer)
        self.vector_layer_combo_box.currentIndexChanged.connect(self.deactivateTrace)
        main_layout.addRow("Output Polyline Trace Layer",self.vector_layer_combo_box)

        #save control points used in trace
        self.save_control_points = QRadioButton("Store Control Points") 
        self.save_control_points.toggled.connect(self.show_control_point_combo_box)
        self.save_control_points.toggled.connect(self.deactivateTrace) #activate comb when ticked
        main_layout.addRow("Save Control Points",self.save_control_points )
        #get point layers for control points
        self.controlpoint_layer_combo_box = QgsMapLayerComboBox()
        self.controlpoint_layer_combo_box.setCurrentIndex(-1)
        self.controlpoint_layer_combo_box.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.controlpoint_layer_combo_box.currentIndexChanged.connect(self.deactivateTrace)
        self.controlpoint_layer_combo_box.setEnabled(False)
        main_layout.addRow("Control Point Layer",self.controlpoint_layer_combo_box)

        #get single band raster layers for cost function
        self.cost_layer_combo_box = QgsMapLayerComboBox()
        self.cost_layer_combo_box.setCurrentIndex(-1)
        self.cost_layer_combo_box.setFilters(QgsMapLayerProxyModel.RasterLayer)
        main_layout.addRow("Cost Layer",self.cost_layer_combo_box)
    
        #invert cost button
        self.invert_cost = QCheckBox()
        self.invert_cost.toggled.connect(self.deactivateTrace)
        main_layout.addRow("Invert Cost", self.invert_cost)
        
        #fit planes using dem?
        self.fit_plane = QCheckBox()
        main_layout.addRow("Fit planes using DEM",self.fit_plane)
        self.fit_plane.toggled.connect(self.show_plane_combo_box)
        #choose dem layer
        self.dem_layer_combo_box = QgsMapLayerComboBox()
        self.dem_layer_combo_box.setCurrentIndex(-1)
        self.dem_layer_combo_box.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.dem_layer_combo_box.currentIndexChanged.connect(self.deactivateTrace)
        self.dem_layer_combo_box.setEnabled(False)
        main_layout.addRow("DEM layer",self.dem_layer_combo_box)
        self.run_trace_button = QPushButton("Start Digitizing")
        self.run_trace_button.clicked.connect(self.toggle_trace_tool)
        main_layout.addRow(self.run_trace_button)

        self.traceToolActive = False
        main_group.setLayout(main_layout)
        trace_main_layout.addWidget(main_group)
        trace_widget.setLayout(trace_main_layout)
         
        return trace_widget
    def deactivateTrace(self):
        if self.traceToolActive == False:
            return
        #if there are points in the trace do you want to keep them?
        if len(self.tracetool.paths) > 0:
            msg = "Save trace?"
            reply = QMessageBox.question(self, 'Deactivating Trace Tool', 
                     msg, QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.tracetool.addLine()
        self.tracetool.rubberBandLine.reset(QgsWkbTypes.LineGeometry)
        self.tracetool.rubberBand.reset(QgsWkbTypes.PointGeometry)
        self.tracetool.deactivate()
        self.traceToolActive = False
        self.canvas.setMapTool(QgsMapToolPan(self.canvas))
        self.run_trace_button.setText("Start Digitizing")
        return
    def updateCostName(self,string=None):
        layer = self.raster_layer_combo_box.currentLayer()
        if layer is None:
            return

        name = layer.name()
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
    def run_batch_line(self):
        line = self.linetools_vector_layer_combo_box.currentLayer()
        dem = self.linetools_dem_layer_combo_box.currentLayer()
        line_tool = gttracetool.GtLineTools(line)
        line_tool.calculate_planes(dem)
    def run_advanced_trace_tool(self):
        target = self.at_vector_layer_combo_box.currentLayer()
        cost = self.at_cost_layer_combo_box.currentLayer() 
        ctrl_pt = self.at_controlpoint_layer_combo_box.currentLayer()
        field= self.unique_field.currentField()
        if target is None:
            self.error("No output layer selected")

            return
        if cost is None:
            self.error("No cost layer selected")
            return
        if ctrl_pt is None:
            self.error("No control points layer selected")
            return
        if field is None:
            self.error("No unique field iD selected")
            return
        if cost.bandCount() != 1:
            self.error("Cost Raster has too many bands")
            return
        if target.geometryType() != QgsWkbTypes.LineGeometry:
            self.error("Output layer has wrong geometry type")
            return 
        if ctrl_pt.geometryType() != QgsWkbTypes.PointGeometry:
            self.error("Control point layer has wrong geometry type")


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
        if target is None:
            self.error("No output layer selected")
            return
        if cost is None:
            self.error("No cost layer selected")
            return

        if cost.bandCount() != 1:
            self.error("Cost Raster has too many bands")
            return
        if target.geometryType() != QgsWkbTypes.LineGeometry:
            self.error("Output layer has wrong geometry type")
            return 
        self.tracetool = gttracetool.GtTraceTool(self.canvas,self.iface,target,cost)
        if self.tracetool is None:
            self.error("Failed to create TraceTool.")
        if self.save_control_points.isChecked():
            ctrl_pt = self.controlpoint_layer_combo_box.currentLayer()
            if ctrl_pt is None:
                self.error("No control point layer selected")
                return
            if ctrl_pt.geometryType() != QgsWkbTypes.PointGeometry:
                self.error("Control points are not points!")
                return
            self.tracetool.setControlPoints(self.controlpoint_layer_combo_box.currentLayer())
        if self.fit_plane.isChecked():
            dem = self.dem_layer_combo_box.currentLayer()
            if dem is None:
                self.error("DEM layer not selected")
                return
            if dem.bandCount() != 1:
                self.error("DEM must be single band")
                return
            self.tracetool.setDem(dem)
        self.tracetool.invertCost(self.invert_cost.isChecked())
        self.run_trace_button.setText("Stop Digitizing")
        self.traceToolActive = True
        self.canvas.setMapTool(self.tracetool)
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
        #print "Info: "+ msg
        QMessageBox.information(self, _plugin_name_, msg)

    def warn(self, msg):
        print("Warning: "+ msg)
        QMessageBox.warning(self, _plugin_name_, msg)

    def error(self, msg):
        print("Error: "+ msg)
        QMessageBox.critical(self, _plugin_name_, msg)
