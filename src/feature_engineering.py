import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities

def compute_inter_intra_ratios(G, feature_name="inter_intra_ratio"):
    comms = list(greedy_modularity_communities(G))
    node2comm = {n: i for i, c in enumerate(comms) for n in c}
    for node in G.nodes():
        comm = node2comm.get(node)
        if comm is None:
            ratio = None
        else:
            intra = sum(node2comm.get(nb) == comm for nb in G.neighbors(node))
            inter = sum(node2comm.get(nb) != comm for nb in G.neighbors(node))
            if intra == 0 and inter > 0:
                ratio = float("inf")
            elif intra:
                ratio = inter / intra
            else:
                ratio = 0
        G.nodes[node][feature_name] = ratio

    return G

def compute_clustering_coefficient(G, feature_name="clustering_coefficient"):
    clustering = nx.clustering(G)
    for node, value in clustering.items():
        G.nodes[node][feature_name] = value
    return G

def compute_degree_centrality(G, feature_name="degree_centrality"):
    degree = nx.degree_centrality(G)
    for node, value in degree.items():
        G.nodes[node][feature_name] = value
    return G

def compute_betweenness_centrality(G, feature_name="betweenness_centrality"):
    betweenness = nx.betweenness_centrality(G)
    for node, value in betweenness.items():
        G.nodes[node][feature_name] = value
    return G

def compute_closeness_centrality(G, feature_name="closeness_centrality"):
    closeness = nx.closeness_centrality(G)
    for node, value in closeness.items():
        G.nodes[node][feature_name] = value
    return G

def add_structural_features(G):
    G = compute_inter_intra_ratios(G)
    G = compute_clustering_coefficient(G)
    G = compute_betweenness_centrality(G)
    G = compute_degree_centrality(G)
    G = compute_closeness_centrality(G)
    return G
