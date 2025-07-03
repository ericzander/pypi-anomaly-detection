import re
import requests

def fetch_dependencies_from_pypi(pkg_name):
    try:
        res = requests.get(f"https://pypi.org/pypi/{pkg_name}/json", timeout=5)
        if res.status_code != 200:
            return []

        raw_deps = res.json().get("info", {}).get("requires_dist", [])
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
