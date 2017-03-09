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
    def remove_control_points(self):
        self.nodes = []
        self.segments = []
    def add_node(self,node):
        self.nodes.append(node)
        np_node = np.array(node,dtype=float)
        if len(self.nodes) < 2:
            return False
        if len(self.segments) < 1:
            self.segments.append([self.nodes[0],self.nodes[1]]) 
            return True
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
                    self.segments.insert(i+1,[prev_end,node])
                    return False#split
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
                #make sure the current index isn't inaccessible
    def shortest_path(self):
        self.paths = []
        for s in self.segments:
            xmin = min(s[0][0],s[1][0])
            xmax = max(s[0][0],s[1][0])
            ymin = min(s[0][1],s[1][1])
            ymax = max(s[0][1],s[1][1])

            im = self.im[xmin:xmax,ymin:ymax]
            end = im.shape            
            end = [end[0]- 1, end[1] - 1]
            #option1 start in bottom corner
            p1 = s[0]
            p2 = s[1]
            if xmin == p1[0] and ymin == p1[1]:
                start = [0,0]
                #start = [0,end[1]]

            elif xmin == p1[0] and ymax == p1[1]:
                start = [0,end[1]]
                end = [end[0],0]
            
            elif xmin == p2[0] and ymin == p2[1]:
                start = [0,0]
            elif xmin == p2[0] and ymax == p2[1]:
                start = [0,end[1]]
                end = [end[0],0]

            else:
                continue
            path, cost = route_through_array(im,start,end,fully_connected=True,geometric=False)
            paths = []
            for p in path:
                paths.append([p[0]+xmin,p[1]+ymin])
            #paths2 = []
            self.paths.append(paths)
        return self.paths

