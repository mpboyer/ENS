"""
Deep Learning on Graphs - ALTEGRAD - Nov 2025
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class GATLayer(nn.Module):
    """GAT layer"""
    def __init__(self, n_feat, n_hidden, alpha=0.05):
        super(GATLayer, self).__init__()
        self.fc = nn.Linear(n_feat, n_hidden, bias=False)
        self.a = nn.Linear(2*n_hidden, 1)
        self.leakyrelu = nn.LeakyReLU(alpha)

    def forward(self, x, adj):
        ############## Task 1
    
        # Get edge indices
        indices = adj.coalesce().indices()
    
        # Apply linear transformation
        Wh = self.fc(x)  # Shape: (n_nodes, n_hidden)
    
        # Compute attention scores for all edges
        # Concatenate source and target node features for each edge
        Wh_i = torch.index_select(Wh, 0, indices[0,:])  # Source nodes
        Wh_j = torch.index_select(Wh, 0, indices[1,:])  # Target nodes
        Wh_concat = torch.cat([Wh_i, Wh_j], dim=1)  # Concatenate
        
        # Compute e_ij = LeakyReLU(a^T [Wh_i || Wh_j])
        h = self.leakyrelu(self.a(Wh_concat))

        h = torch.exp(h.squeeze())
        unique = torch.unique(indices[0,:])
        t = torch.zeros(unique.size(0), device=x.device)
        h_sum = t.scatter_add(0, indices[0,:], h)
        h_norm = torch.gather(h_sum, 0, indices[0,:])
        alpha = torch.div(h, h_norm)
        adj_att = torch.sparse.FloatTensor(indices, alpha, torch.Size([x.size(0), x.size(0)])).to(x.device)
        
        # Message passing: (A ⊙ T) * (Z * W)
        out = torch.sparse.mm(adj_att, Wh)

        return out, alpha


class GNN(nn.Module):
    """GNN model"""
    def __init__(self, nfeat, nhid, nclass, dropout):
        super(GNN, self).__init__()
        self.mp1 = GATLayer(nfeat, nhid)
        self.mp2 = GATLayer(nhid, nhid)
        self.fc = nn.Linear(nhid, nclass)
        self.dropout = nn.Dropout(dropout)
        self.relu = nn.ReLU()

    def forward(self, x, adj):
        
        ############## Task
    
        # First GAT layer with ReLU activation
        x, _ = self.mp1(x, adj)
        x = self.relu(x)
        
        # Dropout
        x = self.dropout(x)
        
        # Second GAT layer with ReLU activation
        x, alpha = self.mp2(x, adj)
        x = self.relu(x)
        
        # Fully-connected layer
        x = self.fc(x)
        return F.log_softmax(x, dim=1), alpha
