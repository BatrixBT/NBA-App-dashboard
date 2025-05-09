from nba_api.stats.endpoints import LeagueDashPlayerStats
import pandas as pd
import sqlite3
import time

con = sqlite3.connect('nba.db')

seasons = ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]

game_types = ["Regular Season", "Playoffs"]

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

            players_df['season'] = season
            players_df['game_type'] = game_type

            players_df['PPG'] = players_df['PTS'] / players_df['GP']
            players_df['APG'] = players_df['AST'] / players_df['GP']
            players_df['RPG'] = players_df['REB'] / players_df['GP']
            players_df['SPG'] = players_df['STL'] / players_df['GP']
            players_df['BPG'] = players_df['BLK'] / players_df['GP']
            players_df['TOPG'] = players_df['TOV'] / players_df['GP']

            cols_to_round = ['PPG', 'APG', 'RPG', 'SPG', 'BPG', 'TOPG']
            players_df[cols_to_round] = players_df[cols_to_round].round(1)

            all_players_df = pd.concat([all_players_df, players_df], ignore_index=True)

            print(f"Fetched {len(players_df)} players for {season} ({game_type}).")
            time.sleep(1)
        except Exception as e:
            print(f"Failed to fetch {game_type} for season {season}: {e}")

print("Inserting all data into database...")
all_players_df.to_sql('players', con, if_exists='replace', index=False)

con.close()

print("✅ All seasons and game types inserted successfully!")