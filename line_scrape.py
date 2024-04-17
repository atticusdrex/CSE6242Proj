import requests
from bs4 import BeautifulSoup 
import pandas as pd

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

categories = ['player-points&subcategory=points', 'player-rebounds&subcategory=rebounds', 'player-assists&subcategory=assists', 'player-defense&subcategory=blocks', 'player-defense&subcategory=steals']

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
            line = cell.find('span', class_='sportsbook-outcome-cell__line').text.strip()
            odds = cell.find('span', class_='sportsbook-odds american default-color').text.strip()

            player_data['odds'].append({
                'line': line,
                'odds': odds
            })

        players_data.append(player_data)
    sportsbook.append(players_data)