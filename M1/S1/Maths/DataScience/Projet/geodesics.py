import csv
from typing import Iterable
import itertools
from functools import cached_property
import os
import time

import numpy as np
import numpy.linalg as npl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpmath import cot
import scipy.sparse as sp
import scipy.sparse.linalg as spl
import tqdm
from matplotlib.colors import LinearSegmentedColormap

# import time

levelsets = 10

cm_data = [[0.2081, 0.1663, 0.5292], [0.2116238095, 0.1897809524, 0.5776761905],
 [0.212252381, 0.2137714286, 0.6269714286], [0.2081, 0.2386, 0.6770857143],
 [0.1959047619, 0.2644571429, 0.7279], [0.1707285714, 0.2919380952,
  0.779247619], [0.1252714286, 0.3242428571, 0.8302714286],
 [0.0591333333, 0.3598333333, 0.8683333333], [0.0116952381, 0.3875095238,
  0.8819571429], [0.0059571429, 0.4086142857, 0.8828428571],
 [0.0165142857, 0.4266, 0.8786333333], [0.032852381, 0.4430428571,
  0.8719571429], [0.0498142857, 0.4585714286, 0.8640571429],
 [0.0629333333, 0.4736904762, 0.8554380952], [0.0722666667, 0.4886666667,
  0.8467], [0.0779428571, 0.5039857143, 0.8383714286],
 [0.079347619, 0.5200238095, 0.8311809524], [0.0749428571, 0.5375428571,
  0.8262714286], [0.0640571429, 0.5569857143, 0.8239571429],
 [0.0487714286, 0.5772238095, 0.8228285714], [0.0343428571, 0.5965809524,
  0.819852381], [0.0265, 0.6137, 0.8135], [0.0238904762, 0.6286619048,
  0.8037619048], [0.0230904762, 0.6417857143, 0.7912666667],
 [0.0227714286, 0.6534857143, 0.7767571429], [0.0266619048, 0.6641952381,
  0.7607190476], [0.0383714286, 0.6742714286, 0.743552381],
 [0.0589714286, 0.6837571429, 0.7253857143],
 [0.0843, 0.6928333333, 0.7061666667], [0.1132952381, 0.7015, 0.6858571429],
 [0.1452714286, 0.7097571429, 0.6646285714], [0.1801333333, 0.7176571429,
  0.6424333333], [0.2178285714, 0.7250428571, 0.6192619048],
 [0.2586428571, 0.7317142857, 0.5954285714], [0.3021714286, 0.7376047619,
  0.5711857143], [0.3481666667, 0.7424333333, 0.5472666667],
 [0.3952571429, 0.7459, 0.5244428571], [0.4420095238, 0.7480809524,
  0.5033142857], [0.4871238095, 0.7490619048, 0.4839761905],
 [0.5300285714, 0.7491142857, 0.4661142857], [0.5708571429, 0.7485190476,
  0.4493904762], [0.609852381, 0.7473142857, 0.4336857143],
 [0.6473, 0.7456, 0.4188], [0.6834190476, 0.7434761905, 0.4044333333],
 [0.7184095238, 0.7411333333, 0.3904761905],
 [0.7524857143, 0.7384, 0.3768142857], [0.7858428571, 0.7355666667,
  0.3632714286], [0.8185047619, 0.7327333333, 0.3497904762],
 [0.8506571429, 0.7299, 0.3360285714], [0.8824333333, 0.7274333333, 0.3217],
 [0.9139333333, 0.7257857143, 0.3062761905], [0.9449571429, 0.7261142857,
  0.2886428571], [0.9738952381, 0.7313952381, 0.266647619],
 [0.9937714286, 0.7454571429, 0.240347619], [0.9990428571, 0.7653142857,
  0.2164142857], [0.9955333333, 0.7860571429, 0.196652381],
 [0.988, 0.8066, 0.1793666667], [0.9788571429, 0.8271428571, 0.1633142857],
 [0.9697, 0.8481380952, 0.147452381], [0.9625857143, 0.8705142857, 0.1309],
 [0.9588714286, 0.8949, 0.1132428571], [0.9598238095, 0.9218333333,
  0.0948380952], [0.9661, 0.9514428571, 0.0755333333],
 [0.9763, 0.9831, 0.0538]]

parula_map = LinearSegmentedColormap.from_list('parula', cm_data)


def vect_cotan(v1, v2):
    return cot(np.arccos(np.dot(v1, v2)))


