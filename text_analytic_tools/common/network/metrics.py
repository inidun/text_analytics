import community  # pip3 install python-louvain packages
import networkx as nx

DISTANCE_METRICS = {

    # 'Mahalanobis': 'mahalanobis',
    # 'Minkowski': 'minkowski',
    # 'Bray-Curtis': 'braycurtis',
    # 'Canberra': 'canberra',
    # 'Chebyshev': 'chebyshev',
    # 'Manhattan': 'cityblock',

    'Correlation': 'correlation',
    'Cosine': 'cosine',
    'Euclidean': 'euclidean',
    'Normalized Euclidean': 'seuclidean',
    'Squared Euclidean': 'sqeuclidean',
    'Kullback-Leibler': 'kullback–leibler',
    'Kullback-Leibler (SciPy)': 'scipy.stats.entropy'

}

def compute_centrality(network):
    centrality = nx.algorithms.centrality.betweenness_centrality(network)
    _, nodes_centrality = zip(*sorted(centrality.items()))
    max_centrality = max(nodes_centrality)
    centrality_vector = [7 + 10 * t / max_centrality for t in nodes_centrality]
    return centrality_vector

def compute_partition(network):
    partition = community.best_partition(network)
    _, nodes_community = zip(*sorted(partition.items()))
    return nodes_community

def partition_colors(nodes_community, color_palette=None):
    if color_palette is None:
        color_palette = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00',
                         '#ffff33', '#a65628', '#b3cde3', '#ccebc5', '#decbe4', '#fed9a6',
                         '#ffffcc', '#e5d8bd', '#fddaec', '#1b9e77', '#d95f02', '#7570b3', '#e7298a',
                         '#66a61e', '#e6ab02', '#a6761d', '#666666']
    community_colors = [ color_palette[x % len(color_palette)] for x in nodes_community ]
    return community_colors

def compute_alpha_vector(value_vector):
    max_value = max(value_vector)
    alphas = list(map(lambda h: 0.1 + 0.6 * (h / max_value), value_vector))
    return alphas
