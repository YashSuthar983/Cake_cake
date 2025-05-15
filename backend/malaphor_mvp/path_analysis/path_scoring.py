# path_analysis/path_scoring.py

import networkx as nx
import pandas as pd

def score_path(path: list, nx_graph: nx.DiGraph, anomaly_results_df: pd.DataFrame) -> float:
    """
    Scores a single path based on the anomaly results of nodes within the path.

    Args:
        path (list): A list of node indices representing the path [node1_idx, node2_idx, ...].
        nx_graph (nx.DiGraph): The NetworkX graph object (used to get node attributes).
        anomaly_results_df (pd.DataFrame): DataFrame containing 'node_index' and 'anomaly_score'.

    Returns:
        float: The risk score of the path (lower score = higher risk, similar to IF).
               Could also return a positive risk score (higher = higher risk).
               Let's use lower score = higher risk for consistency with IF.
    """
    if not path:
        return float('inf') # Or some value indicating invalid path

    # Aggregate anomaly scores of nodes in the path
    # We'll sum the Isolation Forest decision function scores.
    # Lower sum -> more anomalous nodes -> higher risk path.

    total_anomaly_score = 0
    num_nodes_in_path = len(path)

    # Get anomaly scores for all nodes involved in the path
    path_anomaly_scores = anomaly_results_df[anomaly_results_df['node_index'].isin(path)]

    if path_anomaly_scores.empty and num_nodes_in_path > 0:
         # This shouldn't happen if the results_df covers all nodes, but as a safeguard
         return 0 # Neutral score if no scores found? Or inf? Depends on scoring logic.
                   # Let's assume 0 means 'not explicitly anomalous' for the nodes.

    # Simple aggregation: sum of scores. Min score will be the riskiest.
    # You could also use average, or weigh based on node type.
    # For MVP, sum is fine.
    total_anomaly_score = path_anomaly_scores['anomaly_score'].sum()

    # Optional: Add heuristics based on node/edge types in the path
    # Example: penalize paths involving 'user' accessing 'resource' directly if unusual,
    # or paths involving 'config' nodes being modified.
    # This requires accessing node/edge attributes from the nx_graph.
    # node_attributes = [nx_graph.nodes[node_idx] for node_idx in path]
    # Add logic here if needed... e.g., check node_attributes for 'type'

    # Return the aggregated anomaly score.
    # We want lower scores to indicate higher risk, matching Isolation Forest.
    return total_anomaly_score

# This function is used by analyze_paths.py, won't run directly.