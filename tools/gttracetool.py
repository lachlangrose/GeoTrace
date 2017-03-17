# -*- coding: utf-8 -*-
"""
/***************************************************************************
 File Name: tools/gttacetool.py
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
import uuid

class GtTraceTool(QgsMapToolEmitPoint):
    def __init__(self, canvas,iface,target,cost):
        #qgis layers/interface
        self.canvas = canvas
        self.iface = iface
        self.cost = cost
        self.target = target
        #crs reprojection stuff
        self.targetlayerCRSSrsid = self.target.crs().srsid()
        self.costlayerCRSSrsid = self.cost.crs().srsid()
        self.renderer = self.canvas.mapRenderer()
        self.projectCRSSrsid = self.renderer.destinationCrs().srsid()
        self.use_control_points = False
        self.use_dem_for_planes = False
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
        self.trace = trace.ShortestPath()
        self.invert = False
        self.trace.set_image(self.rasterToNumpy(self.cost)) 
    def reset(self):
        self.startPoint = self.endPoint = None
        self.isEmittingPoint = False
        self.rubberBand.reset(QGis.Point)
        self.trace.remove_control_points()
    def invertCost(self,flag):
        if flag == True:
            array = self.rasterToNumpy(self.cost)
            max_v = np.max(array)
            array = max_v+1 - array
            self.trace.set_image(array)
            self.invert = True
        if flag == False:
            array = self.rasterToNumpy(self.cost)
            self.trace.set_image(array)
            self.invert = False
    def delete_control_points(self):
        self.trace.remove_control_points()
        self.rubberBand.reset(QGis.Point)
    def addPoint(self,p):
        #self.rubberBand.reset(QGis.Line)
        if self.costlayerCRSSrsid != self.projectCRSSrsid:
            transform = QgsCoordinateTransform(self.costlayerCRSSrsid, 
                                            self.projectCRSSrsid)
            p = transform.transform(p)
        self.rubberBand.addPoint(p, True)
        self.rubberBand.show()     
    def removeLastPoint(self):
        if self.trace.remove_last_node() == False:
            self.rubberBandLine.reset(QGis.Line)
        self.rubberBand.removeLastPoint()
    def runTrace(self):
        self.rubberBandLine.reset(QGis.Line)
        self.paths = self.trace.shortest_path()
        s = 0
        if len(self.paths) == 0:
            return
        for p in self.paths:
            points = []
            for c in p:
                i = (c[0])
                j = (c[1])
                x_ = (float(i))*self.xsize+self.xmin+self.xsize*.5
                y_ = (float(j))*self.ysize+self.ymin+self.ysize*.5
                p = QgsPoint(x_,y_)
                if self.costlayerCRSSrsid != self.projectCRSSrsid:
                    transform = QgsCoordinateTransform(self.costlayerCRSSrsid, 
                                            self.projectCRSSrsid)
                    p = transform.transform(p)

                self.rubberBandLine.addPoint(p,True,s)
            s+=1
    def setControlPoints(self, vector = None):
        if vector == None:
            self.use_control_points = False
            return 
        self.use_control_points = True
        self.control_points = vector
        return
    def setDem(self,raster= None):
        if raster == None:
            print "no raster"
            self.use_dem_for_planes = False
            return
        pr = self.target.dataProvider()
        fields = pr.fields()
        strike = False
        dip = False
        rms = False
        attributes = []
        for f in fields:
            if f.name() == 'STRIKE':
                strike = True
            if f.name() == 'RMS':
                rms = True
            if f.name() == 'DIP':
                dip = True
        if not dip:
            attributes.append(QgsField("DIP",QVariant.Double))
            print "Creating DIP attribute"
        if not strike:
            attributes.append(QgsField("STRIKE",QVariant.Double))           
            print "Creating STRIKE attribute"
        if not rms:
            attributes.append(QgsField("RMS",QVariant.Double))            
            print "Creating RMS attribute"
        if len(attributes) > 0:
            pr.addAttributes(attributes)
        self.use_dem_for_planes = True
        self.dem = raster
        self.target.updateFields()
        return
    def addField(self,fieldname,fieldtype,layer):
        #slightly less optimised way to add a field but more compartmentalised
        pr = layer.dataProvider()
        fields = pr.fields()
        strike = False
        dip = False
        rms = False
        attributes = []
        for f in fields:
            if f.name() == fieldname:
                return True
        pr.addAttributes([QgsField(fieldname,fieldtype)])
        layer.updateFields()

        print "Creating and adding "+fieldname+" attribute"
        return True
    def addLine(self):
        if len(self.paths) == 0:
            return
        #if using control points add a uuid to the control point and the line
        lineuuid = uuid.uuid1()
        self.addField("COST",QVariant.String,self.target)
        if self.use_control_points:
            #add uuid to control point layer
            self.addField("UUID",QVariant.String,self.control_points)
            self.addField("UUID",QVariant.String,self.target)

            point_pr = self.control_points.dataProvider()
            point_fields = point_pr.fields()
            self.control_points.startEditing()
            pointlayerCRSSrsid = self.control_points.crs().srsid()
            
            for p in self.trace.nodes:

                fet = QgsFeature(point_fields)
                x_ = (float(p[0]))*self.xsize+self.xmin
                y_ = (float(p[1]))*self.ysize+self.ymin
                geom = QgsGeometry.fromPoint(QgsPoint(x_,y_))
                if pointlayerCRSSrsid != self.costlayerCRSSrsid:
                    geom.transform(QgsCoordinateTransform(self.costlayerCRSSrsid,
                                                      pointlayerCRSSrsid))
                fet.setGeometry(geom)
                fet['UUID'] = str(lineuuid)
                point_pr.addFeatures([fet])
            self.control_points.commitChanges()
            self.control_points.updateFields()
        vl = self.target        
        pr = vl.dataProvider()
        fields = pr.fields()
        # Enter editing mode
        vl.startEditing()
        xyz = []
        if self.use_dem_for_planes:
            filepath = self.dem.dataProvider().dataSourceUri()
            dem_src = gdal.Open(filepath)
            dem_gt = dem_src.GetGeoTransform()
            dem_rb = dem_src.GetRasterBand(1)
        for p in self.paths:
            points = []
            for c in p:
                i = (c[0])
                j = (c[1])
                x_ = (float(i))*self.xsize+self.xmin + self.xsize*.5
                y_ = (float(j))*self.ysize+self.ymin + self.ysize*.5
                points.append(QgsPoint(x_, y_))
                if self.use_dem_for_planes:
                    px = int((x_ - dem_gt[0]) / dem_gt[1])
                    py = int((y_ - dem_gt[3]) / dem_gt[5])
                    intval=dem_rb.ReadAsArray(px,py,1,1)[0][0]
                    xyz.append([x_,y_,intval])
            if self.use_dem_for_planes:
                M = np.array(xyz)
                C = M.T.dot(M)
                eigvals, eigvec = np.linalg.eig(C)
                n = eigvec[2]
                if n[2] < 0:
                    n[0] = -n[0]
                    n[1] = -n[1]
                    n[2] = -n[2] 
            fet = QgsFeature(fields)
            geom = QgsGeometry.fromPolyline(points)
            if self.targetlayerCRSSrsid != self.costlayerCRSSrsid:
                geom.transform(QgsCoordinateTransform(self.costlayerCRSSrsid,
                                                  self.targetlayerCRSSrsid))


            fet.setGeometry( geom  )
            if self.invert:
                fet['COST'] = self.cost.name()+"_inverted"
            if not self.invert:
                fet['COST'] = self.cost.name()
            if self.use_dem_for_planes:
                strike = 180.0 - np.arctan2(n[1],n[0]) * 180.0 / np.pi
                point_type = np.sqrt(n[0]*n[0]+n[1]*n[1]+n[2]*n[2])
                dip = np.arctan2(point_type,n[0])*180.0 / np.pi
                
                fet['STRIKE']= float(strike)
                fet['DIP']= float(dip)
                fet['RMS'] = 100.0
            if self.use_control_points:
                fet['UUID'] = str(lineuuid)
            pr.addFeatures( [ fet ] ) 
        vl.commitChanges()
        vl.updateFields()
        self.rubberBandLine.reset(QGis.Line)
        self.canvas.refresh()

        self.reset()
    def keyPressEvent(self,e):
        if e.key() == Qt.Key_Backspace:
            self.removeLastPoint()
            self.runTrace()
        if e.key() == Qt.Key_Enter:
            self.addLine()
    def canvasPressEvent(self, e):
        point = self.toMapCoordinates(e.pos())
        if type(self.cost) != QgsRasterLayer:
            print "error"
            return
        if e.button() == Qt.LeftButton:
            if self.projectCRSSrsid != self.costlayerCRSSrsid:
                transform = QgsCoordinateTransform(self.projectCRSSrsid,
                                                  self.costlayerCRSSrsid)
                point = transform.transform(point)
            i = int((point[0] - self.xmin) / self.xsize)
            j = int((point[1] - self.ymin) / self.ysize)
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
    def deactivate(self):
        super(GtTraceTool, self).deactivate()
        self.emit(SIGNAL("deactivated()"))
