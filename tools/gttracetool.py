
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
import trace
#Using code from http://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/canvas.html
class GtTraceTool(QgsMapToolEmitPoint):
  def __init__(self, canvas,iface):
      self.canvas = canvas
      self.iface = iface
      QgsMapToolEmitPoint.__init__(self, self.canvas)
      self.rubberBand = QgsRubberBand(self.canvas, QGis.Polygon)
      self.rubberBand.setColor(Qt.red)
      self.rubberBand.setWidth(1)
      self.reset()
      self.trace = trace.ShortestPath()
  def reset(self):
      self.startPoint = self.endPoint = None
      self.isEmittingPoint = False
      self.rubberBand.reset(QGis.Line)

  def canvasPressEvent(self, e):
      
      point = self.toMapCoordinates(e.pos())
      layer = self.iface.activeLayer()
      if type(layer) != QgsRasterLayer:
          print "error"
          return
      if e.button() == Qt.LeftButton:
         self.xmin = layer.extent().xMinimum()
         self.ymin = layer.extent().yMinimum()
         self.xsize = layer.rasterUnitsPerPixelX()
         self.ysize = layer.rasterUnitsPerPixelY()
         i = int((point[0] - self.xmin) / self.xsize)
         j = int((point[1] - self.ymin) / self.ysize)
         rows = layer.height()
         columns = layer.width()
         self.trace.add_node([i,j])
      if e.button() == Qt.RightButton:
         self.trace.set_image(self.rasterToNumpy(layer)) 
         self.trace.setup()
         coords = self.trace.shortest_path()
         points = []
         ltype = 'LineString'
         inLayerCRS = layer.crs().authid()

         vl = QgsVectorLayer(ltype + '?crs='+inLayerCRS, \
             'ransac_lines', \
             'memory')
         
         pr = vl.dataProvider()
         # Enter editing mode
         vl.startEditing()
         print "adding points"
         for c in coords:
             points.append(QgsPoint(c[0]*self.xsize+self.xmin,c[1]*self.ysize+self.ymin))
         fet = QgsFeature()
         print "adding geometry"
         fet.setGeometry( QgsGeometry.fromPolyline(points) )
         pr.addFeatures( [ fet ] ) 
         vl.commitChanges()
         self.iface.setActiveLayer(vl)
         QgsMapLayerRegistry.instance().addMapLayer(vl)   
         self.numpyToLayer(self.trace.get_visited())
         self.deactivate()
  def canvasReleaseEvent(self, e):
      self.isEmittingPoint = False
      #r = self.rectangle()
  def rasterToNumpy(self,layer):
      filepath = layer.dataProvider().dataSourceUri()
      ds = gdal.Open(filepath)
      array = np.array(ds.GetRasterBand(1).ReadAsArray())                     
      return array
  def numpyToLayer(self,array):
      array = np.rot90(array)
      outFile = "out2.tiff"
      sx, sy = array.shape
      
      driver = gdal.GetDriverByName("GTiff")
      dsOut = driver.Create("/home/lgrose/out2.tiff", sx,sy)
      bandOut=dsOut.GetRasterBand(1)
      BandWriteArray(bandOut, array)
      bandOut = None
      dsOut = None
      layer = QgsRasterLayer("/home/lgrose/out2.tiff","out2.tiff")
      QgsMapLayerRegistry.instance().addMapLayer(layer)

  #def addPoint(self,point,strike):
      
  def canvasMoveEvent(self, e):
      if not self.isEmittingPoint:
        return

      self.endPoint = self.toMapCoordinates(e.pos())
      self.showRect(self.startPoint, self.endPoint)

  def showRect(self, startPoint, endPoint):
      self.rubberBand.reset(QGis.Line)
      if startPoint.x() == endPoint.x() or startPoint.y() == endPoint.y():
        return

      self.point1 = QgsPoint(startPoint.x(), startPoint.y())
      self.point2 = QgsPoint(endPoint.x(), endPoint.y())
      self.rubberBand.addPoint(self.point1, False)
      self.rubberBand.addPoint(self.point2, True)    # true to update canvas
      self.rubberBand.show()

  def deactivate(self):
      super(GtTraceTool, self).deactivate()
      self.emit(SIGNAL("deactivated()"))
