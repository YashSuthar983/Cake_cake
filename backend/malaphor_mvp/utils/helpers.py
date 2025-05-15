# utils/helpers.py

def print_anomaly_results(results_df, top_n=10):
    """Prints the top N anomaly results."""
    print(f"\n--- Top {top_n} Most Anomalous Nodes ---")
    print(results_df.head(top_n).to_string(index=False))

def print_predicted_anomalies(results_df):
    """Prints nodes predicted as anomalies by Isolation Forest."""
    anomalies = results_df[results_df['prediction'] == -1]
    if anomalies.empty:
        print("\n--- No nodes predicted as anomalies by Isolation Forest ---")
    else:
        print("\n--- Nodes Predicted as Anomalies (-1 prediction) ---")
        print(anomalies.to_string(index=False))

# Add other helper functions here if needed