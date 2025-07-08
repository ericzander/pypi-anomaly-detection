import re
import requests
from bs4 import BeautifulSoup

def fetch_package_names_pypi(timeout=20):
    """Returns a list of ALL package names from the PyPI simple list."""
    resp = requests.get("https://pypi.org/simple/", timeout=timeout)
    soup = BeautifulSoup(resp.text, "html.parser")
    return [a.text for a in soup.find_all("a")]

def fetch_dependencies_pypi(pkg_name) -> list[dict]:
    """Returns list of dicts matching the format of the Libraries.io API response.
    
    When unreported in setup.py or pyproject.toml, some optional dependencies may be
    missing for project with extra configurations (such as the deprecated gym[atari]).
    """
    try:
        res = requests.get(f"https://pypi.org/pypi/{pkg_name}/json", timeout=5)
        if res.status_code != 200:
            return []

        raw_deps = res.json().get("info", {}).get("requires_dist", [])
        if raw_deps is None:
            return []
        
        deps = []

        for dep in raw_deps:
            if not dep:
                continue

            name_match = re.match(r"^([a-zA-Z0-9_.\-]+)", dep)
            if not name_match:
                continue

            name = name_match.group(1).lower()
            match = re.search(r'extra\s*==\s*"([^"]+)"', dep, re.IGNORECASE)
            kind = f'extra == "{match.group(1)}"' if match else "runtime"
            optional = bool(match)

            deps.append({
                "name": name,
                "kind": kind,
                "optional": optional
            })

        return deps

    except Exception as e:
        print(f"PyPI fallback failed for {pkg_name}: {e}")
        return []
