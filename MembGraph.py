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


class MembNetwork(object):

    def __init__(self, graph):

        self.graph = graph



    def read_edges(self, edge_file):

        f = open(edge_file)

        data = f.readlines()
        edge_types = []
        read_flag = False
        for line in data:
            s = line.split()
            if read_flag:
                for thing in s:
                    if thing.isnumeric():
                        edge_types.append(int(thing))
                    else:
                        return edge_types
            else:
                for thing in s:
                    if thing == 'Name="edge_type"':
                        read_flag = True

    def read_vertex_positions(self, edge_file):

        f = open(edge_file)

        data = f.readlines()
        list_points = []
        read_flag = False
        for line in data:
            s = line.split()
            if read_flag:
                for thing in s:
                    if thing.isnumeric():
                        list_points.append(float(thing))
                    else:
                        return False
            else:
                for thing in s:
                    if thing == 'Name="Points"':
                        read_flag = True
        points = np.array((int(len(list_points) /3), 3))
        for ind, lpoint in list_points:
            points[ind/3][ind % 3] = lpoint
        return points


    def create_subgraph(self, type=2):

        new_graph = cp.deepcopy(self.graph)
        edges = new_graph.edges.data()
        to_remove = []

        #list(nx.isolates(new_graph))
        for edge in edges:
            if edge[2]["type"] == type:
                to_remove.append((edge[0], edge[1]))

        for points in to_remove:
            new_graph.remove_edge(*points)
        new_graph.remove_nodes_from(list(nx.isolates(new_graph)))

        return MembNetwork(new_graph)

    def connected_components(self):

        return len(list(nx.connected_components(self.graph)))

    def get_junctions(self):

        d = list(self.graph.degree)

        junctions = [thing[0] for thing in d if thing[1] > 2]

        return junctions

    def get_junctions_plus(self):

        d = list(self.graph.degree)
        junctions = [thing[0] for thing in d if thing[1] != 2]

        return junctions


    def create_junction_graph(self):

        junctions = self.get_junctions_plus()

        new_graph = nx.Graph()

        for ind, j in enumerate(junctions):
            start_edges = self.graph.edges(j)
            for start_edge in start_edges:
                long_edge_type, next_node, length = self.find_junction(j, start_edge, junctions)
                new_graph.add_edge(j, next_node, type=long_edge_type, length=length)

        return MembNetwork(new_graph)

    def find_junction(self, start_node, start_edge, junctions):

        current_node = start_node
        current_edge = start_edge
        next_node = current_edge[1]
        if next_node == current_node:
            next_node = current_edge[0]
        long_edge_type = self.graph.get_edge_data(*current_edge)['type']
        length = 1
        while next_node not in junctions:
            edges = self.graph.edges(next_node)
            current_node, current_edge, next_node = self.get_next_node(current_node, next_node, edges)
            if long_edge_type != self.graph.get_edge_data(*current_edge)['type']:
                long_edge_type = -1
            length += 1

        return long_edge_type, next_node, length

    def get_next_node(self, current_node, next_node, edges):

        next_edge = ""
        for edge in edges:
            if current_node not in edge:
                next_edge = edge

        next_next_node = next_edge[1]
        if next_next_node == next_node:
            next_next_node = next_edge[0]
        return next_node, next_edge, next_next_node

    def junction_types(self):

        junctions = self.get_junctions()

        mixed_0 = 0
        mixed_1 = 0
        mixed_perfect = 0
        type_0 = 0
        type_1 = 0
        for j in junctions:
            types = []
            for edge in self.graph.edges(j):
                types.append(int(self.graph.get_edge_data(*edge)['type']))
            if sum(types) == 0:
                type_0 += 1
            elif sum(types) == len(types):
                type_1 += 1
            elif sum(types) > float(len(types))/2:
                mixed_1 += 1
            elif sum(types) < float(len(types))/2:
                mixed_0 += 1
            else:
                mixed_perfect += 1

        return type_0, type_1, mixed_0, mixed_1, mixed_perfect

    def average_edge_length(self):

        edges = self.graph.edges

        lengths = []
        for edge in edges:
            lengths.append(int(self.graph.get_edge_data(*edge)['length']))

        return np.average(lengths)


    def display(self):

        graph_2_show = self.graph

        colors = ["cyan", "purple", "pink", 'k']
        color_map = [colors[edge[2]['type']] for edge in graph_2_show.edges.data()]

        fig = plt.figure(figsize=(10, 10))
        ax1 = fig.add_subplot(111)
        #ax1.set_title(frame)
        check = nx.Graph()
        check.add_edge(0,1)
        nx.draw_networkx(graph_2_show, edge_color=color_map, with_labels=False, node_size=0, width=5)
        plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
        plt.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)
        for pos in ['right', 'top', 'bottom', 'left']:
            plt.gca().spines[pos].set_visible(False)

        plt.savefig("network.png")
        plt.show()



    def display_edge_lengths(self):

        graph_2_show = self.graph

        colors = ["cyan", "purple", "pink", 'k']
        color_map = [colors[edge[2]['type']] for edge in graph_2_show.edges.data()]

        fig = plt.figure(figsize=(10, 10))
        ax1 = fig.add_subplot(111)
        #ax1.set_title(frame)

        edge_labels = nx.get_edge_attributes(graph_2_show, "length")

        nx.draw_networkx(graph_2_show, pos=nx.spring_layout(graph_2_show, seed=7), with_labels=False,
                                     edge_color=color_map, node_size=0, width=5)
        nx.draw_networkx_edge_labels(graph_2_show, pos=nx.spring_layout(graph_2_show, seed=7), edge_labels=edge_labels)
        plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
        plt.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)
        for pos in ['right', 'top', 'bottom', 'left']:
            plt.gca().spines[pos].set_visible(False)

        plt.savefig("edges.png")
        plt.show()


class GraphFromJson(MembNetwork):

    def __init__(self, jfile, edge_file):

        G = nx.Graph()
        system = mb.System()
        system.read_mesh_from_json(file=jfile)
        edges = system.getEdges()
        edge_types = self.read_edges(edge_file)

        for ind, edge in enumerate(edges):
            G.add_edge(edge.i, edge.j, type=edge_types[ind])

        super(GraphFromJson, self).__init__(G)



