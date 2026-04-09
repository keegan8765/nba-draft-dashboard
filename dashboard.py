import streamlit as st
import duckdb
import pandas as pd

st.set_page_config(
    page_title="NBA Draft Predictor",
    page_icon="🏀",
    layout="wide",
)

@st.cache_resource
def get_connection():
    return duckdb.connect(database="curr_season.duckdb", read_only=True)

con = get_connection()

st.title("NBA Draft Predictor")
st.caption("2026 Draft Class")

search = st.text_input(
    label="Search for a player",
    placeholder="e.g. Jeremy Fears Jr.",
)

if search:
    query = """
        SELECT *
        FROM curr
        WHERE LOWER(Player) LIKE LOWER(?)
        ORDER BY Draft_Prob DESC
    """
    results = con.execute(query, [f"%{search}%"]).fetchdf()

    if results.empty:
        st.warning("No players found. Try a different name or partial name.")
    else:
        st.success(f"Found {len(results)} player(s)")
        selected_name = st.selectbox(
            "Select a player",
            options=results["Player"].tolist(),
        )
        player = results[results["Player"] == selected_name].iloc[0]

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader(player["Player"])
            st.write(
                f"**Team:** {player['Team']}  |  **Position:** {player['Pos']}  |  **Class:** {player['Class']}"
            )

        with col2:
            draft_prob = float(player["Draft_Prob"])
            st.metric(
                label="Draft Probability",
                value=f"{draft_prob:.1%}",
            )

        st.divider()

        st.subheader("Season Stats")
        stat_cols = st.columns(5)

        stats = {
            "PPG": "PPG",
            "APG": "APG",
            "RPG": "RPG",
            "SPG": "SPG",
            "BPG": "BPG",
        }

        for i, (label, col_name) in enumerate(stats.items()):
            with stat_cols[i]:
                if col_name in player:
                    st.metric(label=label, value=f"{float(player[col_name]):.1f}")

        st.divider()

        st.subheader("Games")
        game_cols = st.columns(2)

        with game_cols[0]:
            if "GP" in player:
                st.metric(label="Games Played", value=int(player["GP"]))

        with game_cols[1]:
            if "GS" in player:
                st.metric(label="Games Started", value=int(player["GS"]))

        st.divider()

        st.subheader("Shooting")
        shoot_cols = st.columns(3)

        shooting_stats = {
            "FG%": "FG%",
            "3P%": "3P%",
            "FT%": "FT%",
        }

        for i, (label, col_name) in enumerate(shooting_stats.items()):
            with shoot_cols[i]:
                if col_name in player and pd.notna(player[col_name]):
                    st.metric(label=label, value=f"{float(player[col_name]):.1%}")
                else:
                    st.metric(label=label, value="N/A")

        st.divider()

        with st.expander("View all stats"):
            st.dataframe(
                player.to_frame().T,
                hide_index=True,
                use_container_width=True
            )

st.divider()
st.subheader("All Players")

all_players = con.execute("""
    SELECT Player, Team, Pos, Class, Draft_Prob, GP, GS, PPG, APG, RPG
    FROM curr
    ORDER BY Draft_Prob DESC
""").fetchdf()

st.dataframe(all_players, hide_index=True, use_container_width=True)