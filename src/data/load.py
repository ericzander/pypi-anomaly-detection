import pickle
from pathlib import Path

import pandas as pd
import networkx as nx

def load_and_verify_graph(graph_name, graph_dir, print_summary=True):
    """Load a graph from a gpickle file and print its summary."""
    gpickle_path = graph_dir / f"{graph_name}.gpickle"
    edges_path = graph_dir / f"{graph_name}_edges.csv"

    df_edges = pd.read_csv(edges_path)

    with open(gpickle_path, "rb") as f:
        G = pickle.load(f)

    num_core_packages = G.graph.get("num_core_packages", "N/A")

    # Print graph summary
    if print_summary:
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
    
    return G, df_edges

def merge_top_and_recent_graphs(G_top, G_recent):
    # Create a copy of G_top to avoid modifying the original
    G_merged = G_top.copy()

    # Set is_recent=False for all nodes in G_merged (from G_top)
    nx.set_node_attributes(G_merged, False, "is_recent")

    # Ensure 'core' is correct for all nodes in G_merged (from G_top)
    for node in G_merged.nodes:
        # If node is in G_recent, set 'core' to True if either graph has core True
        if node in G_recent:
            core_top = G_merged.nodes[node].get("core", False)
            core_recent = G_recent.nodes[node].get("core", False)
            G_merged.nodes[node]["core"] = bool(core_top or core_recent)

    # Add nodes from G_recent, setting is_recent=True for those not already present
    for node, data in G_recent.nodes(data=True):
        if node not in G_merged:
            G_merged.add_node(node, **data)
            
        # Set is_recent for all nodes from G_recent
        G_merged.nodes[node]["is_recent"] = True

        # Set core to True if either graph has core=True
        core_merged = G_merged.nodes[node].get("core", False)
        core_recent = data.get("core", False)
        G_merged.nodes[node]["core"] = bool(core_merged or core_recent)

    # Add edges from G_recent that are not already in G_merged
    for u, v, data in G_recent.edges(data=True):
        if not G_merged.has_edge(u, v):
            G_merged.add_edge(u, v, **data)

    return G_merged
