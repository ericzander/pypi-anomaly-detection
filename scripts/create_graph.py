import os
import json
import pickle
import argparse
from pathlib import Path
from datetime import datetime, timezone
import networkx as nx

RAW_DATA_DIR = Path("data/raw/packages")
GRAPH_DIR = Path("data/graph")

def load_package_list(file: Path):
    """Load the top-levelmetadata JSON containing package list."""
    with open(file, encoding="utf-8") as f:
        return json.load(f)

def load_metadata_subset(package_names: list[str]):
    """Load the package metadata JSONs for a subset of projects based on a list of names.."""
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
    """Load all package metadata JSONs."""
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

def add_node_with_metadata(G, pkg_name, meta):
    """Helper function to add a node with metadata to the graph."""
    license = meta.get("normalized_licenses", ["Unknown"])[0] if meta.get("normalized_licenses") else "Unknown"

    # Determine if any critical metadata is missing
    missing_metadata = (
        meta.get("rank") is None or
        meta.get("stars") is None or
        meta.get("forks") is None or
        meta.get("normalized_licenses") is None
    )

    G.add_node(pkg_name,
               rank=meta.get("rank", 0),
               stars=meta.get("stars", 0),
               forks=meta.get("forks", 0),
               license=license,
               latest_release=meta.get("latest_release_published_at", "Unknown"),
               num_optional_deps=len(meta.get("optional_dependencies", [])),
               has_repo=bool(meta.get("repository_url")),
               has_funding=bool(meta.get("funding_urls")),
               num_keywords=len(meta.get("keywords", [])),
               missing_metadata=missing_metadata,
    )

def get_metadata(name, all_data):
    """Retrieve metadata for a package, loading it if necessary."""
    if name not in all_data:
        file_path = RAW_DATA_DIR / f"{name}.json"
        if file_path.exists():
            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
                    all_data[name] = data
            except json.JSONDecodeError:
                print(f"Warning: Failed to decode {file_path}")
    return all_data.get(name, {})


def build_dependency_graph(metadata_dict):
    G = nx.DiGraph()
    all_data = metadata_dict.copy()

    for pkg_name, meta in metadata_dict.items():
        # Add main package node with metadata
        add_node_with_metadata(G, pkg_name, meta)

        # Add nodes and edges for runtime dependencies
        for dep_name in meta.get("runtime_dependencies", []):
            dep_name = dep_name.lower()
            if dep_name:
                dep_meta = get_metadata(dep_name, all_data)
                add_node_with_metadata(G, dep_name, dep_meta)
                G.add_edge(pkg_name, dep_name, kind="runtime", optional=False)

        # Add nodes and edges for optional dependencies
        for dep_entry in meta.get("optional_dependencies", []):
            kind = "unspecified"
            if ":" in dep_entry:
                kind, dep_name = dep_entry.split(":", 1)
            else:
                dep_name = dep_entry
            dep_name = dep_name.lower().strip()
            if dep_name:
                dep_meta = get_metadata(dep_name, all_data)
                add_node_with_metadata(G, dep_name, dep_meta)
                G.add_edge(pkg_name, dep_name, kind=kind, optional=True)

    return G

def make_output_name(meta: dict | None) -> str:
    now = datetime.now(timezone.utc).strftime("%Y%m%d")

    if meta is None:
        return f"graph_all_{now}"
    
    mode = meta.get("mode", "unknown")
    n = meta.get("num_packages", len(meta.get("packages", [])))
    date = meta.get("date", datetime.now(timezone.utc).isoformat())
    date_short = datetime.fromisoformat(date.rstrip("Z")).strftime("%Y%m%d")

    return f"graph_{mode}_n{n}_{date_short}"

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

    args = parser.parse_args()

    if args.infile:
        meta_file = Path(args.infile)
        package_list = load_package_list(meta_file)
        package_names = set(package_list.get("packages", []))
        metadata = load_metadata_subset(package_names)
        graph_name = make_output_name(package_list)
    else:
        metadata = load_all_metadata()
        graph_name = make_output_name(None)

    print(f"Building graph with {len(metadata)} packages...")
    G = build_dependency_graph(metadata)
    print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")

    save_graph(G, graph_name)

if __name__ == "__main__":
    main()
