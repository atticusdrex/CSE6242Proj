import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from datetime import datetime
import requests
from bs4 import BeautifulSoup 

# Read the CSV file containing player stats
df = pd.read_csv('filtered_last_10_games.csv')

# Function to scrape player odds
def scrape_line():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    categories = [
        'player-points&subcategory=points',
        'player-rebounds&subcategory=rebounds',
        'player-assists&subcategory=assists',
        'player-defense&subcategory=blocks',
        'player-defense&subcategory=steals'
    ]

    sportsbook = []

    for cat in categories:
        url = f'https://sportsbook.draftkings.com/leagues/basketball/nba?category={cat}'
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        players_data = []

        for player_wrapper in soup.select('.sportsbook-row-name__wrapper'):
            player_name = player_wrapper.find('span', class_='sportsbook-row-name').text.strip()
            player_data = {
                'player_name': player_name,
                'odds': []
            }

            outcome_cells = player_wrapper.find_parent('th').find_next_siblings('td')
            for cell in outcome_cells:
                line_element = cell.find('span', class_='sportsbook-outcome-cell__line')
                odds_element = cell.find('span', class_='sportsbook-odds american default-color')

                if line_element is not None and odds_element is not None:
                    line = line_element.text.strip()
                    odds = odds_element.text.strip()

                    player_data['odds'].append({
                        'line': line,
                        'odds': odds
                    })

            players_data.append(player_data)
        sportsbook.append(players_data)

    table_dict = {
        'PTS': {},
        'REB': {},
        'AST': {},
        'BLK': {},
        'STL': {}
    }

    for (i, category) in enumerate(table_dict.keys()):
        for player_dict in sportsbook[i]:
            table_dict[category][player_dict['player_name']] = {
                'over': player_dict['odds'][0] if player_dict['odds'] else None,
                'under': player_dict['odds'][1] if len(player_dict['odds']) > 1 else None
            }

    return table_dict

# Scrape player odds data
scraped_data = scrape_line()

# Get the list of players and available stats
players = df['PLAYER_NAME'].unique().tolist()
stats = df.columns[1:].tolist()  # Exclude the first column ('PLAYER_NAME')

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div([
    html.H1("NBA Player Statistics"),
    dcc.Dropdown(
        id="player-dropdown",
        options=[{'label': player, 'value': player} for player in players],
        value=players[0],  # Default value is the first player
        clearable=False,
        style={'width': '50%'}
    ),
    dcc.Dropdown(
        id="stat-dropdown",
        options=[{'label': stat, 'value': stat} for stat in stats],
        value=stats[0],  # Default value is the first stat
        clearable=False,
        style={'width': '50%'}
    ),
    html.Div(id='selected-odds'),
    dcc.Graph(id='player-stats-graph')
])

# Callback to update the over/under odds based on selected player and stat
@app.callback(
    Output('selected-odds', 'children'),
    [Input('player-dropdown', 'value'),
     Input('stat-dropdown', 'value')]
)
def update_odds(selected_player, selected_stat):
    if selected_player in scraped_data[selected_stat]:
        player_odds = scraped_data[selected_stat][selected_player]['over']
        return html.Div(f"Over Odds for {selected_player}: {player_odds}")
    else:
        return html.Div("No odds available for selected player and stat.")

# Callback to update the graph based on selected player and stat
@app.callback(
    Output('player-stats-graph', 'figure'),
    [Input('player-dropdown', 'value'),
     Input('stat-dropdown', 'value')]
)
def update_graph(selected_player, selected_stat):
    # Filter data for the selected player and stat
    player_data = df[df['PLAYER_NAME'] == selected_player]

    # Create scatter plot
    fig = px.scatter(player_data, x='GAME_DATE', y=selected_stat, title=f'{selected_stat} for {selected_player} over last 10 games')
    fig.update_xaxes(title='Game Date')
    fig.update_yaxes(title=selected_stat)

    # Add today's point as a scatter point
    today = datetime.now().strftime('%Y-%m-%d')
    today_point = player_data[player_data['GAME_DATE'] == today][selected_stat]

    # Add a scatter point for today's over line
    if selected_player in scraped_data[selected_stat]:
        over_line = scraped_data[selected_stat][selected_player]['over']['line']
        if over_line is not None:
            fig.add_scatter(x=[today], y=[float(over_line)], mode='markers', marker=dict(color='green'), name=f'Today\'s Over Line')

    fig.add_scatter(x=[today], y=today_point, mode='markers', marker=dict(color='red'), name=f'Today\'s {selected_stat}')

    return fig
# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

