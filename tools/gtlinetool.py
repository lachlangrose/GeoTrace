# [Copyright (c) 2015 Lachlan Grose, Monash University]
from PyQt4.QtCore import *
from PyQt4 import QtGui

from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import numpy as np
import time
#Using code from http://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/canvas.html
class GtLineTool(QgsMapToolEmitPoint):
  def __init__(self, canvas,iface):
      self.canvas = canvas
      self.iface = iface
      QgsMapToolEmitPoint.__init__(self, self.canvas)
      self.rubberBand = QgsRubberBand(self.canvas, QGis.Polygon)
      self.rubberBand.setColor(Qt.red)
      self.rubberBand.setWidth(1)
      self.reset()

  def reset(self):
      self.startPoint = self.endPoint = None
      self.isEmittingPoint = False
      self.rubberBand.reset(QGis.Line)

  def canvasPressEvent(self, e):
      self.startPoint = self.toMapCoordinates(e.pos())
      self.endPoint = self.startPoint
      self.isEmittingPoint = True
      self.showRect(self.startPoint, self.endPoint)

  def canvasReleaseEvent(self, e):
      self.isEmittingPoint = False
      #r = self.rectangle()
      azimuth  = self.point1.azimuth(self.point2)
      newx = (self.point1.x() + self.point2.x()) /  2
      newy = (self.point1.y() + self.point2.y()) / 2
      point = QgsPoint(newx , newy)
      self.addPoint(point, azimuth) 
               
  def addPoint(self,point,strike):
      print "adding point"
      geom = QgsGeometry.fromPoint(point)
      layer = self.canvas.currentLayer()
      layerCRSSrsid = layer.crs().srsid()
      renderer = self.canvas.mapRenderer()
      projectCRSSrsid = renderer.destinationCrs().srsid()
      if layerCRSSrsid != projectCRSSrsid:
            geom.transform(QgsCoordinateTransform(projectCRSSrsid,
                                                  layerCRSSrsid))

      provider = layer.dataProvider()
      fields = provider.fields()
      atrlist = [field.name() for field in layer.pendingFields() ]
      layer.updateFields()
      f = QgsFeature(fields)
      #f[attrName] = azimuth
      f.setGeometry(geom)
      dip, ok = QtGui.QInputDialog.getInt(QtGui.QInputDialog(),
                                                  'Dip',
                                                  'Dip: ',
                                                  QtGui.QLineEdit.Normal, 
                                                  -90)
      if not ok:
            return
      if strike<0:
          strike = 360 - np.abs(strike)
      
      if strike >= 0 and strike <= 45:
          if dip < 0:
              strike = strike + 180
      elif strike > 45 and strike <= 135:
          if dip < 0:
              strike = strike + 180
      elif strike > 135 and strike <= 225:
          if dip > 0:
              strike = strike + 180
      elif strike >225 and strike <= 335:
          if dip > 0:
              strike = strike + 180
      elif strike > 335 and strike <= 360:
          if dip < 0:
              strike = strike -180
      print "after logic" 
      strikein = layer.fieldNameIndex('strike')
      dipin = layer.fieldNameIndex('dip')
      f['strike'] = strike
      f['dip'] = np.abs(dip)
      # this is the preferred way of adding features in QGIS >= 2.4
      # it respects default values, suppression of attribute form, reuse of recent values etc.
      if QGis.QGIS_VERSION_INT >= 20400:
        if self.iface.vectorLayerTools().addFeature(layer, {strikein:strike, dipin:dip}, geom):
            self.canvas.refresh()
            return True
        else:
            return False

        # compatibility code for older versions: QGIS < 2.4
      layer.beginEditCommand("Feature added")
      layer.addFeature(f)
        
      layer.endEditCommand()
         
      self.canvas.refresh()

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
      super(GtLineTool, self).deactivate()
      self.emit(SIGNAL("deactivated()"))
