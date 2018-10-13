# -*- coding: utf-8 -*-
"""
/***************************************************************************
 File Name: tools/gtstereo.py
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

import os.path,  sys
import numpy as np
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import *
from qgis.gui import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import mplstereonet
import random

class GtStereo(QtWidgets.QDialog):
    def __init__(self, canvas, iface, parent=None):
        super(GtStereo, self).__init__(parent)
        self.canvas = canvas
        self.iface = iface
        self.figure, self.ax = mplstereonet.subplots()
        self.ax.grid(color='k',linestyle='-',linewidth=0.1)
        self.ax.text(0.75,-0.04, "lower-hemisphere \n \"schmitt\" \n(equal area) \n projection.",transform = self.ax.transAxes, ha='left', va='center')
        self.canvas = FigureCanvas(self.figure)
        self.polesbutton = QtWidgets.QPushButton('Plot Poles')
        self.polesbutton.clicked.connect(self.plotpoles)
        self.circlebutton = QtWidgets.QPushButton('Fit Fold')
        self.circlebutton.clicked.connect(self.fitfold)
        self.densitybutton = QtWidgets.QPushButton('Plot Density')
        self.densitybutton.clicked.connect(self.plotdensity)
        self.resetbutton = QtWidgets.QPushButton('Clear Plot')
        self.resetbutton.clicked.connect(self.reset)
        self.addToPlot= QPushButton('Add to plot')
        self.addToPlot.clicked.connect(self.add_to_plot)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.vector_layer_combo_box = QgsMapLayerComboBox()
        self.vector_layer_combo_box.setCurrentIndex(-1)
        self.vector_layer_combo_box.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.dip_dir = QCheckBox("Dip Direction")
        self.dip_dir.setChecked(True)
        self.strike = QCheckBox("Strike")
        self.strike.stateChanged.connect(self.strikordirection)
        self.selected_features = QCheckBox()
        self.strike_combo_box = QgsFieldComboBox()
        self.dip_combo_box = QgsFieldComboBox()
        top_form_layout = QtWidgets.QFormLayout()
        layout = QtWidgets.QVBoxLayout()
        self.direction_name = QLabel("Dip Direction") 
        self.feature_type = QComboBox()
        self.feature_type.addItem('Poles to plane')
        self.feature_type.addItem('Lineations')
        self.feature_type.addItem('Poles to plane density')
        self.feature_type.addItem('Planes')
        self.feature_type.addItem('Lineation density')
        self.feature_type.addItem('Find fold axis')

        top_form_layout.addRow("Layer:",self.vector_layer_combo_box)
        top_form_layout.addRow(self.direction_name,self.strike_combo_box)
        top_form_layout.addRow(self.strike,self.dip_dir)
        top_form_layout.addRow("Dip:",self.dip_combo_box)
        top_form_layout.addRow("Selected Features Only:",self.selected_features)
        top_form_layout.addRow("Feature type: ", self.feature_type)
        self.vector_layer_combo_box.layerChanged.connect(self.strike_combo_box.setLayer)  # setLayer is a native slot function
        self.vector_layer_combo_box.layerChanged.connect(self.dip_combo_box.setLayer)  # setLayer is a native slot function
        self.vector_layer_combo_box.layerChanged.connect(self.layer_changed)
        layout.addLayout(top_form_layout)
        plot_object_list = QTableView()
        self.plot_object_model = QStandardItemModel(1,4)
        plot_object_list.setModel(self.plot_object_model)


        plot_and_table = QHBoxLayout()
        plot_and_table.addWidget(self.canvas)
        #plot_and_table.addWidget(plot_object_list)
        plot_and_table_w = QWidget()
        plot_and_table_w.setLayout(plot_and_table)
        layout.addWidget(plot_and_table_w)
        #layout.addWidget(plot_object_list)
        layout.addWidget(self.toolbar)
        #layout.addWidget(self.strike_combo)
        #layout.addWidget(self.dip_combo)
        bottom_form_layout = QtWidgets.QFormLayout()
        bottom_form_layout.addWidget(self.addToPlot)
        #bottom_form_layout.addWidget(self.circlebutton)
        #bottom_form_layout.addWidget(self.densitybutton)
        bottom_form_layout.addWidget(self.resetbutton)
        layout.addLayout(bottom_form_layout)
        self.setLayout(layout)
    def add_to_plot(self):
        if self.feature_type.currentText() == 'Poles to plane':
            self.plotpoles()
        if self.feature_type.currentText() == 'Lineations':
            self.plotlineations()
        if self.feature_type.currentText() =='Poles to plane density':
            self.plotdensity()
        if self.feature_type.currentText() ==  'Planes':
            self.plotcircles()
        if self.feature_type.currentText() ==  'Lineation density':
            self.plotlineations()
        if self.feature_type.currentText() == 'Find fold axis':
            self.fitfold()
        items = []
        items.append(QStandardItem(self.vector_layer_combo_box.currentLayer().name()))
        items.append(QStandardItem(self.feature_type.currentText()))
        #items.append(QStandardItem(str(len(strike))))
        self.plot_object_model.appendRow(items)
    def layer_changed(self,layer):
        if not self.dip_dir.isChecked():
            indx = self.strike_combo_box.findText("strike",Qt.MatchContains)
            self.strike_combo_box.setCurrentIndex(indx)
        if self.dip_dir.isChecked():
            indx = self.strike_combo_box.findText("dir",Qt.MatchContains)
            self.strike_combo_box.setCurrentIndex(indx)
        indx = self.dip_combo_box.findText("dip",Qt.MatchContains) 
        self.dip_combo_box.setCurrentIndex(indx)
    def strikordirection(self,*args,**kwargs):
        if self.strike.isChecked():
            self.direction_name.setText("Strike")
            indx = self.strike_combo_box.findText("strike",Qt.MatchContains)
            self.strike_combo_box.setCurrentIndex(indx)
        if not self.strike.isChecked():
            self.direction_name.setText("Dip Direction")
            indx = self.strike_combo_box.findText("dir",Qt.MatchContains)
            self.strike_combo_box.setCurrentIndex(indx)

    def onclick(self,event):
        strike, dip = mplstereonet.stereonet_math.geographic2pole(event.xdata,event.ydata)
        self.ax.plane(strike,dip)
        self.canvas.draw()
    def plotpoles(self):
        strike, dip = self.get_strike_dip()
        self.ax.hold(False)
        self.ax.hold(True)
        self.ax.pole(strike, dip,marker='o',color='black',markersize=2)
        self.ax.grid(True)
        self.canvas.draw()

    def plotlineations(self):
        trend, plunge = self.get_strike_dip(True)
        self.ax.hold(False)
        self.ax.hold(True)
        self.ax.line(plunge,trend,marker='o',color='black',markersize=2)
        self.ax.grid(True)
        self.canvas.draw()

    def reset(self):
        #hack to reset graph, just plot nothing
        strike = []
        dip = []
        self.ax.hold(False)
        self.ax.plane(strike, dip)
        self.ax.grid(True)
        self.canvas.draw()
        self.plot_object_model.clear()
    def get_strike_dip(self,lineation=False):
        strike = []
        dip = []
        dip_name = self.dip_combo_box.currentField()
        strike_name = self.strike_combo_box.currentField()

        features = self.vector_layer_combo_box.currentLayer().getFeatures()
        if self.selected_features.isChecked() == True:
            features = self.vector_layer_combo_box.currentLayer().selectedFeatures()
        for f in features:
            if f[dip_name] and f[strike_name]:
                dip.append(f[dip_name]) #self.dip_combo.currentText()])
                if self.dip_dir.isChecked() == True and lineation == False:
                    strike.append(f[strike_name]+90)
                else:
                    strike.append(f[strike_name])#self.strike_combo.currentText()]) 
        return strike, dip
    def plotdensity(self):
        strike, dip = self.get_strike_dip()
        # discards the old graph
        self.ax.hold(False)
        self.ax.hold(True)

        cax = self.ax.density_contourf(strike,dip,measurement='poles',cmap=plt.cm.Spectral)
        self.figure.colorbar(cax,ax=self.ax,orientation='horizontal')
        #self.ax.pole(strike, dip)
        self.ax.grid(True)
        # refresh canvas
        self.canvas.draw()

    def plotcircles(self):
        strike, dip = self.get_strike_dip()
        self.ax.hold(False)
        self.ax.plane(strike, dip)
        self.ax.grid()

        # refresh canvas
        self.canvas.draw()
    def fitfold(self):
        strike, dip = self.get_strike_dip()
                # discards the old graph
        self.ax.hold(True)
        fit_strike,fit_dip = mplstereonet.fit_girdle(strike,dip)
        lon, lat = mplstereonet.pole(fit_strike, fit_dip)
        (plunge,), (bearing,) = mplstereonet.pole2plunge_bearing(fit_strike, fit_dip)       
        template = u'Plunge / Direction of Fold Axis\n{:02.0f}\u00b0/{:03.0f}\u00b0'
        self.ax.annotate(template.format(plunge, bearing), ha='center', va='bottom',
            xy=(lon, lat), xytext=(-50, 20), textcoords='offset points',
            arrowprops=dict(arrowstyle='-|>', facecolor='black'))

        self.ax.plane(fit_strike, fit_dip, color='red', lw=2)
        self.ax.pole(fit_strike, fit_dip, marker='o', color='red', markersize=14)
        self.canvas.draw() 

