import os
import json
import time
import argparse
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv

from data.fetch.librariesio import fetch_metadata_librariesio
from data.fetch.pypi import fetch_dependencies_pypi
from data.cleaning import clean_metadata

load_dotenv()

API_KEY = os.getenv("LIBRARIESIO_API_KEY")
if not API_KEY:
    raise ValueError("LIBRARIESIO_API_KEY is not set in the environment.")

DATA_DIR = Path("data/raw/packages")

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_package_names(path):
    with open(path, "r", encoding="utf-8") as f:
        content = json.load(f)
        return content.get("packages", [])

def already_fetched(pkg_name):
    return (DATA_DIR / f"{pkg_name}.json").exists()

def fetch_and_save(pkg_name):
    print(f"Fetching {pkg_name}...")
    if already_fetched(pkg_name):
        print(f"Skipping {pkg_name} (already collected)")
        return

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
        save_json(clean, DATA_DIR / f"{pkg_name}.json")
        print(f"Saved {pkg_name}")
    except Exception as e:
        print(f"Cleaning failed for {pkg_name}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Fetch metadata for a list of packages.")
    parser.add_argument(
        "--filepath",
        type=str,
        required=True,
        help="Path to the JSON file containing the package list (e.g. top_package_names.json or recent_package_names.json)"
    )
    args = parser.parse_args()

    list_path = Path(args.filepath)
    if not list_path.exists():
        raise FileNotFoundError(f"{list_path} does not exist")

    os.makedirs(DATA_DIR, exist_ok=True)
    package_names = load_package_names(list_path)

    for pkg in tqdm(package_names, ncols=80):
        fetch_and_save(pkg)
        time.sleep(3)

if __name__ == "__main__":
    main()
