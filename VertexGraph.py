from __future__ import division
import numpy as np
import numpy.linalg as la
import os.path
import networkx as nx
import copy as cp
from matplotlib import pyplot as plt
plt.rcParams.update({'font.size': 22})
from mpl_toolkits.mplot3d import Axes3D
import pymembrane as mb


class VertexNetwork(object):

    def __init__(self, graph):

        self.graph = graph


    def display(self):

        graph_2_show = self.graph

        colors = ["cyan", "purple", "pink", 'k']
        #color_map = [colors[node[2]['type']] for node in graph_2_show.nodes.data()]
        color_map = ["cyan", "purple", "pink", 'k']

        fig = plt.figure(figsize=(10, 10))
        ax1 = fig.add_subplot(111)
        #ax1.set_title(frame)
        #check = nx.Graph()
        #check.add_edge(0,1)

        nx.draw_networkx(graph_2_show,  with_labels=False)
        #plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
        #plt.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)
        for pos in ['right', 'top', 'bottom', 'left']:
            plt.gca().spines[pos].set_visible(False)

        plt.savefig("network.png")
        plt.show()



    def create_subgraph(self, type=2):

        new_graph = cp.deepcopy(self.graph)
        nodes = new_graph.nodes.data()
        to_remove = []

        #list(nx.isolates(new_graph))
        for node in nodes:
            if node[1]["type"] == type:
                to_remove.append(node[0])

        to_remove.sort(reverse=True)

        for node in to_remove:
            new_graph.remove_node(node)

        new_graph.remove_nodes_from(list(nx.isolates(new_graph)))

        return VertexNetwork(new_graph)

    def connected_components(self):

        return len(list(nx.connected_components(self.graph)))



class GraphFromJson(VertexNetwork):

    def __init__(self, jfile):

        G = nx.Graph()
        system = mb.System()
        system.read_mesh_from_json(file=jfile)
        edges = system.getEdges()
        vertices = system.getVertices()

        name = jfile[:-5] + "_v.txt"
        f = open(name, 'w')
        for v in vertices:
            f.write(str(v.type) + "\n")
        f.close()

        for ind, v in enumerate(vertices):
            G.add_node(ind, type=v.type)

        for ind, edge in enumerate(edges):
            G.add_edge(edge.i, edge.j)

        super(GraphFromJson, self).__init__(G)






