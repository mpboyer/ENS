"""
Graph Mining - ALTEGRAD - Nov 2024
"""

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


############## Task 1
def read_network_data(data_file: str) -> nx.Graph:
    G = nx.read_edgelist(data_file, delimiter="\t", comments="#")
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()

    print(f"Number of nodes: {num_nodes}")
    print(f"Number of edges: {num_edges}")

    return G


############## Task 2
def analyze_connected_components(G: nx.Graph):
    # Get all connected components
    connected_components = list(nx.connected_components(G))

    # Number of connected components
    num_components = len(connected_components)
    print(f"Number of connected components: {num_components}")

    # Get the largest connected component
    # Find the component with the maximum number of nodes
    largest_cc_nodes_set = max(connected_components, key=len)

    # Create subgraph of the largest connected component
    largest_cc = G.subgraph(largest_cc_nodes_set).copy()

    # Compute statistics for the largest connected component
    largest_cc_nodes = largest_cc.number_of_nodes()
    largest_cc_edges = largest_cc.number_of_edges()

    # Compute fractions
    total_nodes = G.number_of_nodes()
    total_edges = G.number_of_edges()

    node_fraction = largest_cc_nodes / total_nodes if total_nodes > 0 else 0
    edge_fraction = largest_cc_edges / total_edges if total_edges > 0 else 0

    # Print results
    print("\nLargest Connected Component Statistics:")
    print(f"Number of nodes: {largest_cc_nodes}")
    print(f"Number of edges: {largest_cc_edges}")
    print(f"Fraction of total nodes: {node_fraction:.4f} ({node_fraction * 100:.2f}%)")
    print(f"Fraction of total edges: {edge_fraction:.4f} ({edge_fraction * 100:.2f}%)")

    return (num_components, largest_cc)


if __name__ == "__main__":
    file_path = "data/CA-HepTh.txt"  # Update this path as needed
    G = read_network_data(file_path)

    num_cc, largest_cc, cc_nodes, cc_edges, node_frac, edge_frac = (
        analyze_connected_components(G)
    )
