import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import scipy.ndimage as ndi

class assist_index:
    @staticmethod
    def distance(point1, point2):
        '''
        Calculate the distance between 2 points.
        --------
        point1, point2: the selected 2 points.
        '''
        x = np.array(point1) - np.array(point2)
        return np.linalg.norm(x)
    def get_theta(vector):
	    y,x = vector
	    if x==0:
	        if y>=0:
	            theta = 90
	        else:
	            theta = 270
	    elif y==0:
	        if x>=0:
	            theta = 0
	        else:
	            theta = 180
	    else:
	        theta = np.rad2deg(np.arctan(vector[0]/(vector[1]+1e-9)))
	        if  y>=0 and x>=0:
	            pass
	        elif y>=0 and x<0:
	            theta += 180
	        elif y<0 and x<0:
	            theta += 180
	        else:
	            theta += 360
	    return theta
    def length(path):
        '''
        Calculate the length of selected path. l2-norm
        --------
        path: the seleced path
        '''
        update = 0
        for i in range(len(path)-1):
            update += assist_index.distance(path[i], path[i+1])
        return update
    def sample(path, sample_interval = 11):
        if len(path) <= sample_interval:
            slice_ = np.array([0, np.round(len(path)/2), -1])
            sampled = path[(slice_,)]
        else:
            slice_ = np.arange(0, len(path), sample_interval)
            if (len(path) % sample_interval == 0):
                pass
            else:
                insert = np.array([-1])
                slice_ = np.vstack([slice_, insert])
        return path[(slice_,)]
    def center(path):
        '''
        Calculate the center of the path.
        '''
        return np.mean(path, axis=0)
    def msrg(path):
        '''
        Mean square radius of gyration.
        '''
        center = assist_index.center(path)
        update = 0
        for loc in path:
            update += (assist_index.distance(center, loc) ** 2)
        return update / len(path)
    def e2e(path):
        '''
        End to end distance.
        '''
        return assist_index.distance(path[0], path[-1])  
    def yield_nodeSeq(path, sample_interval=5):
        '''
        Yield slice for curvature calculating.
        '''
        num = len(path)
        if (num < (2*sample_interval+1)):
            slice_ = np.array([0, np.round(num/2).astype("int"), -1])
            seq = [path[(slice_,)]]
        else:
            seq = []
            for i in range(sample_interval, num-sample_interval, sample_interval):
                slice_ = np.array([i-sample_interval, i, i+sample_interval])
                seq.append(path[(slice_,)])
            if ((num-1) % sample_interval) == 0:
                pass
            else:
                insert = np.array([-sample_interval*2-1, -sample_interval-1, -1])
                seq.append(path[(insert,)])
        return seq  
    def get_radius(node1, node2, node3):
        '''
        Calculate the radius or curvature of the selected 3 nodes.
        '''
        a = assist_index.distance(node1, node2)
        b = assist_index.distance(node2, node3)
        c = assist_index.distance(node1, node3)
        p = (a+b+c)*0.5
        area = (p*(p-a)*(p-b)*(p-c))**0.5
        if area == 0:
            return "linear"
        else:
            radius = a*b*c/4/area
            return radius
    class mechanic:
        @staticmethod
        def Lp(node1, node2, node3):
            '''
            Calcuate the persistence length of the selected 3 nodes.
            '''
            R = assist_index.get_radius(node1, node2, node3)
            if R != "linear":
                L13 = assist_index.distance(node1, node3)
                cosTheta = -(L13**2 - 2*R**2)/(2*R**2)
                L = np.arccos(cosTheta)*R
                Lp_ = -L / (2*np.log(cosTheta))
                return Lp_
            else:
                return np.nan
        def interia(path, weight):
            '''
            Calculate the interia by piD^4/64
            '''
            path_weight = [weight[i-1] for i in path]
            average_s = np.mean(path_weight)
            I = average_s ** 4 / 4
            return I
        def b_modulus(path):
            mid = path[np.around(len(path)/2).astype("int")]
            sta = path[0]
            end = path[-1]
        
            ms = np.linalg.norm(mid - sta)
            ab = np.linalg.norm(sta - end)
            proj = ms*ab/np.linalg.norm(ab)
            
            y = np.sqrt(ms**2 - proj**2)
            if y==0:
                return -1
            else:
                L = assist_index.length(path)
                Cb = (L**3) * (y**-2)
                return Cb            
class loc_process:
    def __init__(self, mask, node_list, path_list):
        self.mask = mask
        self.node = node_list
        self.path = path_list
        self.weight = self.add_weight()
        self.locSeq = self.seq2locSeq()
    def add_weight(self):
        weight = ndi.distance_transform_edt(self.mask)
        update_list = [weight[i,j] for i, j in self.node[:,1:3]]
        return np.array(update_list)
    def seq2locSeq(self):
        update_list = []
        for seq in self.path:
            update_list.append(np.array([self.node[i-1,1:3] for i in seq]))
        return update_list
    def morph_calculate(self, pix_thresh=5, scale=False):
        update_list = []
        for seq in self.locSeq:
            length = assist_index.length(seq)
            msrg = assist_index.msrg(seq)
            e2e = assist_index.e2e(seq)
            update_list.append([length, msrg, e2e])
        update_list = pd.DataFrame(update_list, columns=["length","msrg","e2e"])
        update_list = update_list[update_list["length"]>=pix_thresh]
        if scale == False:
            pass
        else:
            update_list["length"] = update_list["length"]*scale
            update_list["msrg"] = update_list["msrg"]*scale*scale
            update_list["e2e"] = update_list["e2e"]*scale
        return update_list
    def mechanic_calculate(self, pix_thresh=5, scale=False):
        update_list = []
        for seq,path in zip(self.locSeq, self.path):
            length = assist_index.length(seq)
            I = assist_index.mechanic.interia(path, self.weight)
            Cb = assist_index.mechanic.b_modulus(seq)
            locSeq = assist_index.yield_nodeSeq(seq, sample_interval=5)
            
            update = []
            for coSeq in locSeq:
                Lp = assist_index.mechanic.Lp(coSeq[0], coSeq[1], coSeq[2])
                
                update.append(Lp)
            Lp_min = np.nanmin(update)
            update_list.append([length, Lp_min, I, Cb])
        update_list = pd.DataFrame(update_list, columns=["length","Lp","interia","b_modulus"])
        update_list = update_list[update_list["length"]>=pix_thresh]
        if scale == False:
            pass
        else:
            update_list["length"] = update_list["length"]*scale
            update_list["Lp"] = update_list["Lp"]*scale
            update_list["interia"] = update_list["interia"]*(scale**4)
            update_list["b_modulus"] = update_list["b_modulus"]*(scale)
        update_list.fillna(-1)
        return update_list