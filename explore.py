import pandas as pd
from sqlalchemy import create_engine
import sqlite3 as sql
import plotly.express as px
import streamlit as st

RENAME_MAP = {
    "":                "",
    "TEAM_ID":         "Team ID",
    "TEAM_NAME":       "Team Name",
    "GP":              "Games Played",
    "W":               "Wins",
    "L":               "Losses",
    "W_PCT":           "Win Percentage",
    "MIN":             "Minutes Played",
    "FGM":             "Field Goals Made",
    "FGA":             "Field Goals Attempted",
    "FG_PCT":          "Field Goal Percentage",
    "FG3M":            "3-Point Field Goals Made",
    "FG3A":            "3-Point Field Goals Attempted",
    "FG3_PCT":         "3-Point Percentage",
    "FTM":             "Free Throws Made",
    "FTA":             "Free Throws Attempted",
    "FT_PCT":          "Free Throw Percentage",
    "OREB":            "Offensive Rebounds",
    "DREB":            "Defensive Rebounds",
    "REB":             "Total Rebounds",
    "AST":             "Assists",
    "TOV":             "Turnovers",
    "STL":             "Steals",
    "BLK":             "Blocks",
    "BLKA":            "Blocks Against",
    "PF":              "Personal Fouls",
    "PFD":             "Personal Fouls Drawn",
    "PTS":             "Points",
    "PLUS_MINUS":      "Plus/Minus",
    "GP_RANK":         "Games Played Rank",
    "W_RANK":          "Wins Rank",
    "L_RANK":          "Losses Rank",
    "W_PCT_RANK":      "Win Percentage Rank",
    "MIN_RANK":        "Minutes Played Rank",
    "FGM_RANK":        "Field Goals Made Rank",
    "FGA_RANK":        "Field Goals Attempted Rank",
    "FG_PCT_RANK":     "Field Goal Percentage Rank",
    "FG3M_RANK":       "3-Point FG Made Rank",
    "FG3A_RANK":       "3-Point FG Attempted Rank",
    "FG3_PCT_RANK":    "3-Point Percentage Rank",
    "FTM_RANK":        "Free Throws Made Rank",
    "FTA_RANK":        "Free Throws Attempted Rank",
    "FT_PCT_RANK":     "Free Throw Percentage Rank",
    "OREB_RANK":       "Offensive Rebounds Rank",
    "DREB_RANK":       "Defensive Rebounds Rank",
    "REB_RANK":        "Total Rebounds Rank",
    "AST_RANK":        "Assists Rank",
    "TOV_RANK":        "Turnovers Rank",
    "STL_RANK":        "Steals Rank",
    "BLK_RANK":        "Blocks Rank",
    "BLKA_RANK":       "Blocks Against Rank",
    "PF_RANK":         "Personal Fouls Rank",
    "PFD_RANK":        "Personal Fouls Drawn Rank",
    "PTS_RANK":        "Points Rank",
    "PLUS_MINUS_RANK": "Plus/Minus Rank",
    "season":          "Season",
    "game_type":       "Game Type",
    "PPG":             "Points Per Game",
}

def rename_columns(column_list, rename_map=RENAME_MAP):
    return [rename_map.get(col, col) for col in column_list]


def create_graph(x_axis, y_axis, chart_type, df, selected_team):
    df["active"] = df["TEAM_NAME"] == selected_team
    df["marker_size"] = df["active"].map({True: 20, False: 1})

    x_label = RENAME_MAP.get(x_axis, x_axis)
    y_label = RENAME_MAP.get(y_axis, y_axis)

    if x_axis and y_axis:
        if chart_type == "Scatter":
            fig = px.scatter(df, x=x_axis, y=y_axis,
                             template="plotly_dark",
                             color="active",
                             color_discrete_map={True: "red", False: "white"},
                             hover_name="TEAM_NAME",
                             title=f"{y_label} vs {x_label} for all NBA teams",
                             labels={
                                 x_axis: x_label,
                                 y_axis: y_label,
                             },
                             symbol="active",  # use our boolean to pick symbol
                             symbol_map={True: "x", False: "circle"},  # X for selected, circle for others
                             size_max=20,
                             size="marker_size",

                             )
            fig.for_each_trace(lambda trace: trace.update(
                name="Selected Team" if trace.name == "True" else "Other Teams"
            ))

            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please select both X and Y axes to generate the chart.")



