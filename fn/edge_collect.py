import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import itertools
import pandas as pd
from tqdm import tqdm

class network_edge_refine:# 网络边缘细化
    def __init__(self, node_list, connection):

        # all points
        self.node_index = node_list[:,0]
        self.location = node_list[:,1:3]
        self.node_type = node_list[:,3]

        # only nodes
        self.num_of_true_node_index = len(np.where(self.node_type>1)[0])
        self.true_node_index = self.node_index[:self.num_of_true_node_index]
        self.true_node_location = self.location[:self.num_of_true_node_index]

        # short edges: connections of all points including edge points
        self.short_edges = connection.tolist()

        # build full-path graph with all points
        self.fullPathGraph = self.load_fullPathGraph()

        self.true_nodes_only = [node for node in self.fullPathGraph.nodes if node <= self.num_of_true_node_index]

        self.subgraph_true_nodes_only = self.fullPathGraph.subgraph(self.true_nodes_only)####

        # initialize paths
        self.initPaths = []

        self.npos = self.get_location_dict()

    def get_location_dict(self):
        '''
        Collect locations as dictionary.将节点索引和对应的坐标转换为字典格式。
        '''
        update = {}
        for index, loc in zip(self.node_index, self.location):
            update[index] = (loc[1], loc[0])
        return update

    def load_fullPathGraph(self):
        '''
        Build the full-path graph.基于节点和边缘信息创建完整的网络图。
        '''
        net = nx.Graph()
        for i in self.node_index:
            net.add_node(i, node_type = self.node_type[i-1])
        net.add_edges_from(self.short_edges)
        return net
    '''
    def find_initPaths(self):
        #test
        update_path = []# 初始化一个空列表，稍后用于存储满足条件的路径
        print("Total nodes: %d"%self.num_of_true_node_index)# 输出实际节点的总数
        for i in range(1, self.num_of_true_node_index):# 从 1 开始，迭代所有实际节点，但不包括最后一个节点
            completed_num = (i / self.num_of_true_node_index) * 100
            print("{:.2f}%  completed".format(completed_num))

            for j in range(i+1, self.num_of_true_node_index+1):# 对于每个 i，从 i+1 开始迭代到最后一个实际节点
                try:# 进入 try 代码块，尝试执行下面的代码。如果发生异常，将执行 except 代码块
                    #path = nx.shortest_path(self.fullPathGraph, i, j)# 使用 NetworkX 库计算节点 i 和节点 j 之间的最短路径
                    path = nx.shortest_path(self.subgraph_true_nodes_only, i, j)
                    update_path.append((i, j))
                    #if self.initPaths_continuity_check(path) == True:# 检查找到的路径是否连续。如果路径连续，执行以下代码
                        #update_path.append((i, j))# 将节点 i 和节点 j 之间的路径添加到 update_path 列表中
                    #else:# 返回 False，则执行以下代码
                        #pass# 什么都不做，继续下一次迭代
                except nx.NetworkXNoPath:# 计算最短路径时发生异常（例如，两个节点之间没有路径），则执行以下代码
                    pass# 什么都不做，继续下一次迭代
        self.initPaths = np.array(update_path)# 将 update_path 列表转换为 NumPy 数组，并将其存储在类的 initPaths 属性中
    '''


    def find_initPaths(self):
        update_path = []
        print("Total nodes: %d" % self.num_of_true_node_index)

        for i in tqdm(range(1, self.num_of_true_node_index), desc="Processing nodes"):
            for j in range(i + 1, self.num_of_true_node_index + 1):
                try:
                    path = nx.shortest_path(self.fullPathGraph, i, j)
                    if self.initPaths_continuity_check(path):
                        update_path.append((i, j))
                except nx.NetworkXNoPath:
                    pass

        self.initPaths = np.array(update_path)


    def initPaths_continuity_check(self, path):
        '''
        Check if there is other nodes in the way.检查路径中是否存在其他节点。
        --------
        path: the selected node.
        '''
        path_check = path[1:-1]
        # if any node exsists in the path, there will be zero or minus.
        other_node = [(x-self.num_of_true_node_index)>0 for x in path_check]
        res = np.all(other_node)
        if res == True:
            return True
        else:
            return False

    def path2coSeq(self, path):
        '''
        Acquire the coordinate sequence of the selected path.获取选定路径的坐标序列。
        '''
        seq = []
        for index in path:
            seq.append(self.location[index-1].tolist())
        return seq

    def draw_Lp_map(self, Lp_list):# 绘制 Lp 图。

        Lp_image = np.zeros(shape=(906,905))

        for Lp_element in Lp_list:
            (node1, node2) = Lp_element[0]
            Lp = Lp_element[1]
            path = nx.shortest_path(self.fullPathGraph, node1, node2)
            coSeq = self.path2coSeq(path)

            if type(Lp) != np.float64:
                for loc in coSeq:
                    Lp_image[loc[0], loc[1]] = -1
            elif Lp > 200:
                for loc in coSeq:
                    Lp_image[loc[0], loc[1]] = -1
            else:
                for loc in coSeq:
                    Lp_image[loc[0], loc[1]] = np.log(Lp)
        return Lp_image

