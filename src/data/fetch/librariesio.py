import requests
from data.fetch.pypi import fetch_dependencies_pypi

def fetch_metadata_librariesio(package_name, api_key, timeout=20):
    """Fetch metadata for a PyPI package from Libraries.io."""
    BASE_URL = "https://libraries.io/api/pypi/{}/latest/dependencies?api_key={}"
    url = BASE_URL.format(package_name, api_key)

    try:
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
