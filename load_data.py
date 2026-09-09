import pandas as pd
import os

# Check if file exists
print("Files in folder:")
print(os.listdir('.'))

# Load the data
try:
    df = pd.read_csv('Agriculture_price_dataset.csv')
    print("\n=== AGMARKNET Price Data ===")
    print(df.head(10))
    print(f"\nTotal rows: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")
except Exception as e:
    print(f"Error: {e}")