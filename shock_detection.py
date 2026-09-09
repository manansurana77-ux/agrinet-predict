import pandas as pd
import numpy as np

print("=== AgriNet-Predict: Price Shock Detection ===")

# Load cleaned data
# Why: we need our clean tomato/onion price data
df = pd.read_csv('cleaned_data.csv')

# Focus on Tomato only first
# Why: tomato has most price volatility in India
tomato = df[df['commodity'] == 'Tomato'].copy()

# Convert date column to proper date format
# Why: so Python understands dates correctly for sorting
tomato['date'] = pd.to_datetime(tomato['date'])

# Sort by market and date
# Why: we need prices in time order for each market
tomato = tomato.sort_values(['market', 'date'])

# Calculate price shock for each market
results = []

for market in tomato['market'].unique():
    market_data = tomato[tomato['market'] == market].copy()
    
    # Skip markets with very little data
    # Why: need at least 10 days to calculate meaningful trend
    if len(market_data) < 10:
        continue
    
    # Calculate 7-day rolling average
    # Why: compare today's price to last 7 days average
    # gives much more accurate shock detection than all-time average
    market_data['rolling_avg'] = (
        market_data['price'].rolling(7).mean()
    )
    
    # Calculate how much price changed in percentage
    # Why: percentage change is more meaningful than absolute change
    # Rs 100 drop means different things for Rs 500 vs Rs 5000 commodity
    market_data['price_change'] = (
        (market_data['price'] - market_data['rolling_avg']) 
        / market_data['rolling_avg'] * 100
    )
    
    # Get the most recent data point
    # Why: we want to know current market status
    latest = market_data.dropna().iloc[-1]
    price_change = latest['price_change']
    
    # Classify into 4 shock levels
    # Why: gives farmer clear actionable information
    # instead of just "shock or no shock"
    if price_change < -20:
        shock_level = "🔴 SEVERE SHOCK"
    elif price_change < -10:
        shock_level = "🟠 MODERATE SHOCK"
    elif price_change < -5:
        shock_level = "🟡 MILD SHOCK"
    else:
        shock_level = "🟢 STABLE"
    
    results.append({
        'market': market,
        'current_price': round(latest['price'], 2),
        'average_price': round(latest['rolling_avg'], 2),
        'price_change_%': round(price_change, 2),
        'shock_level': shock_level
    })

# Create results dataframe
results_df = pd.DataFrame(results)

# Sort by price change — worst shocks first
# Why: farmer needs to see most urgent markets first
results_df = results_df.sort_values('price_change_%')

print("\n=== Market Shock Status ===")
print(results_df.to_string(index=False))

print(f"\n=== Summary ===")
print(f"Total markets analysed: {len(results_df)}")
print(f"Severe shocks: {len(results_df[results_df['shock_level'].str.contains('SEVERE')])}")
print(f"Moderate shocks: {len(results_df[results_df['shock_level'].str.contains('MODERATE')])}")
print(f"Mild shocks: {len(results_df[results_df['shock_level'].str.contains('MILD')])}")
print(f"Stable markets: {len(results_df[results_df['shock_level'].str.contains('STABLE')])}")

# Save results to CSV
# Why: we will use this data in the farmer advisory later
results_df.to_csv('shock_status.csv', index=False)
print("\nShock status saved as shock_status.csv!")
