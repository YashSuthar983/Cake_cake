import torch
import torch.nn.functional as F
from ..model.graphsage_model import GraphSAGE
from ..data_processing.build_graph import build_graph # Assuming build_graph creates a PyG Data object

def train_graphsage(data, epochs=50, lr=0.01, hidden_channels=64, out_channels=32):
    """
    Trains the GraphSAGE model.

    Args:
        data (torch_geometric.data.Data): The graph data.
        epochs (int): Number of training epochs.
        lr (float): Learning rate.
        hidden_channels (int): Number of hidden units in GNN layers.
        out_channels (int): Dimension of the final node embeddings.

    Returns:
        torch.nn.Module: The trained GraphSAGE model.
        torch.Tensor: The learned node embeddings.
    """
    in_channels = data.x.size(1) # Number of input features per node
    model = GraphSAGE(in_channels, hidden_channels, out_channels)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    # Self-supervised training task: Reconstruct node features
    # We'll use a simple linear layer after the GNN to try and reconstruct
    # the original features from the learned embeddings.
    reconstruction_decoder = torch.nn.Linear(out_channels, in_channels)
    reconstruction_optimizer = torch.optim.Adam(reconstruction_decoder.parameters(), lr=lr)

    criterion = torch.nn.MSELoss() # Mean Squared Error for reconstruction

    model.train()
    reconstruction_decoder.train()

    print("Starting GraphSAGE training...")
    for epoch in range(epochs):
        optimizer.zero_grad()
        reconstruction_optimizer.zero_grad()

        embeddings = model(data.x, data.edge_index) # Get embeddings
        reconstructed_features = reconstruction_decoder(embeddings) # Try to reconstruct original features

        loss = criterion(reconstructed_features, data.x) # Calculate reconstruction loss

        loss.backward()
        optimizer.step()
        reconstruction_optimizer.step()

        if (epoch + 1) % 10 == 0:
            print(f'Epoch {epoch+1}/{epochs}, Loss: {loss.item():.4f}')

    print("Training finished.")
    model.eval() # Set model to evaluation mode
    reconstruction_decoder.eval() # Decoder too
    with torch.no_grad():
        final_embeddings = model(data.x, data.edge_index) # Get final embeddings after training

    return model, final_embeddings

if __name__ == '__main__':
    # Example usage:
    # Ensure data is generated and graph is built first
    from data_processing.generate_simulated_data import generate_data
    from data_processing.build_graph import build_graph

    generate_data()
    graph_data = build_graph()
    trained_model, node_embeddings = train_graphsage(graph_data)

    print("\nFirst 5 node embeddings:")
    print(node_embeddings[:5])
    print(f"\nEmbeddings shape: {node_embeddings.shape}")