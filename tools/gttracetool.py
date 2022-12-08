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

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.core import *
from qgis.gui import *
#import osgeo 
try:
    from osgeo import gdal
    from osgeo import gdalnumeric
except ImportError:
    import gdal
    import gdalnumeric
    
import numpy as np
import time
import gttrace as trace
import uuid
from skimage import filters
phasepack_ = True
try:
    import phasepack
except:
    phasepack_ = False
class GtTraceBase(object):
    def __init__(self,*args):
        self.canvas = args[0]
        self.cost = args[1]
        self.target = args[2]
        #self.canvas = kwargs['canvas']
        #self.cost = kwargs['cost']
        #self.target = kwargs['target']
        #crs reprojection stuff
        self.targetlayerCRSSrsid = self.target.crs()
        self.costlayerCRSSrsid = self.cost.crs()
        #self.renderer = self.canvas.mapRenderer()
        self.projectCRSSrsid =  self.canvas.mapSettings().destinationCrs()

        #if self.targetlayerCRSSrsid != self.costlayerCRSSrsid:
            #print "Target and cost have different CRS"
        self.use_control_points = False
        self.use_dem_for_planes = False
        self.xmin = self.cost.extent().xMinimum()
        self.ymin = self.cost.extent().yMinimum()
        self.xmax = self.cost.extent().xMaximum()
        self.ymax = self.cost.extent().yMaximum()
        self.xsize = self.cost.rasterUnitsPerPixelX()
        self.ysize = self.cost.rasterUnitsPerPixelY()
        self.trace = trace.ShortestPath()
        self.invert = False
        self.trace.set_image(self.rasterToNumpy(self.cost)) 
        self.paths = []#self.trace.shortest_path()
    def runTrace(self):
        self.paths = self.trace.shortest_path()
    def rasterToNumpy(self,layer):
        #TODO add in check for if raster has more than 1 badn here and ask which band to use
        try:
            filepath = layer.dataProvider().dataSourceUri()
            ds = gdal.Open(filepath)
            array = np.array(ds.GetRasterBand(1).ReadAsArray()).astype('int')                     
            array = np.rot90(np.rot90(np.rot90(array)))
        except:
            self.iface.messageBar().pushCritical(
                "Error", "GDAL try another file")
            return False
        else:
            min_ = np.min(array)
            if min_<0: #we don't want negative or zero costs
                array+=abs(min_)+1
            return array
    def setDem(self,raster= None):
        if raster == None:
            #print "no raster"
            self.use_dem_for_planes = False
            return
        pr = self.target.dataProvider()
        fields = pr.fields()
        strike = False
        dip = False
        e1 = False
        e2 = False
        e3 = False
        planarity = False
        qual = False

        attributes = []
        for f in fields:
            if f.name() == 'DIP_DIR':
                strike = True
            if f.name() == 'E_1':
                e1 = True
            if f.name() == 'E_2':
                e2 = True
            if f.name() == 'E_3':
                e3 = True
            if f.name() == 'Planarity':
                planarity = True
            if f.name() == 'Plane_Qual':
                qual = True
            if f.name() == 'DIP':
                dip = True
        if not dip:
            attributes.append(QgsField("DIP",QVariant.Double))
            #print "Creating DIP attribute"
        if not strike:
            attributes.append(QgsField("DIP_DIR",QVariant.Double))           
            #print "Creating DIP_DIR attribute"
        if not e1:
            attributes.append(QgsField("E_1",QVariant.Double))            
            #print "Creating EIGENVALUE_1 attribute"
        if not e2:
            attributes.append(QgsField("E_2",QVariant.Double))            
            #print "Creating EIGENVALUE_2 attribute"
        if not e3:
            attributes.append(QgsField("E_3",QVariant.Double))            
            #print "Creating EIGENVALUE_3 attribute"
        if not planarity:
            attributes.append(QgsField("Planarity",QVariant.Double))            
        if not qual:
            attributes.append(QgsField("Plane_Qual",QVariant.String))            

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

        #print "Creating and adding "+fieldname+" attribute"
        return True

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
    def addLine(self,lineuuid=None):
        if len(self.paths) == 0:
            return
        #if using control points add a uuid to the control point and the line
        if lineuuid==None:
            lineuuid = uuid.uuid1()
        self.addField("COST",QVariant.String,self.target)
        self.addField("UUID",QVariant.String,self.target) #add UID field
        if self.use_control_points:
            #add uuid to control point layer
            self.addField("UUID",QVariant.String,self.control_points)

            point_pr = self.control_points.dataProvider()
            point_fields = point_pr.fields()
            self.control_points.startEditing()
            pointlayerCRSSrsid = self.control_points.crs()
            
            for p in self.trace.nodes:

                fet = QgsFeature(point_fields)
                x_ = (float(p[0]))*self.xsize+self.xmin
                y_ = (float(p[1]))*self.ysize+self.ymin
                geom = QgsGeometry.fromPointXY(QgsPointXY(x_,y_))
                if pointlayerCRSSrsid != self.costlayerCRSSrsid:
                    geom.transform(QgsCoordinateTransform(self.costlayerCRSSrsid,
                                                      pointlayerCRSSrsid,
                                                      QgsProject.instance()))
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
            if self.dem == None:
                #print "No DEM selected"
                return
            filepath = self.dem.dataProvider().dataSourceUri()
            dem_src = gdal.Open(filepath)
            dem_gt = dem_src.GetGeoTransform()
            dem_rb = dem_src.GetRasterBand(1)
        
        points = []
        for c in self.paths:
            i = (c[0])
            j = (c[1])
            x_ = (float(i))*self.xsize+self.xmin + self.xsize*.5
            y_ = (float(j))*self.ysize+self.ymin + self.ysize*.5
            points.append(QgsPointXY(x_, y_))
            if self.use_dem_for_planes:
                px = int((x_ - dem_gt[0]) / dem_gt[1])
                py = int((y_ - dem_gt[3]) / dem_gt[5])
                intval=dem_rb.ReadAsArray(px,py,1,1)[0][0]
                xyz.append([x_,y_,intval])
        if self.use_dem_for_planes:
            M = np.array(xyz)
            M -=  np.mean(M,axis=0)
            C = M.T.dot(M)
            eigvals, eigvec = np.linalg.eig(C)
            n = eigvec[np.argmin(eigvals)]
            if n[2] < 0:
                n[0] = -n[0]
                n[1] = -n[1]
                n[2] = -n[2] 

        fet = QgsFeature(fields)
        geom = QgsGeometry.fromPolylineXY(points)
        if self.targetlayerCRSSrsid != self.costlayerCRSSrsid:
            geom.transform(QgsCoordinateTransform(self.costlayerCRSSrsid,
                                              self.targetlayerCRSSrsid,QgsProject.instance()))


        fet.setGeometry( geom  )
        fet['UUID'] = str(lineuuid) #store UUID on polyline also
        if self.invert:
            fet['COST'] = self.cost.name()+"_inverted"
        if not self.invert:
            fet['COST'] = self.cost.name()
        if self.use_dem_for_planes:
            dip_dir = 90. - np.arctan2(n[1],n[0]) * 180.0 / np.pi
            if dip_dir > 360.:
                dip_dir -= 360.
            if dip_dir < 0:
                dip_dir +=360
            point_type = np.sqrt(n[0]*n[0]+n[1]*n[1]+n[2]*n[2])
            dip = np.arccos(n[2])*180.0 / np.pi
            eigvals.sort()
            fet['DIP_DIR']= float(dip_dir)
            fet['DIP']= float(dip)
            fet['E_1'] = float(eigvals[2])
            fet['E_2'] = float(eigvals[1])
            fet['E_3'] = float(eigvals[0])
            fet['Planarity'] = float(1-eigvals[0]/eigvals[1])
            if float(1-eigvals[0]/eigvals[1]) > 0.75:
                fet['Plane_Qual'] = 'Good'
            elif float(1-eigvals[0]/eigvals[1]) > 0.5:
                fet['Plane_Qual'] = 'Average'
            elif float(1-eigvals[0]/eigvals[1]) < 0.5:
                fet['Plane_Qual'] = 'Bad'
    
        if self.use_control_points:
            fet['UUID'] = str(lineuuid)
        vl.addFeature(fet)
        vl.commitChanges()
        vl.updateFields()
        vl.dataProvider().forceReload()
        self.canvas.refresh()

