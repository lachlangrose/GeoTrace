
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
from PyQt4.QtCore import *
from PyQt4 import QtGui

from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from osgeo import gdal
from osgeo.gdalnumeric import *
from osgeo.gdalconst import *
import numpy as np
import time
import gttrace as trace


class GtTraceTool(QgsMapToolEmitPoint):
    def __init__(self, canvas,iface,target,cost):
        self.canvas = canvas
        self.iface = iface
        self.cost = cost
        self.target = target
        self.use_control_points = False
        self.xmin = self.cost.extent().xMinimum()
        self.ymin = self.cost.extent().yMinimum()
        self.xmax = self.cost.extent().xMaximum()
        self.ymax = self.cost.extent().yMaximum()
        self.xsize = self.cost.rasterUnitsPerPixelX()
        self.ysize = self.cost.rasterUnitsPerPixelY()
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        self.rubberBand = QgsRubberBand(self.canvas, QGis.Point)
        self.rubberBand.setColor(Qt.red)
        self.rubberBandLine = QgsRubberBand(self.canvas,QGis.Line)
        self.rubberBandLine.setColor(Qt.red)
        self.rubberBandLine.setWidth(1)
        #self.reset()
        self.trace = trace.ShortestPath()
    def reset(self):
        self.startPoint = self.endPoint = None
        self.isEmittingPoint = False
        self.rubberBand.reset(QGis.Point)
        self.trace = trace.ShortestPath()
    def delete_control_points(self):
        self.trace.remove_control_points()
        self.rubberBand.reset(QGis.Point)
    def addPoint(self,p):
        #self.rubberBand.reset(QGis.Line)
        self.rubberBand.addPoint(p, True)
        self.rubberBand.show()     
    def runTrace(self):
        self.rubberBandLine.reset(QGis.Line)
        self.trace.set_image(self.rasterToNumpy(self.cost)) 
        self.paths = self.trace.shortest_path()
        s = 0
        for p in self.paths:
            points = []
            for c in p:
                i = (c[0])
                j = (c[1])
                x_ = (float(i))*self.xsize+self.xmin
                y_ = (float(j))*self.ysize+self.ymin
                self.rubberBandLine.addPoint(QgsPoint(x_,y_),True,s)
            s+=1
    def setControlPoints(self, vector = None):
        if vector == None:
            self.use_control_points = False
            return 
        self.use_control_points = True
        self.control_points = vector
        return

    def addLine(self):

        targetlayerCRSSrsid = self.target.crs().srsid()

        renderer = self.canvas.mapRenderer()
        projectCRSSrsid = renderer.destinationCrs().srsid()
        if self.use_control_points:
            point_pr = self.control_points.dataProvider()
            point_fields = point_pr.fields()
            self.control_points.startEditing()
            pointlayerCRSSrsid = self.control_points.crs().srsid()

            for p in self.trace.nodes:

                fet = QgsFeature(point_fields)
                x_ = (float(p[0]))*self.xsize+self.xmin
                y_ = (float(p[1]))*self.ysize+self.ymin
                geom = QgsGeometry.fromPoint(QgsPoint(x_,y_))
                if layerCRSSrsid != projectCRSSrsid:
                    geom.transform(QgsCoordinateTransform(projectCRSSrsid,
                                                      layerCRSSrsid))
                fet.setGeometry(geom) 
                point_pr.addFeatures([fet])
            self.control_points.commitChanges()
        vl = self.target        
        pr = vl.dataProvider()
        fields = pr.fields()
        # Enter editing mode
        vl.startEditing()
        for p in self.paths:
            points = []
            for c in p:
                i = (c[0])
                j = (c[1])
                x_ = (float(i))*self.xsize+self.xmin
                y_ = (float(j))*self.ysize+self.ymin
                points.append(QgsPoint(x_, y_))
            fet = QgsFeature(fields)
            geom = QgsGeometry.fromPolyline(points)
            if targetlayerCRSSrsid != projectCRSSrsid:
                geom.transform(QgsCoordinateTransform(projectCRSSrsid,
                                                  targetlayerCRSSrsid))


            fet.setGeometry( geom  )

            pr.addFeatures( [ fet ] ) 
        vl.commitChanges()
        #self.iface.setActiveLayer(vl)
        #QgsMapLayerRegistry.instance().addMapLayer(vl)   
        self.rubberBandLine.reset(QGis.Line)
        self.reset()
        #self.deactivate()
    def canvasPressEvent(self, e):
        point = self.toMapCoordinates(e.pos())
        if type(self.cost) != QgsRasterLayer:
            print "error"
            return
        if e.button() == Qt.LeftButton:

           i = int((point[0] -self.xmin) / self.xsize)
           j = int(( point[1]-self.ymin) / self.ysize)
           self.rows = self.cost.height()
           self.columns = self.cost.width()
           j1 = j
           i1 = i
           self.trace.add_node([i1,j1])
           self.addPoint(point)
           self.runTrace()
        if e.button() == Qt.RightButton:
           self.addLine()
    def canvasReleaseEvent(self, e):
        self.isEmittingPoint = False
        #r = self.rectangle()
    def rasterToNumpy(self,layer):
        filepath = layer.dataProvider().dataSourceUri()
        ds = gdal.Open(filepath)
        array = np.array(ds.GetRasterBand(1).ReadAsArray())                     
        array = np.rot90(np.rot90(np.rot90(array)))
        return array
    def numpyToLayer(self,array,name):
        array = (np.rot90(array))
        outFile = name+".tiff"
        sx, sy = array.shape
        
        driver = gdal.GetDriverByName("GTiff")
        dsOut = driver.Create("/home/lgrose/out2.tiff", sx,sy)
        bandOut=dsOut.GetRasterBand(1)
        BandWriteArray(bandOut, array)
        bandOut = None
        dsOut = None
        layer = QgsRasterLayer("/home/lgrose/out2.tiff","out2.tiff")
        QgsMapLayerRegistry.instance().addMapLayer(layer)
    
    def deactivate(self):
        super(GtTraceTool, self).deactivate()
        self.emit(SIGNAL("deactivated()"))
