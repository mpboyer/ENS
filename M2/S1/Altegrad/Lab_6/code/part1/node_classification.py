"""
Deep Learning on Graphs - ALTEGRAD - Nov 2025
"""

import networkx as nx
import numpy as np
from scipy.sparse.linalg import eigs
from scipy.sparse import diags, eye

from sklearn.linear_model import LogisticRegression
from sklearn.manifold import SpectralEmbedding
from sklearn.metrics import accuracy_score
from deepwalk import deepwalk
import matplotlib.pyplot as plt


# Loads the karate network
G = nx.read_weighted_edgelist(
    "../data/karate.edgelist", delimiter=" ", nodetype=int, create_using=nx.Graph()
)
print("Number of nodes:", G.number_of_nodes())
print("Number of edges:", G.number_of_edges())

n = G.number_of_nodes()

# Loads the class labels
class_labels = np.loadtxt("../data/karate_labels.txt", delimiter=",", dtype=np.int32)
idx_to_class_label = dict()
for i in range(class_labels.shape[0]):
    idx_to_class_label[class_labels[i, 0]] = class_labels[i, 1]

y = list()
for node in G.nodes():
    y.append(idx_to_class_label[node])

y = np.array(y)


############## Task 5
# Visualizes the karate network

plt.figure(figsize=(10, 8))
nx.draw_networkx(G, node_color=y, cmap=plt.cm.coolwarm, with_labels=True)
plt.title("Karate Network Visualization")
plt.show()

############## Task 6
# Extracts a set of random walks from the karate network and feeds them to the Skipgram model
n_dim = 128
n_walks = 10
walk_length = 20
model = deepwalk(G, n_walks, walk_length, n_dim)

embeddings = np.zeros((n, n_dim))
for i, node in enumerate(G.nodes()):
    embeddings[i, :] = model.wv[str(node)]

idx = np.random.RandomState(seed=42).permutation(n)
idx_train = idx[: int(0.8 * n)]
idx_test = idx[int(0.8 * n) :]

X_train = embeddings[idx_train, :]
X_test = embeddings[idx_test, :]

y_train = y[idx_train]
y_test = y[idx_test]


############## Task 7
# Trains a logistic regression classifier and use it to make predictions

logreg = LogisticRegression(solver="liblinear", random_state=42)
logreg.fit(X_train, y_train)
y_pred = logreg.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy of Logitic Regression: {accuracy:.4f}")

############## Task 8
# Generates spectral embeddings

sk_spectral_embedding = SpectralEmbedding(
    n_components=n_dim, random_state=42, affinity="nearest_neighbors"
)
sk_spectral_embeddings = sk_spectral_embedding.fit_transform(nx.adjacency_matrix(G))

X_train_sk_spectral = sk_spectral_embeddings[idx_train, :]
X_test_sk_spectral = sk_spectral_embeddings[idx_test, :]

logreg_sk_spectral = LogisticRegression(solver="liblinear", random_state=42)
logreg_sk_spectral.fit(X_train_sk_spectral, y_train)
y_pred_sk_spectral = logreg_sk_spectral.predict(X_test_sk_spectral)

accuracy_sk_spectral = accuracy_score(y_test, y_pred_sk_spectral)
print(
    f"Accuracy of Logistic Regression with SKLearn Spectral Embeddings: {accuracy_sk_spectral:.4f}"
)

A = nx.adjacency_matrix(G)

degrees = dict(G.degree())
d_values = [degrees[node] for node in sorted(G.nodes())]
D = diags(d_values).toarray()

D_inv = diags([1 / d for d in d_values]).toarray()

Lrw = np.eye(G.number_of_nodes()) - (D_inv @ A)

eigenvalues, eigenvectors = eigs(Lrw, k=2, which="SR")
eigenvalues = eigenvalues.real
eigenvectors = eigenvectors.real

# Sort eigenvectors by eigenvalues (ascending order)
sorted_indices = np.argsort(eigenvalues)
largest_eigenvectors = eigenvectors[:, sorted_indices[:2]]

X_train_lrw = largest_eigenvectors[idx_train, :]
X_test_lrw = largest_eigenvectors[idx_test, :]

logreg_lrw = LogisticRegression(solver="liblinear", random_state=42)
logreg_lrw.fit(X_train_lrw, y_train)
y_pred_lrw = logreg_lrw.predict(X_test_lrw)

accuracy_lrw = accuracy_score(y_test, y_pred_lrw)
print(
    f"Accuracy of Logistic Regression with Lrw Spectral Embeddings: {accuracy_lrw:.4f}"
)
