import os
import json
import argparse
from dotenv import load_dotenv

from data.fetch.librariesio import fetch_metadata_librariesio
from data.cleaning import clean_metadata

load_dotenv()

API_KEY = os.getenv("LIBRARIESIO_API_KEY")
if not API_KEY:
    raise ValueError("LIBRARIESIO_API_KEY is not set in the environment.")

DATA_DIR = "data/raw/packages"

def main(package_list):
    """Download metadata for each package, using PyPI as fallback if specified."""
    os.makedirs(DATA_DIR, exist_ok=True)

    for pkg in package_list:
        print(f"Fetching {pkg}...")
        data = fetch_metadata_librariesio(pkg, api_key=API_KEY)

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

    args = parser.parse_args()
    main(args.packages)
