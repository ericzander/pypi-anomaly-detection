import os
import argparse
from pathlib import Path
from dotenv import load_dotenv

from data.fetch.bigquery import (
    get_top_pypi_packages,
    get_recent_pypi_packages,
    save_package_list,
)

OUTPUT_DIR = Path("data")
TOP_FILE = OUTPUT_DIR / "top_package_names.json"
RECENT_FILE = OUTPUT_DIR / "recent_package_names.json"

DEFAULT_N = 200
DEFAULT_DAYS = 2

load_dotenv()

cred = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not cred or not Path(cred).exists():
    raise FileNotFoundError(f"Missing GCP credentials: {cred}")

def main(mode: str, n: int, days: int):
    if mode == "top":
        print(f"Fetching top {n} package names over the last {days} days...")
        packages = get_top_pypi_packages(n=n, days=days)
        save_package_list(packages, TOP_FILE, mode=mode,n=n, days=days)
    elif mode == "recent":
        print(f"Fetching {n} most recently uploaded packages names...")
        packages = get_recent_pypi_packages(n=n)
        save_package_list(packages, RECENT_FILE, mode=mode, n=n, days=None)
    else:
        raise ValueError("Mode must be 'top' or 'recent'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch PyPI package names from BigQuery.")
    parser.add_argument("--mode", choices=["top", "recent"], default="top", help="Fetch mode")
    parser.add_argument("--n", type=int, default=DEFAULT_N, help="Number of packages to fetch")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help="Lookback days (only for 'top')")

    args = parser.parse_args()
    main(args.mode, args.n, args.days)
