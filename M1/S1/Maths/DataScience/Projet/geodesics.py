import numpy as np
import numpy.linalg as npl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import csv
from typing import Iterable
import itertools
from functools import cached_property
from mpmath import cot
import scipy.sparse as sp
import scipy.sparse.linalg as spl
import tqdm

# import time

levelsets = 30


def vect_cotan(v1, v2):
    return cot(np.arccos(np.dot(v1, v2)))


def _colorfunc(t):
    return npl.norm(t) ** 2


class Manifold:
    def __init__(self, path, label=None):
        self.points = None
        self.faces = None
        self.label = label
        self.name = path[:-4].split('/')[-1]
        if path is not None:
            self.load_ascii_from_off(path)

    @property
    def tikz_dat_file(self):
        # Used to export to a format recognized by tikz.
        return "\n\n".join("\n".join(" ".join(map(str, self.points[i])) for i in f) for f in self.faces)

    @cached_property
    def colorfunc(self):
        return np.array(list(map(_colorfunc, self.points)))

    @cached_property
    def n(self):
        """
        :return: Number of Points
        """
        return len(self.points)

    @cached_property
    def m(self):
        """
        :return: Number of Faces
        """
        return len(self.faces)

    def __repr__(self):
        return f"{self.__name__}(label={self.label}, n_points={len(self.points)}, n_faces={len(self.faces)}"

    @classmethod
    def from_data(cls, data, label=None):
        """
        Creates an item from a list containing an off file.
        :param data: List item containing an object in off format
        :param label: label for the object to create
        :return: object
        """
        obj = cls(path=None, label=label)
        obj.load_list(data)
        return obj

    def load_ascii_from_off(self, path):
        """
        Loads from an off file in ascii format. Calls load_list.
        :param path: Path to off file in ascii format containing a 3D object.
        :return: None, adds data into object.
        """
        with open(path, 'r') as f:
            data = csv.reader(f, delimiter=' ')
            data = list(filter(lambda t: t and t != ' ', data))
        self.load_list(data)

    def load_list(self, data):
        """
        :param data: Data to load in OFF format.
        :return: None, is called on already instantiated item.
        """
        if len(data[0]) != 1 and data[0][0] != 'OFF':
            raise ValueError("Il n'y a pas le header OFF")

        # La deuxième ligne contient (n_points, n_faces)
        # print(data)
        p, f = [int(x) for x in data[1][:2]]

        # Les lignes suivantes contiennent les faces et les points
        points = [r[:3] for r in data[2:2 + p]]
        faces = []
        for r in data[2 + p:2 + p + f]:
            try:
                n = int(r[0])
                face = [int(x) for x in list(filter(lambda t: t, r))[1:n + 1]]
                faces.append(face)
            except ValueError:
                continue

        self.points = np.array(points, dtype=float)
        self.faces = np.array(faces)

    def plot(self, ax=None, symbols=None, function=None, show_axis=False, level_sets=False):
        """
        Plots the manifold in 3D using a colormap defined by a function.
        :param ax: Previously defined matplotlib 3D axis
        :param symbols: Symbols to use for plotting
        :param function: Function as a vector of its values on the manifold, used to get colours for the faces
        :param show_axis: Boolean
        :param level_sets: Boolean indicating whether to plot the function or its levelsets.
        :return:
        """
        if symbols is None:
            symbols = {}

        if ax is None:
            mx = self.points.max(axis=0)
            c = 0.5 * (mx + self.points.min(axis=0))
            r = 1.1 * np.max(mx - c)
            xlim, ylim, zlim = np.column_stack([c - r, c + r])

            fig = plt.figure()
            ax = fig.add_subplot(
                111,
                projection='3d',
                xlim=xlim,
                ylim=ylim,
                zlim=zlim,
                xlabel='X',
                ylabel='Y',
                zlabel='Z',
                aspect='equal'
            )

        cmap = plt.get_cmap('viridis')
        # print(cmap)

        if function is not None:
            face_colors = []
            max_val = max(function)
            min_val = min(function)
            function = (function - min_val) / (max_val - min_val)
            if level_sets:
                print("Plotting with level sets")
                for f in self.faces:
                    mean_value = np.mean([function[e] for e in f])
                    print(mean_value)
                    color = np.cos((2 * np.pi * levelsets * mean_value))
                    # print(color)
                    face_colors.append(cmap(color))
            else:
                for f in self.faces:
                    mean = np.mean([function[e] for e in f])
                    face_colors.append(cmap(mean))
            edge_colors = None
        else:
            face_colors = '#7D1DD3'
            edge_colors = '#FFE500'

        sym = dict(
            points=None,
            edges=edge_colors,
            faces=face_colors,
            linewidth=0.0001,
        )
        sym.update(symbols)

        if not show_axis:
            ax.set_axis_off()

        if sym['points'] is not None:
            x = self.points
            ax.plot(x[:, 0], x[:, 1], x[:, 2], sym['points'])

        if sym['faces'] is not None:
            if sym['edges'] is None:
                sym['edges'] = sym['faces']

            v = [self.points[f] for f in self.faces]
            poly = Poly3DCollection(
                v, edgecolor=sym['edges'],
                facecolor=sym['faces'], linewidth=sym['linewidth']
            )
            ax.add_collection(poly)
            ax.view_init(vertical_axis='y', elev=0, azim=45)
        return ax

    @cached_property
    def get_points(self):
        return lambda face: np.array([self.points[p] for p in self.faces[face]])

    @cached_property
    def vertices(self):
        return lambda index: np.array([self.points[p] for p in self.faces[:, index]])

    @cached_property
    def unnormalized_normals(self):
        a0 = self.vertices(0)
        a1 = self.vertices(1)
        a2 = self.vertices(2)
        return np.array(
            list(
                map(
                    lambda t: np.cross(*t),
                    zip(
                        map(lambda t: t[1] - t[0], zip(a1, a0)),
                        map(lambda t: t[1] - t[0], zip(a2, a0))
                    )
                )
            )
        )

    @cached_property
    def areas(self):
        return np.array(
            list(
                map(
                    lambda t: npl.norm(t) / 2,
                    self.unnormalized_normals
                )
            )
        )

    @cached_property
    def normalize(self):
        return lambda point: point / npl.norm(point) if npl.norm(point) else point

    @cached_property
    def normals(self):
        return sp.csr_matrix(list(map(self.normalize, self.unnormalized_normals)))

    @cached_property
    def diagareas(self):
        doubareas = 1 / (2 * self.areas)
        return sp.diags(list(itertools.chain(doubareas, doubareas, doubareas)), 0)

    @cached_property
    def diagareasf(self):
        doubareas = (2 * self.areas)
        return sp.diags(list(itertools.chain(doubareas, doubareas, doubareas)), 0)

    @cached_property
    def sum_op(self):
        """

        Pour i < m, e[i, j] = 0 si j \notin face i, sinon
        :return:
        """
        e = sp.dok_matrix((3 * self.m, self.n))
        normals = self.normals
        for j in tqdm.trange(self.m):
            # print(j)
            p = self.get_points(j)
            for i, index in enumerate(self.faces[j]):
                s = (i + 1) % 3
                t = (i + 2) % 3
                n = normals[j].toarray()[0]
                opp_edge = p[t] - p[s]
                jeji = np.cross(n, opp_edge)
                e[j, index] += jeji[0]
                e[j + self.m, index] += jeji[1]
                e[j + 2 * self.m, index] += jeji[2]
        return e

    @cached_property
    def gradient_op(self):
        return self.diagareas.dot(self.sum_op)

    @cached_property
    def divergence_op(self):
        return self.gradient_op.transpose().dot(self.diagareasf)

    @cached_property
    def laplacian_op(self):
        g = self.gradient_op
        d = self.divergence_op
        res = d.dot(g)
        return res

    def heat_variation_level_sets(self, vertex: int, time_step: int):
        assert vertex <= self.n
        delta = np.zeros((self.n, 1))
        delta[vertex] = 1
        laplacian = self.laplacian_op
        mat = sp.identity(laplacian.shape[0]) + time_step * laplacian
        return mat.inverse().dot(delta)

    def geodesics(self, vertex: int, time_step: int):
        assert vertex <= self.n
        delta = np.zeros((self.n, 1))
        delta[vertex] = 1
        print("Computing Laplacian")
        grad = self.gradient_op
        div = grad.transpose().dot(self.diagareasf)
        laplacian = div.dot(grad)
        print("Inverting Laplacian")
        mat = sp.identity(laplacian.shape[0]) + time_step * laplacian
        mat = spl.inv(mat)
        print("Computing Diffusion Step")
        u = mat.dot(delta)
        g = grad.dot(u)
        h = -self.normalize(g)
        ophi = mat.dot(div.dot(h))
        return ophi

    def implicit_time_stepping_heat_equation(self, vertex: int, time_step: float, iterations: Iterable[int],
                                             level_sets=False):
        assert vertex <= self.n
        u = np.zeros((self.n, 1))
        u[vertex] = 1
        laplacian = self.laplacian_op
        with open(f"{self.name}_values.txt", 'w') as f:
            f.write(f"Vertex: {vertex}, Time Step: {time_step}, Iterations: {iterations}\n\n")
            f.write(str(laplacian))
            f.write("\n\n")
        _mat = sp.identity(laplacian.shape[0]) + time_step * laplacian
        mat = spl.inv(_mat)
        # print(u)
        for i in tqdm.trange(max(iterations) + 1):
            u = mat.dot(u)
            if i in iterations:
                # print(u)
                self.plot(show_axis=True, function=u, level_sets=level_sets)
                # plt.savefig(f'Figures/{self.name}_{i}.png')
                # with open(f"{self.name}_values.txt", 'a') as f:
                #     f.write(f"Itération: {i}\n" + str(u.transpose()) + "\n\n")
        return


if __name__ == '__main__':
    file = "toolbox_graph/elephant-50kv.off"
    manif = Manifold(file)
    # manif.plot()
    # print(manif.points, manif.faces)
    # print(manif.laplacian_op.toarray())
    # manif.implicit_time_stepping_heat_equation(
    #     vertex=1, time_step=10, iterations=list(filter(lambda t: t % 10 == 0, range(50)))
    # )
    phi = manif.geodesics(vertex=1, time_step=100)
    manif.plot(show_axis=True, function=phi, level_sets=True)
    plt.show()
