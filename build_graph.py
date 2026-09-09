import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load cleaned data
df = pd.read_csv('cleaned_data.csv')

# Focus on Tomato only first
tomato = df[df['commodity'] == 'Tomato']

# Pivot — each market becomes a column
# rows = dates, columns = markets, values = price
pivot = tomato.pivot_table(
    index='date', 
    columns='market', 
    values='price'
)

# Keep only markets with enough data
# (at least 100 days of price data)
pivot = pivot.dropna(thresh=100, axis=1)

print(f"Markets with enough data: {pivot.shape[1]}")
print(f"Date range: {pivot.index[0]} to {pivot.index[-1]}")

# Calculate price correlation between all markets
# If two markets have correlation > 0.7
# they are connected in our graph
correlation = pivot.corr()

print(f"\n=== Price Correlation Matrix ===")
print(f"Shape: {correlation.shape}")

# Find strongly connected market pairs
edges = []
markets = correlation.columns.tolist()

for i in range(len(markets)):
    for j in range(i+1, len(markets)):
        corr_value = correlation.iloc[i, j]
        if corr_value > 0.7:  # strong connection
            edges.append({
                'market1': markets[i],
                'market2': markets[j],
                'correlation': round(corr_value, 3)
            })

edges_df = pd.DataFrame(edges)
edges_df.to_csv('mandi_edges.csv', index=False)

print(f"\n=== Mandi Graph Edges ===")
print(f"Total connected market pairs: {len(edges_df)}")
print(edges_df.head(10))