class GtMapToolEmitPoint(QgsMapToolEmitPoint):
    def __init__(self,*args):
        #super(GtMapToolEmitPoint,self).__init__(args[0])
        canvas = args[0]#kwargs['canvas']
        QgsMapToolEmitPoint.__init__(self,canvas)
class GtTraceTool(GtTraceBase,GtMapToolEmitPoint):
    #deactivatedt = pyqtSignal()
    def __init__(self, canvas_,iface_,target_,cost_):
        #qgis layers/interface
        GtMapToolEmitPoint.__init__(self,canvas_) 
        GtTraceBase.__init__(self,canvas_,cost_,target_,iface_)
        #super(GtTraceTool,self).__init__(canvas_,cost_,target_,iface_,canvas_)
        #    super(GtMapToolEmitPoint,self).__init__(canvas_)
        self.iface = iface_
        self.rubberBand = QgsRubberBand(self.canvas, QgsWkbTypes.PointGeometry)
        self.rubberBand.setColor(Qt.red)
        self.rubberBandLine = QgsRubberBand(self.canvas,QgsWkbTypes.LineGeometry)
        self.rubberBandLine.setColor(Qt.red)
        self.rubberBandLine.setWidth(1)

    def reset(self):
        self.startPoint = self.endPoint = None
        self.isEmittingPoint = False
        self.trace.remove_control_points()
        self.clearRubberBand()
        #self.rubberBandLine.reset(QgsWkbTypes.LineGeometry)
        #self.rubberBand.reset(QgsWkbTypes.PointGeometry)
    def clearRubberBand(self):
        if self.rubberBandLine:
            self.rubberBandLine.reset(QgsWkbTypes.LineGeometry)
            self.rubberBand.reset(QgsWkbTypes.PointGeometry)
    def delete_control_points(self):
        #
        if self.rubberBand:
            self.rubberBand.reset(QgsWkbTypes.PointGeometry)
        self.trace.remove_control_points()
    def addPoint(self,p):
        #self.rubberBand.reset(QgsWkbTypes.LineGeometry)
        if self.costlayerCRSSrsid != self.projectCRSSrsid:
            transform = QgsCoordinateTransform(self.costlayerCRSSrsid, 
                                            self.projectCRSSrsid,
                                            QgsProject.instance())
            p = transform.transform(p)
        self.rubberBand.addPoint(p, True)
        self.rubberBand.show()     
    def removeLastPoint(self):
        if self.trace.remove_last_node() == False:
            self.rubberBandLine.reset(QgsWkbTypes.LineGeometry)
        self.rubberBand.removeLastPoint()
    def runInteractiveTrace(self):
        self.rubberBandLine.reset(QgsWkbTypes.LineGeometry)
        self.runTrace()
        s = 0
        if len(self.paths) == 0:
            return
        for c in self.paths:
            i = (c[0])
            j = (c[1])
            x_ = (float(i))*self.xsize+self.xmin+self.xsize*.5
            y_ = (float(j))*self.ysize+self.ymin+self.ysize*.5
            p = QgsPointXY(x_,y_)
            if self.costlayerCRSSrsid != self.projectCRSSrsid:
                transform = QgsCoordinateTransform(self.costlayerCRSSrsid, 
                                        self.projectCRSSrsid,
                                        QgsProject.instance())
                p = transform.transform(p)

            self.rubberBandLine.addPoint(p,True)
    def setControlPoints(self, vector = None):
        if vector == None:
            self.use_control_points = False
            return 
        self.use_control_points = True
        self.control_points = vector
        return
    def keyReleaseEvent(self,e):
        if e.key() == Qt.Key_Backspace:
            self.removeLastPoint()
            self.runInteractiveTrace()
            e.accept()
        if e.key() == Qt.Key_Enter:
            self.addLine()
            self.reset()
        if e.key() == Qt.Key_Escape:
            self.reset()
    def keyPressEvent(self,e):
        if e.key() == Qt.Key_Backspace:
            e.accept()
            return
        if e.key() == Qt.Key_Enter:
            return
        if e.key() == Qt.Key_Escape:
            return
        return
    def canvasPressEvent(self, e):
        point = self.toMapCoordinates(e.pos())
        if type(self.cost) != QgsRasterLayer:
            return
        if e.button() == Qt.LeftButton:
            if self.projectCRSSrsid != self.costlayerCRSSrsid:
                transform = QgsCoordinateTransform(self.projectCRSSrsid,
                                                  self.costlayerCRSSrsid,
                                                  QgsProject.instance())
                point = transform.transform(point)
            i = int((point[0] - self.xmin) / self.xsize)
            j = int((point[1] - self.ymin) / self.ysize)
            self.rows = self.cost.height()
            self.columns = self.cost.width()
            j1 = j
            i1 = i
            if i < 0 or i>self.columns or j <0 or j > self.rows:
                self.iface.messageBar().pushWarning(
                "Warning", "Selected point is not within raster and cannot be used")
                return 
            self.trace.add_node([i1,j1])
            self.addPoint(point)
            self.runInteractiveTrace()

        if e.button() == Qt.RightButton:
           self.addLine()
           self.reset()
           #clear rubber band

    def canvasReleaseEvent(self, e):
        self.isEmittingPoint = False
        #r = self.rectangle()
    def deactivate(self):
        self.delete_control_points()
        self.clearRubberBand()
        QgsMapToolEmitPoint.deactivate(self)
        #self.deactivatedt.emit()
        #slight bug when this signal is allowed to 
        #emit we get a recursive error TODO debug
        #manage the memory
    #    self.emit(SIGNAL("deactivated()"))
