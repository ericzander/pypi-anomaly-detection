import os
import requests
import time
from dotenv import load_dotenv

from data.fetch.pypi import fetch_dependencies_pypi

load_dotenv()

API_KEY = os.getenv("LIBRARIESIO_API_KEY")

def fetch_package_names_librariesio(pages=2, timeout=20):
    SEARCH_URL = "https://libraries.io/api/search"

    names = []
    for page in range(1, pages + 1):
        print(f"Fetching page {page}...", end=" ")

        try:
            res = requests.get(SEARCH_URL, params={
                "platforms": "pypi",
                "per_page": 100,
                "page": page,
                "api_key": API_KEY
            }, timeout=timeout)

            if res.status_code != 200:
                print(f"HTTP {res.status_code}")
                break

            data = res.json()
            page_names = [project["name"] for project in data if "name" in project]
            names.extend(page_names)

            print(f"{len(page_names)} packages")

            if len(data) < 100:
                print("Reached final page.")
                break

            time.sleep(1)
        except requests.exceptions.Timeout:
            print(f"Timeout on page {page}")
            break
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break

    return names

def fetch_metadata_librariesio(package_name, timeout=20):
    """Fetch metadata for a PyPI package from Libraries.io."""
    BASE_URL = "https://libraries.io/api/pypi/{}/latest/dependencies?api_key={}"

    try:
        url = BASE_URL.format(package_name, API_KEY)
        res = requests.get(url, timeout=timeout)
        if res.status_code != 200:
            return None

        meta = res.json()
        if not meta.get("dependencies"):
            print(
                f"Libraries.io returned no dependencies for {package_name}. Falling back to PyPI.")
            meta["dependencies"] = fetch_dependencies_pypi(package_name)

        return meta

    except Exception as e:
        print(f"Error fetching from Libraries.io: {e}")
    return None
