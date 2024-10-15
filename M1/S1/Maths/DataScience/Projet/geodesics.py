import numpy as np
import numpy.linalg as npl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import csv


class Manifold:
    def __init__(self, path, label=None):
        self.points = None
        self.faces = None
        self.label = label
        if path is not None:
            self.load_ascii_from_off(path)

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
            data = list(data)
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
            n = int(r[0])
            face = [int(x) for x in r[1:n + 1]]
            faces.append(face)

        self.points = np.array(points, dtype='float')
        self.faces = faces

    def plot(self, ax=None, symbols=None):
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

        sym = dict(
            points=None,
            edges='#FFE500',
            faces='#7D1DD3',
        )
        sym.update(symbols)
        ax.set_axis_off()
        if sym['points'] is not None:
            x = self.points
            ax.plot(x[:, 0], x[:, 1], x[:, 2], sym['points'])

        if sym['faces'] is not None:
            if sym['edges'] is None:
                sym['edges'] = sym['faces']

            v = [self.points[f] for f in self.faces]
            poly = Poly3DCollection(v, edgecolor=sym['edges'], facecolor=sym['faces'])
            ax.add_collection(poly)
            ax.view_init(vertical_axis='y', elev=0, azim=45)
        return ax

    def get_points(self):
        return lambda face: np.array([self.points[p] for p in self.faces[face]])

    @classmethod
    def unnormalized_normal(cls):
        return lambda face_vertices: np.cross(face_vertices[1] - face_vertices[0], face_vertices[2] - face_vertices[0])

    @classmethod
    def area(cls):
        return lambda face_vertices: npl.norm(cls.unnormalized_normal()(face_vertices)) / 2

    @classmethod
    def normalize(cls):
        return lambda point: point / npl.norm(point) if npl.norm(point) else point

    @classmethod
    def gradient(cls):
        return []


if __name__ == '__main__':
    manif = Manifold("toolbox_graph/camel.off")
    manif.plot()
    plt.show()
