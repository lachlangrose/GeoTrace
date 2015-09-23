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
import numpy as np
import time
#Using code from http://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/canvas.html
class GtRectangleTool(QgsMapToolEmitPoint):
  def __init__(self, canvas,iface):
      self.canvas = canvas
      self.iface = iface
      QgsMapToolEmitPoint.__init__(self, self.canvas)
      self.rubberBand = QgsRubberBand(self.canvas, QGis.Polygon)
      #self.rubberBand.setColor(Qt.red)
      self.rubberBand.setWidth(1)
      self.reset()

  def reset(self):
      self.startPoint = self.endPoint = None
      self.isEmittingPoint = False
      self.rubberBand.reset(QGis.Polygon)

  def canvasPressEvent(self, e):
      self.startPoint = self.toMapCoordinates(e.pos())
      self.endPoint = self.startPoint
      self.isEmittingPoint = True
      self.showRect(self.startPoint, self.endPoint)

  def canvasReleaseEvent(self, e):
      self.isEmittingPoint = False
      r = self.rectangle()
      if r is not None:
        ##what to do
        #bit of a quick and dirty gui to allow the user to customise the number
        # of tiles and the names of the tiles. In the future create a proper dialog
        #allowing for all to be entered in the same page.
        text, ok = QtGui.QInputDialog.getText(QtGui.QInputDialog(),
                                                  'GeoTools Tile Creator',
                                                  'Base Tile Name: ',
                                                  QtGui.QLineEdit.Normal, 
                                                  'base_map_tile')
        if not ok:
            return
        nx, ok = QtGui.QInputDialog.getInt(QtGui.QInputDialog(),
                                                  'GeoTools Tile Creator',
                                                  'Number of tiles in x direction: ',
                                                  QtGui.QLineEdit.Normal, 
                                                  5)
        if not ok:
            return
        ny, ok = QtGui.QInputDialog.getInt(QtGui.QInputDialog(),
                                                  'GeoTools Tile Creator',
                                                  'Number of tiles in x direction: ',
                                                  QtGui.QLineEdit.Normal, 
                                                  3)

        if not ok:
            return
        #Work out the size of each tile
        width = np.abs(r.xMaximum() - r.xMinimum())
        height = np.abs(r.yMaximum() - r.yMinimum())
        xmax = r.xMaximum()
        xmin = r.xMinimum()

        ymax = r.yMaximum()
        ymin = r.yMinimum()

        xstep = width / nx
        ystep = height / ny
        for a in range(0,nx+1):
            for b in range(0,ny+1):
                nxmax = xmin+a*xstep
                nxmin = xmin+(a-1)*xstep
                nymax = ymin+b*ystep
                nymin = ymin+(b-1)*ystep
                print nxmax, nxmin, nymax, nymin
                rect  = QgsRectangle(nxmin,nymin,nxmax,nymax)
                self.iface.mapCanvas().setExtent(rect)
                self.iface.mapCanvas().refresh()
                #Ask user if the map has loaded
                ok = QMessageBox.question(QtGui.QWidget(), 'GeoTools', "Has the map loaded?", 
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                #c, ok = QtGui.QInputDialog.getInt(QtGui.QInputDialog(),
                #                          'GeoTools Tile Creator',
                #                          'continuen: ',
                #                          QtGui.QLineEdit.Normal, 
                #                          5)
                if not ok:
                    return
                name = text+str(a)+str(b)
                self.iface.mapCanvas().saveAsImage(name+'.tif',None,'tif')
               
               
  def canvasMoveEvent(self, e):
      if not self.isEmittingPoint:
        return

      self.endPoint = self.toMapCoordinates(e.pos())
      self.showRect(self.startPoint, self.endPoint)

  def showRect(self, startPoint, endPoint):
      self.rubberBand.reset(QGis.Polygon)
      if startPoint.x() == endPoint.x() or startPoint.y() == endPoint.y():
        return

      point1 = QgsPoint(startPoint.x(), startPoint.y())
      point2 = QgsPoint(startPoint.x(), endPoint.y())
      point3 = QgsPoint(endPoint.x(), endPoint.y())
      point4 = QgsPoint(endPoint.x(), startPoint.y())

      self.rubberBand.addPoint(point1, False)
      self.rubberBand.addPoint(point2, False)
      self.rubberBand.addPoint(point3, False)
      self.rubberBand.addPoint(point4, True)    # true to update canvas
      self.rubberBand.show()

  def rectangle(self):
      if self.startPoint is None or self.endPoint is None:
        return None
      elif self.startPoint.x() == self.endPoint.x() or self.startPoint.y() == self.endPoint.y():
        return None

      return QgsRectangle(self.startPoint, self.endPoint)

  def deactivate(self):
      super(GtRectangleTool, self).deactivate()
      self.emit(SIGNAL("deactivated()"))

