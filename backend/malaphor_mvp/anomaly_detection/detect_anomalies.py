import torch
import pandas as pd
from sklearn.ensemble import IsolationForest
from ..training.train import train_graphsage # Assuming train_graphsage returns embeddings

def detect_anomalies(data, embeddings, contamination='auto'):
    """
    Detects anomalies using Isolation Forest on node embeddings.

    Args:
        data (torch_geometric.data.Data): The graph data object (needed for index mapping).
        embeddings (torch.Tensor): The learned node embeddings from the GNN.
        contamination ('auto' or float): The proportion of outliers in the data set.

    Returns:
        pandas.DataFrame: A DataFrame with node IDs, original types, anomaly scores, and prediction.
    """
    # Isolation Forest works best on numpy arrays
    embeddings_np = embeddings.cpu().numpy()

    # Initialize and train Isolation Forest
    # Note: Isolation Forest is unsupervised, it learns what "normal" looks like
    # on the entire dataset it's fit on. For a real scenario, you might train
    # IF on embeddings of known good data or a training subset. For MVP, we fit on all.
    iso_forest = IsolationForest(contamination=contamination, random_state=42)
    print("Fitting Isolation Forest on node embeddings...")
    iso_forest.fit(embeddings_np)

    # Predict anomaly scores (-higher means less anomalous, +lower means more anomalous)
    # and prediction (-1 for outlier, 1 for inlier)
    anomaly_scores = iso_forest.decision_function(embeddings_np)
    predictions = iso_forest.predict(embeddings_np)

    # Map results back to original node IDs and types
    results_df = pd.DataFrame({
        'node_index': range(len(data.idx_to_id)),
        'node_id': [data.idx_to_id[i] for i in range(len(data.idx_to_id))],
        'anomaly_score': anomaly_scores,
        'prediction': predictions # -1 is anomaly
    })

    # Add original node type for context
    type_map_df = pd.DataFrame({
        'node_id': list(data.id_to_idx.keys()),
        'node_type': [data.unique_types[int(data.x[i, 0].item())] for i in range(len(data.idx_to_id))]
        # Note: This line assumes node types are stored correctly in the graph data object
        # Let's refine this based on how we stored type info in build_graph
    })
    # Correct way to get types: Get original types from the all_entities df or store it better
    # For now, let's load the entities list or use the mapping created in build_graph
    # Assuming build_graph added unique_types and type_to_int to data object
    # The type for a node index `i` corresponds to data.x[i, 0] after mapping.
    original_types = [data.unique_types[int(data.x[i, 0].item())] for i in range(len(data.idx_to_id))]
    results_df['node_type'] = original_types


    # Sort by anomaly score (lower score means more anomalous)
    results_df = results_df.sort_values(by='anomaly_score').reset_index(drop=True)

    print("\nAnomaly detection finished.")
    return results_df

if __name__ == '__main__':
    # Example usage:
    from data_processing.generate_simulated_data import generate_data
    from data_processing.build_graph import build_graph

    generate_data()
    graph_data = build_graph()
    # Train GNN to get embeddings
    _, node_embeddings = train_graphsage(graph_data)

    # Detect anomalies
    anomaly_results = detect_anomalies(graph_data, node_embeddings, contamination=0.1) # Assume 10% anomalies

    print("\nTop 10 most anomalous nodes:")
    print(anomaly_results.head(10))

    print("\nNodes predicted as anomalies (-1):")
    print(anomaly_results[anomaly_results['prediction'] == -1])