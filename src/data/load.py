import pickle
from pathlib import Path

import pandas as pd

def load_and_verify_graph(graph_name, graph_dir):
    """Load a graph from a gpickle file and print its summary."""
    gpickle_path = graph_dir / f"{graph_name}.gpickle"
    edges_path = graph_dir / f"{graph_name}_edges.csv"

    df_edges = pd.read_csv(edges_path)

    with open(gpickle_path, "rb") as f:
        G = pickle.load(f)

    num_core_packages = G.graph.get("num_core_packages", "N/A")

    # Print graph summary
    print(f"Graph '{graph_name}':")
    print(f"  {G.number_of_nodes():,} nodes")
    print(f"  {num_core_packages} core packages")
    print(f"  {G.number_of_edges():,} dependencies")
    print(f"  directed={G.is_directed()}")
    print("\nSample node metadata:")
    for node, data in list(G.nodes(data=True))[:5]:
        summary = ", ".join(f"{k}={v}" for k, v in list(data.items())[:3])
        print(f"  {node}: {summary}")
    print("\nSample edge metadata:")
    for u, v, data in list(G.edges(data=True))[:5]:
        summary = ", ".join(f"{k}={v_}" for k, v_ in data.items())
        print(f"  {u} -> {v}: {summary}")
    return G, df_edges #, df_nodes
