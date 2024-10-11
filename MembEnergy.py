from __future__ import division
import numpy as np
import numpy.linalg as la
import os.path
import copy as cp
from matplotlib import pyplot as plt
plt.rcParams.update({'font.size': 22})
from mpl_toolkits.mplot3d import Axes3D
import pymembrane as mb


class MembEnergy(object):

    def __init__(self, jfile, edge_file):

        edge_types = self.read_edges(edge_file)

        self.system = mb.System()
        # read the mesh
        self.system.read_mesh_from_json(jfile)



        edges = self.system.getEdges()
        Ne = len(edges)
        for ei in range(len(edge_types)):
            edges[ei].type = edge_types[ei]
        self.system.setEdges(edges)



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
                        read_flag = False
            else:
                for thing in s:
                    if thing == 'Name="Points"':
                        read_flag = True
        points = np.array((int(len(list_points) /3), 3))
        for ind, lpoint in list_points:
            points[ind/3][ind % 3] = lpoint
        return points

    def read_vertex_ids(self, vertex_file):

        f = open(vertex_file)

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
                    if thing == 'Name="VertexType"':
                        read_flag = True

    def compute_stretching_energy(self):

        evolver = mb.Evolver(self.system)

        evolver.add_force("Mesh>Harmonic", {"k": {"0": str(10.), "1": str(10.), "2": str(10.)},
                                            "l0": {"0": str(1.0), "1": str(1.0), "2": str(1.0)}})

        computer = self.system.compute_mesh()
        energies = computer.energy(evolver)

        Es = energies["edges"]

        return Es

    def compute_bending_itz(self, kappa0=.1, kappa1=2, kappa2=100):

        evolver = mb.Evolver(self.system)
        kappas = [kappa0, kappa1, kappa2]

        factor = 1 / np.sqrt(3)
        kappas = np.multiply(kappas, factor)

        evolver.add_force("Mesh>BendingGK", {"H0": {"0": "0.", "1": "0.", "2": "0."},
                                             "kappaH": {"0": str(kappas[0]), "1": str(kappas[1]), "2": str(kappas[2])},
                                             "kappaG": {"0": str(-0.66667 * kappas[0]), "1": str(-0.66667 * kappas[1]),
                                                        "2": str(-0.66667 * kappas[2])}})

        computer = self.system.compute_mesh()
        energies = computer.energy(evolver)
        Eb = energies["vertices"]
        return Eb

    def compute_bending_itz2(self, kappa0=.1, kappa1=2, kappa2=100):

        evolver = mb.Evolver(self.system)
        kappas = [kappa0, kappa1, kappa2]

        factor = 1 / np.sqrt(3)
        kappas = np.multiply(kappas, factor)

        evolver.add_force("Mesh>BendingGK", {"H0": {"0": "0.", "1": "0.", "2": "0."},
                                             "kappaH": {"0": str(kappas[0]), "1": str(kappas[1]), "2": str(kappas[2])},
                                             "kappaG": {"0": str(-1.0 * kappas[0]), "1": str(-1.0 * kappas[1]),
                                                        "2": str(-1.0 * kappas[2])}})

        computer = self.system.compute_mesh()
        energies = computer.energy(evolver)
        Eb = energies["vertices"]
        return Eb

    def compute_bending_nv(self, kappa0=.1, kappa1=2, kappa2=100):

        kappa_dict = {}
        factor = np.sqrt(3) / 2

        for i in range(49):
            kappa_dict[str(i)] = str(0)

        kappa_dict[str(0)] = str(factor * kappa0)
        kappa_dict[str(1)] = str(factor * (kappa0 + kappa1) / 2)
        kappa_dict[str(4)] = str(factor * (kappa0 + kappa2) / 2)
        kappa_dict[str(3)] = str(factor * kappa1)
        kappa_dict[str(7)] = str(factor * (kappa2 + kappa1) / 2)
        kappa_dict[str(12)] = str(factor * kappa2)

        evolver = mb.Evolver(self.system)
        evolver.add_force("Mesh>Bending", {"kappa": kappa_dict})
        computer = self.system.compute_mesh()
        energies = computer.energy(evolver)
        Eb = energies["edges"]

        return Eb

    def compute_bending_ne(self, kappa0=.1, kappa1=2, kappa2=100):

        evolver = mb.Evolver(self.system)
        kappas = [kappa0, kappa1, kappa2]

        factor = np.sqrt(3) / 2
        kappas = np.multiply(kappas, factor)

        evolver.add_force("Mesh>Bending", {"kappa": {"0": str(kappas[0]), "1": str(kappas[1]), "2": str(kappas[2])}})
        computer = self.system.compute_mesh()
        energies = computer.energy(evolver)
        Eb = energies["edges"]
        return Eb

    def compute_line_tension(self, gamma=.05):

        evolver = mb.Evolver(self.system)
        gamma_dict = {}
        uniform = gamma
        for i in range(49):
            gamma_dict[str(i)] = str(0)

        gamma_dict[str(1)] = str(uniform)
        gamma_dict[str(4)] = str(uniform)
        gamma_dict[str(7)] = str(uniform)

        evolver.add_force("Mesh>Line Tension", {"gamma": gamma_dict})
        computer = self.system.compute_mesh()
        energies = computer.energy(evolver)
        Elt = energies["vertices"]

        return Elt

    def compute_line_tension_realc(self, gamma=.05):

        evolver = mb.Evolver(self.system)
        gamma_dict = {}
        uniform = gamma
        for i in range(49):
            gamma_dict[str(i)] = str(0)

        gamma_dict[str(0)] = str(uniform)
        gamma_dict[str(1)] = str(uniform)
        gamma_dict[str(2)] = str(uniform)

        evolver.add_force("Mesh>Line Tension", {"gamma": gamma_dict})
        computer = self.system.compute_mesh()
        energies = computer.energy(evolver)
        Elt = energies["vertices"]

        return Elt



