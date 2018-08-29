# -*- coding: utf-8 -*-
"""
/***************************************************************************
 File Name: tools/gtrose.py
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
#currentPath = os.path.dirname( __file__ )
#sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from qgis.core import *
from qgis.gui import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from matplotlib.projections import register_projection
import random
class GtRose(QtWidgets.QDialog):
    def __init__(self, canvas, iface, parent=None):
        super(GtRose, self).__init__(parent)
        self.canvas = canvas
        self.iface = iface
        self.figure = plt.Figure()
        self.ax = self.figure.add_subplot(1, 2, 1, projection = 'polar')
        self.hist_ax = self.figure.add_subplot(1,2,2)
        self.canvas = FigureCanvas(self.figure)
        self.ax.text(0.75,-0.04, "Rose diagram is \n number weighted",transform = self.ax.transAxes, ha='left', va='center')

        self.ax.set_theta_offset(0.5*np.pi) 
        self.ax.set_theta_direction(-1)

        # Just some button connected to `plot` method
        self.polesbutton = QtWidgets.QPushButton('Plot')
        self.polesbutton.clicked.connect(self.plot)
        #self.circlebutton = QtWidgets.QPushButton('Fit Fold')
        #self.circlebutton.clicked.connect(self.fitfold)
        #self.densitybutton = QtWidgets.QPushButton('Plot Density')
        #self.densitybutton.clicked.connect(self.plotdensity)
        self.resetbutton = QtWidgets.QPushButton('Clear Plot')
        self.resetbutton.clicked.connect(self.reset)

        self.vector_layer_combo_box = QgsMapLayerComboBox()
        self.vector_layer_combo_box.setCurrentIndex(-1)
        self.vector_layer_combo_box.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.dip_dir = QCheckBox("Dip Direction")
        self.strike = QCheckBox("Strike")
        self.dip_dir.setChecked(True)
        self.strike.stateChanged.connect(self.strikordirection)
        self.button_group = QButtonGroup()
        self.button_group.addButton(self.dip_dir)
        self.button_group.addButton(self.strike)

        self.selected_features = QCheckBox()
        self.strike_combo_box = QgsFieldComboBox()
        self.colour_combo_box = QgsFieldComboBox()
        #self.dip_combo_box = QgsFieldComboBox()
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.direction_name = QLabel("Dip Direction") 
        self.number_of_petals = QSpinBox()
        self.number_of_petals.setValue(18)
        self.length_bins = QSpinBox()
        self.length_bins.setValue(5)
        self.reverse_lines  = QCheckBox()
        self.alpha_value = QDoubleSpinBox()
        self.alpha_value.setMaximum(1.0)
        self.alpha_value.setMinimum(0.0)
        self.alpha_value.setValue(0.7)
        ##self.figure.canvas.mpl_connect('button_press_event',self.onclick)
        ## set the layout
        top_form_layout = QtWidgets.QFormLayout()
        layout = QtWidgets.QVBoxLayout()
        top_form_layout.addRow("Layer:",self.vector_layer_combo_box)
        top_form_layout.addRow(self.direction_name,self.strike_combo_box)
        top_form_layout.addRow("Colour map field: ", self.colour_combo_box)
        #top_form_layout.addRow("Dip:",self.dip_combo_box)
        top_form_layout.addRow(self.strike,self.dip_dir)
        top_form_layout.addRow("Selected Features Only:",self.selected_features)
        top_form_layout.addRow("Number of rose petals:",self.number_of_petals)
        top_form_layout.addRow("Length bins:",self.length_bins)
        top_form_layout.addRow("Reverse Colouring:",self.reverse_lines)
        top_form_layout.addRow("Plot Transparency:",self.alpha_value)
        self.vector_layer_combo_box.layerChanged.connect(self.strike_combo_box.setLayer)  # setLayer is a native slot function
        self.vector_layer_combo_box.layerChanged.connect(self.layer_changed)

        self.vector_layer_combo_box.layerChanged.connect(self.colour_combo_box.setLayer)  # setLayer is a native slot function
        #self.vector_layer_combo_box.layerChanged.connect(self.dip_combo_box.setLayer)  # setLayer is a native slot function
        layout.addLayout(top_form_layout)
        layout.addWidget(self.canvas)
        layout.addWidget(self.toolbar)
        
        ##layout.addWidget(self.strike_combo)
        ##layout.addWidget(self.dip_combo)
        bottom_form_layout = QtWidgets.QFormLayout()
        bottom_form_layout.addWidget(self.polesbutton)
        #bottom_form_layout.addWidget(self.circlebutton)
        #bottom_form_layout.addWidget(self.densitybutton)
        bottom_form_layout.addWidget(self.resetbutton)
        layout.addLayout(bottom_form_layout)
        self.setLayout(layout)
    def onclick(self,event):
        return
    def layer_changed(self,layer):
        if not self.dip_dir.isChecked():
            indx = self.strike_combo_box.findText("strike",Qt.MatchContains)
            self.strike_combo_box.setCurrentIndex(indx)
        if self.dip_dir.isChecked():
            indx = self.strike_combo_box.findText("dir",Qt.MatchContains)
            self.strike_combo_box.setCurrentIndex(indx)
    def strikordirection(self,*args,**kwargs):
        if self.strike.isChecked():
            self.direction_name.setText("Strike")
            indx = self.strike_combo_box.findText("strike",Qt.MatchContains)
            if not indx:
                indx = self.strike_combo_box.findText("azi",Qt.MatchContains)

            self.strike_combo_box.setCurrentIndex(indx)
        if not self.strike.isChecked():
            self.direction_name.setText("Dip Direction")
            indx = self.strike_combo_box.findText("dir",Qt.MatchContains)
            self.strike_combo_box.setCurrentIndex(indx)

    
    def plot(self):
        if self.strike_combo_box.currentField() is None:
            return
        n = int(self.vector_layer_combo_box.currentLayer().featureCount())
        data = np.zeros((2,n))
        i = 0
        strike_name = self.strike_combo_box.currentField()        
        length_name = self.colour_combo_box.currentField()
        features = self.vector_layer_combo_box.currentLayer().getFeatures()
        if self.selected_features.isChecked() == True:
            features = self.vector_layer_combo_box.currentLayer().selectedFeatures()
        #get data from features
            
        for f in features:
            #d = f.geometry().azimuth()
            if strike_name:
               d= f[strike_name]
            l =  f.geometry().length()
            if length_name:
                l =  f[length_name]
            if d == NULL:
                continue
            data[0,i] = d
            if self.dip_dir.isChecked():
                data[0,i]+=90.
            if data[0,i] >= 360:
                data[0,i] -=360
            data[1,i] = l#f.geometry().length()
            i = i + 1
        weighted = False
        
        angle = self.number_of_petals.value()#360 / angle
        nsection = 360 / angle

        nsection = int(round(nsection)) #round to nearest int
        #update angle 
        angle = 360. / nsection
        sectionadd = 180./angle
        direction = np.linspace(0, 360, nsection, False) / 180. * np.pi
        #array to store the accumulator
        length_sections = self.length_bins.value()
        bins = np.zeros((nsection,length_sections+2))
        max_length = np.max(data[1,:])
        l_bin_size = max_length / length_sections

        for i in range(data.shape[1]):
        #column 2 is the angle column number - 1

            tmp = int((data[0,i] - data[0,i] % angle) / angle)

            ltmp = int((data[1,i] - data[1,i] % l_bin_size ) / l_bin_size)
            if self.reverse_lines.isChecked() == True:
            #    #longest lines in the centre of the plot
                ltmp = length_sections-ltmp
            #find which bin the line is in for orientation
            if tmp > sectionadd:
                tmp2 = tmp - sectionadd
                tmp2 = int(tmp2)
            if tmp < sectionadd:
                tmp2 = tmp + sectionadd
                tmp2 = int(tmp2)
            else:
                #update accumulator for this feature
                bins[tmp,ltmp+1] +=1
                bins[tmp2,ltmp+1] +=1
               
        width = angle / 180.0 * np.pi * np.ones(nsection)
        #if self.normalise_by_feature_number.isChecked():
        bins /= float(n)
        #last column is the frequency for the orientation
        #eg total petal length
        bins[:,-1] = np.sum(bins[:,:-1],axis=1)
        #c is pseudocolor, i+1 is index of length bin sum to i is the bottom position
        bottoms = np.zeros(nsection)
        n,b , patches = self.hist_ax.hist(data[1,:],length_sections)
        for i, c in enumerate(np.linspace(0,1,length_sections)):
            bars = self.ax.bar(direction, bins[:,i+1],\
            width=width,bottom=bottoms)
            patches[i].set_facecolor(plt.cm.Spectral(c))
            patches[i].set_alpha(self.alpha_value.value())
            #bars = self.ax.bar(direction, bins[:,-1],width=width,bottom=0.0)
            for bar in bars:
                bar.set_facecolor(plt.cm.Spectral(c))#cmap(c)plt.cm.Greys(.5))
                bar.set_edgecolor(None)
                bar.set_alpha(self.alpha_value.value())
            bottoms +=bins[:,i+1]

        #self.figure.title('Histogram')
        self.ax.set_theta_offset(0.5*np.pi) 
        self.ax.set_theta_direction(-1)
        self.ax.set_rticks([])
        self.hist_ax.set_title("Length Histogram")
        self.ax.set_title("Rose Diagram")
        self.canvas.draw()
        return
    def reset(self):
        self.ax.clear()
        self.hist_ax.clear()
        ##hack to reset graph, just plot nothing
        #self.ax.hold(False)
        #self.ax.bar([],[], 0, bottom=0.0)
        #self.ax.set_theta_offset(0.5*np.pi) 
        #self.ax.set_theta_direction(-1)
        ##self.ax.grid(True)
        self.canvas.draw()


    def plotdensity(self):
        return
    def plotcircles(self):
        return
    def fitfold(self):
        return