class assist_index:# 辅助计算
    @staticmethod
    def distance(point1, point2):
        '''
        Calculate the distance between 2 points.计算两点之间的距离。
        --------
        point1, point2: the selected 2 points.
        '''
        x = np.array(point1) - np.array(point2)
        return np.linalg.norm(x)

    def length(path):
        '''
        Calculate the length of selected path. l2-norm 计算选定路径的长度。
        --------
        path: the seleced path
        '''
        update = 0
        for i in range(len(path)-1):
            update += assist_index.distance(path[i], path[i+1])
        return update

    def sample(path, sample_interval = 11):# 对路径进行采样。
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
        Calculate the center of the path.计算路径的中心。
        '''
        return np.mean(path, axis=0)

    def msrg(path):
        '''
        Mean square radius of gyration.计算路径的平均平方回转半径。
        '''
        center = assist_index.center(path)
        update = 0
        for loc in path:
            update += (assist_index.distance(center, loc) ** 2)
        return update / len(path)

    def e2e(path):
        '''
        End to end distance.计算路径的端到端距离。
        '''
        return assist_index.distance(path[0], path[-1])


    def yield_nodeSeq(path, sample_interval=5):
        '''
        Yield slice for curvature calculating.为计算曲率生成切片。
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
        Calculate the radius or curvature of the selected 3 nodes.计算选定的三个节点的曲率半径。
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
            Calcuate the persistence length of the selected 3 nodes.计算选定的三个节点的持久长度。
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
class edge_opt:
    def __init__(self, node_list, path_list):

        # all points
        self.node_index = node_list[:,0]
        self.location = node_list[:,1:3]
        self.node_type = node_list[:,3]

        # only nodes, initialize
        self.num_of_true_node_index = len(np.where(self.node_type>1)[0])
        self.true_node_index = self.node_index[:self.num_of_true_node_index]
        self.true_node_location = self.location[:self.num_of_true_node_index]

        self.init_edges = np.array(path_list)
        self.Graph = self.load_Graph()

    def remove_edges(self, remove):
        '''
        Remove the wrong edges.
        '''
        before = self.init_edges.shape[0]
        before_ = self.init_edges.tolist()
        remove_ = remove.tolist()
        update = np.array([x for x in before_ if x not in remove_])
        self.init_edges = update
        after = self.init_edges.shape[0]
        print("%.f / %.f branch edges removed"%(before-after, before))

        nodes = list(set(self.init_edges.flatten().tolist()))
        self.node_type = np.ones(shape = self.node_type.shape)
        for node in nodes:
            self.node_type[node-1] = 2
    def update_property(self):
        '''
        Update the node information after changing node_type.
        '''
        self.num_of_true_node_index = len(np.where(self.node_type == 2)[0])
        self.true_node_index = self.node_index[np.where(self.node_type == 2)]
        self.true_node_location = self.location[np.where(self.node_type == 2)]

    def load_Graph(self):
        '''
        Build the graph with only nodes, so the paths are simplified.
        '''
        net = nx.Graph()
        for i in self.true_node_index:
            net.add_node(i, node_type = self.node_type[i-1])
        net.add_edges_from(self.init_edges)
        return net

    def opt_redundantNode(self):
        '''
        Remove redundant nodes from the graph.
        '''
        update_con_list_short = []
        edge_opt_before = self.init_edges.shape[0]
        for i in range(1, self.num_of_true_node_index+1):
            for j in range(i+1, self.num_of_true_node_index+1):
                node_i = self.location[i-1,:]
                node_j = self.location[j-1,:]
                distance_i2j = assist_index.distance(node_i, node_j)
                # if two nodes are next to each other, record them.
                if distance_i2j < 1.5:
                    update_con_list_short.append([i,j])
                else:
                    pass
        # build the redundant relationship
        Graph_short = nx.Graph()
        for i in self.true_node_index:
            Graph_short.add_node(i, node_type = self.node_type[i-1])
        Graph_short.add_edges_from(update_con_list_short)

        # find connective subgraph
        for sub_Graph_short in sorted(nx.connected_components(Graph_short), key=len, reverse=True):
            sub_Graph_node_list = list(sub_Graph_short)
            # when the node cluster is able to be simplified
            if len(sub_Graph_node_list) > 1:
                # only keep the first node
                node_keep = sub_Graph_node_list[0]
                node_remove_list = sub_Graph_node_list[1:]
                # for every node needed to be removed
                for node_remove in node_remove_list:
                    # search its location and replace with the node kept
                    self.init_edges[np.where(self.init_edges==node_remove)] = node_keep
                    # change the property from "node" into "edge"
                    self.node_type[node_remove-1] = 1
        # remove double node-kept edges
        self.init_edges = self.init_edges[np.where(self.init_edges[:,0] != self.init_edges[:,1])]

        for i in range(len(self.init_edges)):
            if self.init_edges[i,0] > self.init_edges[i,1]:
                self.init_edges[i] = np.array([self.init_edges[i,1],self.init_edges[i,0]])

        self.init_edges = np.unique(self.init_edges, axis=0)


        opt_before = self.num_of_true_node_index
        self.update_property()
        opt_after = self.num_of_true_node_index
        edge_opt_after = self.init_edges.shape[0]
        print("%.f / %.f nodes were removed during opt_redundantNode"%(opt_before-opt_after, opt_before))
        print("%.f / %.f edges were removed during opt_redundantNode"%(edge_opt_before-edge_opt_after, edge_opt_before))
        self.Graph = self.load_Graph()

    def opt_nodeDegree(self):
        '''
        Optimize the nodes with degree == 2.
        '''
        degree_list = list(nx.degree(self.Graph))
        for (i, j) in degree_list:
            if j == 2:
                self.node_type = 1

                # update the edge, remove the redundant
                self.update_remove_2degreeNodeEdge(i)

            elif j == 0:
                self.node_type = 0

        # update the node type
        self.update_node_property()

        #self.update_Graph
    def update_remove_2degreeNodeEdge(self, node):
        '''
        If the node degree is 2, this node exsists in the path_list twice.
        '''
        node_location = np.where(self.init_edges==node)

    def update_image(self):
        '''
        Update the image with new node_type.
        --------
        node_type: the list of nodes types
        '''
        blank_image = np.zeros(shape=(896,895))
        for (idx, loc) in zip(self.node_type, self.location):
            blank_image[loc[0],loc[1]] = idx
        plt.imshow(blank_image)

    def path2coSeq(self, path):
        '''
        Acquire the coordinate sequence of the selected path.
        '''
        seq = []
        for index in path:
            seq.append(self.location[index-1].tolist())
        return np.array(seq)

    def edges_Lp(self,sample_interval, Graph):
        '''
        Calculate persistence length for every edges.
        '''
        output = []
        for [i,j] in self.init_edges:
            path = np.array(nx.shortest_path(Graph, i, j))
            nodeSeq = assist_index.yield_nodeSeq(path, sample_interval)

            update = []
            for Seq in nodeSeq:
                coSeq = self.path2coSeq(Seq)
                Lp = assist_index.mechanic.Lp(coSeq[0], coSeq[1], coSeq[2])
                update.append(Lp)
            Lp_min = np.nanmin(update)
            #print("Edge(%d, %d): length: %d, Lp: %.2f"%(i,j,len(path), Lp_min))
            output.append([(i,j), Lp_min])
        return output

    def edges_len(self, Graph):
        '''
        Calculate length, msrg, e2e for every edges.
        '''
        output = []
        for [i,j] in self.init_edges:
            path = np.array(nx.shortest_path(Graph, i, j))
            coSeq = self.path2coSeq(path)

            Seq_len = assist_index.length(coSeq)
            Seq_msrg = assist_index.msrg(coSeq)
            Seq_e2e = assist_index.e2e(coSeq)

            output.append([(i,j), Seq_len, Seq_msrg, Seq_e2e])
        return output
