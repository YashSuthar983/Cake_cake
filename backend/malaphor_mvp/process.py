# backend/malaphor_core/process.py

import os
import pandas as pd
import torch

# Import your existing modules (assuming they are in malaphor_core)
from .data_processing.generate_simulated_data import generate_data
from .data_processing.build_graph import build_graph
from .training.train import train_graphsage
from .anomaly_detection.detect_anomalies import detect_anomalies
from .path_analysis.analyze_paths import analyze_paths

# Ensure a data directory exists if generating simulated data
if not os.path.exists('backend/malaphor_core/data'):
    os.makedirs('backend/malaphor_core/data')

def run_full_pipeline(csv_filepath):
    """
    Runs the full Malaphor MVP pipeline on a given CSV file.

    Args:
        csv_filepath (str): Path to the input CSV file.

    Returns:
        dict: A dictionary containing graph data (nodes, edges) and risky paths
              ready for JSON serialization and frontend use.
    """
    print(f"--- Running Malaphor Pipeline on {csv_filepath} ---")

    # 1. Build Graph
    # build_graph needs to return more than just the PyG Data object now.
    # It needs to return enough info to reconstruct nodes and edges for the frontend
    # with their original IDs and types.
    # Let's modify build_graph to return (pyg_data, node_list_for_frontend, edge_list_for_frontend)
    try:
        pyg_data, all_entities_df, edges_df = build_graph(csv_filepath)
    except FileNotFoundError:
         # If using simulated data initially and file doesn't exist
         if "simulated_cloud_data.csv" in csv_filepath:
              print("Simulated data not found, generating...")
              generate_data(csv_filepath) # Assuming generate_data takes filepath
              pyg_data, all_entities_df, edges_df = build_graph(csv_filepath)
         else:
             raise # Re-raise if it's not the simulated data case

    print("Graph built.")

    # 2. Train GraphSAGE
    print("Training GraphSAGE model...")
    epochs = 150
    lr = 0.005
    hidden_channels = 64
    out_channels = 32

    _, node_embeddings = train_graphsage(
        data=pyg_data,
        epochs=epochs,
        lr=lr,
        hidden_channels=hidden_channels,
        out_channels=out_channels
    )
    print("GraphSAGE training finished.")


    # 3. Detect Node Anomalies
    print("Detecting individual node anomalies...")
    contamination_rate = 0.2 # This might need tuning or be user-settable
    anomaly_results_df = detect_anomalies(
        data=pyg_data,
        embeddings=node_embeddings,
        contamination=contamination_rate
    )
    print("Node anomaly detection finished.")


    # 4. Analyze Paths
    print("Analyzing paths...")
    max_path_length = 4
    risky_paths = analyze_paths(
        pyg_data=pyg_data,
        anomaly_results_df=anomaly_results_df,
        max_path_length=max_path_length
    )
    print(f"Found {len(risky_paths)} risky paths.")


    # --- Prepare Data for Frontend ---

    # Nodes: Combine original entity info and anomaly results
    nodes_for_frontend = []
    # Ensure anomaly_results_df is indexed by node_index
    anomaly_results_df = anomaly_results_df.set_index('node_index')

    for i in range(pyg_data.num_nodes):
         original_id = pyg_data.idx_to_id[i]
         node_type_int = int(pyg_data.x[i, 0].item())
         original_type = pyg_data.unique_types[node_type_int]

         # Get anomaly data for this node index
         anomaly_info = anomaly_results_df.loc[i].to_dict() if i in anomaly_results_df.index else {'anomaly_score': None, 'prediction': None}

         nodes_for_frontend.append({
             'id': original_id, # Use original ID as Cytoscape node ID
             'label': original_id, # Label for display
             'type': original_type,
             'anomaly_score': anomaly_info.get('anomaly_score'),
             'prediction': anomaly_info.get('prediction'), # -1 for anomaly
             'features': pyg_data.x[i].tolist(), # Include raw features if needed
             'node_index': i # Keep internal index for potential debugging
         })

    # Edges: Use original IDs
    edges_for_frontend = []
    # edges_df returned by build_graph should contain source_id, target_id, relationship_type
    for _, row in edges_df.iterrows():
         edges_for_frontend.append({
             'source': row['source_id'],
             'target': row['target_id'],
             'relationship_type': row['relationship_type'] # Add edge type as attribute
         })

    # Risky Paths: Convert to a JSON-friendly format using original IDs
    risky_paths_for_frontend = []
    # risky_paths is a list of (score, path_as_original_ids, path_as_indices)
    for score, path_ids, path_indices in risky_paths:
         # Optionally add types to the path nodes for display
         path_with_types = []
         for node_id, node_index in zip(path_ids, path_indices):
             node_type_int = int(pyg_data.x[node_index, 0].item())
             node_type_str = pyg_data.unique_types[node_type_int]
             path_with_types.append(f"{node_id} ({node_type_str})")

         risky_paths_for_frontend.append({
             'score': float(score), # Ensure score is a standard float
             'path_ids': path_ids,
             'path_with_types': " -> ".join(path_with_types) # Simple string for display
         })


    results = {
        'nodes': nodes_for_frontend,
        'edges': edges_for_frontend,
        'risky_paths': risky_paths_for_frontend[:10] # Return top N paths
    }

    print("--- Pipeline Finished ---")
    return results

# No __main__ block here, this file is imported by Flask app