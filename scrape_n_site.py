import requests
from bs4 import BeautifulSoup 
import sys
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

categories = ['player-points&subcategory=points', 'player-rebounds&subcategory=rebounds', 'player-assists&subcategory=assists', 'player-defense&subcategory=blocks', 'player-defense&subcategory=steals']

def scrape_line():
    sportsbook = []

    for cat in categories:
        url = f'https://sportsbook.draftkings.com/leagues/basketball/nba?category={cat}'
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        players_data = []

        for player_wrapper in soup.select('.sportsbook-row-name__wrapper'):
            player_name_tag = player_wrapper.find('span', class_='sportsbook-row-name')
            if player_name_tag:
                player_name = player_name_tag.text.strip()
                player_data = {
                    'player_name': player_name,
                    'odds': []
                }

                outcome_cells = player_wrapper.find_parent('th').find_next_siblings('td')
                for cell in outcome_cells:
                    line_tag = cell.find('span', class_='sportsbook-outcome-cell__line')
                    odds_tag = cell.find('span', class_='sportsbook-odds american default-color')
                    if line_tag and odds_tag:
                        line = line_tag.text.strip()
                        odds = odds_tag.text.strip()

                        player_data['odds'].append({
                            'line': line,
                            'odds': odds
                        })

                players_data.append(player_data)
            else:
                print(f"Warning: No player name found for category {cat}")
        sportsbook.append(players_data)

    table = sportsbook

    table_dict = {
        'PTS': {},
        'REB': {},
        'AST': {},
        'BLK': {},
        'STL': {}
    }

    for (i, category) in enumerate(table_dict.keys()):
        for player_dict in table[i]:
            if 'odds' in player_dict and len(player_dict['odds']) >= 2:
                table_dict[category][player_dict['player_name']] = {
                    'over': player_dict['odds'][0],
                    'under': player_dict['odds'][1]
                }

    return table_dict

sys.stdout.reconfigure(encoding='utf-8')
scraped_data = scrape_line()

print(scraped_data)


app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("NBA Player Statistics"),
    dcc.Dropdown(
        id="stat-dropdown",
        options=[{'label': stat, 'value': stat} for stat in scraped_data.keys()],
        value='PTS',
        clearable=False
    ),
    dcc.Dropdown(
        id="player-dropdown",
        clearable=False
    ),
    html.Div(id="player-info")
])

@app.callback(
    Output("player-dropdown", "options"),
    Input("stat-dropdown", "value")
)
def set_player_options(selected_stat):
    return [{'label': player, 'value': player} for player in scraped_data[selected_stat].keys()]

@app.callback(
    Output("player-dropdown", "value"),
    Input("player-dropdown", "options")
)
def set_player_default(options):
    return options[0]['value'] if options else None

@app.callback(
    Output("player-info", "children"),
    [Input("stat-dropdown", "value"),
     Input("player-dropdown", "value")]
)
def update_player_info(selected_stat, selected_player):
    if selected_player:
        player_info = scraped_data[selected_stat][selected_player]
        return html.Div([
            html.H3(selected_player),
            html.P(f"Over/Under: {player_info['over']['line']} / {player_info['under']['line']}"),
            html.P(f"Odds: {player_info['over']['odds']} / {player_info['under']['odds']}")
        ])
    return "Select a player"

if __name__ == "__main__":
    app.run_server(debug=True)

