from flask import Flask, render_template, request
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import plotly

app = Flask(__name__)

# Load all data when app starts
print("Loading AgriNet-Predict data...")
shock_df = pd.read_csv('shock_status.csv')
risk_df = pd.read_csv('propagation_risk.csv')
price_df = pd.read_csv('cleaned_data.csv')
print("Data loaded successfully!")

@app.route('/')
def home():
    # Count shock statistics
    severe = len(shock_df[shock_df['shock_level'].str.contains('SEVERE')])
    moderate = len(shock_df[shock_df['shock_level'].str.contains('MODERATE')])
    mild = len(shock_df[shock_df['shock_level'].str.contains('MILD')])
    stable = len(shock_df[shock_df['shock_level'].str.contains('STABLE')])
    at_risk = len(risk_df)

    # Create shock distribution bar chart
    fig1 = go.Figure(go.Bar(
        x=['🔴 Severe', '🟠 Moderate', '🟡 Mild', '🟢 Stable'],
        y=[severe, moderate, mild, stable],
        marker_color=['red', 'orange', 'yellow', 'green']
    ))
    fig1.update_layout(
        title='Market Shock Status Across India',
        xaxis_title='Shock Level',
        yaxis_title='Number of Markets',
        plot_bgcolor='white'
    )
    chart1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

    # Top 10 most at risk markets
    top_risk = risk_df.head(10)
    fig2 = go.Figure(go.Bar(
        x=top_risk['at_risk_market'],
        y=top_risk['propagation_risk_score'],
        marker_color='red'
    ))
    fig2.update_layout(
        title='Top 10 Markets at Risk of Price Shock',
        xaxis_title='Market',
        yaxis_title='Risk Score',
        plot_bgcolor='white'
    )
    chart2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('home.html',
        severe=severe,
        moderate=moderate,
        mild=mild,
        stable=stable,
        at_risk=at_risk,
        chart1=chart1,
        chart2=chart2
    )

@app.route('/advisory', methods=['GET', 'POST'])
def advisory():
    advisory_result = None

    if request.method == 'POST':
        market_name = request.form.get('market')

        # Get shock status
        market_shock = shock_df[
            shock_df['market'].str.lower() == market_name.lower()
        ]

        # Get propagation risk
        market_risk = risk_df[
            risk_df['at_risk_market'].str.lower() == market_name.lower()
        ]

        if len(market_shock) > 0:
            shock = market_shock.iloc[0]
            risk_info = market_risk.iloc[0] if len(market_risk) > 0 else None

            advisory_result = {
                'market': market_name,
                'current_price': shock['current_price'],
                'average_price': shock['average_price'],
                'price_change': shock['price_change_%'],
                'shock_level': shock['shock_level'],
                'risk_info': risk_info.to_dict() if risk_info is not None else None
            }
        else:
            advisory_result = {'error': f"Market '{market_name}' not found"}

    return render_template('advisory.html',
        advisory=advisory_result
    )

@app.route('/prices')
def prices():
    # Show tomato price trend for top markets
    tomato = price_df[price_df['commodity'] == 'Tomato']
    top_markets = ['Bilsi', 'Gorakhpur', 'Ghaziabad', 
                   'Bareilly', 'Fatehpur']

    fig = go.Figure()
    for market in top_markets:
        market_data = tomato[tomato['market'] == market].copy()
        market_data['date'] = pd.to_datetime(market_data['date'])
        market_data = market_data.sort_values('date')

        if len(market_data) > 0:
            fig.add_trace(go.Scatter(
                x=market_data['date'],
                y=market_data['price'],
                name=market,
                mode='lines'
            ))

    fig.update_layout(
        title='Tomato Price Trends — Top Markets',
        xaxis_title='Date',
        yaxis_title='Price (₹/quintal)',
        plot_bgcolor='white'
    )
    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('prices.html', chart=chart)

if __name__ == '__main__':
    app.run(debug=True)
    