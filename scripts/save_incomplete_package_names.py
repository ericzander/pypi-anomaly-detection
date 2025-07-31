import json
from pathlib import Path

from tqdm import tqdm

DATA_DIR = Path("data/raw/packages")
OUTPUT_FILE = Path("data/missing_package_names.json")

def has_missing_metadata(meta):
    return (
        meta.get("rank") is None or
        meta.get("stars") is None or
        meta.get("forks") is None or
        meta.get("normalized_licenses") is None
    )

def main():
    missing_names = []
    files = list(DATA_DIR.glob("*.json"))
    for file in tqdm(files, desc="Checking packages for missing metadata", ncols=80):
        try:
            with open(file, encoding="utf-8") as f:
                meta = json.load(f)
            if has_missing_metadata(meta):
                name = meta.get("name", None)
                if name:
                    missing_names.append(name)
        except Exception as e:
            print(f"Error reading {file}: {e}")

    # Save the missing names to the output file in the format: {"packages": [...]}
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump({"packages": sorted(missing_names)}, f, indent=2)
    print(f"Found {len(missing_names)} packages with missing metadata. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
