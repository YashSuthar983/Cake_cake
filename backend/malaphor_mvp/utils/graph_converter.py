import networkx as nx
import torch_geometric.data

def to_networkx(data: torch_geometric.data.Data, node_ids, edge_types=None):
    """
    Converts a PyG Data object to a NetworkX graph.
    Includes node IDs as attributes.
    Optionally includes edge types.
    """
    G = nx.DiGraph() # Use DiGraph for directed edges

    # Add nodes with original IDs and any relevant features
    for i, node_id in enumerate(node_ids):
        node_features = data.x[i].tolist() # Convert tensor features to list
        # For MVP, let's also add anomaly score if available (will pass this later)
        G.add_node(i, original_id=node_id, features=node_features) # Use integer index as node ID for NetworkX

    # Add edges
    edge_index = data.edge_index.t().tolist() # Get edges as list of (src, dest) tuples

    # For MVP, we didn't explicitly add edge types to the PyG Data object in a standard way.
    # If your data had edge types associated with the edge_index, you'd add them here.
    # Let's assume for now edges just represent a connection. If you simulate edge types,
    # you would need to build edge features in build_graph and handle them.
    # For a simple MVP, we'll add the edge.

    for src, dest in edge_index:
         G.add_edge(src, dest) # Add edge using integer indices

    print(f"Converted PyG graph ({data.num_nodes} nodes, {data.num_edges} edges) to NetworkX graph ({G.number_of_nodes()} nodes, {G.number_of_edges()} edges).")
    return G

# We won't run this directly, it's a utility.