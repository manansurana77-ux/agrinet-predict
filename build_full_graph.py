import pandas as pd
import numpy as np

print("=== Building Full Mandi Graph ===")

# Load cleaned data
df = pd.read_csv('cleaned_data.csv')

# Focus on Tomato
tomato = df[df['commodity'] == 'Tomato'].copy()
tomato['date'] = pd.to_datetime(tomato['date'])

# Pivot — markets as columns
pivot = tomato.pivot_table(
    index='date',
    columns='market',
    values='price'
)

# Keep markets with at least 30 days data
# (lowered from 100 to include more markets)
pivot = pivot.dropna(thresh=30, axis=1)

print(f"Markets with enough data: {pivot.shape[1]}")

# Fill remaining missing values
pivot = pivot.ffill().bfill()
# Calculate correlation
correlation = pivot.corr()

# Build edges — lower threshold to 0.5
# to capture more market connections
edges = []
markets = correlation.columns.tolist()

for i in range(len(markets)):
    for j in range(i+1, len(markets)):
        corr_value = correlation.iloc[i, j]
        if corr_value > 0.5:
            edges.append({
                'market1': markets[i],
                'market2': markets[j],
                'correlation': round(corr_value, 3)
            })

edges_df = pd.DataFrame(edges)
edges_df.to_csv('mandi_edges.csv', index=False)

print(f"Total markets in graph: {len(markets)}")
print(f"Total edges found: {len(edges_df)}")
print(f"\nSample edges:")
print(edges_df.head(10).to_string(index=False))
