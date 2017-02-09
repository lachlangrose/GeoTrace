import numpy as np
class ShortestPath():
    def __init__(self):
        self.nodes = []
        self.path_vertex = []
    def set_image(self,im):
        self.im = im
        self.im2 = np.zeros(self.im.shape)
        self.path = np.zeros(self.im.shape)
        self.l, self.w = im.shape

    def add_node(self,node):
        self.nodes.append(node)
    def index_to_i_j(self,index):
        j = index - (index // self.w * self.w)
        i = (index - j) / self.w
        return i,j
    def mark_visited(self,index):
        self.im2[self.index_to_i_j(index)] = 1
    def mark_path(self,index):
        self.path[self.index_to_i_j(index)] = 1
    def i_j_to_index(self,ij):
        index = ij[0]*self.w + ij[1]
        return index
    def setup(self):
        self.s_idx = self.i_j_to_index(self.nodes[0])
        self.e_idx = self.i_j_to_index(self.nodes[1])
    def dist_from_idx(self,p1,p2):
        i1, j1 = self.index_to_i_j(p1)
        i2, j2 = self.index_to_i_j(p2)
        return math.sqrt(i1*i2 + j2*j2)
    def get_segment_cost(self,p1,p2):
        return (self.im[self.index_to_i_j(p1)] - self.im[self.index_to_i_j(p2)])**2
    def find_neighbours(self,p,d=0):
        i, j = self.index_to_i_j(p)
        indexes = []
        jstart = -1
        istart = -1
        jstop = 2
        istop = 2
        if i < 1:
            istart = 0
        if j < 1:
            jstart = 0
        if j > self.w-2:
            jstop = 1
        if i > self.l-2:
            istop = 1
        for ii in xrange(istart,istop,1):
            for jj in xrange(jstart,jstop,1):
                indexes.append(self.i_j_to_index([i+ii,j+jj]))
        return indexes
    def find_closest_point(self,openSet,dist):
        smallest_cost = 99999

        for pair in openSet.iteritems():
            cost = dist[pair[0]]
            if cost < smallest_cost:
                smallest_cost = cost
                current = pair[0]
        return current            
                #make sure the current index isn't inaccessible
    def shortest_path(self):
        print "Running shortest path algorithm"
        im = self.im
        s_idx = self.s_idx
        e_idx = self.e_idx
        #declare all variables
        #containers for storing path etc
        closedSet = {}
        openSet = {}
        dist = {}
        #distance to start from start = 0
        dist[s_idx] = 0
        openSet[s_idx] = s_idx
        current = 0
        cost = 0
        iter_count = 0
        #while there is something in openset
        while openSet:
            iter_count+=1
            smallest_cost = 99999
            #get the shortest distance
            #current_d = min_element(current)
            current = self.find_closest_point(openSet,dist)
            closedSet[current] = openSet[current]
            #self.mark_visited(current)
            del openSet[current]
            #print current, e_idx
            if current == e_idx:
                path = []
                current = closedSet[current]
                while current != s_idx:
                    path.append(self.index_to_i_j(current))
                    current = closedSet[current]
                path.append(self.index_to_i_j(current))
                return path
            #cur_d2 = self.dist_from_idx(current,e_idx)
            for p in self.find_neighbours(current):
                #next_d2 = self.dist_from_idx(p,e_idx)
                
                #if next_d2 >= cur_d2:
                #    continue
                if p in closedSet:#closedSet.has_key(p):
                    continue
                cost = self.get_segment_cost(current,p)
                cost += dist[current]
                if p in dist:
                    if cost < dist[p]:
                        dist[p] = cost
                        closedSet[p] = current
                    else:
                        continue
                else:
                    openSet[p] = current
                    dist[p] = cost

