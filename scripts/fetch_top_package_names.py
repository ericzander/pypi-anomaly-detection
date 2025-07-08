import os
from pathlib import Path
from dotenv import load_dotenv
from data.fetch.bigquery import get_top_pypi_packages, save_package_list

OUTPUT_FILE = Path("data/top_package_names.json")
N = 200
DAYS = 2

load_dotenv()

cred = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not cred or not Path(cred).exists():
    raise FileNotFoundError(f"Missing GCP credentials: {cred}")

if __name__ == "__main__":
    packages = get_top_pypi_packages(n=N, days=DAYS)
    save_package_list(packages, OUTPUT_FILE, n=N, days=DAYS)
