import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv

class GraphSAGE(nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels, num_layers=2):
        super(GraphSAGE, self).__init__()

        self.num_layers = num_layers
        self.convs = nn.ModuleList()
        # Input layer
        self.convs.append(SAGEConv(in_channels, hidden_channels))
        # Hidden layers
        for _ in range(num_layers - 2):
            self.convs.append(SAGEConv(hidden_channels, hidden_channels))
        # Output layer (produces embeddings)
        self.convs.append(SAGEConv(hidden_channels, out_channels))

    def forward(self, x, edge_index):
        # Propagate features through GraphSAGE layers
        for i in range(self.num_layers):
            x = self.convs[i](x, edge_index)
            if i < self.num_layers - 1:
                # Apply activation and dropout between layers
                x = F.relu(x)
                # x = F.dropout(x, p=0.5, training=self.training) # Optional: Add dropout

        # The output 'x' now contains the node embeddings
        return x