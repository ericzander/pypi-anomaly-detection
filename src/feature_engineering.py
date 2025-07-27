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

def add_features(G):
    G = compute_inter_intra_ratios(G)

    return G
