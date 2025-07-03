import os
import re
import json
import argparse

from data.fetch_librariesio import fetch_metadata_librariesio
from data.fetch_pypi import enrich_with_pypi

DATA_DIR = "data/raw"

def clean_metadata(meta: dict) -> dict:
    def extract_runtime_dependencies(raw_deps):
        # Consolidate raw dependencies into a list of unique, required package names
        return sorted(set(
            dep["name"].lower()
            for dep in raw_deps
            if dep.get("kind") == "runtime" and not dep.get("optional", False)
        ))

    def extract_optional_dependencies(raw_deps):
        deps = set()

        for dep in raw_deps:
            name = dep.get("name", "").lower()
            kind = dep.get("kind", "")
            is_optional = dep.get("optional", False)

            # Match extras like 'extra == "test"'
            match = re.match(r'extra\s*==\s*"([^"]+)"', kind)
            if match:
                extra = match.group(1).lower()
                deps.add(f"{extra}:{name}")
            elif is_optional:
                deps.add(f"unspecified:{name}")

        return sorted(deps)

    # Clean licenses
    licenses = meta.get("licenses", [])
    if isinstance(licenses, list):
        license_str = ", ".join(licenses)[:100]
    elif isinstance(licenses, str):
        license_str = licenses[:100]
    else:
        license_str = "Unknown"
    meta["licenses"] = license_str

    # Remove versions if present (using latest only)
    meta.pop("versions", None)

    # Extract set of dependencies
    raw_deps = meta.get("dependencies", [])
    meta["runtime_dependencies"] = extract_runtime_dependencies(raw_deps)
    meta["optional_dependencies"] = extract_optional_dependencies(raw_deps)
    meta.pop("dependencies", None)

    return meta

def ensure_dir(path):
    """Ensure the directory at 'path' exists."""
    os.makedirs(path, exist_ok=True)

def main(package_list, use_pypi_fallback):
    """Download metadata for each package, using PyPI as fallback if specified."""
    ensure_dir(DATA_DIR)

    for pkg in package_list:
        print(f"Fetching {pkg}...")
        data = fetch_metadata_librariesio(pkg)

        if not data and use_pypi_fallback:
            print("Libraries.io failed. Trying PyPI fallback...")
            data = enrich_with_pypi(pkg)

        if data:
            data = clean_metadata(data)

            out_path = os.path.join(DATA_DIR, f"{pkg}.json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        else:
            print(f"Failed to fetch {pkg} from all sources.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download PyPI package metadata.")
    parser.add_argument("--packages", nargs="+", required=True,
                        help="List of package names")
    parser.add_argument("--use-pypi-fallback", action="store_true",
                        help="Use PyPI if Libraries.io fails")

    args = parser.parse_args()
    main(args.packages, args.use_pypi_fallback)