def _colorfunc(t):
    return npl.norm(t) ** 2


class Manifold:
    def __init__(self, path, label=None):
        self.points = None
        self.faces = None
        self.label = label
        if path is not None:
            self.name = path[:-4].split('/')[-1]
            self.load_ascii_from_off(path)

    @property
    def tikz_dat_file(self):
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

    def load_from_str(self, off):
        data = csv.reader(off, delimiter=' ')
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

        cmap = parula_map

        if function is not None:
            face_colors = []
            max_val = max(function)
            min_val = min(function)
            function = (function - min_val) / (max_val - min_val)
            if level_sets:
                for f in self.faces:
                    mean_value = np.mean([function[e] for e in f])
                    color = np.cos((2 * np.pi * levelsets * mean_value))
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
    def areamatrix(self):
        areas = self.areas
        area_diag = [0. for _ in self.points]
        for i, f in enumerate(self.faces):
            for v in f:
                area_diag[v] += 1 / 3 * areas[i]
        return sp.diags(area_diag, 0)

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
        https://computergraphics.stackexchange.com/questions/8835/calculating-the-gradient-of-a-triangular-mesh
        :return:
        """
        e = sp.dok_matrix((3 * self.m, self.n))
        normals = self.normals
        for j in range(self.m):
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
        return self.gradient_op.T.dot(self.diagareasf)

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
        grad = self.gradient_op
        div = grad.T.dot(self.diagareasf)
        laplacian = div.dot(grad)
        mat = sp.eye(self.n) + time_step * laplacian
        mat = spl.inv(mat)
        u = mat.dot(delta)
        g = grad.dot(u)
        h = -g
        laplacian_inv = spl.inv(laplacian)
        ophi = laplacian_inv.dot(div.dot(h)).T
        ophi = np.reshape(ophi, (self.n,))
        ophi = ophi - min(ophi)
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
        for i in range(max(iterations) + 1):
            u = mat.dot(u)
            if i in iterations:
                self.plot(show_axis=True, function=u, level_sets=level_sets)
                name_file = f"{self.name}_t={time_step}_i={i}_{level_sets}.png"
                plt.savefig(f'Figures/{name_file}')
        plt.show()
        return


def plane_square_manifold(epsilon):
    even = np.arange(0, 1 + epsilon/2, epsilon)  # Evenly spaced by epsilon points
    points = []
    for x in even:
        for y in even:
            points.append((x, y, 0))
    n = len(even)
    # print(dict(enumerate(points)))
    faces = []
    for i in range(len(points)):
        if i % n < n - 1 and i + n < len(points) :
            faces.append((3, i, i + 1, i + n))
        if i % n > 0 and i + n < len(points):
            faces.append((3, i, i + n, i + n - 1))
    # print(faces)
    manifold = "OFF\n"
    manifold += f"{len(points)} {len(faces)}\n"
    manifold += "\n".join(map(lambda p: " ".join(map(str, p)), points)) + "\n"
    manifold += "\n".join(map(lambda p: " ".join(map(str, p)), faces))
    return manifold


def plane_comparator(batches):
    # Here we will only look at [0, 1]^{2} as the plane
    errors = []
    times = []
    for i in tqdm.trange(1, batches, desc="Comparing for the plane.", leave=True):
        t1 = time.time()
        epsilon = 1 / i
        m = plane_square_manifold(epsilon)
        with open(f"plane_manifold_{i}.off", "w") as f:
            f.write(m)
        manif = Manifold(f"plane_manifold_{i}.off")
        true_g = np.array([np.sqrt(epsilon) * npl.norm(np.array([k % (i + 1), k // (i + 1) ])) for k in range(manif.n)])
        g = manif.geodesics(0, (1 / i)**2)
        if i % 10 == 0:
            ax = manif.plot(function=g)
            ax.set_title(f'Figures/plane_compar_err_{i}.pdf')
            plt.savefig(f'Figures/plane_compar_err_{i}.pdf')
            ax = manif.plot(function=true_g)
            ax.set_title(f'Figures/plane_compar_true_{i}.pdf')
            plt.savefig(f'Figures/plane_compar_true_{i}.pdf')
        c = np.mean(abs(true_g - g))
        t2 = time.time()
        errors.append(c)
        times.append(t2 - t1)
        try:
            os.remove(f"plane_manifold_{i}.off")
        except FileNotFoundError:
            pass
        # print(c)
    return errors, times
