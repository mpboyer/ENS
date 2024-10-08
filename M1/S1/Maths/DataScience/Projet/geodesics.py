import numpy as np


def cross(v1, v2):
    return np.array([v1[1] * v2[2] - v2[1] * v1[2], v1[2] * v2[0] - v2[2] * v1[0], v1[0] * v2[1] - v2[0] * v1[1]])


class Vertex():
    def __init__(self, identifier):
        self.id = identifier
        self.coordinates = np.array([0., 0., 0.])
        self.neighbours = []
        self.faces = []


class Manifold():
    def __init__(self, vertices, edges, faces):
        self.number_vertices = len(vertices)
        self.edges = edges
        self.faces = faces
        self.vertices = np.zeros((len(vertices), 3))
