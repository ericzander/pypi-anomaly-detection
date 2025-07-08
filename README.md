# Graph-based anomaly detection in the Python Package Index (PyPI)

## Overview
Model the PyPI dependency network as a graph. Use self-supervised Graph Neural Networks (GNNs) to learn node embeddings and detect suspicious packages with unusual dependency patterns.

## Plan
- Data collection
- Graph construction
- Modeling
- Anomaly detection (scoring)
- Exploration + presentation
  
## Data
Data is sourced as follows:

* Dependencies: [PyPI JSON API](https://docs.pypi.org/api/json/)
* Additional package metadata: [Libraries.io](https://libraries.io/)
* Package download/usage stats: [PyPI Download Statistics (BigQuery)](https://docs.pypi.org/api/bigquery/)

## Tools
- Graph Construction: NetworkX/PyG
- GNNs: GraphSAGE/DGI/GCN
- Anomaly Detection: Outlier scores from embeddings or structure
- Visualization: PCA/t-SNE, Streamlit/website?
