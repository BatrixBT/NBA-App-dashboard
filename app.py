import streamlit as st
from sqlalchemy import create_engine
import pandas as pd

from metrics import get_player_stats, player_overview, player_overview_apg, get_player_metric_figs, get_team_stats,get_team_metric_figs
from explore import rename_columns, create_graph, RENAME_MAP, rename_columns2, create_graph2, RENAME_MAP2

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

def prev_season(season: str) -> str:
    """
    Given a season string like "2022-23", return the previous season "2021-22".
    """
    start_year = int(season.split("-")[0])
    prev_start = start_year - 1
    prev_end = start_year
    return f"{prev_start}-{str(prev_end)[-2:]}"

# — Initialize a persistent flag —
if "analysis_ready" not in st.session_state:
    st.session_state.analysis_ready = False

# — Sidebar form —
with st.sidebar.form("filter_form"):
    st.header("Stats to Display")
    stat_choice = st.radio("", ["Player stats", "Team stats"])
    st.divider()

    st.subheader("Season")
    season = st.radio("", ["2024-25","2023-24","2022-23","2021-22","2020-21"])
    st.divider()

    st.subheader("Type")
    season_type = st.radio("", ["Regular Season","Playoffs"])
    st.divider()

    # When they click this, flip our session_state flag
    if st.form_submit_button("🔍 Analyse"):
        st.session_state.analysis_ready = True

st.sidebar.divider()
st.sidebar.header("Predictive model")
st.sidebar.write("Coming soon …")

