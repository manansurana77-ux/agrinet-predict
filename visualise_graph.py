import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx

# Load edges
edges = pd.read_csv('mandi_edges.csv')

# Build graph
G = nx.Graph()

# Add edges with correlation as weight
for _, row in edges.iterrows():
    G.add_edge(row['market1'], 
               row['market2'], 
               weight=row['correlation'])

print(f"Total markets (nodes): {G.number_of_nodes()}")
print(f"Total connections (edges): {G.number_of_edges()}")

# Draw the graph
plt.figure(figsize=(15, 10))
plt.title("AgriNet-Predict: Indian Mandi Price Network Graph", 
          fontsize=16, fontweight='bold')

# Layout
pos = nx.spring_layout(G, seed=42)

# Draw nodes
nx.draw_networkx_nodes(G, pos, 
                       node_color='lightblue',
                       node_size=500)

# Draw edges
nx.draw_networkx_edges(G, pos, 
                       alpha=0.5,
                       edge_color='gray')

# Draw labels
nx.draw_networkx_labels(G, pos, 
                        font_size=7,
                        font_weight='bold')

plt.axis('off')
plt.tight_layout()
plt.savefig('mandi_network_graph.png', 
            dpi=150, bbox_inches='tight')
plt.show()

print("\nGraph saved as mandi_network_graph.png!")
