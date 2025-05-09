import sqlite3
import pandas as pd

con = sqlite3.connect('nba.db')

# Read the entire 'players' table into a DataFrame
players_db = pd.read_sql_query("SELECT * FROM players", con)

# Show the first few rows
print(players_db.head())

# Always good to close the connection
con.close()

