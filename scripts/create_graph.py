import os
import json
import pickle
import argparse
from pathlib import Path
from datetime import datetime, timezone
import networkx as nx

RAW_DATA_DIR = Path("data/raw/packages")
GRAPH_DIR = Path("data/graph")

def load_json_file(file_path: Path) -> dict:
    """Load a JSON file and handle errors."""
    if not file_path.exists():
        print(f"Warning: Missing file {file_path}")
        return {}
    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Warning: Failed to decode {file_path}")
        return {}

def load_sourcerank_data(package_name: str) -> dict:
    """Load the SourceRank JSON for a given package."""
    file_path = Path(f"data/raw/sourcerank/{package_name}_sourcerank.json")
    return load_json_file(file_path)

def load_metadata(package_names: list[str] = None) -> dict:
    """Load package metadata JSONs, optionally for a subset of projects."""
    all_data = {}
    files = RAW_DATA_DIR.glob("*.json") if package_names is None else [
        RAW_DATA_DIR / f"{name}.json" for name in package_names]

    for file_path in files:
        data = load_json_file(file_path)
        if data:
            name = data.get("name", "").lower()
            sourcerank_data = load_sourcerank_data(name)
            if "stars" in sourcerank_data:
                sourcerank_data["stars_sr"] = sourcerank_data.pop("stars")
            data.update(sourcerank_data)
            data['sourcerank_missing'] = (sourcerank_data == {})
            all_data[name] = data

    return all_data

def add_node_with_metadata(G: nx.DiGraph, pkg_name: str, meta: dict, is_core: bool = False):
    """Helper function to add a node with metadata to the graph."""
    license = meta.get("normalized_licenses", ["Unknown"])[
        0] if meta.get("normalized_licenses") else "Unknown"
    missing_metadata = (
        meta.get("rank") is None or
        meta.get("stars") is None or
        meta.get("forks") is None or
        meta.get("normalized_licenses") is None
    )

    G.add_node(pkg_name,
               SourceRank=meta.get("rank", 0),
               stars=meta.get("stars", 0),
               forks=meta.get("forks", 0),
               license=license,
               latest_release=meta.get(
                   "latest_release_published_at", "Unknown"),
               num_optional_deps=len(meta.get("optional_dependencies", [])),
               repo_url=meta.get("repository_url", "Unknown"),
               has_repo=bool(meta.get("repository_url")),
               has_funding=bool(meta.get("funding_urls")),
               num_keywords=len(meta.get("keywords", [])),
               missing_metadata=missing_metadata,
               core=is_core,
               sourcerank_missing=meta.get('sourcerank_missing', True),
               # Add SourceRank data
               basic_info_present=meta.get("basic_info_present", 0),
               repository_present=meta.get("repository_present", 0),
               readme_present=meta.get("readme_present", 0),
               license_present=meta.get("license_present", 0),
               versions_present=meta.get("versions_present", 0),
               follows_semver=meta.get("follows_semver", 0),
               recent_release=meta.get("recent_release", 0),
               not_brand_new=meta.get("not_brand_new", 0),
               one_point_oh=meta.get("one_point_oh", 0),
               dependent_projects=meta.get("dependent_projects", 0),
               dependent_repositories=meta.get("dependent_repositories", 0),
               contributors=meta.get("contributors", 0),
               subscribers=meta.get("subscribers", 0),
               all_prereleases=meta.get("all_prereleases", 0),
               any_outdated_dependencies=meta.get(
                   "any_outdated_dependencies", 0),
               is_deprecated=meta.get("is_deprecated", 0),
               is_unmaintained=meta.get("is_unmaintained", 0),
               is_removed=meta.get("is_removed", 0),
               )

def get_metadata(name: str, all_data: dict) -> dict:
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

def build_dependency_graph(metadata_dict: dict) -> nx.DiGraph:
    """Build a dependency graph from metadata."""
    G = nx.DiGraph()
    all_data = metadata_dict.copy()
    core_packages = set(metadata_dict.keys())

    for pkg_name, meta in metadata_dict.items():
        add_node_with_metadata(G, pkg_name, meta, is_core=True)

        for dep_name in meta.get("runtime_dependencies", []):
            dep_name = dep_name.lower()
            if dep_name:
                dep_meta = get_metadata(dep_name, all_data)
                add_node_with_metadata(
                    G, dep_name, dep_meta, is_core=(dep_name in core_packages))
                G.add_edge(pkg_name, dep_name, kind="runtime", optional=False)

        for dep_entry in meta.get("optional_dependencies", []):
            kind = "unspecified"
            if ":" in dep_entry:
                kind, dep_name = dep_entry.split(":", 1)
            else:
                dep_name = dep_entry
            dep_name = dep_name.lower().strip()
            if dep_name:
                dep_meta = get_metadata(dep_name, all_data)
                add_node_with_metadata(
                    G, dep_name, dep_meta, is_core=(dep_name in core_packages))
                G.add_edge(pkg_name, dep_name, kind=kind, optional=True)

    G.graph["num_core_packages"] = len(core_packages)
    return G

def make_output_name(meta: dict | None) -> str:
    """Generate a name for the output graph file."""
    now = datetime.now(timezone.utc).strftime("%Y%m%d")
    if meta is None:
        return f"graph_all_{now}"

    mode = meta.get("mode", "unknown")
    n = meta.get("num_packages", len(meta.get("packages", [])))
    date = meta.get("date", datetime.now(timezone.utc).isoformat())
    date_short = datetime.fromisoformat(date.rstrip("Z")).strftime("%Y%m%d")

    return f"graph_{mode}_n{n}_{date_short}"

def save_graph(G: nx.DiGraph, name: str):
    """Save the graph to a file."""
    os.makedirs(GRAPH_DIR, exist_ok=True)
    graph_file = GRAPH_DIR / f"{name}.gpickle"
    edges_file = GRAPH_DIR / f"{name}_edges.csv"

    with open(graph_file, "wb") as f:
        pickle.dump(G, f)

    df_edges = nx.to_pandas_edgelist(G)
    df_edges.to_csv(edges_file, index=False)
    print(f"Graph saved to {graph_file} and {edges_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Build a PyPI dependency graph.")
    parser.add_argument("--infile", type=str,
                        help="Path to JSON file with package names")

    args = parser.parse_args()

    if args.infile:
        meta_file = Path(args.infile)
        package_list = load_json_file(meta_file)
        package_names = set(package_list.get("packages", []))
        metadata = load_metadata(package_names)
        graph_name = make_output_name(package_list)
    else:
        metadata = load_metadata()
        graph_name = make_output_name(None)

    print(f"Building graph with {len(metadata)} packages...")
    G = build_dependency_graph(metadata)
    print(
        f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")

    save_graph(G, graph_name)

if __name__ == "__main__":
    main()
