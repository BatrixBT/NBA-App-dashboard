import sqlite3
import pandas as pd

con = sqlite3.connect('nba.db')

players_db = pd.read_sql_query("SELECT * FROM players", con)

print(players_db.head())

con.close()

