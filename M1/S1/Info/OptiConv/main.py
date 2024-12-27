import functools

from random import randint
import numpy as np
import numpy.linalg as npl


def projection(lower, upper, value):
    return min(upper, max(value, lower))


def d(λ, X):
    return -(1/2) * λ.T.dot(X.T).dot(X).dot(λ) + sum(λ)


def gradientD(λ, X):
    return np.array([1 for _ in λ]) - X.T.dot(X).dot(λ)


def gradient_ascent_dual_svm(dataset, alpha, iterations):
    """
    :param alpha: parameter of the SVM problem
    :param dataset: List of couples x_{i}:np.array, y_{i}:+-1 representing our classes
    :param iterations: Number of iterations to compute
    :return:
    """
    proj = functools.partial(projection, lower=0.0, upper=alpha)
    X = np.zeros((n:=len(dataset[0][0]), m:=len(dataset)))
    for i in range(m):
        X[i] = dataset[i][0] * dataset[i][1]

    λ = 0
    h = max(npl.eigvalsh(X))
    for _ in range(iterations):
        oλ = λ
        λ = map(proj, oλ + h * gradientD(oλ, X))
        while d(λ, X) > d(oλ, X) + (1/(h * 2)) * (npl.norm(λ - oλ) ** 2):
            h = h /2
            λ = map(proj, oλ + h * gradientD(oλ, X))

    return X.dot(λ)


def randomized_coordinate_ascent(dataset, alpha, iterations):
    proj = functools.partial(projection, lower=0.0, upper=alpha)
    λ = np.zeros(m:= len(dataset))
    n = len(dataset[0][0])
    w = np.zeros(n)
    for _ in range(iterations):
        i = randint(0, m - 1)
        oλ = λ[i]
        λ = λ.copy()
        λ[i] = proj(oλ + (1 - (yi := dataset[i][1]) * (xi := dataset[i][0]).T.dot(w))/(npl.norm(xi)**2))
        w = w + yi * xi.dot(λ[i] - oλ)
    return w
