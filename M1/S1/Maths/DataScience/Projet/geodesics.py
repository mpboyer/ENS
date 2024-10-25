import numpy as np
import numpy.linalg as npl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import csv
from typing import Callable, Iterable
import itertools
from functools import cached_property
from mpmath import cot


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
            self.load_ascii_from_off(path)

    @cached_property
    def n(self):
        return len(self.points)

    @cached_property
    def m(self):
        return len(self.faces)

    def __repr__(self):
        return f"{self.__name__}(label={self.label}, n_points={len(self.points)}, n_faces={len(self.faces)}"

    @classmethod
    def from_data(cls, data, label=None):
        obj = cls(path=None, label=label)
        obj.load_list(data)
        return obj

    def load_ascii_from_off(self, path):
        with open(path, 'r') as f:
            data = csv.reader(f, delimiter=' ')
            data = list(filter(lambda t: t, data))
        self.load_list(data)

    def load_list(self, data):
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

    def plot(self, ax=None, symbols=None, function=None, show_axis=False):
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

        if function is not None:
            face_colors = []
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
            poly = Poly3DCollection(v) # , edgecolor=sym['edges'], facecolor=sym['faces'], linewidth=sym['linewidth'])
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
    def face_unnormalized_normal(self):
        return lambda face_vertices: np.cross(face_vertices[1] - face_vertices[0], face_vertices[2] - face_vertices[0])

    @cached_property
    def unnormalized_normals(self):
        a0 = self.vertices(0)
        a1 = self.vertices(1)
        a2 = self.vertices(2)
        return np.array(list(map(lambda t: np.cross(*t), zip(map(lambda t: t[1] - t[0], zip(a1, a0)), map(lambda t: t[1] - t[0], zip(a2, a0))))))

    @cached_property
    def face_area(self):
        return lambda face_vertices: npl.norm(self.face_unnormalized_normal(face_vertices)) / 2

    @cached_property
    def areas(self):
        return np.array(list(map(lambda t: npl.norm(t) / 2, self.unnormalized_normals)))

    @cached_property
    def normalize(self):
        return lambda point: point / npl.norm(point) if npl.norm(point) else point

    @cached_property
    def normals(self):
        return np.array(list(map(self.normalize, self.unnormalized_normals)))

    @cached_property
    def spdiags(self):
        l = 2 * self.areas
        return np.diag(list(itertools.chain(l, l, l)))

    @cached_property
    def sum_op(self):
        e = np.zeros((3 * self.m, self.n))
        normals = self.normals
        for j in range(self.m):
            p = self.get_points(j)
            for i, index in enumerate(self.faces[j]):
                s = (index + 1) % 3
                t = (index + 2) % 3
                JEJI = np.cross(normals[j], p[t] - p[s])
                e[j, i] = JEJI[0]
                e[j + self.m, i] = JEJI[1]
                e[j + 2 * self.m, i] = JEJI[2]
        return e

    # grad(f)(j) = 1/2Aj sum_{i= 1}^{3}f_{i}N_{j} ^ e_{i + 1, i + 2}
    @cached_property
    def pointwise_gradient(self):
        # gradient: (V -> \R) -> F -> \R^{3}
        return lambda function: \
            (lambda face_vertices:
             sum(function(f) * np.cross(self.normalize(self.face_unnormalized_normal(face_vertices)), face_vertices[(index + 2) % 3] - face_vertices[(index + 1) % 3])
                 for (f, index) in enumerate(face_vertices) / (2 * self.face_area(face_vertices)))
             )

    @cached_property
    def gradient_op(self):
        return np.matmul(self.spdiags, self.sum_op)

    def gradient(self, function: Callable[Iterable[float], float]):
        res = np.matmul(self.gradient_op, np.array(list(map(function, self.points))))
        return np.array([[res[j], res[j + self.m], res[j + 2 * self.m]] for j in range(self.m)])

    @cached_property
    def divergence_op(self):
        return np.matmul(self.gradient_op.transpose(), self.spdiags)

    @cached_property
    def laplacian_op(self):
        g = self.gradient_op
        d = np.matmul(g.transpose(), self.spdiags)
        return np.matmul(d, g)

    def laplacian(self, function):
        res = np.matmul(self.laplacian_op, np.array(list(map(function, self.points))))
        return res

    @cached_property
    def colorfunc(self):
        return np.array(list(map(_colorfunc, self.points)))


if __name__ == '__main__':
    manif = Manifold("toolbox_graph/camel.off")
    manif.plot(show_axis=True, symbols=dict(shade=True))
    plt.show()
    # plt.savefig('avant.png')
    # manif.plot(show_axis=True, function=manif.laplacian(_colorfunc))
    # plt.savefig('apres.png')