# — Main area —
if st.session_state.analysis_ready:

    st.header(f"📊 {stat_choice} — {season} ({season_type})")
    engine = create_engine("sqlite:///nba.db")

    if stat_choice == "Player stats":
        # 1) Load all players up front
        players_df = pd.read_sql(
            """
            SELECT DISTINCT PLAYER_NAME
            FROM players
            WHERE season    = :season
              AND game_type = :game_type
            ORDER BY PLAYER_NAME
            """,
            engine,
            params={"season": season, "game_type": season_type}
        )
        # 2) Prepend an empty choice
        all_players = [""] + players_df["PLAYER_NAME"].tolist()

        # 3) Single selectbox with a blank first entry
        selected_player = st.selectbox(
            "Search & select a player…",
            all_players,
            index=0,
            key="selected_player"
        )

        # 4) Only when they pick a non-blank name do we fire the stats query
        if selected_player:
            stats_df = pd.read_sql(
                """
                SELECT *
                FROM players
                WHERE season       = :season
                  AND game_type    = :game_type
                  AND PLAYER_NAME  = :player
                """,
                engine,
                params={
                    "season":    season,
                    "game_type": season_type,
                    "player":    selected_player
                }
            )


            columns_df = pd.read_sql(
                """
                SELECT DISTINCT *
                FROM players
                WHERE season       = :season
                  AND game_type    = :game_type
                  AND PLAYER_NAME  = :player
                """,
                engine,
                params={
                    "season":    season,
                    "game_type": season_type,
                    "player":    selected_player
                }
            )
            columns_list = [""] + columns_df.columns.tolist()

            tab1, tab2 = st.tabs(["Overview", "Explore"])
            with tab1:
                st.subheader(f"Current season {selected_player} stats")

                # 1) fetch current- and last-season stats (all 6 at once)
                curr = get_player_stats(selected_player, season, season_type)
                season_prev = prev_season(season)
                try:
                    prev = get_player_stats(selected_player, season_prev, season_type)
                except ValueError:
                    prev = (None,) * 6

                # 2) compute a delta for each (None if missing)
                deltas = []
                for c, p in zip(curr, prev):
                    if p is None:
                        deltas.append(None)
                    else:
                        deltas.append(c - p)

                # 3) display all six metrics side by side
                labels = ["PPG", "APG", "RPG", "SPG", "BPG", "TOPG"]
                cols = st.columns(6)
                for col, label, val, delta in zip(cols, labels, curr, deltas):
                    # if delta is None, st.metric will omit the badge
                    delta_str = f"{delta:+.1f}" if delta is not None else None
                    col.metric(label, f"{val:.1f}", delta_str)
                st.caption("All metrics compare current season vs. previous season averages.")
                st.divider()

                st.subheader(" How do they rank versus top players in the league?")

                metric_figs = get_player_metric_figs(
                    selected_player, season, season_type, top_n=10
                )

                # 2) build a 3×2 grid of columns
                rows = [st.columns(2) for _ in range(3)]

                # 3) loop and place each chart
                for idx, (metric, fig) in enumerate(metric_figs):
                    row = rows[idx // 2]
                    col = row[idx % 2]
                    col.plotly_chart(fig, use_container_width=True)

                st.info("Expand the page to see the full graph.")

            with tab2:
                columns_df = pd.read_sql(
                    """
                    SELECT DISTINCT *
                    FROM players
                    WHERE season       = :season
                      AND game_type    = :game_type
                    """,
                    engine,
                    params={
                        "season": season,
                        "game_type": season_type,
                        "player": selected_player
                    }
                )

                DISPLAY_TO_INTERNAL = {disp: key for key, disp in RENAME_MAP2.items()}

                numeric_cols = (
                    columns_df
                    .select_dtypes(include=["number"])
                    .columns
                    .tolist()
                )
                numeric_cols = [c for c in numeric_cols if c != "PLAY"]

                display_cols = [""] + [RENAME_MAP2.get(c, c) for c in numeric_cols]

                players = [""] + sorted(columns_df["PLAYER_NAME"].unique().tolist())

                st.subheader("Make your own chart")
                chart_type = st.radio("Chart type", ["Scatter"], horizontal=True)

                if chart_type == "Scatter":
                    x_disp = st.selectbox("X-axis", display_cols)
                    y_disp = st.selectbox("Y-axis", display_cols)

                    x_axis = DISPLAY_TO_INTERNAL.get(x_disp, x_disp)
                    y_axis = DISPLAY_TO_INTERNAL.get(y_disp, y_disp)

                    create_graph2(x_axis, y_axis, chart_type, columns_df, selected_player)


    if stat_choice == "Team stats":

        teams_df = pd.read_sql(
            """
            SELECT DISTINCT TEAM_NAME
            FROM teams
            WHERE season    = :season
              AND game_type = :game_type
            ORDER BY TEAM_NAME
            """,
            engine,
            params={"season": season, "game_type": season_type}
        )

        all_teams = [""] + teams_df["TEAM_NAME"].tolist()

        selected_team = st.selectbox(
            "Search & select a team…",
            all_teams,
            index=0,
            key="selected_team"
        )

        if selected_team:
            stats_df = pd.read_sql(
                """
                SELECT *
                FROM teams
                WHERE season       = :season
                  AND game_type    = :game_type
                  AND TEAM_NAME  = :team
                """,
                engine,
                params={
                    "season":    season,
                    "game_type": season_type,
                    "team":    selected_team
                }
            )
            tab1, tab2 = st.tabs(["Overview", "Explore"])
            with tab1:
                st.subheader(f"Current season {selected_team} stats")

                curr = get_team_stats(selected_team, season, season_type)
                season_prev = prev_season(season)

                try:
                    prev = get_team_stats(selected_team, season_prev, season_type)
                except ValueError:
                    prev = (None,) * 6

                # 2) compute a delta for each (None if missing)
                deltas = []
                for c, p in zip(curr, prev):
                    if p is None:
                        deltas.append(None)
                    else:
                        deltas.append(c - p)

                # 3) display all six metrics side by side
                labels = ["Wins", "Losses", "Win %", "PPG", "FG %", "3PT %"]
                cols = st.columns(6)
                for col, label, val, delta in zip(cols, labels, curr, deltas):
                    # if delta is None, st.metric will omit the badge
                    delta_str = f"{delta:+.2f}" if delta is not None else None
                    col.metric(label, f"{val}", delta_str)
                st.caption("All metrics compare current season vs. previous season averages.")

                st.divider()

                st.subheader(" How do they rank versus top teams in the league?")

                metric_figs = get_team_metric_figs(
                    selected_team, season, season_type, top_n=10
                )

                # 2) build a 3×2 grid of columns
                rows = [st.columns(2) for _ in range(3)]

                # 3) loop and place each chart
                for idx, (metric, fig) in enumerate(metric_figs):
                    row = rows[idx // 2]
                    col = row[idx % 2]
                    col.plotly_chart(fig, use_container_width=True)

                st.info("Expand the page to see the full graph.")
            with tab2:
                columns_df = pd.read_sql(
                    """
                    SELECT DISTINCT *
                    FROM teams
                    WHERE season       = :season
                      AND game_type    = :game_type
                    """,
                    engine,
                    params={
                        "season": season,
                        "game_type": season_type,
                        "player": selected_team
                    }
                )
                DISPLAY_TO_INTERNAL = {disp: key for key, disp in RENAME_MAP.items()}

                numeric_cols = (
                    columns_df
                    .select_dtypes(include=["number"])
                    .columns
                    .tolist()
                )
                numeric_cols = [c for c in numeric_cols if c != "TEAM_ID"]

                display_cols = [""] + [RENAME_MAP.get(c, c) for c in numeric_cols]

                teams = [""] + sorted(columns_df["TEAM_NAME"].unique().tolist())

                st.subheader("Make your own chart")
                chart_type = st.radio("Chart type", ["Scatter"], horizontal=True)

                if chart_type == "Scatter":
                    x_disp = st.selectbox("X-axis", display_cols)
                    y_disp = st.selectbox("Y-axis", display_cols)

                    x_axis = DISPLAY_TO_INTERNAL.get(x_disp, x_disp)
                    y_axis = DISPLAY_TO_INTERNAL.get(y_disp, y_disp)

                    create_graph(x_axis, y_axis, chart_type, columns_df, selected_team)




else:
    st.info("Pick your metrics in the sidebar and click **Analyse** to load the data.")