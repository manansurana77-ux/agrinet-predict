import pandas as pd

# Load data
df = pd.read_csv('Agriculture_price_dataset.csv')

# 1. Check shape
print("=== Dataset Shape ===")
print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")

# 2. Check missing values
print("\n=== Missing Values ===")
print(df.isnull().sum())

# 3. Check all commodities
print("\n=== Commodities Available ===")
print(df['Commodity'].unique())

# 4. Check all states
print("\n=== States Available ===")
print(df['STATE'].unique())

# 5. Check price range
print("\n=== Price Range ===")
print(df[['Min_Price','Max_Price','Modal_Price']].describe())

# 6. Check date range
print("\n=== Date Range ===")
print(f"From: {df['Price Date'].min()}")
print(f"To: {df['Price Date'].max()}")