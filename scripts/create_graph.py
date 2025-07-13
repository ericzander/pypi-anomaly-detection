import os
import json
import pickle
import argparse
from pathlib import Path
import networkx as nx

RAW_DATA_DIR = Path("data/raw/packages")
GRAPH_DIR = Path("data/graph")

def load_package_list(path: Path):
    with open(path, encoding="utf-8") as f:
        return set(json.load(f).get("packages", []))

def load_metadata_subset(package_names):
    all_data = {}
    for name in package_names:
        file_path = RAW_DATA_DIR / f"{name}.json"
        if not file_path.exists():
            print(f"Warning: Missing file for {name}")
            continue
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
                all_data[name] = data
        except json.JSONDecodeError:
            print(f"Warning: Failed to decode {file_path}")
    return all_data

def load_all_metadata():
    all_data = {}
    for file in RAW_DATA_DIR.glob("*.json"):
        try:
            with open(file, encoding="utf-8") as f:
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

        for dep_name in meta.get("runtime_dependencies", []):
            dep_name = dep_name.lower()
            if dep_name:
                G.add_node(dep_name)
                G.add_edge(pkg_name, dep_name, kind="runtime", optional=False)

        for dep_entry in meta.get("optional_dependencies", []):
            kind = "unspecified"
            if ":" in dep_entry:
                kind, dep_name = dep_entry.split(":", 1)
            else:
                dep_name = dep_entry
            dep_name = dep_name.lower().strip()
            if dep_name:
                G.add_node(dep_name)
                G.add_edge(pkg_name, dep_name, kind=kind, optional=True)

    return G

def save_graph(G, name):
    os.makedirs(GRAPH_DIR, exist_ok=True)
    graph_file = GRAPH_DIR / f"{name}.gpickle"
    edges_file = GRAPH_DIR / f"{name}_edges.csv"

    with open(graph_file, "wb") as f:
        pickle.dump(G, f)

    df_edges = nx.to_pandas_edgelist(G)
    df_edges.to_csv(edges_file, index=False)
    print(f"Graph saved to {graph_file} and {edges_file}")

def main():
    parser = argparse.ArgumentParser(description="Build a PyPI dependency graph.")
    parser.add_argument("--infile", type=str, help="Path to JSON file with package names")
    parser.add_argument("--outfile", type=str, required=True, help="Base name for output graph files")

    args = parser.parse_args()
    names_file = Path(args.infile) if args.infile else None
    graph_name = args.outfile

    print("Loading package metadata...")

    if names_file:
        package_names = load_package_list(names_file)
        metadata = load_metadata_subset(package_names)
    else:
        metadata = load_all_metadata()

    print(f"Building graph with {len(metadata)} packages...")
    G = build_dependency_graph(metadata)

    print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    save_graph(G, graph_name)

if __name__ == "__main__":
    main()