class GtBatchTrace(GtTraceBase):
    def __init__(self, canvas,target,iface,cost,controlpoints,fieldname):
            #qgis layers/interface
        GtTraceBase.__init__(self,canvas,cost,target,iface)
        #super(GtBatchTrace,self).__init__(canvas,cost,target)
        self.controlpoints = controlpoints
        self.fieldname = fieldname
        self.cpCRSSrsid = self.controlpoints.crs()
        self.iface = iface
    def runBatchTrace(self):
        points = []
        idx = self.controlpoints.fields().indexFromName(self.fieldname)
        values = self.controlpoints.uniqueValues(idx)
        self.addField(self.fieldname,QVariant.String,self.target)
        for f in self.controlpoints.getFeatures():
            if f[self.fieldname] == None:
                return False
        for v in values:
            temp = []
            for fet in self.controlpoints.getFeatures():
                if fet[self.fieldname] == v:
                    point = fet.geometry().asPoint()
                    if self.cpCRSSrsid != self.costlayerCRSSrsid:
                        ##print "transforming"
                        ##print point
                        transform = QgsCoordinateTransform(self.cpCRSSrsid,
                                                  self.costlayerCRSSrsid,
                                                  QgsProject.instance())
                        point = transform.transform(point)
                        ##print point
                    ##print point[0], self.xmin, self.xsize
                    ##print point[1], self.ymin, self.ysize
                    i = int((point[0] - self.xmin) / self.xsize)
                    j = int((point[1] - self.ymin) / self.ysize)
                    ##print point, i, j
                    self.rows = self.cost.height()
                    self.columns = self.cost.width()
                    j1 = j
                    i1 = i
                    if i < 0 or i>self.columns or j <0 or j > self.rows:
                        self.iface.messageBar().pushWarning(
                        "Warning", "Selected point is not within raster and cannot be used")
                        continue
                    self.trace.add_node([i1,j1])
            self.runTrace()
            self.addLine(v)
            self.trace.remove_control_points()

        return True
