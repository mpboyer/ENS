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

        cmap = parula_map
        # cmap = plt.get_cmap('seismic')
        # print(cmap)

        if function is not None:
            face_colors = []
            max_val = max(function)
            min_val = min(function)
            function = (function - min_val) / (max_val - min_val)
            if level_sets:
                # print("Plotting with level sets")
                for f in self.faces:
                    mean_value = np.mean([function[e] for e in f])
                    # print(mean_value)
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
    def areamatrix(self):
        areas = self.areas
        area_diag = [0. for _ in self.points]
        for i, f in enumerate(self.faces):
            print(f)
            for v in f:
                area_diag[v] += 1 / 3 * areas[i]
        return sp.diags(area_diag, 0)

    @cached_property
    def laplacian_sum_op(self):
        s = np.array(0., like=(self.n, self.n))
        for f in self.faces:
            j1, j2, j3 = f

        return

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
        for j in range(self.m):  # tqdm.trange(self.m, leave=False):
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
        # print("Computing Laplacian")
        grad = self.gradient_op
        div = grad.T.dot(self.diagareasf)
        laplacian = div.dot(grad)
        # print(laplacian)
        # print("Inverting Laplacian")
        mat = sp.eye(self.n) + time_step * laplacian
        mat = spl.inv(mat)
        # print("Computing Diffusion Step")
        u = mat.dot(delta)
        g = grad.dot(u)
        h = -g
        laplacian_inv = spl.inv(laplacian)
        ophi = laplacian_inv.dot(div.dot(h)).T
        ophi = np.reshape(ophi, (self.n,))
        ophi = ophi - min(ophi)
        # print(ophi)
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
        for i in range(max(iterations) + 1):  # tqdm.trange(max(iterations) + 1, leave=False):
            u = mat.dot(u)
            if i in iterations:
                # print(u)
                self.plot(show_axis=True, function=u, level_sets=level_sets)
                name_file = f"{self.name}_t={time_step}_i={i}_{level_sets}.png"
                plt.savefig(f'Figures/{name_file}')
                # with open(f"{self.name}_values.txt", 'a') as f:
                #     f.write(f"Itération: {i}\n" + str(u.transpose()) + "\n\n")
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
    fake_errors = []
    times = []
    for i in tqdm.trange(1, batches, desc="Comparing for the plane.", leave=True):
        t1 = time.time()
        epsilon = 1 / i
        m = plane_square_manifold(epsilon)
        with open(f"plane_manifold_{i}.off", "w") as f:
            f.write(m)
        manif = Manifold(f"plane_manifold_{i}.off")
        true_g = np.array([np.sqrt(epsilon) * npl.norm(np.array([k % (i + 1), k // (i + 1) ])) for k in range(manif.n)])
        graph_g = np.array([np.sqrt(epsilon) * sum(np.array([k % (i + 1), k // (i + 1) ])) for k in range(manif.n)])
        g = manif.geodesics(0, 1e-5)
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
        fake_errors.append(np.mean(abs(true_g - graph_g)))
        times.append(t2 - t1)
        try:
            os.remove(f"plane_manifold_{i}.off")
        except FileNotFoundError:
            pass
        # print(c)
    return errors, fake_errors


def sphere_comparator():
    # TODO: Compare on number of points
    return


if __name__ == '__main__':
    # err, fake_err = plane_comparator(100)
    # with open("fake_plane.txt", "w") as f:
    #     f.write(str(fake_err))
    #     f.write("\n")
    #     f.write(str(err))

    # tim = np.array([0.013149023056030273, 0.020489931106567383, 0.03502511978149414, 0.05764174461364746,
    #            0.09006428718566895,
    # 0.11829209327697754, 0.15219831466674805, 0.19966363906860352, 0.24759960174560547, 0.3016645908355713, 0.36319780349731445, 0.43642115592956543, 0.5085740089416504, 0.588261604309082, 0.6055846214294434, 0.5321588516235352, 0.5333161354064941, 0.5925807952880859, 0.665614128112793, 0.7518506050109863, 0.8330981731414795, 0.9165232181549072, 1.068143606185913, 1.1483819484710693, 1.2146315574645996, 1.347912311553955, 1.4571983814239502, 1.6533777713775635, 1.7653348445892334, 1.8603324890136719, 2.0015053749084473, 2.160510301589966, 2.304192543029785, 2.516556978225708, 2.659261465072632, 2.808661937713623, 3.004868507385254, 3.275782823562622, 3.4321444034576416, 3.656442880630493, 3.9170353412628174, 4.202671766281128, 4.357384443283081, 4.7114574909210205, 4.971206903457642, 5.432301759719849, 5.646081924438477, 5.932646036148071, 6.220357894897461, 6.641796588897705, 6.983593225479126, 7.317787170410156, 7.8660500049591064, 8.602615356445312, 8.889338254928589, 9.128491640090942, 9.521665811538696, 9.917006492614746, 10.42499566078186, 10.813038110733032, 12.094079732894897, 13.044790506362915, 12.898698329925537, 13.446001529693604, 14.203690528869629, 14.943839311599731, 15.875797033309937, 16.614152193069458, 16.892996549606323, 18.298852682113647, 18.427256107330322, 19.281900644302368, 19.80189609527588, 20.651122570037842, 21.602256298065186, 22.77059841156006, 23.715381622314453, 24.505598306655884, 25.375815391540527, 26.976271152496338, 28.28458595275879, 29.85113501548767, 30.105552196502686, 30.820223093032837, 32.393033027648926, 33.69677686691284, 34.32210874557495, 35.16563868522644, 36.882479190826416, 37.398133277893066, 39.01607298851013, 40.273043155670166, 42.13457107543945, 44.42324090003967, 45.13938760757446, 46.633127212524414, 49.642672061920166, 51.82348918914795, 52.44626760482788])
    fake_err = [np.float64(0.1464466094067262), np.float64(0.2581115237855768), np.float64(0.34305159950969916), np.float64(0.413191747775405), np.float64(0.4739470139200022), np.float64(0.5281647211152665), np.float64(0.5775256857797603), np.float64(0.6231088948217861), np.float64(0.665651458904677), np.float64(0.7056814867106909), np.float64(0.7435917765816608), np.float64(0.7796834185519701), np.float64(0.8141929802554383), np.float64(0.8473102049238446), np.float64(0.879189956539994), np.float64(0.9099605330350837), np.float64(0.9397296060510764), np.float64(0.9685885628266329), np.float64(0.996615744063643), np.float64(1.023878901400225), np.float64(1.0504370919973065), np.float64(1.0763421597477536), np.float64(1.1016399079637833), np.float64(1.1263710384233738), np.float64(1.1505719111316883), np.float64(1.1742751648449101), np.float64(1.1975102282643098), np.float64(1.2203037445148786), np.float64(1.2426799262041355), np.float64(1.264660854428797), np.float64(1.286266732162167), np.float64(1.3075161002384266), np.float64(1.328426022458894), np.float64(1.349012245043027), np.float64(1.3692893346352708), np.float64(1.3892707982865151), np.float64(1.4089691882035895), np.float64(1.4283961935631277), np.float64(1.4475627212882916), np.float64(1.4664789673663976), np.float64(1.485154480025827), np.float64(1.5035982158789718), np.float64(1.5218185899645702), np.float64(1.5398235204799788), np.float64(1.557620468875713), np.float64(1.5752164758863294), np.float64(1.5926181939896347), np.float64(1.6098319167173687), np.float64(1.626863605182552), np.float64(1.643718912139687), np.float64(1.660403203852428), np.float64(1.67692158000796), np.float64(1.6932788918870718), np.float64(1.7094797589730164), np.float64(1.7255285841599604), np.float64(1.7414295677026317), np.float64(1.7571867200321551), np.float64(1.772803873548668), np.float64(1.7882846934887873), np.float64(1.8036326879550795), np.float64(1.8188512171851634), np.float64(1.8339435021296966), np.float64(1.8489126324011926), np.float64(1.8637615736491462), np.float64(1.8784931744112503), np.float64(1.8931101724854862), np.float64(1.9076152008633873), np.float64(1.9220107932608577), np.float64(1.9362993892793963), np.float64(1.950483339227467), np.float64(1.9645649086289638), np.float64(1.9785462824432354), np.float64(1.9924295690188962), np.float64(2.006216803801669), np.float64(2.0199099528146918), np.float64(2.033510915928132), np.float64(2.0470215299334846), np.float64(2.0604435714366147), np.float64(2.07377875958245), np.float64(2.087028758623133), np.float64(2.100195180340481), np.float64(2.1132795863327387), np.float64(2.12628349017479), np.float64(2.1392083594602838), np.float64(2.152055617733474), np.float64(2.1648266463179544), np.float64(2.177522786048946), np.float64(2.190145338915272), np.float64(2.20269556961671), np.float64(2.2151747070419985), np.float64(2.227583945672369), np.float64(2.239924446915153), np.float64(2.25219734037166), np.float64(2.2644037250432594), np.float64(2.2765446704792924), np.float64(2.2886212178702108), np.float64(2.300634381089113), np.float64(2.3125851476846027), np.float64(2.324474479827748)]
    err = [np.float64(0.47854957589600816), np.float64(0.3331178092072416), np.float64(0.7676095222024307), np.float64(0.7552459849007055), np.float64(0.8036210036369048), np.float64(0.9981417406936368), np.float64(1.1795555577142007), np.float64(1.2876234933315323), np.float64(1.419846210624426), np.float64(1.509433773079624), np.float64(1.567868052419781), np.float64(1.7698459552629835), np.float64(1.7866071737469527), np.float64(1.9317202365323718), np.float64(1.9849542253185977), np.float64(2.123193403222161), np.float64(2.2219455958764787), np.float64(2.3180228049842175), np.float64(2.39674626570144), np.float64(2.482141490342916), np.float64(2.5692208028500447), np.float64(2.6393341669027452), np.float64(2.725786370783511), np.float64(2.856938660419562), np.float64(2.866570524288031), np.float64(2.9579865908034164), np.float64(3.0217734997302648), np.float64(3.0918593482297334), np.float64(3.1693476026246046), np.float64(3.2414304783944514), np.float64(3.302824521362246), np.float64(3.369578319681982), np.float64(3.4400115273460155), np.float64(3.499638220124812), np.float64(3.556227821912326), np.float64(3.644186487012385), np.float64(3.6981062715039696), np.float64(3.7501994068368028), np.float64(3.809630291564401), np.float64(3.8699841808753686), np.float64(3.9335852937043576), np.float64(3.9873011026672978), np.float64(4.053631909663748), np.float64(4.103071768490018), np.float64(4.164402048565011), np.float64(4.2219279619003665), np.float64(4.275765011590856), np.float64(4.3344859679927605), np.float64(4.381935798858256), np.float64(4.441032793741062), np.float64(4.493155158430741), np.float64(4.554417682044583), np.float64(4.59742036999634), np.float64(4.651938059051716), np.float64(4.703527038293598), np.float64(4.752825551367579), np.float64(2.2053865877193783), np.float64(4.8637793788860835), np.float64(4.906607507309652), np.float64(4.963469463859358), np.float64(5.001730535068715), np.float64(5.049993576512656), np.float64(5.102826317202104), np.float64(5.146386368541422), np.float64(5.193236998159585), np.float64(5.240091126973547), np.float64(5.287086672024641), np.float64(5.330987009099841), np.float64(5.380916196486229), np.float64(5.424539897104953), np.float64(5.4704032511690155), np.float64(5.514943567085832), np.float64(5.559986364973512), np.float64(5.605050586036641), np.float64(5.6490299510672415), np.float64(5.695103866247409), np.float64(5.736073491424627), np.float64(5.779279285735278), np.float64(5.8223533551847035), np.float64(5.865651011283237), np.float64(5.907572781224347), np.float64(5.949567948763174), np.float64(5.9916896473196894), np.float64(6.03318674351393), np.float64(6.073844390350174), np.float64(6.115652659912414), np.float64(6.156739470909129), np.float64(6.198084139450606), np.float64(6.238209985312597), np.float64(6.283971095689327), np.float64(6.317466999381283), np.float64(6.358282472610332), np.float64(6.398040893745537), np.float64(6.43864979198441), np.float64(6.476545890384705), np.float64(6.504448053340971), np.float64(6.552339751297614), np.float64(6.5822759022266055), np.float64(6.630861163554649)]
    fig, ax = plt.subplots(1, 1)
    ax.plot(err, c="#7d1dd3", label="Actual computed accuracy")
    ax.plot(fake_err, c="#ffe500", label="Theoretical bound on accuracy")
    ax.legend()
    ax.set_title(r"$\ell^2$ error for rectangular plane subdivision")
    plt.savefig("Figures/compare_err_comp_planes_i<=100.pdf")
    # plt.clf()
    # fig, ax = plt.subplots(1, 1)
    # ax.plot(tim, c="#7d1dd3")
    # ax.set_title(r"Time for rectangular plane subdivision geodesics computation")
    # plt.savefig("Figures/tim_comp_planes_i<=100.pdf")

    # file = "toolbox_graph/camel.off"
    # manif = Manifold(file)
    # # manif.plot()
    # # print(manif.points, manif.faces)
    # # print(manif.laplacian_op.toarray())
    # manif.implicit_time_stepping_heat_equation(
    #     vertex=0, time_step=10, iterations=list(filter(lambda t: t % 10 == 0, range(101))), level_sets=False,
    # )
    # plt.show()
