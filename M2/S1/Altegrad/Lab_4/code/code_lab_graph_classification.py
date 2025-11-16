"""
Graph Mining - ALTEGRAD - Nov 2024
"""

import networkx as nx
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from torch_geometric.datasets import TUDataset
from torch_geometric.utils import to_networkx

############## Task 7


# load Mutag dataset
def load_dataset():
    # Load the MUTAG dataset
    dataset = TUDataset(root="./data", name="MUTAG")

    Gs = []
    for data in dataset:
        # Convert each graph from PyTorch Geometric to NetworkX format
        G = to_networkx(
            data, to_undirected=True
        )  # Convert the graph, optionally make it undirected
        Gs.append(G)

    # Extract the labels (y) for each graph in the dataset
    y = [data.y.item() for data in dataset]

    return Gs, y


Gs, y = load_dataset()

# Gs, y = create_dataset()
G_train, G_test, y_train, y_test = train_test_split(
    Gs, y, test_size=0.2, random_state=42
)


# Compute the shortest path kernel
def shortest_path_kernel(Gs_train, Gs_test):
    all_paths = dict()
    sp_counts_train = dict()

    for i, G in enumerate(Gs_train):
        sp_lengths = dict(nx.shortest_path_length(G))
        sp_counts_train[i] = dict()
        nodes = G.nodes()
        for v1 in nodes:
            for v2 in nodes:
                if v2 in sp_lengths[v1]:
                    length = sp_lengths[v1][v2]
                    if length in sp_counts_train[i]:
                        sp_counts_train[i][length] += 1
                    else:
                        sp_counts_train[i][length] = 1

                    if length not in all_paths:
                        all_paths[length] = len(all_paths)

    sp_counts_test = dict()

    for i, G in enumerate(Gs_test):
        sp_lengths = dict(nx.shortest_path_length(G))
        sp_counts_test[i] = dict()
        nodes = G.nodes()
        for v1 in nodes:
            for v2 in nodes:
                if v2 in sp_lengths[v1]:
                    length = sp_lengths[v1][v2]
                    if length in sp_counts_test[i]:
                        sp_counts_test[i][length] += 1
                    else:
                        sp_counts_test[i][length] = 1

                    if length not in all_paths:
                        all_paths[length] = len(all_paths)

    phi_train = np.zeros((len(Gs_train), len(all_paths)))
    for i in range(len(Gs_train)):
        for length in sp_counts_train[i]:
            phi_train[i, all_paths[length]] = sp_counts_train[i][length]

    phi_test = np.zeros((len(Gs_test), len(all_paths)))
    for i in range(len(Gs_test)):
        for length in sp_counts_test[i]:
            phi_test[i, all_paths[length]] = sp_counts_test[i][length]

    K_train = np.dot(phi_train, phi_train.T)
    K_test = np.dot(phi_test, phi_train.T)

    return K_train, K_test


############## Task 8
# Compute the graphlet kernel
def graphlet_kernel(Gs_train, Gs_test, n_samples=200):
    graphlets = [nx.Graph(), nx.Graph(), nx.Graph(), nx.Graph()]

    graphlets[0].add_nodes_from(range(3))

    graphlets[1].add_nodes_from(range(3))
    graphlets[1].add_edge(0, 1)

    graphlets[2].add_nodes_from(range(3))
    graphlets[2].add_edge(0, 1)
    graphlets[2].add_edge(1, 2)

    graphlets[3].add_nodes_from(range(3))
    graphlets[3].add_edge(0, 1)
    graphlets[3].add_edge(1, 2)
    graphlets[3].add_edge(0, 2)

    phi_train = np.zeros((len(G_train), 4))

    for i, G in enumerate(Gs_train):
        nodes = list(G.nodes())
        if len(nodes) < 3:
            continue
        for _ in range(n_samples):
            sample_nodes = np.random.choice(nodes, 3)
            subg = G.subgraph(sample_nodes)
            for j, graphlet in enumerate(graphlets):
                if nx.is_isomorphic(subg, graphlet):
                    phi_train[i, j] += 1
                    break
        phi_train[i] /= n_samples

    phi_test = np.zeros((len(G_test), 4))

    phi_test = np.zeros((len(Gs_test), 4))
    for i, G in enumerate(Gs_test):
        nodes = list(G.nodes())
        if len(nodes) < 3:
            continue
        for _ in range(n_samples):
            sample_nodes = np.random.choice(nodes, 3)
            subg = G.subgraph(sample_nodes)
            for j, graphlet in enumerate(graphlets):
                if nx.is_isomorphic(subg, graphlet):
                    phi_test[i, j] += 1
                    break
        phi_test[i] /= n_samples

    K_train = np.dot(phi_train, phi_train.T)
    K_test = np.dot(phi_test, phi_train.T)

    return K_train, K_test


############## Task 9

if __name__ == "__main__":
    K_train_g, K_test_g = graphlet_kernel(G_train, G_test)


############## Task 10

if __name__ == "__main__":
    K_train_sp, K_test_sp = shortest_path_kernel(G_train, G_test)
    clf_sp = SVC(kernel="precomputed")
    clf_sp.fit(K_train_sp, y_train)

    y_pred_sp = clf_sp.predict(K_test_sp)

    accuracy_sp = accuracy_score(y_test, y_pred_sp)

    print(f"Shortest Path Kernel - Accuracy: {accuracy_sp:.4f}")

    # Train SVM classifier with graphlet kernel
    clf_g = SVC(kernel="precomputed")
    clf_g.fit(K_train_g, y_train)

    # Predict with graphlet kernel
    y_pred_g = clf_g.predict(K_test_g)

    accuracy_g = accuracy_score(y_test, y_pred_g)
    print(f"Graphlet Kernel - Accuracy: {accuracy_g:.4f}")

    print(
        f"Shortest Path Kernel outperforms Graphlet Kernel: {accuracy_sp > accuracy_g}"
    )
    print(f"Difference in accuracy: {abs(accuracy_sp - accuracy_g):.4f}")
