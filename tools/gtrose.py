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
import matplotlib.gridspec as gridspec

import random
class GtRose(QtWidgets.QDialog):
    def __init__(self, canvas, iface, parent=None):
        super(GtRose, self).__init__(parent)
        self.canvas = canvas
        self.iface = iface
        self.figure = plt.Figure(figsize=(10,10))
        #use gridspec to try and make the histogram a bit shorter to fit with the rose diagram
        #basically just adding padding 
        gs2 = gridspec.GridSpec(8, 3,height_ratios=[8,8,8,8,8,8,8,1])
        gs2.update(wspace=0.75,hspace=0.05)
        self.ax = self.figure.add_subplot(gs2[1:-2, :-1],projection='polar')
        self.rose_title_ax = self.figure.add_subplot(gs2[0:1, :-1])
        self.rose_title_ax.axis('off')
        self.hist_ax = self.figure.add_subplot(gs2[1:-2, -1])
        #tricking mpl to put the titles level
        self.hist_title_ax = self.figure.add_subplot(gs2[0:1, -1])
        self.hist_title_ax.axis('off')
        self.cax = self.figure.add_subplot(gs2[-1:, :])
        self.cax.axis('off')
        self.canvas = FigureCanvas(self.figure)
        #self.ax.text(0.75,-0.04, "Rose diagram is \n number weighted",transform = self.ax.transAxes, ha='left', va='center')
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
        self.max_length = QDoubleSpinBox()
        self.max_length.setMaximum(9999999.0)
        self.max_length.setMinimum(0.0)
        self.max_length.setValue(0.)
        self.use_max_length = QCheckBox()
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
        top_form_layout.addRow("Number of length bins:",self.length_bins)
        top_form_layout.addRow("Reverse Colouring:",self.reverse_lines)
        top_form_layout.addRow("Plot Transparency:",self.alpha_value)
        top_form_layout.addRow("Use colour map max:",self.use_max_length)
        top_form_layout.addRow("Colour map max:",self.max_length)
        self.max_length.setEnabled(False)
        self.use_max_length.stateChanged.connect(self.toggle_use_max_length)
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
        #self.ax.set_tick_params(pad=5)
        self.hist_title_ax.set_title("Length Histogram")
        self.rose_title_ax.set_title("Rose Diagram")
        self.ax.tick_params(axis='both', which='major', labelsize=6)
        self.hist_ax.tick_params(axis='both', which='major', labelsize=6)
        self.setLayout(layout)
    def onclick(self,event):
        return
    def toggle_use_max_length(self,*args,**kwargs): #not sure what the arguments it gives are but just catch them using args and kwargs
        if self.use_max_length.isChecked():
            self.max_length.setEnabled(True)
        else:
            self.max_length.setEnabled(False)
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
        
        nsection = self.number_of_petals.value()#360 / angle
        #nsection = 360 / angle

        nsection = int(round(nsection)) #round to nearest int

        sectadd = nsection
        #update angle 
        angle = 180. / nsection
        #sectionadd = 180./angle
        direction = np.linspace(0, 180, nsection, False) / 180. * np.pi
        direction = np.hstack([direction,(np.linspace(0, 180, nsection, False)+180) / 180. * np.pi])
        nsection = 2*nsection
        #array to store the accumulator
        length_sections = self.length_bins.value()
        bins = np.zeros((nsection,length_sections+2))
        max_length = np.max(data[1,:])
        if self.use_max_length.isChecked():
            max_length = self.max_length.value()
        else:
            self.max_length.setValue(max_length)
        if max_length <= 0:
            print("max_length = 0")
            return
        l_bin_size = max_length / length_sections
        #create a fake image for a colorbar
        Z = [[0,0],[0,0]]
        levels = np.arange(0,max_length+l_bin_size,l_bin_size)
        CS3 = plt.contourf(Z, levels, cmap=plt.cm.Spectral)
        plt.clf()
        #now do real plotting
        for i in range(data.shape[1]):
        #column 2 is the angle column number - 1
            f_angle = data[0,i]
            if f_angle > 180.0:
                f_angle = f_angle- 180.
            if f_angle < 0.0:
                f_angle = f_angle+180.
            tmp = (int(((f_angle)/angle))%nsection)# - data[0,i] % angle) / angle)
            ltmp = int((data[1,i] - data[1,i] % l_bin_size ) / l_bin_size)
            tmp2 = tmp + sectadd 
            if self.reverse_lines.isChecked() == True:
            #    #longest lines in the centre of the plot
                ltmp = length_sections-ltmp
            ##find which bin the line is in for orientation
            #if tmp > sectionadd:
            #    tmp2 = tmp - sectionadd
            #    tmp2 = int(tmp2)
            #if tmp < sectionadd:
            #    tmp2 = tmp + sectionadd
            #    tmp2 = int(tmp2)
            #update accumulator for this feature
            bins[tmp,ltmp+1] +=1
            if tmp2 < nsection:
                bins[tmp2,ltmp+1] +=1
            #print(direction[tmp],direction[tmp2])
               
        width = angle / 180.0 * np.pi * np.ones(nsection)
        #if self.normalise_by_feature_number.isChecked():
        bins /= float(n)
        #last column is the frequency for the orientation
        #eg total petal length
        bins[:,-1] = np.sum(bins[:,:-1],axis=1)
        #c is pseudocolor, i+1 is index of length bin sum to i is the bottom position
        bottoms = np.zeros(nsection)
        direction+=np.deg2rad(angle/2.)
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
        self.hist_ax.set_xlim([0,max_length])
        self.figure.sca(self.ax)
        self.cb = self.figure.colorbar(CS3,orientation='horizontal',cax=self.cax)
        self.cax.axis('on')
        self.cax.tick_params(axis='both', which='major', labelsize=6)

        self.canvas.draw()
        return
    def reset(self):
        self.ax.clear()
        self.hist_ax.clear()
        #self.cb.remove()
        self.cax.clear()
        self.cax.axis('off')

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
