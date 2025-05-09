from nba_api.stats.endpoints import LeagueDashPlayerStats
import pandas as pd
import sqlite3
import time

# Connect to your SQLite database
con = sqlite3.connect('nba.db')

# List of NBA seasons you want to pull
seasons = ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]

# Define the types of games you want
game_types = ["Regular Season", "Playoffs"]

# Create an empty DataFrame to store all data
all_players_df = pd.DataFrame()

for season in seasons:
    for game_type in game_types:
        print(f"Fetching {game_type} data for season {season}...")
        try:
            player_stats = LeagueDashPlayerStats(
                season=season,
                season_type_all_star=game_type
            )
            players_df = player_stats.get_data_frames()[0]

            # Add the season and game type columns
            players_df['season'] = season
            players_df['game_type'] = game_type

            # Calculate per-game stats (on this batch only!)
            players_df['PPG'] = players_df['PTS'] / players_df['GP']
            players_df['APG'] = players_df['AST'] / players_df['GP']
            players_df['RPG'] = players_df['REB'] / players_df['GP']
            players_df['SPG'] = players_df['STL'] / players_df['GP']
            players_df['BPG'] = players_df['BLK'] / players_df['GP']
            players_df['TOPG'] = players_df['TOV'] / players_df['GP']

            # Round nicely to 1 decimal place
            cols_to_round = ['PPG', 'APG', 'RPG', 'SPG', 'BPG', 'TOPG']
            players_df[cols_to_round] = players_df[cols_to_round].round(1)

            # Append to the big DataFrame
            all_players_df = pd.concat([all_players_df, players_df], ignore_index=True)

            print(f"Fetched {len(players_df)} players for {season} ({game_type}).")
            time.sleep(1)  # Be nice to the NBA servers
        except Exception as e:
            print(f"Failed to fetch {game_type} for season {season}: {e}")

# Save the combined DataFrame into the database
print("Inserting all data into database...")
all_players_df.to_sql('players', con, if_exists='replace', index=False)

# Close the database connection
con.close()

print("✅ All seasons and game types inserted successfully!")