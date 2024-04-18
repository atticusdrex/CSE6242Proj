import pandas as pd

# Read the original CSV file
df = pd.read_csv("game_logs.csv")

# Convert GAME_DATE column to datetime
df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])

# Filter data for this year
this_year = pd.Timestamp.now().year
df_this_year = df[df['GAME_DATE'].dt.year == this_year]

# Define columns of interest
columns_of_interest = ['PLAYER_NAME', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'GAME_DATE']

# Group by player name and select the last 10 games for each player
last_10_games = df_this_year.groupby('PLAYER_NAME').apply(lambda group: group.nlargest(10, 'GAME_DATE'))[columns_of_interest]

# Write the filtered data to a new CSV file
last_10_games.to_csv('filtered_last_10_games.csv', index=False)


