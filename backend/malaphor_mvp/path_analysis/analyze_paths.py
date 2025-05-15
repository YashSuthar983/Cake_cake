# path_analysis/analyze_paths.py

import networkx as nx
import pandas as pd
from ..utils.graph_converter import to_networkx
from ..path_analysis.path_scoring import score_path
import torch_geometric.data # Import for type hinting

def analyze_paths(pyg_data: torch_geometric.data.Data, anomaly_results_df: pd.DataFrame, max_path_length=4):
    """
    Identifies potential attack paths in the graph, scores them, and reports the riskiest.

    Args:
        pyg_data (torch_geometric.data.Data): The PyG graph data object.
        anomaly_results_df (pd.DataFrame): DataFrame from anomaly_detection,
                                         including 'node_index' and 'anomaly_score'.
        max_path_length (int): The maximum number of hops to consider for a path.

    Returns:
        list: A list of tuples, each containing (path_score, path_as_original_ids, path_as_indices).
              Sorted by score (lowest score = riskiest path)
    """
    print(f"\nAnalyzing paths (max length: {max_path_length})...")

    # Convert PyG data to NetworkX for easier path traversal
    nx_graph = to_networkx(pyg_data, pyg_data.idx_to_id.values()) # Pass node_ids for attribute

    # --- Identify Potential Start and End Nodes ---
    # For MVP, let's define simple criteria based on node types and names in simulated data
    start_node_criteria = lambda node_id, node_type: 'user' in node_type or 'vm_z' in node_id # Users, or potentially external-facing/compromised VMs
    end_node_criteria = lambda node_id, node_type: 'db' in node_type or 's3' in node_id or 'sg' in node_type # Databases, S3, Security Groups (high value/impact)

    potential_starts_idx = [i for i, node_id in pyg_data.idx_to_id.items() if start_node_criteria(node_id, pyg_data.unique_types[int(pyg_data.x[i, 0].item())])]
    potential_ends_idx = [i for i, node_id in pyg_data.idx_to_id.items() if end_node_criteria(node_id, pyg_data.unique_types[int(pyg_data.x[i, 0].item())])]

    print(f"Identified {len(potential_starts_idx)} potential start nodes and {len(potential_ends_idx)} potential end nodes.")
    print(f"Starts: {[pyg_data.idx_to_id[i] for i in potential_starts_idx]}")
    print(f"Ends: {[pyg_data.idx_to_id[i] for i in potential_ends_idx]}")


    # --- Enumerate and Score Paths ---
    risky_paths = []

    for start_node_idx in potential_starts_idx:
        for end_node_idx in potential_ends_idx:
            if start_node_idx == end_node_idx:
                continue # Don't look for paths from a node to itself

            # Find all simple paths up to max_path_length
            # Note: This can be computationally expensive on large graphs!
            # For MVP, keep graph small and max_path_length low.
            try:
                for path_indices in nx.all_simple_paths(nx_graph, source=start_node_idx, target=end_node_idx, cutoff=max_path_length - 1): # cutoff is num_edges = path_length - 1
                    # Score the found path
                    path_score = score_path(path_indices, nx_graph, anomaly_results_df)

                    # Convert node indices back to original IDs for reporting
                    path_original_ids = [pyg_data.idx_to_id[idx] for idx in path_indices]

                    risky_paths.append((path_score, path_original_ids, path_indices))
            except nx.NetworkXNoPath:
                continue # No path found between these two nodes

    # Sort paths by score (lowest score first = riskiest)
    risky_paths.sort(key=lambda x: x[0])

    print(f"Found and scored {len(risky_paths)} paths.")
    return risky_paths

def print_risky_paths(risky_paths, pyg_data: torch_geometric.data.Data, top_n=5): # Added pyg_data
    """Prints the top N riskiest paths."""
    print(f"\n--- Top {top_n} Riskiest Paths ---")
    if not risky_paths:
        print("No paths found.")
        return

    for i, (score, path_ids, path_indices) in enumerate(risky_paths[:top_n]):
        # Optional: Get node types for better context in output
        path_with_types = []
        for node_idx, node_id in zip(path_indices, path_ids):
             # This lookup is now correct because pyg_data is available
             node_index = path_indices[path_ids.index(node_id)] # Get index from id using original mapping
             node_type_int = int(pyg_data.x[node_index, 0].item())
             node_type_str = pyg_data.unique_types[node_type_int]
             path_with_types.append(f"{node_id} ({node_type_str})")


        print(f"Rank {i+1}: Score={score:.4f}")
        print("  Path: " + " -> ".join(path_ids))
        print("  Path (with types): " + " -> ".join(path_with_types))
        print("-" * 20)