import pandas as pd
import sqlite3 as sql
from sqlalchemy import create_engine
import streamlit as st
import plotly.express as px

engine = create_engine("sqlite:///nba.db")

def get_player_stats(name: str, season: int, game_type: str):

    query = """
        SELECT
            PPG,
            APG,
            RPG,
            SPG,
            BPG,
            TOPG
        FROM players
        WHERE PLAYER_NAME = :name
          AND season      = :season
          AND game_type   = :game_type
        LIMIT 1
    """

    df = pd.read_sql(
        query,
        con=engine,
        params={
            "name":      name,
            "season":    season,
            "game_type": game_type
        }
    )

    if df.empty:
        raise ValueError(f"No stats for {name} in season={season}, game_type={game_type}")

    row = df.iloc[0]
    return (
        row["PPG"],
        row["APG"],
        row["RPG"],
        row["SPG"],
        row["BPG"],
        row["TOPG"]
    )

def player_overview(name: str, season: int, game_type: str):
    query = """
            SELECT * FROM players WHERE 
            season      = :season
            AND game_type  = :game_type
             order by PPG DESC
             LIMIT 10
             """
    df = pd.read_sql(query, con=engine, params={"season": season, "game_type": game_type})

    query_player = """
    SELECT * FROM players
    WHERE season  = :season
    AND game_type  = :game_type
    AND PLAYER_NAME = :name
    """

    df2 = pd.read_sql(query_player, con=engine, params={"name": name, "season": season, "game_type": game_type})

    df_combined = pd.concat([df, df2], ignore_index=True)
    df_unique = df_combined.drop_duplicates(subset="PLAYER_NAME", keep="first")

    df_unique["active"] = df_unique["PLAYER_NAME"] == name
    df_unique["color"] = df_unique["active"].map({True: "crimson", False: "lightgray"})
    df_unique = df_unique.sort_values(by=["PPG"], ascending=True)

    fig = px.bar(
        df_unique,
        x = "PPG",
        y = "PLAYER_NAME",
        orientation = "h",
        text = "PPG",
        template="plotly_dark",
        labels={"PLAYER_NAME": "Player", "PPG": "PPG", "active": ""}
    )
    fig.update_layout(showlegend=False)
    fig.update_traces(
        marker_color=df_unique["color"],
        texttemplate="%{x:.1f}",
        textposition="outside"
    )

    return fig

def player_overview_apg(name: str, season: int, game_type: str):
    query = """
            SELECT * FROM players WHERE 
            season      = :season
            AND game_type  = :game_type
             order by APG DESC
             LIMIT 10
             """
    df = pd.read_sql(query, con=engine, params={"season": season, "game_type": game_type})

    query_player = """
    SELECT * FROM players
    WHERE season  = :season
    AND game_type  = :game_type
    AND PLAYER_NAME = :name
    """

    df2 = pd.read_sql(query_player, con=engine, params={"name": name, "season": season, "game_type": game_type})

    df_combined = pd.concat([df, df2], ignore_index=True)
    df_unique = df_combined.drop_duplicates(subset="PLAYER_NAME", keep="first")

    df_unique["active"] = df_unique["PLAYER_NAME"] == name
    df_unique["color"] = df_unique["active"].map({True: "crimson", False: "lightgray"})
    df_unique = df_unique.sort_values(by=["APG"], ascending=True)

    fig = px.bar(
        df_unique,
        x = "APG",
        y = "PLAYER_NAME",
        orientation = "h",
        text = "APG",
        template="plotly_dark",
        labels={"PLAYER_NAME": "Player", "APG": "APG", "active": ""}
    )
    fig.update_layout(showlegend=False)
    fig.update_traces(
        marker_color=df_unique["color"],
        texttemplate="%{x:.1f}",
        textposition="outside"
    )

    return fig


