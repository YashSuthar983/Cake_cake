# import pandas as pd
# import torch
# import torch_geometric.data
# import networkx as nx

# def build_graph(filepath="data/simulated_cloud_data.csv"):
#     """Builds a PyG Data object from simulated cloud data."""
#     df = pd.read_csv(filepath)

#     # 1. Create a list of all unique entities (nodes)
#     sources = df[['source_id', 'source_type']].rename(columns={'source_id': 'id', 'source_type': 'type'})
#     targets = df[['target_id', 'target_type']].rename(columns={'target_id': 'id', 'target_type': 'type'})
#     all_entities = pd.concat([sources, targets]).drop_duplicates().reset_index(drop=True)

#     # Map original IDs to integer indices (required by PyG)
#     id_to_idx = {id: idx for idx, id in enumerate(all_entities['id'])}
#     idx_to_id = {idx: id for id, idx in id_to_idx.items()}
#     num_nodes = len(all_entities)

#     print(f"Created {num_nodes} nodes.")

#     # 2. Create Edge Index (adjacency list format for PyG)
#     # PyG expects a tensor of shape [2, num_edges]
#     source_indices = df['source_id'].apply(lambda x: id_to_idx[x]).values
#     target_indices = df['target_id'].apply(lambda x: id_to_idx[x]).values
#     edge_index = torch.tensor([source_indices, target_indices], dtype=torch.long)

#     print(f"Created {edge_index.size(1)} edges.")

#     # 3. Create Node Features (x)
#     # Let's use node type as a feature (requires encoding)
#     # Also, aggregate edge features (feature1, feature2) to incident nodes as a simple node feature
#     unique_types = all_entities['type'].unique()
#     type_to_int = {type: i for i, type in enumerate(unique_types)}
#     all_entities['type_int'] = all_entities['type'].apply(lambda x: type_to_int[x])

#     # Simple feature aggregation: sum of feature1 and average of feature2 for incoming/outgoing edges
#     # This is a simplified approach for MVP; real feature engineering would be more complex
#     aggregated_features = {}
#     for idx, entity_id in idx_to_id.items():
#         incoming_edges = df[df['target_id'] == entity_id]
#         outgoing_edges = df[df['source_id'] == entity_id]

#         sum_feature1 = incoming_edges['feature1'].sum() + outgoing_edges['feature1'].sum()
#         avg_feature2 = 0
#         total_feature2_count = 0
#         if not incoming_edges.empty:
#             avg_feature2 += incoming_edges['feature2'].sum()
#             total_feature2_count += len(incoming_edges)
#         if not outgoing_edges.empty:
#             avg_feature2 += outgoing_edges['feature2'].sum()
#             total_feature2_count += len(outgoing_edges)
#         if total_feature2_count > 0:
#              avg_feature2 /= total_feature2_count

#         # Combine node type integer and aggregated features
#         aggregated_features[idx] = [all_entities.loc[all_entities['id'] == entity_id, 'type_int'].iloc[0], sum_feature1, avg_feature2]

#     # Ensure features are in the correct order corresponding to node indices
#     node_features_list = [aggregated_features[i] for i in range(num_nodes)]
#     x = torch.tensor(node_features_list, dtype=torch.float)

#     print(f"Node features shape: {x.shape}")

#     # 4. Create PyG Data object
#     data = torch_geometric.data.Data(x=x, edge_index=edge_index)

#     # Store mappings for later use
#     data.id_to_idx = id_to_idx
#     data.idx_to_id = idx_to_id
#     data.unique_types = unique_types
#     data.type_to_int = type_to_int

#     print("PyG Data object created.")
#     return data

# if __name__ == '__main__':
#     # Ensure data file exists first
#     from data_processing.generate_simulated_data import generate_data
#     generate_data()
#     # Then build graph
#     graph_data = build_graph()
#     print(graph_data)



import pandas as pd
import torch
import torch_geometric.data
# import networkx as nx # No longer needed here

def build_graph(filepath):
    """
    Builds a PyG Data object and returns data needed for frontend.

    Returns:
        tuple: (pyg_data, all_entities_df, edges_df)
    """
    df = pd.read_csv(filepath)

    # 1. Create a list of all unique entities (nodes)
    sources = df[['source_id', 'source_type']].rename(columns={'source_id': 'id', 'source_type': 'type'})
    targets = df[['target_id', 'target_type']].rename(columns={'target_id': 'id', 'target_type': 'type'})
    all_entities_df = pd.concat([sources, targets]).drop_duplicates().reset_index(drop=True)

    # Map original IDs to integer indices (required by PyG)
    id_to_idx = {id: idx for idx, id in enumerate(all_entities_df['id'])}
    idx_to_id = {idx: id for id, idx in id_to_idx.items()}
    num_nodes = len(all_entities_df)

    # 2. Create Edge Index (adjacency list format for PyG)
    source_indices = df['source_id'].apply(lambda x: id_to_idx[x]).values
    target_indices = df['target_id'].apply(lambda x: id_to_idx[x]).values
    edge_index = torch.tensor([source_indices, target_indices], dtype=torch.long)


    # 3. Create Node Features (x)
    unique_types = all_entities_df['type'].unique()
    type_to_int = {type: i for i, type in enumerate(unique_types)}
    all_entities_df['type_int'] = all_entities_df['type'].apply(lambda x: type_to_int[x]) # Add int type back to df

    aggregated_features = {}
    for idx in range(num_nodes): # Iterate by index to match PyG order
        entity_id = idx_to_id[idx]
        incoming_edges = df[df['target_id'] == entity_id]
        outgoing_edges = df[df['source_id'] == entity_id]

        sum_feature1 = incoming_edges['feature1'].sum() + outgoing_edges['feature1'].sum()
        avg_feature2 = 0
        total_feature2_count = 0
        if not incoming_edges.empty:
            avg_feature2 += incoming_edges['feature2'].sum()
            total_feature2_count += len(incoming_edges)
        if not outgoing_edges.empty:
            avg_feature2 += outgoing_edges['feature2'].sum()
            total_feature2_count += len(outgoing_edges)
        if total_feature2_count > 0:
             avg_feature2 /= total_feature2_count

        aggregated_features[idx] = [all_entities_df.loc[all_entities_df['id'] == entity_id, 'type_int'].iloc[0], sum_feature1, avg_feature2]


    node_features_list = [aggregated_features[i] for i in range(num_nodes)] # Ensure ordered by index
    x = torch.tensor(node_features_list, dtype=torch.float)


    # 4. Create PyG Data object
    data = torch_geometric.data.Data(x=x, edge_index=edge_index)

    # Store mappings and types within PyG data object (useful for other steps)
    data.id_to_idx = id_to_idx
    data.idx_to_id = idx_to_id
    data.unique_types = unique_types
    data.type_to_int = type_to_int

    # Return PyG data, and DFs containing original info for frontend
    return data, all_entities_df, df # Return edges_df (original df) for frontend edge info