import pandas as pd

print("=== AgriNet-Predict: Farmer Advisory System ===")

# Load all our results
shock_df = pd.read_csv('shock_status.csv')
risk_df = pd.read_csv('propagation_risk.csv')

print("\nEnter farmer details:")
farmer_market = input("Your market name (e.g. Bilsi, Gorakhpur): ")
farmer_commodity = "Tomato"

# Check if market is already in shock
market_shock = shock_df[
    shock_df['market'].str.lower() == farmer_market.lower()
]

# Check if market is at risk
market_risk = risk_df[
    risk_df['at_risk_market'].str.lower() == farmer_market.lower()
]

print(f"\n{'='*50}")
print(f"  AgriNet-Predict Advisory for {farmer_market}")
print(f"  Commodity: {farmer_commodity}")
print(f"{'='*50}")

if len(market_shock) > 0:
    shock = market_shock.iloc[0]
    
    if 'SEVERE' in shock['shock_level']:
        print(f"\n🔴 CURRENT STATUS: SEVERE PRICE SHOCK")
        print(f"   Current Price: ₹{shock['current_price']}/quintal")
        print(f"   Average Price: ₹{shock['average_price']}/quintal")
        print(f"   Price Drop: {shock['price_change_%']}%")
        print(f"\n⚠️  ADVISORY: Price has already crashed badly.")
        print(f"   If you have unsold stock — sell immediately")
        print(f"   at whatever price available.")
        print(f"   Do NOT wait — prices may drop further.")
        
    elif 'MODERATE' in shock['shock_level']:
        print(f"\n🟠 CURRENT STATUS: MODERATE PRICE SHOCK")
        print(f"   Current Price: ₹{shock['current_price']}/quintal")
        print(f"   Price Drop: {shock['price_change_%']}%")
        print(f"\n⚠️  ADVISORY: Prices are falling.")
        print(f"   Consider selling within next 2 days.")
        
    elif 'MILD' in shock['shock_level']:
        print(f"\n🟡 CURRENT STATUS: MILD PRICE DIP")
        print(f"   Current Price: ₹{shock['current_price']}/quintal")
        print(f"   Price Drop: {shock['price_change_%']}%")
        print(f"\n👀 ADVISORY: Monitor closely.")
        print(f"   Small dip — could recover in 2-3 days.")
        
    else:
        print(f"\n🟢 CURRENT STATUS: STABLE")
        print(f"   Current Price: ₹{shock['current_price']}/quintal")
        
        if len(market_risk) > 0:
            risk = market_risk.iloc[0]
            print(f"\n⚠️  WARNING: Incoming shock detected!")
            print(f"   {risk['connected_shocked_markets']} nearby")
            print(f"   markets are in severe shock")
            print(f"   Shock arrives in approximately:")
            print(f"   {risk['estimated_days_until_shock']} day(s)")
            print(f"   Risk Score: {risk['propagation_risk_score']}")
            print(f"\n🚨 ADVISORY: SELL TODAY!")
            print(f"   Price crash expected within")
            print(f"   {risk['estimated_days_until_shock']} day(s)")
            print(f"   Do not wait — sell now at")
            print(f"   current price ₹{shock['current_price']}/quintal")
        else:
            print(f"\n✅ ADVISORY: Market looks safe.")
            print(f"   No incoming shocks detected.")
            print(f"   You can hold your produce.")

else:
    print(f"\n⚠️  Market '{farmer_market}' not found in database.")
    print(f"   Please check spelling and try again.")
    print(f"\n   Available markets include:")
    print(f"   Bilsi, Gorakhpur, Ghaziabad, Bareilly,")
    print(f"   Fatehpur, Etawah, Baraut, Gonda")

print(f"\n{'='*50}")
print(f"  Powered by AgriNet-Predict GNN System")
print(f"  Data Source: AGMARKNET India")
print(f"{'='*50}")
