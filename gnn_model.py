import pandas as pd
import numpy as np
import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from torch_geometric.data import Data
from sklearn.preprocessing import LabelEncoder

print("=== AgriNet-Predict GNN Model ===")

# Load data
df = pd.read_csv('cleaned_data.csv')
edges = pd.read_csv('mandi_edges.csv')

# Focus on Tomato only
tomato = df[df['commodity'] == 'Tomato']

# Encode market names to numbers
le = LabelEncoder()
all_markets = pd.concat([
    edges['market1'], 
    edges['market2']
]).unique()
le.fit(all_markets)

# Build edge index for GNN
edge_src = le.transform(edges['market1'])
edge_dst = le.transform(edges['market2'])
edge_index = torch.tensor(
    [edge_src, edge_dst], 
    dtype=torch.long
)

print(f"Total markets (nodes): {len(all_markets)}")
print(f"Total connections (edges): {len(edges)}")

# Build node features
# For each market: average price, max price, min price
node_features = []
for market in all_markets:
    market_data = tomato[tomato['market'] == market]['price']
    if len(market_data) > 0:
        avg_price = market_data.mean()
        max_price = market_data.max()
        min_price = market_data.min()
        std_price = market_data.std()
    else:
        avg_price = max_price = min_price = std_price = 0
    node_features.append([avg_price, max_price, 
                          min_price, std_price])

x = torch.tensor(node_features, dtype=torch.float)
print(f"Node features shape: {x.shape}")

# Build target — predict if price will drop
# (price shock detection)
targets = []
for market in all_markets:
    market_data = tomato[tomato['market'] == market]['price']
    if len(market_data) > 1:
        # 1 = price dropped (shock), 0 = stable
        last_price = market_data.iloc[-1]
        avg_price = market_data.mean()
        shock = 1 if last_price < avg_price * 0.85 else 0
    else:
        shock = 0
    targets.append(shock)

y = torch.tensor(targets, dtype=torch.long)
print(f"Price shocks detected: {sum(targets)} out of {len(targets)} markets")

# Create PyG graph data object
graph_data = Data(x=x, edge_index=edge_index, y=y)
print(f"\nGraph created successfully!")
print(f"Graph: {graph_data}")

# Define GNN Model
class AgriGNN(torch.nn.Module):
    def __init__(self):
        super(AgriGNN, self).__init__()
        # Layer 1 — learns from neighbours
        self.conv1 = GCNConv(4, 16)
        # Layer 2 — deeper learning
        self.conv2 = GCNConv(16, 8)
        # Output layer — shock or no shock
        self.classifier = torch.nn.Linear(8, 2)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        # Pass through GNN layers
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.3, training=self.training)
        x = self.conv2(x, edge_index)
        x = F.relu(x)
        x = self.classifier(x)
        return F.log_softmax(x, dim=1)

# Initialize model
model = AgriGNN()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

print("\n=== Training GNN Model ===")

# Train for 100 epochs
for epoch in range(100):
    model.train()
    optimizer.zero_grad()
    out = model(graph_data)
    loss = F.nll_loss(out, graph_data.y)
    loss.backward()
    optimizer.step()
    
    if epoch % 10 == 0:
        print(f"Epoch {epoch}: Loss = {loss.item():.4f}")

print("\n=== GNN Training Complete! ===")

# Test predictions
model.eval()
with torch.no_grad():
    predictions = model(graph_data)
    pred_classes = predictions.argmax(dim=1)
    
print("\n=== Price Shock Predictions ===")
for i, market in enumerate(all_markets):
    status = "🚨 SHOCK DETECTED" if pred_classes[i] == 1 else "✅ STABLE"
    print(f"{market}: {status}")

# Save model
torch.save(model.state_dict(), 'agripredict_gnn.pth')
print("\nModel saved as agripredict_gnn.pth!")
