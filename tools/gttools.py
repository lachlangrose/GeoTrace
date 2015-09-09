from PyQt4.QtCore import *
from PyQt4 import QtGui

from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import numpy as np
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

        width = np.abs(r.xMaximum() - r.xMinimum())
        height = np.abs(r.yMaximum() - r.yMinimum())
        xmax = r.xMaximum()
        xmin = r.xMinimum()

        ymax = r.yMaximum()
        ymin = r.yMinimum()

        xstep = width / nx
        ystep = height / ny
        for a in range(1,nx):
            for b in range(1,ny):
                nxmax = xmin+a*xstep
                nxmin = xmin+(a-1)*xstep
                nymax = ymin+b*ystep
                nymin = ymin+(b-1)*ystep
                self.canvas.setExtent(QgsRectangle(nxmin,nymin,nxmax,nymax))
                self.canvas.refresh()

                ##setting up print composer
                mapRenderer = self.iface.mapCanvas().mapRenderer()
                c = QgsComposition(mapRenderer)
                c.setPlotStyle(QgsComposition.Print)

                x, y = 0, 0
                w, h = c.paperWidth(), c.paperHeight()
                composerMap = QgsComposerMap(c, x,y,w,h)
                c.addItem(composerMap)
                #item.setComposerMap(composerMap)
                #item.applyDefaultSize()
                #c.addItem(item)
                name = text+str(a)+str(b)
                dpi = 300#c.printResolution
                dpmm = dpi / 25.4
                width = int(dpmm * c.paperWidth())
                height = int(dpmm * c.paperHeight())

                # create output image and initialize it
                image = QImage(QSize(width, height), QImage.Format_ARGB32)
                image.setDotsPerMeterX(dpmm * 1000)
                image.setDotsPerMeterY(dpmm * 1000)
                image.fill(0)

                # render the composition
                imagePainter = QPainter(image)
                sourceArea = QRectF(0, 0, c.paperWidth(), c.paperHeight())
                targetArea = QRectF(0, 0, width, height)
                c.render(imagePainter, targetArea, sourceArea)
                imagePainter.end()

                image.save(name+".tif", "tif")
                #create a world file for the image
                c.setWorldFileMap(composerMap)
                c.setGenerateWorldFile(True)
                wf = c.computeWorldFileParameters()
                with open(name+".tfw","w") as f:
                    f.write('%s\n' % wf[0])
                    f.write('%s\n' % int(wf[1]))
                    f.write('%s\n' % int(wf[3]))
                    f.write('%s\n' % wf[4])
                    f.write('%s\n' % wf[2])
                    f.write('%s\n' % wf[5])
               
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