class edge_merge:
    @staticmethod
    def degree_check(full_graph, simple_graph, bunch):
        '''
        Get the nodes with wrong branches.
        --------
        full_graph: short connections
        simple_graph: long connections
        '''
        short_degree = np.array(list(nx.degree(full_graph, nbunch=bunch)))
        long_degree = np.array(list(nx.degree(simple_graph, nbunch=bunch)))

        long_degree[:,1] = long_degree[:,1] - short_degree[:,1]
        update = long_degree[np.where(long_degree[:,1] > 0)]

        return update[:,0]

    def find_pairs(node, simple_graph):
        '''
        Generate pairs for selected node.
        '''
        neighbor = list(nx.neighbors(simple_graph, node))
        for neighbor_ in neighbor:
            if node < neighbor_:
                yield (node, neighbor_)
            else:
                yield (neighbor_, node)
    def branch_determine(path1, path2):
        '''
        Conditions for 2 branch paths.
        '''
        # share nodes
        share = [x for x in path1 if x in path2]

        # if 4 more nodes are same, it is needless branch.
        if len(share) >= 4:
            if len(path1) >= len(path2):
                return "path1"
            else:
                return "path2"
        else:
            return "True branch"

    def branch_opt(branch_nodes, full_graph, simple_graph):
        '''
        Optimize the branches.
        --------
        branch_nodes: from degree check
        full_graph: used to find path        
        simple_graph: used to generate edges
        '''
        # record the edges to be removed
        remove_edges = []
        # check every node with extra edges
        for branch_node in branch_nodes:
            edges = []
            # collect edges related to the selected branch_node
            for edge in edge_merge.find_pairs(branch_node, simple_graph):
                edges.append(edge)
            # collect paths of these edges.
            paths = [nx.shortest_path(full_graph, edge[0], edge[1]) for edge in edges]
            # combinations path1 - path2
            for path1, path2 in itertools.combinations(paths, 2):
                res = edge_merge.branch_determine(path1, path2)
                if res == "True branch":
                    pass
                elif res == "path1":
                    remove_edges.append((path1[0], path1[-1]))
                elif res == "path2":
                    remove_edges.append((path2[0], path2[-1]))
        return np.array(remove_edges)
