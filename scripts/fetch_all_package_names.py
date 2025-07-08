from pathlib import Path

from data.fetch.pypi import fetch_package_names_pypi

PAGES = 2
OUTPUT_FILE = Path("data/all_package_names.txt")

def save_package_list(pkg_names, path):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        for name in pkg_names:
            f.write(name + "\n")

    print(f"Saved {len(pkg_names)} packages names to {path}")

def main():
    packages = fetch_package_names_pypi()
    save_package_list(packages, OUTPUT_FILE)

if __name__ == "__main__":
    main()
