from flask import Flask, render_template, request
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import plotly
import networkx as nx

app = Flask(__name__)

# Load all data when app starts
print("Loading AgriNet-Predict data...")
shock_df = pd.read_csv('shock_status.csv')
risk_df = pd.read_csv('propagation_risk.csv')
price_df = pd.read_csv('cleaned_data.csv')
edges_df = pd.read_csv('mandi_edges.csv')
print("Data loaded successfully!")

@app.route('/')
def home():
    severe = len(shock_df[shock_df['shock_level'].str.contains('SEVERE')])
    moderate = len(shock_df[shock_df['shock_level'].str.contains('MODERATE')])
    mild = len(shock_df[shock_df['shock_level'].str.contains('MILD')])
    stable = len(shock_df[shock_df['shock_level'].str.contains('STABLE')])
    at_risk = len(risk_df)

    fig1 = go.Figure(go.Bar(
        x=['Severe', 'Moderate', 'Mild', 'Stable'],
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

        market_shock = shock_df[
            shock_df['market'].str.lower() == market_name.lower()
        ]
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

    return render_template('advisory.html', advisory=advisory_result)

@app.route('/prices')
def prices():
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
        yaxis_title='Price (Rs/quintal)',
        plot_bgcolor='white'
    )
    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('prices.html', chart=chart)

@app.route('/graph')
def network_graph():

    # Get filter from URL
    filter_type = request.args.get('filter', 'top50')

    # Build full graph
    G = nx.Graph()
    for _, row in edges_df.iterrows():
        G.add_edge(row['market1'], row['market2'],
                   weight=row['correlation'])

    # Filter markets based on selection
    if filter_type == 'severe':
        # Show only severely shocked markets
        severe_markets = shock_df[
            shock_df['shock_level'].str.contains('SEVERE')
        ]['market'].tolist()
        selected = [m for m in severe_markets if m in G.nodes()]

    elif filter_type == 'atrisk':
        # Show at risk markets
        risk_markets = risk_df['at_risk_market'].tolist()
        selected = [m for m in risk_markets[:30] if m in G.nodes()]

    elif filter_type == 'all':
        # Show all markets
        selected = list(G.nodes())

    else:
        # Default — top 50 most connected markets
        degree_dict = dict(G.degree())
        sorted_markets = sorted(
            degree_dict, key=degree_dict.get, reverse=True
        )
        selected = sorted_markets[:50]

    # Build subgraph with selected markets only
    subgraph = G.subgraph(selected)

    # Layout
    pos = nx.spring_layout(subgraph, seed=42, k=1.2)

    # Build edge lines
    edge_x, edge_y = [], []
    for edge in subgraph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.8, color='#AAAAAA'),
        hoverinfo='none',
        mode='lines'
    )

    # Build nodes
    node_x, node_y = [], []
    node_text, node_hover = [], []
    node_color, node_size = [], []

    for node in subgraph.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

        market_shock = shock_df[shock_df['market'] == node]
        if len(market_shock) > 0:
            level = market_shock.iloc[0]['shock_level']
            price = market_shock.iloc[0]['current_price']
            change = market_shock.iloc[0]['price_change_%']

            if 'SEVERE' in level:
                node_color.append('red')
                node_size.append(20)
            elif 'MODERATE' in level:
                node_color.append('orange')
                node_size.append(16)
            elif 'MILD' in level:
                node_color.append('gold')
                node_size.append(14)
            else:
                node_color.append('green')
                node_size.append(12)

            node_hover.append(
                f"<b>{node}</b><br>"
                f"Status: {level}<br>"
                f"Current Price: Rs{price}/quintal<br>"
                f"Price Change: {change}%<br>"
                f"Connections: {G.degree(node)}"
            )
        else:
            node_color.append('steelblue')
            node_size.append(12)
            node_hover.append(
                f"<b>{node}</b><br>"
                f"Connections: {G.degree(node)}"
            )

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        hovertext=node_hover,
        text=node_text,
        textposition='top center',
        textfont=dict(size=9, color='#222222'),
        marker=dict(
            color=node_color,
            size=node_size,
            line=dict(width=2, color='white')
        )
    )

    title_map = {
        'top50': 'Top 50 Most Connected Mandi Markets',
        'severe': 'Severely Shocked Markets Only',
        'atrisk': 'At-Risk Markets (Incoming Shock)',
        'all': 'All 428 Markets (Full Network)'
    }

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=dict(
                text=f'AgriNet-Predict: {title_map.get(filter_type, "")}',
                font=dict(size=18)
            ),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=60),
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False
            ),
            plot_bgcolor='white',
            height=650
        )
    )

    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('graph.html',
                          chart=chart,
                          current_filter=filter_type)

    # Spring layout for positioning nodes
    pos = nx.spring_layout(G, seed=42, k=0.5)

    # Build edge lines
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#CCCCCC'),
        hoverinfo='none',
        mode='lines'
    )

    # Build nodes with colors based on shock status
    node_x, node_y = [], []
    node_text, node_hover = [], []
    node_color, node_size = [], []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

        # Get shock status for this market
        market_shock = shock_df[shock_df['market'] == node]
        if len(market_shock) > 0:
            level = market_shock.iloc[0]['shock_level']
            price = market_shock.iloc[0]['current_price']
            change = market_shock.iloc[0]['price_change_%']

            if 'SEVERE' in level:
                node_color.append('red')
                node_size.append(16)
            elif 'MODERATE' in level:
                node_color.append('orange')
                node_size.append(14)
            elif 'MILD' in level:
                node_color.append('gold')
                node_size.append(12)
            else:
                node_color.append('green')
                node_size.append(10)

            node_hover.append(
                f"Market: {node}<br>"
                f"Status: {level}<br>"
                f"Current Price: Rs{price}/quintal<br>"
                f"Price Change: {change}%"
            )
        else:
            node_color.append('steelblue')
            node_size.append(10)
            node_hover.append(f"Market: {node}")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        hovertext=node_hover,
        text=node_text,
        textposition='top center',
        textfont=dict(size=7, color='#333333'),
        marker=dict(
            color=node_color,
            size=node_size,
            line=dict(width=1.5, color='white')
        )
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=dict(
                text='AgriNet-Predict: Inter-Mandi Price Network Graph',
                font=dict(size=18)
            ),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=60),
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False
            ),
            plot_bgcolor='white',
            height=620
        )
    )

    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('graph.html', chart=chart)

if __name__ == '__main__':
    app.run(debug=True)
