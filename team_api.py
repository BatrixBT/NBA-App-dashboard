from nba_api.stats.endpoints import LeagueDashTeamStats
import pandas as pd
import sqlite3
import time

# Connect to SQLite database
con = sqlite3.connect('nba.db')

# List of NBA seasons you want to pull
seasons = ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]

# Define game types
game_types = ["Regular Season", "Playoffs"]

# Create an empty DataFrame for all team data
all_teams_df = pd.DataFrame()

for season in seasons:
    for game_type in game_types:
        print(f"Fetching {game_type} team data for season {season}...")
        try:
            team_stats = LeagueDashTeamStats(
                season=season,
                season_type_all_star=game_type
            )
            teams_df = team_stats.get_data_frames()[0]

            # Add season and game_type columns
            teams_df['season'] = season
            teams_df['game_type'] = game_type

            # Append to the big DataFrame
            all_teams_df = pd.concat([all_teams_df, teams_df], ignore_index=True)

            print(f"Fetched {len(teams_df)} teams for {season} ({game_type}).")
            time.sleep(1)  # Pause between requests
        except Exception as e:
            print(f"Failed to fetch {game_type} team data for season {season}: {e}")

# Insert the combined DataFrame into the 'teams' table
print("Inserting all team data into database...")
all_teams_df.to_sql('teams', con, if_exists='replace', index=False)

# Close the database connection
con.close()

print("✅ All team stats inserted successfully!")