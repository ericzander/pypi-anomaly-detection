# Graph-based anomaly detection in the Python Package Index (PyPI)

## Overview
Model the PyPI dependency network as a graph. Use self-supervised Graph Neural Networks (GNNs) to learn node embeddings and detect suspicious packages with unusual dependency patterns.

## Data
* Package metadata: [Libraries.io](https://libraries.io/)
* Unfound dependencies: [PyPI JSON API](https://docs.pypi.org/api/json/)
* Package download/usage: [PyPI Download Statistics (BigQuery)](https://docs.pypi.org/api/bigquery/)

## Tools
- Graph Construction: NetworkX/PyG
- GNNs: GraphSAGE/DGI/GCN
- Anomaly Detection: Outlier scores from embeddings or structure
- Visualization: PCA/t-SNE, Streamlit/website?

## Plan
- Data collection
- Graph construction
- Modeling
- Anomaly detection (scoring)
- Exploration + presentation
