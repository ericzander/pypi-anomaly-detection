import re

def clean_metadata(meta: dict) -> dict:
    def extract_runtime_dependencies(raw_deps):
        # Consolidate raw dependencies into a list of unique, required package names
        return sorted(set(
            dep["name"].lower()
            for dep in raw_deps
            if dep.get("kind") == "runtime" and not dep.get("optional", False)
        ))

    def extract_optional_dependencies(raw_deps):
        deps = set()

        for dep in raw_deps:
            name = dep.get("name", "").lower()
            kind = dep.get("kind", "")
            is_optional = dep.get("optional", False)

            # Match extras like 'extra == "test"'
            match = re.match(r'extra\s*==\s*"([^"]+)"', kind)
            if match:
                extra = match.group(1).lower()
                deps.add(f"{extra}:{name}")
            elif is_optional:
                deps.add(f"unspecified:{name}")

        return sorted(deps)

    # Clean licenses
    licenses = meta.get("licenses", [])
    if isinstance(licenses, list):
        license_str = ", ".join(licenses)[:100]
    elif isinstance(licenses, str):
        license_str = licenses[:100]
    else:
        license_str = "Unknown"
    meta["licenses"] = license_str

    # Remove versions if present (using latest only)
    meta.pop("versions", None)

    # Extract set of dependencies
    raw_deps = meta.get("dependencies", [])
    meta["runtime_dependencies"] = extract_runtime_dependencies(raw_deps)
    meta["optional_dependencies"] = extract_optional_dependencies(raw_deps)
    meta.pop("dependencies", None)

    return meta
