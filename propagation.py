import pandas as pd
import numpy as np

print("=== AgriNet-Predict: Price Shock Propagation ===")

# Load shock status and edges
shock_df = pd.read_csv('shock_status.csv')
edges_df = pd.read_csv('mandi_edges.csv')

# Get severely shocked markets
severe_shocks = shock_df[
    shock_df['shock_level'].str.contains('SEVERE')
]['market'].tolist()

print(f"\nCurrently in SEVERE SHOCK: {len(severe_shocks)} markets")
print(severe_shocks[:5], "...")

# For each stable market find if it is connected
# to a shocked market
print("\n=== Propagation Risk Analysis ===")
propagation_risk = []

stable_markets = shock_df[
    shock_df['shock_level'].str.contains('STABLE')
]['market'].tolist()

for stable_market in stable_markets:
    # Find all markets connected to this stable market
    connected_shocked = []
    
    # Check edges where this market appears
    connected1 = edges_df[
        edges_df['market1'] == stable_market
    ]['market2'].tolist()
    
    connected2 = edges_df[
        edges_df['market2'] == stable_market
    ]['market1'].tolist()
    
    all_connected = connected1 + connected2
    
    # Check how many connected markets are in shock
    for connected_market in all_connected:
        if connected_market in severe_shocks:
            # Get correlation strength
            corr1 = edges_df[
                (edges_df['market1'] == stable_market) & 
                (edges_df['market2'] == connected_market)
            ]['correlation']
            
            corr2 = edges_df[
                (edges_df['market2'] == stable_market) & 
                (edges_df['market1'] == connected_market)
            ]['correlation']
            
            corr = corr1.values[0] if len(corr1) > 0 else (
                corr2.values[0] if len(corr2) > 0 else 0
            )
            
            connected_shocked.append({
                'shocked_market': connected_market,
                'correlation': corr
            })
    
    if connected_shocked:
        # Calculate propagation risk score
        max_corr = max([c['correlation'] for c in connected_shocked])
        num_shocked = len(connected_shocked)
        
        # Risk score = correlation strength x number of shocked neighbours
        risk_score = round(max_corr * num_shocked * 100, 1)
        
        # Estimate days until shock arrives
        # Higher correlation = faster propagation
        days_until_shock = max(1, round((1 - max_corr) * 10))
        
        propagation_risk.append({
            'at_risk_market': stable_market,
            'connected_shocked_markets': num_shocked,
            'max_correlation': round(max_corr, 3),
            'propagation_risk_score': risk_score,
            'estimated_days_until_shock': days_until_shock,
            'warning': '⚠️ SELL NOW' if risk_score > 50 else '👀 MONITOR'
        })

# Sort by risk score
risk_df = pd.DataFrame(propagation_risk)

if len(risk_df) > 0:
    risk_df = risk_df.sort_values(
        'propagation_risk_score', ascending=False
    )
    
    print(risk_df.head(20).to_string(index=False))
    
    print(f"\n=== Propagation Summary ===")
    print(f"Stable markets at risk: {len(risk_df)}")
    print(f"SELL NOW warnings: {len(risk_df[risk_df['warning'].str.contains('SELL')])}")
    print(f"MONITOR warnings: {len(risk_df[risk_df['warning'].str.contains('MONITOR')])}")
    
    # Save propagation risk
    risk_df.to_csv('propagation_risk.csv', index=False)
    print("\nPropagation risk saved as propagation_risk.csv!")
else:
    print("No propagation risk detected in connected markets")
    