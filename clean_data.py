import pandas as pd

# Load data
df = pd.read_csv('Agriculture_price_dataset.csv')

# 1. Convert date column to proper date format
df['Price Date'] = pd.to_datetime(df['Price Date'])

# 2. Filter only Tomato and Onion
# (most price shock prone commodities)
df = df[df['Commodity'].isin(['Tomato', 'Onion'])]

# 3. Keep only useful columns
df = df[['STATE', 'Market Name', 'Commodity', 
         'Modal_Price', 'Price Date']]

# 4. Rename columns for simplicity
df.columns = ['state', 'market', 'commodity', 
              'price', 'date']

# 5. Sort by date
df = df.sort_values('date')

# 6. Save cleaned data
df.to_csv('cleaned_data.csv', index=False)

print("=== Cleaned Data ===")
print(df.head(10))
print(f"\nTotal rows after cleaning: {len(df)}")
print(f"Markets: {df['market'].nunique()}")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")