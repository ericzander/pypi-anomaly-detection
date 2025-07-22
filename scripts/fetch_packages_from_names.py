import os
import json
import time
import argparse
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv

from data.fetch.librariesio import fetch_metadata_librariesio, fetch_sourcerank_info_librariesio
from data.fetch.pypi import fetch_dependencies_pypi
from data.cleaning import clean_metadata

load_dotenv()

API_KEY = os.getenv("LIBRARIESIO_API_KEY")
if not API_KEY:
    raise ValueError("LIBRARIESIO_API_KEY is not set in the environment.")

DATA_DIR_PKG = Path("data/raw/packages")
DATA_DIR_SR = Path("data/raw/sourcerank")

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_package_names(path):
    with open(path, "r", encoding="utf-8") as f:
        content = json.load(f)
        return content.get("packages", [])

def collect_dependency_names(metadata_dir: Path, core_packages: list[str]) -> set[str]:
    deps = set()

    for name in core_packages:
        file_path = metadata_dir / f"{name}.json"
        if not file_path.exists():
            continue
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            continue

        for dep in data.get("runtime_dependencies", []):
            deps.add(dep.lower())

        for entry in data.get("optional_dependencies", []):
            if ":" in entry:
                _, dep = entry.split(":", 1)
            else:
                dep = entry
            deps.add(dep.lower().strip())

    return deps - set(core_packages)

def fetch_and_save_metadata(pkg_name, overwrite=False, sleep_time=1.5):
    print(f"Fetching {pkg_name}...")
    if not overwrite and (DATA_DIR_PKG / f"{pkg_name}.json").exists():
        print(f"Skipping {pkg_name} (already collected)")
        return

    time.sleep(sleep_time)

    meta = fetch_metadata_librariesio(pkg_name, API_KEY)
    if not meta:
        meta = {
            "name": pkg_name,
            "dependencies": fetch_dependencies_pypi(pkg_name)
        }

    if not meta:
        print(f"Failed to fetch {pkg_name}")
        return

    try:
        clean = clean_metadata(meta)
        save_json(clean, DATA_DIR_PKG / f"{pkg_name}.json")
        print(f"Saved {pkg_name}")
    except Exception as e:
        print(f"Cleaning failed for {pkg_name}: {e}")

def fetch_and_save_sourcerank(pkg_name, overwrite=False, sleep_time=1.5):
    print(f"Fetching SourceRank for {pkg_name}...")
    sourcerank_path = DATA_DIR_SR / f"{pkg_name}_sourcerank.json"
    if not overwrite and sourcerank_path.exists():
        print(f"Skipping SourceRank for {pkg_name} (already collected)")
        return

    time.sleep(sleep_time)

    try:
        sourcerank_info = fetch_sourcerank_info_librariesio(pkg_name, API_KEY)
        if sourcerank_info:
            save_json(sourcerank_info, sourcerank_path)
            print(f"Saved SourceRank for {pkg_name}")
        else:
            print(f"Failed to fetch SourceRank for {pkg_name}")
    except Exception as e:
        print(f"Error fetching SourceRank for {pkg_name}: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Fetch metadata for a list of packages.")
    parser.add_argument(
        "--filepath",
        type=str,
        required=True,
        help="Path to the JSON file containing the package list (e.g. top_package_names.json or recent_package_names.json)"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing package metadata files if they exist."
    )
    args = parser.parse_args()

    list_path = Path(args.filepath)
    if not list_path.exists():
        raise FileNotFoundError(f"{list_path} does not exist")

    os.makedirs(DATA_DIR_PKG, exist_ok=True)
    os.makedirs(DATA_DIR_SR, exist_ok=True)
    package_names = load_package_names(list_path)

    # Fetch core package metadata and SourceRank info
    for pkg in tqdm(package_names, desc="Core", ncols=80):
        fetch_and_save_metadata(pkg, args.overwrite)
        fetch_and_save_sourcerank(pkg, args.overwrite)

    # Collect dependency names
    dependency_names = collect_dependency_names(DATA_DIR_PKG, package_names)
    print(
        f"\nFound {len(dependency_names)} unique direct dependencies to fetch...")

    # Fetch dependency metadata
    for dep in tqdm(sorted(dependency_names), desc="Dependencies", ncols=80):
        fetch_and_save_metadata(dep, args.overwrite)
        fetch_and_save_sourcerank(dep, args.overwrite)

if __name__ == "__main__":
    main()
