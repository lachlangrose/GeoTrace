# -*- coding: utf-8 -*-
"""
/***************************************************************************
 File Name: tools/gttace.py
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

import numpy as np
import math
from skimage.graph import route_through_array

class ShortestPath():
    def __init__(self):
        self.nodes = []
        self.segments = []
        self.path_vertex = []
        self.c = 0
    def set_image(self,im):
        self.im = im
        self.im2 = np.zeros(self.im.shape)
        self.path = np.zeros(self.im.shape)
        self.l, self.w = im.shape
        self.imshape = self.im2.shape
    def remove_control_points(self):
        self.nodes = []
        self.segments = []
    def remove_last_node(self):
        if len(self.nodes) > 0:
            del self.nodes[-1]
        return self.setup_segments()
    def add_node(self,node):
        self.nodes.append(node)
        return self.setup_segments()
    def add_node_to_segments(self,node):
        if len(self.segments) >= 1:
            #first check if the point occurs inside a segment
            for i in range(len(self.segments)):
                start = np.array(self.segments[i][0],dtype=float)
                end = np.array(self.segments[i][1],dtype=float)
                ns = node - start
                ne = node - end
                ds = np.linalg.norm(ns)
                de = np.linalg.norm(ne)
                ns /= ds
                ne /= de
                dot =np.dot(ns,ne)
                if dot < 0:
                    prev_end = self.segments[i][1]
                    self.segments[i][1] = node
                    self.segments.insert(i+1,[node,prev_end])
                    return True
            #if adding to the end, do we add to start or end?
            start = np.array(self.segments[0][0],dtype=float)
            end = np.array(self.segments[len(self.segments)-1][1],dtype=float)
            ns = node - start
            ne = node - end
            ds = np.linalg.norm(ns)
            de = np.linalg.norm(ne)
            if ds < de:
                self.segments.insert(0,[start,node])
                return True
            if de < ds:
                self.segments.append([end,node])
                return True

    def setup_segments(self):
        if len(self.nodes) < 2:
            return False
        self.segments = []
        self.segments.append([self.nodes[0],self.nodes[-1]]) 
        for i in range(1,len(self.nodes)-1):
            np_node = np.array(self.nodes[i],dtype=float)
            self.add_node_to_segments(np_node)                  
        return True
        
        
    def shortest_path(self):
        self.paths = []
        #if segments is empty then don't do anything
        if len(self.segments) == 0:
            return []
        for s in self.segments:
            imshape = self.im.shape
            xmin = min(s[0][0],s[1][0])
            xmax = max(s[0][0],s[1][0])
            ymin = min(s[0][1],s[1][1])
            ymax = max(s[0][1],s[1][1])
            
            #Calculate local image to compute shortet path, including a buffer around the points of 100px (maybe this should be base?)
            buffer_v = 100
            xmin = max(xmin-buffer_v, 0) #n.b. min/max args ensure bounds remain within the image...
            ymin = max(ymin-buffer_v, 0)
            xmax = min(xmax+buffer_v, self.imshape[0])
            ymax = min(ymax+buffer_v, self.imshape[1])
            
            #extract local image
            im = self.im[xmin:xmax,ymin:ymax]
            
            #get start and end points in local-image coords
            start = [s[0][0]-xmin,s[0][1]-ymin]
            end = [s[1][0]-xmin,s[1][1]-ymin]

            #compute shortest path
            path, cost = route_through_array(im,start,end,fully_connected=True,geometric=True)

            if len(self.paths) > 0:
                if path[0][0] + xmin != self.paths[-1][0] or \
                    path[0][1] + ymin != self.paths[-1][1]:
                    for p in reversed(path):
                        self.paths.append([p[0]+xmin,p[1]+ymin])
                else:
                    for p in path:               
                        self.paths.append([p[0]+xmin,p[1]+ymin])
            else:
                for p in path:               
                    self.paths.append([p[0]+xmin,p[1]+ymin])

            #paths2 = []
        return self.paths#self.segments


