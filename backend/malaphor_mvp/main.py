# # main.py

# import os
# from data_processing.generate_simulated_data import generate_data
# from data_processing.build_graph import build_graph
# from training.train import train_graphsage
# from anomaly_detection.detect_anomalies import detect_anomalies
# from utils.helpers import print_anomaly_results, print_predicted_anomalies

# DATA_FILE = "data/simulated_cloud_data.csv"
# MODEL_SAVE_PATH = "output/graphsage_model.pth" # Not strictly needed for MVP, but good practice
# EMBEDDINGS_SAVE_PATH = "output/node_embeddings.pt"

# def ensure_output_dir():
#     """Ensures the output directory exists."""
#     output_dir = os.path.dirname(MODEL_SAVE_PATH)
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)
#         print(f"Created output directory: {output_dir}")

# if __name__ == '__main__':
#     ensure_output_dir()

#     print("--- Malaphor MVP Pipeline ---")

#     # 1. Generate or load data
#     if not os.path.exists(DATA_FILE):
#         print(f"\n{DATA_FILE} not found. Generating simulated data...")
#         generate_data(DATA_FILE)
#     else:
#         print(f"\nUsing existing data file: {DATA_FILE}")

#     # 2. Build Graph
#     print("\nBuilding graph from data...")
#     graph_data = build_graph(DATA_FILE)
#     print(graph_data) # Print summary of the graph data object

#     # 3. Train GraphSAGE
#     print("\nTraining GraphSAGE model...")
#     # Define hyperparameters for training (can tune these)
#     epochs = 100 # Increased epochs for better embedding learning
#     lr = 0.005
#     hidden_channels = 64
#     out_channels = 32 # Size of the final embedding vector

#     trained_model, node_embeddings = train_graphsage(
#         data=graph_data,
#         epochs=epochs,
#         lr=lr,
#         hidden_channels=hidden_channels,
#         out_channels=out_channels
#     )
#     # Optional: Save model and embeddings
#     # torch.save(trained_model.state_dict(), MODEL_SAVE_PATH)
#     # torch.save(node_embeddings, EMBEDDINGS_SAVE_PATH)

#     # 4. Detect Anomalies
#     print("\nDetecting anomalies...")
#     # Set contamination based on expected anomaly percentage (or 'auto')
#     # For our simulated data, we added 3 specific anomalies out of ~11 nodes/entities.
#     # So contamination is roughly 3 / 11 = ~0.27. Let's use a slightly lower number like 0.2
#     # Or use 'auto' and let Isolation Forest decide. Let's use a float for better control.
#     contamination_rate = 0.2 # Adjust based on your expectation or sensitivity

#     anomaly_results_df = detect_anomalies(
#         data=graph_data, # Pass data object for index mapping
#         embeddings=node_embeddings,
#         contamination=contamination_rate
#     )

#     # 5. Report Results
#     print_anomaly_results(anomaly_results_df, top_n=10)
#     print_predicted_anomalies(anomaly_results_df)

#     print("\n--- Malaphor MVP Pipeline Finished ---")




# main.py (Updated)

import os
from data_processing.generate_simulated_data import generate_data
from data_processing.build_graph import build_graph
from training.train import train_graphsage
from anomaly_detection.detect_anomalies import detect_anomalies
from path_analysis.analyze_paths import analyze_paths, print_risky_paths # Import new functions
from utils.helpers import print_anomaly_results # Keep helper for node anomalies

DATA_FILE = "data/simulated_cloud_data.csv"
# MODEL_SAVE_PATH = "output/graphsage_model.pth" # Not strictly needed for MVP
# EMBEDDINGS_SAVE_PATH = "output/node_embeddings.pt" # Not strictly needed for MVP

def ensure_output_dir():
    """Ensures the output directory exists."""
    # output_dir = os.path.dirname(MODEL_SAVE_PATH) # Adjust if saving paths
    output_dir = "output" # Let's just create a generic output folder
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

if __name__ == '__main__':
    ensure_output_dir()

    print("--- Malaphor MVP Pipeline (Attack Path Analysis) ---")

    # 1. Generate or load data
    if not os.path.exists(DATA_FILE):
        print(f"\n{DATA_FILE} not found. Generating simulated data...")
        generate_data(DATA_FILE)
    else:
        print(f"\nUsing existing data file: {DATA_FILE}")

    # 2. Build Graph
    print("\nBuilding graph from data...")
    graph_data = build_graph(DATA_FILE)
    print(graph_data) # Print summary of the graph data object

    # 3. Train GraphSAGE
    print("\nTraining GraphSAGE model...")
    epochs = 150 # Increase epochs slightly for potentially better embeddings for paths
    lr = 0.005
    hidden_channels = 64
    out_channels = 32 # Size of the final embedding vector

    # We only need the embeddings for path analysis, not the trained model itself for this MVP
    _, node_embeddings = train_graphsage(
        data=graph_data,
        epochs=epochs,
        lr=lr,
        hidden_channels=hidden_channels,
        out_channels=out_channels
    )

    # 4. Detect Node Anomalies (Optional, but useful for path scoring)
    print("\nDetecting individual node anomalies...")
    contamination_rate = 0.2 # Adjust based on your expectation or sensitivity

    anomaly_results_df = detect_anomalies(
        data=graph_data, # Pass data object for index mapping and types
        embeddings=node_embeddings,
        contamination=contamination_rate
    )

    # Print node anomaly results as before (optional, helps understand path scores)
    print_anomaly_results(anomaly_results_df, top_n=5) # Print top 5 node anomalies
    # print_predicted_anomalies(anomaly_results_df) # Less useful now, focus on paths

    # 5. Analyze Paths (NEW STEP)
    risky_paths = analyze_paths(
        pyg_data=graph_data,
        anomaly_results_df=anomaly_results_df,
        max_path_length=4 # Max 3 hops (start -> 1 -> 2 -> end)
    )

    # 6. Report Risky Paths
    print_risky_paths(risky_paths, graph_data, top_n=5)

    print("\n--- Malaphor MVP Pipeline Finished ---")