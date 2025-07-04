import os
import json
import time
from pathlib import Path

from data.fetch.librariesio import fetch_metadata_librariesio
from data.fetch.pypi import fetch_dependencies_pypi
from data.cleaning import clean_metadata

DATA_DIR = Path("data/raw/packages")
PACKAGE_LIST = ["numpy", "pandas", "scikit-learn", "requests", "matplotlib"]

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def already_fetched(pkg_name):
    return (DATA_DIR / f"{pkg_name}.json").exists()

def fetch_and_save(pkg_name):
    print(f"Fetching {pkg_name}...")
    if already_fetched(pkg_name):
        print(f"Skipping {pkg_name} (already collected)")
        return

    meta = fetch_metadata_librariesio(pkg_name)
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
        save_json(clean, DATA_DIR / f"{pkg_name}.json")
        print(f"Saved {pkg_name}")
    except Exception as e:
        print(f"Cleaning failed for {pkg_name}: {e}")

def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    for pkg in PACKAGE_LIST:
        fetch_and_save(pkg)
        time.sleep(1)

if __name__ == "__main__":
    main()
