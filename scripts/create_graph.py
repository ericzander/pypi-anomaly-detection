import os
import json
import pickle
from pathlib import Path
import networkx as nx

RAW_DATA_DIR = Path("data/raw/packages")
GRAPH_DIR = Path("data/graph")
GRAPH_FILE = GRAPH_DIR / "pypi_graph.gpickle"
EDGES_FILE = GRAPH_DIR / "pypi_edges.csv"

def load_all_metadata(data_dir=RAW_DATA_DIR):
    all_data = {}
    for file in data_dir.glob("*.json"):
        with open(file, encoding="utf-8") as f:
            try:
                data = json.load(f)
                name = data["name"].lower()
                all_data[name] = data
            except json.JSONDecodeError:
                print(f"Warning: Failed to decode {file}")
    return all_data

def build_dependency_graph(metadata_dict):
    G = nx.DiGraph()

    for pkg_name, meta in metadata_dict.items():
        G.add_node(pkg_name)

        # Handle runtime dependencies
        for dep_name in meta.get("runtime_dependencies", []):
            dep_name = dep_name.lower()
            if not dep_name:
                continue
            G.add_node(dep_name)
            G.add_edge(pkg_name, dep_name, kind="runtime", optional=False)

        # Handle optional dependencies
        for dep_entry in meta.get("optional_dependencies", []):
            kind = "unspecified"

            # Handle extras like "dev:pybind11"
            if ":" in dep_entry:
                kind, dep_name = dep_entry.split(":", 1)
            else:
                dep_name = dep_entry
            dep_name = dep_name.lower().strip()

            if not dep_name:
                continue
            G.add_node(dep_name)
            G.add_edge(pkg_name, dep_name, kind=kind, optional=True)

    return G

def save_graph(G):
    os.makedirs(GRAPH_DIR, exist_ok=True)

    # Save binary graph
    with open(GRAPH_FILE, "wb") as f:
        pickle.dump(G, f)

    # Save edge list with attributes
    df_edges = nx.to_pandas_edgelist(G)
    df_edges.to_csv(EDGES_FILE, index=False)

def main():
    print("Loading package metadata...")
    metadata = load_all_metadata()

    print(f"Building graph with {len(metadata)} packages...")
    G = build_dependency_graph(metadata)

    print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    save_graph(G)

if __name__ == "__main__":
    main()
