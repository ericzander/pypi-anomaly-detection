import os
import requests
from dotenv import load_dotenv

from data.fetch_pypi import fetch_dependencies_from_pypi

load_dotenv()

API_KEY = os.getenv("LIBRARIESIO_API_KEY")
BASE_URL = "https://libraries.io/api/pypi/{}/latest/dependencies?api_key={}"

def fetch_metadata_librariesio(package_name):
    """Fetch metadata for a PyPI package from Libraries.io."""
    try:
        url = BASE_URL.format(package_name, API_KEY)
        res = requests.get(url, timeout=5)
        if res.status_code != 200:
            return None
        
        meta = res.json()
        if not meta.get("dependencies"):
            print(f"Libraries.io returned no dependencies for {package_name}. Falling back to PyPI.")
            meta["dependencies"] = fetch_dependencies_from_pypi(package_name)

        return meta

    except Exception as e:
        print(f"Error fetching from Libraries.io: {e}")
    return None