RENAME_MAP2 = {
    "PLAYER_ID": "Player ID",
    "PLAYER_NAME": "Player Name",
    "NICKNAME": "Nickname",
    "TEAM_ID": "Team ID",
    "TEAM_ABBREVIATION": "Team Abbreviation",
    "AGE": "Age",
    "GP": "Games Played",
    "W": "Wins",
    "L": "Losses",
    "W_PCT": "Win Percentage",
    "MIN": "Minutes Played",
    "FGM": "Field Goals Made",
    "FGA": "Field Goals Attempted",
    "FG_PCT": "Field Goal Percentage",
    "FG3M": "3PT Made",
    "FG3A": "3PT Attempted",
    "FG3_PCT": "3PT Percentage",
    "FTM": "Free Throws Made",
    "FTA": "Free Throws Attempted",
    "FT_PCT": "Free Throw Percentage",
    "OREB": "Offensive Rebounds",
    "DREB": "Defensive Rebounds",
    "REB": "Total Rebounds",
    "AST": "Assists",
    "TOV": "Turnovers",
    "STL": "Steals",
    "BLK": "Blocks",
    "BLKA": "Blocks Against",
    "PF": "Personal Fouls",
    "PFD": "Fouls Drawn",
    "PTS": "Points",
    "PLUS_MINUS": "Plus/Minus",
    "NBA_FANTASY_PTS": "Fantasy Points",
    "DD2": "Double-Doubles",
    "TD3": "Triple-Doubles",
    "WNBA_FANTASY_PTS": "Fantasy Points (WNBA)",
    "GP_RANK": "Games Played Rank",
    "W_RANK": "Wins Rank",
    "L_RANK": "Losses Rank",
    "W_PCT_RANK": "Win Percentage Rank",
    "MIN_RANK": "Minutes Played Rank",
    "FGM_RANK": "Field Goals Made Rank",
    "FGA_RANK": "Field Goals Attempted Rank",
    "FG_PCT_RANK": "Field Goal Percentage Rank",
    "FG3M_RANK": "3PT Made Rank",
    "FG3A_RANK": "3PT Attempted Rank",
    "FG3_PCT_RANK": "3PT Percentage Rank",
    "FTM_RANK": "Free Throws Made Rank",
    "FTA_RANK": "Free Throws Attempted Rank",
    "FT_PCT_RANK": "Free Throw Percentage Rank",
    "OREB_RANK": "Offensive Rebounds Rank",
    "DREB_RANK": "Defensive Rebounds Rank",
    "REB_RANK": "Total Rebounds Rank",
    "AST_RANK": "Assists Rank",
    "TOV_RANK": "Turnovers Rank",
    "STL_RANK": "Steals Rank",
    "BLK_RANK": "Blocks Rank",
    "BLKA_RANK": "Blocks Against Rank",
    "PF_RANK": "Personal Fouls Rank",
    "PFD_RANK": "Fouls Drawn Rank",
    "PTS_RANK": "Points Rank",
    "PLUS_MINUS_RANK": "Plus/Minus Rank",
    "NBA_FANTASY_PTS_RANK": "Fantasy Points Rank",
    "DD2_RANK": "Double-Doubles Rank",
    "TD3_RANK": "Triple-Doubles Rank",
    "WNBA_FANTASY_PTS_RANK": "Fantasy Points (WNBA) Rank",
    "season": "Season",
    "game_type": "Game Type",
    "PPG": "Points Per Game",
    "APG": "Assists Per Game",
    "RPG": "Rebounds Per Game",
    "SPG": "Steals Per Game",
    "BPG": "Blocks Per Game",
    "TOPG": "Turnovers Per Game"
}


def rename_columns2(column_list, rename_map=RENAME_MAP2):
    return [rename_map.get(col, col) for col in column_list]


def create_graph2(x_axis, y_axis, chart_type, df, selected_player):
    df["active"] = df["PLAYER_NAME"] == selected_player
    df["marker_size"] = df["active"].map({True: 20, False: 1})

    x_label = RENAME_MAP2.get(x_axis, x_axis)
    y_label = RENAME_MAP2.get(y_axis, y_axis)

    if x_axis and y_axis:
        if chart_type == "Scatter":
            fig = px.scatter(df, x=x_axis, y=y_axis,
                             template="plotly_dark",
                             color="active",
                             color_discrete_map={True: "red", False: "white"},
                             hover_name="PLAYER_NAME",
                             title=f"{y_label} vs {x_label} for NBA players",
                             labels={
                                 x_axis: x_label,
                                 y_axis: y_label,
                             },
                             symbol="active",  # use our boolean to pick symbol
                             symbol_map={True: "x", False: "circle"},  # X for selected, circle for others
                             size_max=20,
                             size="marker_size",

                             )
            fig.for_each_trace(lambda trace: trace.update(
                name="Selected player" if trace.name == "True" else "Other players"
            ))

            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please select both X and Y axes to generate the chart.")

