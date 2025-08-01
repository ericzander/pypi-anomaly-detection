import requests
from data.fetch.pypi import fetch_dependencies_pypi

def fetch_metadata_librariesio(package_name, api_key, timeout=20):
    """Fetch metadata for a PyPI package from Libraries.io."""
    BASE_URL = "https://libraries.io/api/pypi/{}/latest/dependencies?api_key={}"
    url = BASE_URL.format(package_name, api_key)

    dependencies = fetch_dependencies_pypi(package_name)

    try:
        res = requests.get(url, timeout=timeout)
        if res.status_code == 200:
            meta = res.json()
        else:
            meta = {}
    except Exception as e:
        print(f"Error fetching from Libraries.io for {package_name}: {e}")
        meta = {}

    meta["name"] = package_name
    meta["dependencies"] = dependencies

    return meta

def fetch_sourcerank_info_librariesio(package_name, api_key, timeout=20):
    """Fetch the SourceRank breakdown for a PyPI package from Libraries.io."""
    BASE_URL = "https://libraries.io/api/pypi/{}/sourcerank?api_key={}"
    url = BASE_URL.format(package_name, api_key)

    try:
        res = requests.get(url, timeout=timeout)
        if res.status_code == 200:
            info = res.json()
        else:
            print(f"Failed to fetch SourceRank for {package_name}: status {res.status_code}")
            return {}
    except Exception as e:
        print(f"Error fetching SourceRank from Libraries.io for {package_name}: {e}")
        return {}
    
    return info