class network_graph:
    def __init__(self):
        self.edges = np.array(np.load("Len_list_cut.npy",allow_pickle=True)[:,0].tolist())
        self.nodes_location = np.load("node_list_cut.npy")[:,1:3]
        self.nodes = self.get_nodes()

        self.length = np.load("Len_list_cut.npy",allow_pickle=True)[:,1]
        self.msrg = np.load("Len_list_cut.npy",allow_pickle=True)[:,2]
        self.e2e = np.load("Len_list_cut.npy",allow_pickle=True)[:,3]
        self.lp = np.load("Lp_list_cut.npy",allow_pickle=True)[:,1:]

        self.node_Graph = self.build_node_Graph()
        self.node_pos = self.get_nodes_pos()

        self.node_npos_dual = self.get_dual_pos()
        self.node_list_dual = self.get_dual_node()
        self.edge_dual = self.get_dual_edge()

        self.image = np.load("img_skeleton_cut.npy").astype("int")

    def get_nodes(self):
        '''
        Collect nodes with 1 edge at least.
        '''
        nodes = self.edges.flatten()
        nodes_set = set(list(nodes))
        return np.array(list(nodes_set))

    def get_nodes_pos(self):
        '''
        Collect nodes position.
        '''
        pos = {}
        for node, loc in zip(self.nodes, self.nodes_location):
            pos[node] = loc.tolist()
        return pos

    def build_node_Graph(self):
        '''
        Build graph.
        '''
        net = nx.Graph()
        for node_index in self.nodes:
            net.add_node(node_index)
        for edge,length_,msrg_,e2e_,lp_ in zip(self.edges,self.length,self.msrg,self.e2e,self.lp):
            net.add_edge(edge[0], edge[1],
                         length = length_,
                         msrg = msrg_,
                         e2e = e2e_,
                         lp = lp_)
        return net

    def get_dual_pos(self):
        '''
        Get mid of e2e as the pos of dual node.
        '''
        pos = {}
        i = 0
        for edge in self.edges:
            node1, node2 = edge[0], edge[1]
            loc1, loc2 = self.nodes_location[node1-1], self.nodes_location[node2-1]
            locs = ((loc1 + loc2) *0.5).tolist()
            pos[i] = [locs[1],locs[0]]
            i += 1
        return pos


    def get_dual_node(self):
        '''
        Get index for edges.
        '''
        num = self.edges.shape[0]
        return np.arange(num)

    def get_dual_edge(self):
        '''
        Get 
        '''
        num = self.edges.shape[0]
        update = []
        # one edge and edges left
        for i in range(num-1):
            edge_inCheck = self.edges[i]
            edge_inList = self.edges[i+1:]
            # two nodes of the edge
            node1, node2 = edge_inCheck[0], edge_inCheck[1]
            index1 = np.where(edge_inList==node1)[0]
            index2 = np.where(edge_inList==node2)[0]
            index = np.hstack([index1,index2])+i+1
            for j in index:
                update.append((i, j))
        return np.array(update)

    def build_edge_Graph(self):
        '''
        Build dual graph.
        '''
        node_npos_dual = self.node_npos_dual
        node_list_dual = self.node_list_dual.tolist()
        edge_dual = self.edge_dual.tolist()

        net = nx.Graph()
        for node_index_dual in node_list_dual:
            net.add_node(node_index_dual)
        for edge,length_,msrg_,e2e_,lp_ in zip(edge_dual,self.length,self.msrg,self.e2e,self.lp):
            net.add_edge(edge[0], edge[1],
                         length = length_,
                         msrg = msrg_,
                         e2e = e2e_,
                         lp = lp_)
        return net

    def draw_Graph(self):
        plt.imshow(self.image, cmap="binary")
        plt.scatter(self.nodes_location[:,1],self.nodes_location[:,0])
def get_labels(num):
    labels = {}
    for i in num:
        labels[i] = i
    return labels
def get_path_list(fullGraph,simpleGraph):
    update = []
    for [i, j] in list(simpleGraph.edges):
        path = list(nx.shortest_path(fullGraph, i, j))
        update.append(path)
    return update