class CostCalculator():
    def __init__(self,layer):
        self.layer = layer
        self.bands = self.layer.bandCount()
    def layer_to_numpy(self,layer):
        #somewhat ram hungry 
        filepath = layer.dataProvider().dataSourceUri()
        ds = gdal.Open(filepath)
        self.transform = ds.GetGeoTransform()
        self.wkt = ds.GetProjection()
        if ds == None:
            return
        arrays = []
        for i in range(self.layer.bandCount()):
            array = np.array(ds.GetRasterBand(i+1).ReadAsArray()).astype('int')
            arrays.append(np.rot90(array,3))
        return arrays
    def layer_band_to_numpy(self,layer,band=0):
        filepath = layer.dataProvider().dataSourceUri()
        ds = gdal.Open(filepath)
        self.transform = ds.GetGeoTransform()
        self.wkt = ds.GetProjection()
        if ds == None:
            return False
        if band < self.layer.bandCount():
            array = np.array(ds.GetRasterBand(band+1).ReadAsArray()).astype('int')
            return np.rot90(array,3)
        return False 
    def numpy_to_layer(self,array,name):
        array = np.rot90(array)
        sy, sx = array.shape
        pathname = QgsProject.instance().readPath("./")+'/'+name
        driver = gdal.GetDriverByName("GTiff")
        dsOut = driver.Create(pathname, sx+1,sy+1,1,gdal.GDT_Float32 ,)
        dsOut.SetGeoTransform(self.transform)
        dsOut.SetProjection(self.wkt)
        bandOut=dsOut.GetRasterBand(1)
        gdalnumeric.BandWriteArray(bandOut, array)
        bandOut = None
        dsOut = None
        layer = QgsRasterLayer(pathname,name)
        QgsProject.instance().addMapLayer(layer)
    def run_calculator(self,string,name):
        if 'sobel' in string:
            array = self.calc_edges(0)
            self.numpy_to_layer(array,name) 
            return
        if 'sobh' in string:
            array = self.calc_edges(1)
            self.numpy_to_layer(array,name) 
            return
        if 'sobv' in string:
            array = self.calc_edges(2)
            self.numpy_to_layer(array,name) 
            return        
        if 'prewitt' in string:
            array = self.calc_edges(3)
            self.numpy_to_layer(array,name) 
            return 
        if 'roberts' in string:
            array = self.calc_edges(4)
            self.numpy_to_layer(array,name) 
            return 
        if 'scharr' in string:
            array = self.calc_edges(5)
            self.numpy_to_layer(array,name) 
            return             
        if 'phase' in string and phasepack_:
            array = self.calc_edges(6)
            self.numpy_to_layer(array,name) 
            return
        if 'darkness' in string:
            array = self.calc_darkness()
            self.numpy_to_layer(array,name) 
            return            
    def calc_darkness(self):
        cost = self.layer_band_to_numpy(self.layer,0)
        cost += self.layer_band_to_numpy(self.layer,1)
        cost += self.layer_band_to_numpy(self.layer,2)
        #cost /= float(arr_len)
        return cost
        ##print cost.shape
 
    def calc_edges(self,t):
        self.layer_to_numpy(self.layer)    
        if self.layer.bandCount() > 1:
            #print "returning false"
            return False
        if t == 0:
            return filters.sobel(self.arrays[0].astype(float))
        if t == 1:
            return filters.sobel_h(self.arrays[0].astype(float))
        if t == 2:
            return filters.sobel_v(self.arrays[0].astype(float))    
        if t == 3:
            return filters.prewitt(self.arrays[0].astype(float))    
        if t == 4:
            return filters.roberts(self.arrays[0].astype(float))    
        if t == 5:
            return filters.scharr(self.arrays[0].astype(float))  
        if t == 6 and phasepack_:
            out = phasepack.phasecong(self.arrays[0].astype(float))
            return out[0]
              
