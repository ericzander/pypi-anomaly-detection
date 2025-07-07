import os
import json
from datetime import datetime
from google.cloud import bigquery

def get_top_pypi_packages(n=200, days=7):
    client = bigquery.Client()
    query = f"""
        SELECT file.project AS name, COUNT(*) AS downloads
        FROM `bigquery-public-data.pypi.file_downloads`
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        GROUP BY name ORDER BY downloads DESC LIMIT {n}
    """
    return [row.name for row in client.query(query).result()]

def save_package_list(packages, path, n, days):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    output = {
        "date": datetime.utcnow().isoformat() + "Z",
        "num_packages": n,
        "days": days,
        "packages": packages
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
