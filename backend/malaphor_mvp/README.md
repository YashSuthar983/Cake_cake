# Malaphor MVP: AI-Enhanced Threat Hunting (GraphSAGE on Simulated Cloud Data)

This project is a Minimum Viable Product demonstrating the core concept of Malaphor: using Graph Neural Networks (specifically GraphSAGE) to detect anomalies in a graph representation of cloud resource relationships and access patterns.

## MVP Focus

*   **Graph Representation:** Convert simulated cloud logs and configurations into a graph where nodes are entities (users, resources, security groups, etc.) and edges are relationships (accesses, belongs-to, allows, etc.).
*   **GraphSAGE Embeddings:** Train a GraphSAGE model on this graph to learn a low-dimensional vector representation (embedding) for each node, capturing its structural role and feature information within the graph.
*   **Anomaly Detection:** Use an unsupervised anomaly detection algorithm (Isolation Forest) on the learned node embeddings. Nodes whose embeddings are outliers in the embedding space are flagged as potentially anomalous.

## Project Structure