class GtLineTools():
    """
    A base class for working with polyline shapefiles
    """
    def __init__(self,layer):
        self.layer = layer
    def calculate_planes(self,dem):
        if dem == None:
            return False
        if dem.crs().srsid() != self.layer.crs().srsid():
            print('Coordinate systems different')
            return False
        if self.layer.crs().isGeographic():
            print('Geographic')
            return False

        attributes = []
        pr = self.layer.dataProvider()
        fields = pr.fields()
        strike = False
        dip = False
        e1 = False
        e2 = False
        e3 = False
        planarity = False
        qual = False
        self.layer.startEditing()
        for f in fields:
            if f.name() == 'DIP_DIR':
                strike = True
            if f.name() == 'E_1':
                e1 = True
            if f.name() == 'E_2':
                e2 = True
            if f.name() == 'E_3':
                e3 = True
            if f.name() == 'Planarity':
                planarity = True
            if f.name() == 'Plane_Qual':
                qual = True
            if f.name() == 'DIP':
                dip = True
        if not dip:
            attributes.append(QgsField("DIP",QVariant.Double))
            #print "Creating DIP attribute"
        if not strike:
            attributes.append(QgsField("DIP_DIR",QVariant.Double))           
            #print "Creating DIP_DIR attribute"
        if not e1:
            attributes.append(QgsField("E_1",QVariant.Double))            
            #print "Creating EIGENVALUE_1 attribute"
        if not e2:
            attributes.append(QgsField("E_2",QVariant.Double))            
            #print "Creating EIGENVALUE_2 attribute"
        if not e3:
            attributes.append(QgsField("E_3",QVariant.Double))            
            #print "Creating EIGENVALUE_3 attribute"
        if not planarity:
            attributes.append(QgsField("Planarity",QVariant.Double))            
        if not qual:
            attributes.append(QgsField("Plane_Qual",QVariant.String))            

        if len(attributes) > 0:
            print('adding attr')
            pr.addAttributes(attributes)
        

        self.layer.commitChanges()
        self.layer.startEditing()
        for fet in self.layer.getFeatures():
            xyz = []
            for l in fet.geometry().asMultiPolyline(): #points in line geo
                #code adapted from valutool plugin/profiletool
                for p in l:
                    ident = dem.dataProvider().identify(
                        QgsPointXY(p), QgsRaster.IdentifyFormatValue )
                    if ident is not None and (1 in ident.results()):
                        attr = ident.results()[1]
                    else:
                        attr = 0
                        print('not good')
                    xyz.append([p[0],p[1],attr])
            try:
                M = np.array(xyz)
                M -=  np.mean(M,axis=0)
                C = M.T.dot(M)
                eigvals, eigvec = np.linalg.eig(C)
                n = eigvec[np.argmin(eigvals)]
            except:
                return False
            if n[2] < 0:
                n[0] = -n[0]
                n[1] = -n[1]
                n[2] = -n[2]
            dip_dir = 90. - np.arctan2(n[1],n[0]) * 180.0 / np.pi
            if dip_dir > 360.:
                dip_dir -= 360.
            if dip_dir < 0:
                dip_dir +=360
            point_type = np.sqrt(n[0]*n[0]+n[1]*n[1]+n[2]*n[2])
            dip = np.arccos(n[2])*180.0 / np.pi
            eigvals.sort()
            attributes = {}
            attributes['DIP_DIR'] = float(dip_dir)
            attributes['DIP'] = float(dip)
            attributes['E_1']= float(eigvals[2])
            attributes['E_2']= float(eigvals[1])
            attributes['E_3']= float(eigvals[0])
            attributes['Planarity'] = float(1-eigvals[0]/eigvals[1])
            if float(1-eigvals[0]/eigvals[1]) > 0.75:
                attributes['Plane_Qual'] = 'Good'
            elif float(1-eigvals[0]/eigvals[1]) > 0.5:
                attributes['Plane_Qual'] = 'Average'
            elif float(1-eigvals[0]/eigvals[1]) < 0.5:
                attributes['Plane_Qual'] = 'Bad'
            for a in fet.fields().names():
                self.layer.changeAttributeValue(fet.id(),fet.fields().indexFromName(a),attributes[a])
        self.layer.commitChanges()
        self.layer.updateFields()
        self.layer.dataProvider().forceReload()
        return True

