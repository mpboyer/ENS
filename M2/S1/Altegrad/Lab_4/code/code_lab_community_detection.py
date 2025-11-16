"""
Graph Mining - ALTEGRAD - Nov 2024
"""

import networkx as nx
import numpy as np
from scipy.sparse.linalg import eigs
from scipy.sparse import diags, eye
from random import randint
from sklearn.cluster import KMeans


############## Task 3
# Perform spectral clustering to partition graph G into k clusters
def spectral_clustering(G, k):
    A = nx.adjacency_matrix(G)

    # Get number of nodes
    n = G.number_of_nodes()

    # Compute degree matrix D (diagonal matrix with degrees on diagonal)
    degrees = np.array([G.degree(node) for node in G.nodes()])
    # D = diags(degrees, format="csr")

    # Compute D^(-1)
    D_inv = diags(1.0 / degrees, format="csr")

    # Compute normalized Laplacian: L_rw = I - D^(-1) * A
    identity = eye(n, format="csr")
    L_w = identity - D_inv @ A

    # Compute the k smallest eigenvalues and eigenvectors
    # Use 'SM' for smallest magnitude eigenvalues
    eigenvalues, eigenvectors = eigs(L_w, k=k, which="SM")

    # We need the real part (eigenvalues should be real for symmetric matrices)
    U = np.real(eigenvectors)

    # Apply k-means to the rows of U
    kmeans = KMeans(n_clusters=k, random_state=42)
    labels = kmeans.fit_predict(U)

    # Create clustering dictionary: node -> cluster
    clustering = {}
    for idx, node in enumerate(G.nodes()):
        clustering[node] = labels[idx]

    return clustering


############## Task 4


# Load the graph (assuming it's already loaded as G from previous tasks)
# Get the largest connected component
#
if __name__ == "__main__":
    data_file = "data/CA-HepTh.txt"
    G = nx.read_edgelist(data_file, delimiter="\t", comments="#")
    connected_components = list(nx.connected_components(G))
    largest_cc_nodes = max(connected_components, key=len)
    largest_cc = G.subgraph(largest_cc_nodes).copy()

    k = 50
    clustering_spectral = spectral_clustering(largest_cc, k)

    print(f"Spectral clustering completed with k={k} clusters")
    print(f"Number of nodes assigned to clusters: {len(clustering_spectral)}")

    # Check distribution of cluster sizes
    cluster_sizes = {}
    for node, cluster in clustering_spectral.items():
        cluster_sizes[cluster] = cluster_sizes.get(cluster, 0) + 1

    print(f"Number of unique clusters: {len(cluster_sizes)}")
    print(f"Min cluster size: {min(cluster_sizes.values())}")
    print(f"Max cluster size: {max(cluster_sizes.values())}")
    print(f"Average cluster size: {np.mean(list(cluster_sizes.values())):.2f}")


############## Task 5
# Compute modularity value from graph G based on clustering
#
def modularity(G, clustering):
    m = G.number_of_edges()

    if m == 0:
        return 0.0

    # Get unique clusters
    clusters = set(clustering.values())

    # Initialize modularity
    Q = 0.0

    for c in clusters:
        # Get nodes in cluster c
        nodes_in_c = [node for node, cluster in clustering.items() if cluster == c]

        # l_c: number of edges within cluster c
        l_c = 0
        for u in nodes_in_c:
            for v in nodes_in_c:
                if u < v and G.has_edge(u, v):
                    l_c += 1

        # d_c: sum of degrees of nodes in cluster c
        d_c = sum(G.degree(node) for node in nodes_in_c)

        # Add contribution of cluster c to modularity
        Q += (l_c / m) - (d_c / (2 * m)) ** 2

    return Q
    return modularity


############## Task 6
if __name__ == "__main__":
    # Compute modularity for spectral clustering result
    mod_spectral = modularity(largest_cc, clustering_spectral)
    print(f"\nModularity of Spectral Clustering (k={k}): {mod_spectral:.4f}")

    # Create random clustering
    random_mods = []
    for _ in range(50):
        clustering_random = {}
        for node in largest_cc.nodes():
            clustering_random[node] = randint(0, k - 1)

        # Compute modularity for random clustering
        random_mods.append(modularity(largest_cc, clustering_random))

    random_mods = np.array(random_mods)
    mod_random = random_mods.mean()
    print(f"Modularity of Random Clustering (k={k}): {mod_random:.4f}")

    # Compare results
    print(f"\nDifference: {mod_spectral - mod_random:.4f}")
    if mod_spectral > mod_random:
        print(
            "Spectral clustering produces significantly better community structure than random assignment."
        )
    else:
        print("Random clustering unexpectedly has higher modularity.")