def get_player_metric_figs(name: str, season: str, game_type: str, top_n: int = 10):
    """
    Returns a list of (metric_name, fig) for the six hard-coded metrics.
    """
    metrics = ["PPG", "APG", "RPG", "SPG", "BPG", "TOPG"]
    figs = []

    for metric in metrics:
        top_df = pd.read_sql(
            f"""
            SELECT PLAYER_NAME, {metric}
              FROM players
             WHERE season    = :season
               AND game_type = :game_type
             ORDER BY {metric} DESC
             LIMIT {top_n}
            """,
            engine,
            params={"season": season, "game_type": game_type}
        )

        stats = get_player_stats(name, season, game_type)
        stat_map = dict(zip(metrics, stats))
        player_val = stat_map[metric]
        player_row = pd.DataFrame({"PLAYER_NAME": [name], metric: [player_val]})

        df = pd.concat([top_df, player_row], ignore_index=True)
        df = df.drop_duplicates(subset="PLAYER_NAME", keep="first")
        df["active"] = df["PLAYER_NAME"] == name
        df = df.sort_values(metric, ascending=True).reset_index(drop=True)
        df["color"] = df["active"].map({True: "crimson", False: "lightgray"})

        NAMES = {
            "PPG": "PPG",
            "APG": "APG",
            "RPG": "RPG",
            "SPG": "SPG",
            "BPG": "BPG",
            "TOPG": "TOPG"
        }

        names = NAMES.get(metric, metric)
        fig = px.bar(
            df,
            x=metric,
            y="PLAYER_NAME",
            orientation="h",
            text=metric,
            template="plotly_dark",
            labels={"PLAYER_NAME": "Player", metric: names},
            title= f"Top 10 players by {names}"
        )
        fig.update_traces(
            marker_color=df["color"],
            texttemplate="%{x:.1f}",
            textposition="outside"
        )
        fig.update_layout(
            showlegend=False,
            bargap=0.15,
            margin=dict(l=50, r=50, t=70, b=20),
            width = 900,
            height = 400
        )

        figs.append((metric, fig))

    return figs


def get_team_stats(name: str, season: str, game_type: str):
    query = """
        SELECT
            W,
            L,
            FG_PCT,
            FG3_PCT,
            PPG,
            W_PCT
        FROM teams
        WHERE TEAM_NAME = :name
          AND season      = :season
          AND game_type   = :game_type
        LIMIT 1
    """
    df = pd.read_sql(
        query,
        con=engine,
        params={
            "name":      name,
            "season":    season,
            "game_type": game_type
        }
    )
    if df.empty:
        raise ValueError(f"No stats for {name} in season={season}, game_type={game_type}")

    row = df.iloc[0]
    return (
        row["W"],
        row["L"],
        row["W_PCT"],
        row["PPG"],
        row["FG_PCT"],
        row["FG3_PCT"]
    )

def get_team_metric_figs(name: str, season: str, game_type: str, top_n: int = 10):
    """
    Returns a list of (metric_name, fig) for the six hard-coded metrics.
    """
    metrics = ["W", "L", "W_PCT", "PPG", "FG_PCT", "FG3_PCT"]
    figs = []

    for metric in metrics:
        top_df = pd.read_sql(
            f"""
            SELECT TEAM_NAME, {metric}
              FROM teams
             WHERE season    = :season
               AND game_type = :game_type
             ORDER BY {metric} DESC
             LIMIT {top_n}
            """,
            engine,
            params={"season": season, "game_type": game_type}
        )

        stats = get_team_stats(name, season, game_type)
        stat_map = dict(zip(metrics, stats))
        team_val = stat_map[metric]
        team_row = pd.DataFrame({"TEAM_NAME": [name], metric: [team_val]})

        df = pd.concat([top_df, team_row], ignore_index=True)
        df = df.drop_duplicates(subset="TEAM_NAME", keep="first")
        df["active"] = df["TEAM_NAME"] == name
        df = df.sort_values(metric, ascending=True).reset_index(drop=True)
        df["color"] = df["active"].map({True: "crimson", False: "lightgray"})

        NAMES = {
            "W": "Wins",
            "L": "Losses",
            "W_PCT": "Win %",
            "PPG": "Points per game",
            "FG_PCT": " FG %",
            "FG3_PCT": "3PT %"
        }

        names = NAMES.get(metric, metric)
        fig = px.bar(
            df,
            x=metric,
            y="TEAM_NAME",
            orientation="h",
            text=metric,
            template="plotly_dark",
            labels={"TEAM_NAME": "Team", metric: names},
            title=f"Top 10 teams by {names}"
        )
        fig.update_traces(
            marker_color=df["color"],
            textposition="outside"
        )
        fig.update_layout(
            showlegend=False,
            bargap=0.15,
            margin=dict(l=50, r=50, t=70, b=20),
            width = 900,
            height = 400
        )

        figs.append((metric, fig))

    return figs

