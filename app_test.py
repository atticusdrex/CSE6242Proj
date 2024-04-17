import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go

# Read the CSV file into a DataFrame
df = pd.read_csv("Example_DS.csv")

# This long format is more suitable for plotting in Dash with Plotly
df_long = df.melt(id_vars=["Player"], var_name="Points", value_name="Probability")

# Initialize the Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        id='player-dropdown',
        options=[{'label': player, 'value': player} for player in df['Player'].unique()],
        value='Damian Lillard'  # Setting a default value
    ),
    dcc.Graph(id='probability-distribution'),
    html.Div(id='slider-output'),
    dcc.Slider(
        id='points-slider',
        min=0,
        max=50,
        step=1,
        value=26,
        marks={i: str(i) for i in range(0, 51, 5)}  # Mark every 5 points on the slider for readability
    ),
    html.Br(),
    html.Label('Amount Wagered:'),
    dcc.Input(id='bet-input', type='number', placeholder='Enter your bet amount'),
    html.Br(),
    html.Label('Odds (Decimal):'),
    dcc.Input(id='odds-input', type='number', placeholder='Enter the odds'),
    html.Br(),
    html.Div(id='expected-return-output')
])

@app.callback(
    [Output('probability-distribution', 'figure'),
     Output('slider-output', 'children'),
     Output('expected-return-output', 'children')],
    [Input('player-dropdown', 'value'),
     Input('points-slider', 'value'),
     Input('bet-input', 'value'),
     Input('odds-input', 'value')]
)
def update_graph(selected_player, selected_points, bet_amount, odds):
    filtered_df = df_long[df_long['Player'] == selected_player]
    
    # Determine the color of each bar based on its position relative to the slider value
    colors = ['red' if int(point) <= selected_points else 'green' for point in filtered_df['Points']]
    
    fig = go.Figure(data=[
        go.Bar(x=filtered_df['Points'], y=filtered_df['Probability'], marker_color=colors)
    ])
    
    fig.update_layout(title_text=f'Probability Distribution for {selected_player}', xaxis_title="Points", yaxis_title="Probability")
    
    # Calculate the sum of probabilities for points above the selected threshold
    probabilities_sum = filtered_df[filtered_df['Points'].astype(int) > selected_points]['Probability'].sum()
    output_text = f'Probability of scoring more than {selected_points} points: {probabilities_sum:.4f}'
    
    # Calculate the expected return
    if bet_amount is not None and odds is not None:
        expected_return = bet_amount * odds * probabilities_sum
        expected_return_output = f'Expected return: {expected_return:.2f}'
    else:
        expected_return_output = ''
    
    return fig, output_text, expected_return_output

if __name__ == '__main__':
    app.run_server(debug=True)








